"""Transactional commerce saga. Provider I/O always happens after committing claims."""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from types import SimpleNamespace
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import paypal, paypal_accounts
from .models import (Audit, FulfilmentProof, InventoryReservation, Merchant,
    MerchantLocation, Order, OrderItem, OutboxJob, PaymentAttempt, PaymentEvent,
    PickupBooking, PickupSlot, Product, ProviderOperation, Refund, utcnow)
from .merchant_notify import notify_reservation


def guid(prefix):
    return prefix + '_' + uuid.uuid4().hex[:24]


def demo_mode():
    return os.getenv('DEMO_MODE', 'false').lower() == 'true'


def iso(value):
    if not value:
        return None
    return value.replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')


def audit(db, actor, action, entity='', details=''):
    db.add(Audit(actor=getattr(actor, 'subject', str(actor)), action=action,
                 entity_id=entity, details=details))


def enqueue(db, kind, key, payload, available_at=None):
    job = db.scalar(select(OutboxJob).where(OutboxJob.dedupe_key == key))
    if job:
        if job.state in ('DONE', 'FAILED'):
            job.state = 'PENDING'
            job.attempts = 0
            job.available_at = available_at or utcnow()
        return job
    job = OutboxJob(id=guid('job'), kind=kind, dedupe_key=key,
                    payload=json.dumps(payload), available_at=available_at or utcnow())
    db.add(job)
    db.flush()
    return job


def event(db, order, kind, details=None, key=None):
    key = key or f'{order.id}:{kind}'
    if not db.scalar(select(PaymentEvent.id).where(PaymentEvent.dedupe_key == key)):
        db.add(PaymentEvent(id=guid('evt'), order_id=order.id, event_type=kind,
                            dedupe_key=key, details=json.dumps(details or {})))
        enqueue(db, 'domain_event', key, {'order_id': order.id, 'event_type': kind})
        if kind in ('payment.captured', 'payment.demo_captured'):
            enqueue(db, 'order_invoice', 'invoice:' + order.id, {'order_id': order.id})


EVENT_MESSAGES = {
    'payment.provider_created': 'PayPal sandbox payment started',
    'payment.provider_abandoned': 'The earlier PayPal window was closed before approval, so no money moved. A new payment was started.',
    'payment.approved': 'Payment approved in PayPal',
    'payment.captured': 'Payment captured',
    'payment.refunded': 'Payment refunded',
    'payment.refund_requested': 'Refund requested',
    'payment.failed': 'Payment needs attention',
}


def event_message(kind: str) -> str:
    """Human wording for a payment event notification (never the raw event code)."""
    if kind in EVENT_MESSAGES:
        return EVENT_MESSAGES[kind]
    if kind.endswith('_uncertain'):
        return 'PayPal has not confirmed this payment yet; it will be checked again'
    return kind.replace('.', ': ').replace('_', ' ')


def schedule_reconcile(db, order):
    enqueue(db, 'reconcile', 'reconcile:' + order.id, {'order_id': order.id},
            utcnow() + timedelta(seconds=30))


def lock_order(db: Session, order_id: str) -> Order:
    # UPDATE is a row lock on Postgres and a write lock on SQLite. Unlike a
    # read-then-write ORM mutation, it also serializes SQLite demo requests.
    changed = db.execute(update(Order).where(Order.id == order_id)
                         .values(version=Order.version + 1)
                         .execution_options(synchronize_session=False))
    if changed.rowcount != 1:
        raise HTTPException(404, 'Order not found')
    return db.get(Order, order_id, populate_existing=True)


def order_items(db, order):
    items = list(db.scalars(select(OrderItem).where(OrderItem.order_id == order.id)
                           .order_by(OrderItem.product_id)))
    if items:
        return items
    # Compatibility for orders written by the original prototype.
    prod = db.get(Product, order.product_id)
    return [SimpleNamespace(product_id=order.product_id, quantity=order.quantity,
        unit_price_cents=order.amount_cents // order.quantity,
        product_name=prod.name if prod else '', sku=prod.sku if prod else '')]


def opening(merchant, location=None, now=None):
    if merchant.status_override == 'closed':
        return False
    if location and (not location.active or location.operational_status == 'closed'):
        return False
    if location and location.operational_status == 'open':
        return True
    if merchant.status_override == 'open':
        return True
    now = now or datetime.now(timezone.utc)
    if location:
        try:
            local = now.astimezone(ZoneInfo(location.timezone))
            regular = json.loads(location.hours)
            special = json.loads(location.special_hours)
            periods = special.get(local.date().isoformat(), regular.get(str(local.weekday()), []))
            minute = local.hour * 60 + local.minute
            if local.date().isoformat() in special and not periods:
                return False
            for period in periods or []:
                start, end = period['start'], period['end']
                a = int(start[:2]) * 60 + int(start[3:])
                b = int(end[:2]) * 60 + int(end[3:])
                if (a <= minute < b) if a <= b else (minute >= a):
                    return True
            previous = local.date() - timedelta(days=1)
            previous_periods = special.get(previous.isoformat(), regular.get(str(previous.weekday()), []))
            for period in previous_periods or []:
                a = int(period['start'][:2]) * 60 + int(period['start'][3:])
                b = int(period['end'][:2]) * 60 + int(period['end'][3:])
                if a > b and minute < b:
                    return True
            return False
        except (ValueError, TypeError, KeyError, ZoneInfoNotFoundError):
            return None
    if merchant.hours == '24 hours':
        return True
    # Legacy branchless listings: never apply an invented timezone in production.
    if not demo_mode():
        return None
    local = now.astimezone(ZoneInfo('America/Los_Angeles'))
    if local.weekday() == 6 and 'Sun closed' in merchant.hours:
        return False
    times = re.findall(r'(\d{2}):(\d{2})', merchant.hours)
    if len(times) < 2:
        return None
    a, b = [int(h) * 60 + int(m) for h, m in times[:2]]
    n = local.hour * 60 + local.minute
    return a <= n < b if a <= b else n >= a or n < b


class BasketItem(BaseModel):
    product_id: str = Field(min_length=1, max_length=48)
    quantity: int = Field(default=1, ge=1, le=10, strict=True)


class ReserveInput(BaseModel):
    product_id: str | None = None
    quantity: int = Field(default=1, ge=1, le=10, strict=True)
    items: list[BasketItem] | None = Field(default=None, min_length=1, max_length=30)
    location_id: str | None = None
    idempotency_key: str = Field(min_length=8, max_length=100)
    buyer_name: str = Field(default='Local shopper', max_length=130)

    @model_validator(mode='after')
    def valid_basket(self):
        if bool(self.product_id) == bool(self.items):
            raise ValueError('Supply product_id or items, exclusively')
        ids = [x.product_id for x in self.lines()]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate product IDs are not allowed')
        return self

    def lines(self):
        return self.items or [BasketItem(product_id=self.product_id, quantity=self.quantity)]


def reserve(db, principal, body):
    lines = sorted(body.lines(), key=lambda x: x.product_id)
    existing = db.scalar(select(Order).where(Order.buyer_subject == principal.subject,
                                            Order.idempotency_key == body.idempotency_key))
    if existing:
        check_idempotency(db, existing, body)
        return existing
    products = [db.get(Product, x.product_id) for x in lines]
    if any(p is None or not p.active for p in products):
        raise HTTPException(404, 'Product unavailable')
    if any(json.loads(p.source_metadata or '{}').get('checkout_mode') == 'merchant_native' for p in products):
        raise HTTPException(409, 'This source requires merchant-native checkout. Open the store checkout from the product card.')
    if len({p.merchant_id for p in products}) != 1 or len({p.currency for p in products}) != 1:
        raise HTTPException(409, 'A basket must use one merchant and currency')
    locations = {p.location_id for p in products if p.location_id}
    if len(locations) > 1 or (body.location_id and locations and locations != {body.location_id}):
        raise HTTPException(409, 'A basket must use one branch')
    merchant_id = products[0].merchant_id
    location_id = body.location_id or next(iter(locations), None)
    location = db.get(MerchantLocation, location_id) if location_id else None
    if location_id and (not location or location.merchant_id != merchant_id or not location.active):
        raise HTTPException(409, 'Invalid pickup branch')
    merchant = db.get(Merchant, merchant_id)
    if opening(merchant, location) is False:
        raise HTTPException(409, 'Merchant is currently closed; request a different store')
    synthetic = demo_mode() and all(p.synthetic for p in products)
    if synthetic and any(utcnow() - p.stock_updated_at > timedelta(days=1) for p in products):
        raise HTTPException(409, 'Stock information is too old; merchant confirmation required')
    expires = utcnow() + timedelta(minutes=10)
    total = sum(p.price_cents * x.quantity for p, x in zip(products, lines))
    if total <= 0 or total > 2_147_483_647:
        raise HTTPException(422, 'Purchase exceeds the supported money range')
    order = Order(id=guid('ord'), merchant_id=merchant_id, location_id=location_id,
        product_id=products[0].id, quantity=sum(x.quantity for x in lines),
        amount_cents=total,
        currency=products[0].currency, buyer_subject=principal.subject, buyer_name=body.buyer_name,
        idempotency_key=body.idempotency_key, hold_expires_at=expires,
        confirmation_status='CONFIRMED' if synthetic else 'PENDING',
        expected_payee_id=os.getenv('PAYPAL_MERCHANT_ID') or os.getenv('PAYPAL_PAYEE_MERCHANT_ID') or None)
    try:
        # Insert the idempotency constraint before acquiring stock rows.
        db.add(order)
        db.flush()
        made = []
        for prod, line in zip(products, lines):
            if synthetic:
                changed = db.execute(update(Product).where(Product.id == prod.id,
                    Product.active.is_(True), Product.quantity - Product.hold_quantity >= line.quantity)
                    .values(hold_quantity=Product.hold_quantity + line.quantity))
                if changed.rowcount != 1:
                    raise HTTPException(409, 'Insufficient stock for reservation')
            elif prod.quantity - prod.hold_quantity < line.quantity:
                raise HTTPException(409, 'Listed quantity unavailable; contact the merchant')
            made.append(OrderItem(id=guid('item'), order_id=order.id, product_id=prod.id,
                product_name=prod.name, sku=prod.sku, quantity=line.quantity, unit_price_cents=prod.price_cents))
            db.add(made[-1])
            db.add(InventoryReservation(id=guid('res'), order_id=order.id, product_id=prod.id,
                quantity=line.quantity, expires_at=expires, state='HELD' if synthetic else 'PENDING_CONFIRMATION',
                source='synthetic_local' if synthetic else 'manual_confirmation',
                proof_id='demo:' + order.id if synthetic else None))
        event(db, order, 'order.reserved')
        notify_reservation(db, order, made)
        enqueue(db, 'expire', 'expire:' + order.id, {'order_id': order.id}, expires)
        audit(db, principal, 'order.reserved', order.id)
        db.commit()
        return order
    except IntegrityError:
        db.rollback()
        existing = db.scalar(select(Order).where(Order.buyer_subject == principal.subject,
                                                Order.idempotency_key == body.idempotency_key))
        if existing:
            check_idempotency(db, existing, body)
            return existing
        raise HTTPException(409, 'Reservation conflict')
    except HTTPException:
        db.rollback()
        raise


def check_idempotency(db, existing, body):
    old = sorted((x.product_id, x.quantity) for x in order_items(db, existing))
    new = sorted((x.product_id, x.quantity) for x in body.lines())
    if old != new or (body.location_id and existing.location_id != body.location_id):
        raise HTTPException(409, 'Idempotency key cannot be reused for a different purchase')


def confirm_reservation(db, order_id, principal):
    order = lock_order(db, order_id)
    if order.status != 'RESERVED' or order.payment_status != 'NOT_STARTED' or utcnow() >= order.hold_expires_at:
        raise HTTPException(409, 'Valid unpaid reservation required')
    if order.confirmation_status == 'CONFIRMED':
        return order
    for res in db.scalars(select(InventoryReservation).where(InventoryReservation.order_id == order.id)
                           .order_by(InventoryReservation.product_id)):
        if res.state != 'PENDING_CONFIRMATION':
            raise HTTPException(409, 'Invalid reservation state')
        changed = db.execute(update(Product).where(Product.id == res.product_id,
            Product.active.is_(True), Product.quantity - Product.hold_quantity >= res.quantity)
            .values(hold_quantity=Product.hold_quantity + res.quantity))
        if changed.rowcount != 1:
            db.rollback()
            raise HTTPException(409, 'Insufficient stock for confirmation')
        res.state = 'HELD'
        res.source = 'merchant_confirmation'
        res.proof_id = principal.subject + ':' + order.id
    order.confirmation_status = 'CONFIRMED'
    order.confirmed_by = principal.subject
    order.confirmed_at = utcnow()
    event(db, order, 'inventory.merchant_confirmed')
    audit(db, principal, 'inventory.merchant_confirmed', order.id)
    db.commit()
    return order


def release_booking(db, order):
    booking = db.scalar(select(PickupBooking).where(PickupBooking.order_id == order.id))
    if booking and booking.active:
        db.execute(update(PickupSlot).where(PickupSlot.id == booking.slot_id, PickupSlot.booked_count > 0)
                   .values(booked_count=PickupSlot.booked_count - 1))
        booking.active = False


def release_inventory(db, order):
    if order.hold_released or order.inventory_committed:
        return
    reservations = list(db.scalars(select(InventoryReservation).where(
        InventoryReservation.order_id == order.id).order_by(InventoryReservation.product_id)))
    for res in reservations:
        if res.state == 'HELD':
            changed = db.execute(update(Product).where(Product.id == res.product_id,
                Product.hold_quantity >= res.quantity).values(hold_quantity=Product.hold_quantity - res.quantity))
            if changed.rowcount != 1:
                raise HTTPException(409, 'Inventory hold inconsistency; operator review required')
        res.state = 'RELEASED'
    if not reservations:  # original single-item orders
        db.execute(update(Product).where(Product.id == order.product_id,
            Product.hold_quantity >= order.quantity).values(hold_quantity=Product.hold_quantity - order.quantity))
    order.hold_released = True


def expire_order(db, order_id):
    order = lock_order(db, order_id)
    if order.hold_expires_at > utcnow() or order.status != 'RESERVED':
        db.commit()
        return
    # Uncertain create/capture calls quarantine the hold until readback. A
    # timeout does not prove no provider order/payment exists.
    if order.payment_status in ('CREATING', 'CAPTURING', 'RECONCILIATION_REQUIRED'):
        schedule_reconcile(db, order)
        db.commit()
        return
    if order.payment_status in ('NOT_STARTED', 'CREATED'):
        release_inventory(db, order)
        release_booking(db, order)
        order.status = 'EXPIRED'
        order.payment_status = 'EXPIRED'
        event(db, order, 'order.expired')
    db.commit()


def expire_holds(db):
    ids = list(db.scalars(select(Order.id).where(Order.hold_expires_at <= utcnow(),
        Order.status == 'RESERVED', Order.payment_status.in_(['NOT_STARTED', 'CREATED']))))
    db.commit()
    for oid in ids:
        expire_order(db, oid)


def commit_inventory(db, order):
    if order.inventory_committed:
        return
    if order.hold_released or order.confirmation_status != 'CONFIRMED':
        raise HTTPException(409, 'Captured funds without valid stock hold; refund/reconcile required')
    for item in order_items(db, order):
        changed = db.execute(update(Product).where(Product.id == item.product_id,
            Product.hold_quantity >= item.quantity, Product.quantity >= item.quantity)
            .values(quantity=Product.quantity - item.quantity,
                    hold_quantity=Product.hold_quantity - item.quantity, stock_updated_at=utcnow()))
        if changed.rowcount != 1:
            raise HTTPException(409, 'Captured funds without valid stock hold; refund/reconcile required')
    db.execute(update(InventoryReservation).where(InventoryReservation.order_id == order.id)
               .values(state='CONSUMED'))
    order.inventory_committed = True
    order.hold_released = True


def restock(db, order):
    if order.inventory_committed and not order.inventory_restocked:
        for item in order_items(db, order):
            db.execute(update(Product).where(Product.id == item.product_id)
                       .values(quantity=Product.quantity + item.quantity))
        order.inventory_restocked = True
    elif not order.inventory_committed:
        release_inventory(db, order)
    release_booking(db, order)


def require_payable(order):
    if order.status != 'RESERVED' or order.hold_released or order.payment_status in (
            'CAPTURED', 'REFUND_PENDING', 'REFUNDED', 'REVERSED', 'EXPIRED'):
        raise HTTPException(409, 'Order no longer payable')
    if order.confirmation_status != 'CONFIRMED':
        raise HTTPException(409, 'Merchant confirmation required before payment')
    if order.hold_expires_at <= utcnow():
        raise HTTPException(409, 'Reservation expired; payment must be reconciled')


def mock_pay(db, order_id, principal):
    if not demo_mode():
        raise HTTPException(403, 'Mock payments disabled outside demo mode')
    order = lock_order(db, order_id)
    if order.payment_status == 'CAPTURED' and order.payment_mode == 'demo':
        return order
    require_payable(order)
    if order.payment_status != 'NOT_STARTED' or order.paypal_order_id:
        raise HTTPException(409, 'Provider payment may exist; reconcile before changing payment mode')
    if not all(db.get(Product, x.product_id).synthetic for x in order_items(db, order)):
        raise HTTPException(403, 'Mock payment is restricted to synthetic inventory')
    commit_inventory(db, order)
    order.status = 'PAID'
    order.payment_status = 'CAPTURED'
    order.payment_mode = 'demo'
    event(db, order, 'payment.demo_captured', {'synthetic': True})
    audit(db, principal, 'payment.demo_only', order.id, 'NO FUNDS MOVED')
    db.commit()
    return order


def money_cents(amount, currency):
    if not isinstance(amount, dict) or amount.get('currency_code') != currency:
        raise HTTPException(409, 'Provider currency mismatch')
    value = amount.get('value')
    if not isinstance(value, str) or not re.fullmatch(r'\d{1,12}\.\d{2}', value):
        raise HTTPException(409, 'Provider amount must be an exact two-decimal string')
    try:
        number = Decimal(value)
        if not number.is_finite():
            raise InvalidOperation
        return int(number * 100)
    except (InvalidOperation, ValueError, OverflowError):
        raise HTTPException(409, 'Invalid provider amount')


def parse_capture(data, order):
    if not isinstance(data, dict) or data.get('id') != order.paypal_order_id or data.get('status') != 'COMPLETED':
        raise HTTPException(409, 'PayPal order not completed; reconcile later')
    units = data.get('purchase_units') or []
    if len(units) != 1:
        raise HTTPException(409, 'Unexpected PayPal purchase units')
    unit = units[0]
    if unit.get('custom_id') not in (None, order.id) or unit.get('reference_id') not in (None, 'default', order.id):
        raise HTTPException(409, 'Provider purchase reference mismatch')
    if order.expected_payee_id and unit.get('payee', {}).get('merchant_id') != order.expected_payee_id:
        raise HTTPException(409, 'Provider payee mismatch')
    captures = unit.get('payments', {}).get('captures') or []
    if len(captures) != 1:
        raise HTTPException(409, 'Expected one full capture; manual reconciliation required')
    capture = captures[0]
    if (capture.get('status') != 'COMPLETED' or not capture.get('id')
            or money_cents(capture.get('amount'), order.currency) != order.amount_cents):
        raise HTTPException(409, 'PayPal capture missing or amount mismatch; manual reconciliation required')
    return capture['id']


def claim_operation(db, order, kind):
    op = db.scalar(select(ProviderOperation).where(ProviderOperation.order_id == order.id,
                                                  ProviderOperation.kind == kind))
    if op:
        if op.state == 'COMPLETED':
            raise HTTPException(409, 'Provider operation already completed; reconcile')
        if op.lease_until and op.lease_until > utcnow():
            raise HTTPException(409, 'Provider operation in progress; retry after reconciliation')
        # PayPal's default deduplication retention is finite. Never replay an
        # unknown write beyond the safe window with a new or expired key.
        if utcnow() - op.created_at >= timedelta(hours=6):
            raise HTTPException(409, 'Provider idempotency window elapsed; operator reconciliation required')
        op.state = 'IN_FLIGHT'
        op.lease_until = utcnow() + timedelta(seconds=120)
        op.attempts += 1
    else:
        # These IDs match the existing REST adapter's stable per-order contract.
        op = ProviderOperation(id=guid('op'), order_id=order.id, kind=kind,
            request_id=(kind.lower() + '-' + order.id)[:38], state='IN_FLIGHT',
            lease_until=utcnow() + timedelta(seconds=120))
        db.add(op)
    return op


def uncertain(db, order_id, kind, error):
    db.rollback()
    order = lock_order(db, order_id)
    op = db.scalar(select(ProviderOperation).where(ProviderOperation.order_id == order_id,
                                                  ProviderOperation.kind == kind))
    if op and op.state != 'COMPLETED':
        op.state = 'UNCERTAIN'
        op.lease_until = None
        op.last_error = type(error).__name__
        if order.payment_status not in ('REFUNDED', 'REVERSED', 'CAPTURED', 'PROVIDER_REVIEW_REQUIRED'):
            order.payment_status = 'REFUND_PENDING' if kind == 'REFUND' else 'RECONCILIATION_REQUIRED'
        event(db, order, 'payment.' + kind.lower() + '_uncertain')
        schedule_reconcile(db, order)
    db.commit()


def create_kwargs(db, order, request_id=None):
    """Extra create_order args: the store's own sandbox payee and/or a fresh request id."""
    kw = {}
    payee = paypal_accounts.payee_for(db, order.merchant_id)
    if payee:
        kw['payee'] = payee
        if payee.get('merchant_id'):
            order.expected_payee_id = payee['merchant_id']
    if request_id:
        kw['request_id'] = request_id
    return kw


def record_created(db, order_id, data, kw):
    pid = data.get('id')
    if not isinstance(pid, str) or not pid:
        raise HTTPException(502, 'PayPal did not return an order identifier')
    order = lock_order(db, order_id)
    order.paypal_order_id = pid
    if order.payment_status not in ('CAPTURED', 'REFUND_PENDING', 'REFUNDED', 'REVERSED'):
        order.payment_status = 'CREATED'
    op = db.scalar(select(ProviderOperation).where(ProviderOperation.order_id == order_id,
                                                  ProviderOperation.kind == 'CREATE'))
    op.state = 'COMPLETED'
    op.provider_id = pid
    op.lease_until = None
    attempt = db.scalar(select(PaymentAttempt).where(PaymentAttempt.order_id == order_id))
    attempt.provider_order_id = pid
    attempt.state = 'CREATED'
    payee = kw.get('payee')
    event(db, order, 'payment.provider_created', {'provider_order_id': pid,
          'payee': 'merchant_account' if payee else 'platform_sandbox'}, key=f'{order_id}:created:{pid}')
    db.commit()
    return order


async def create_payment(db, order_id):
    order = lock_order(db, order_id)
    if order.paypal_order_id:
        if order.payment_status in ('REFUNDED', 'REFUND_PENDING', 'REVERSED') or order.status != 'RESERVED':
            raise HTTPException(409, 'Order no longer payable')
        return order
    require_payable(order)
    if order.payment_mode == 'demo':
        raise HTTPException(409, 'Synthetic payment already selected')
    op = claim_operation(db, order, 'CREATE')
    kw = create_kwargs(db, order)
    attempt = db.scalar(select(PaymentAttempt).where(PaymentAttempt.order_id == order.id))
    if not attempt:
        db.add(PaymentAttempt(id=guid('pay'), order_id=order.id, amount_cents=order.amount_cents,
            currency=order.currency, expected_payee_id=order.expected_payee_id))
    order.payment_status = 'CREATING'
    order.payment_mode = 'paypal_sandbox'
    schedule_reconcile(db, order)
    db.commit()
    try:
        data = await paypal.create_order(order, **kw)
        return record_created(db, order_id, data, kw)
    except Exception as exc:
        uncertain(db, order_id, 'CREATE', exc)
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(502, 'PayPal create uncertain; reconciliation queued') from exc


RESTARTABLE = ('CREATED', 'SAVED', 'PAYER_ACTION_REQUIRED', 'VOIDED')


async def resume_payment(db, order_id):
    """Server-side readback of an unfinished PayPal order. Captures if the buyer approved it."""
    order = lock_order(db, order_id)
    if order.payment_status == 'CAPTURED' and order.payment_mode == 'paypal_sandbox':
        db.commit()
        return {'action': 'captured', 'provider_status': 'COMPLETED', 'order': order}
    if order.payment_mode != 'paypal_sandbox' or not order.paypal_order_id:
        db.commit()
        raise HTTPException(409, 'No PayPal order to resume')
    if order.payment_status in ('REFUND_PENDING', 'REFUNDED', 'REVERSED', 'PROVIDER_REVIEW_REQUIRED'):
        db.commit()
        raise HTTPException(409, 'Order no longer payable')
    pid = order.paypal_order_id
    db.commit()
    data = await paypal.get_order(pid)
    status = data.get('status') if isinstance(data, dict) and data.get('id') == pid else None
    if status == 'COMPLETED':
        return {'action': 'captured', 'provider_status': status, 'order': await reconcile_payment(db, order_id)}
    if status == 'APPROVED':
        order = lock_order(db, order_id)
        event(db, order, 'payment.approved', {'provider_order_id': pid}, key=f'{order_id}:approved:{pid}')
        db.commit()
        if order.payment_status == 'CREATED':
            order = await capture_payment(db, order_id)
        else:
            order = await reconcile_payment(db, order_id)
        return {'action': 'captured' if order.payment_status == 'CAPTURED' else 'wait',
                'provider_status': status, 'order': order}
    order = db.get(Order, order_id)
    if status in RESTARTABLE:
        return {'action': 'pay_again', 'provider_status': status, 'order': order}
    return {'action': 'wait', 'provider_status': status, 'order': order}


async def restart_payment(db, order_id):
    """Create a NEW PayPal order for the same reservation after PayPal confirms the old one was never approved."""
    order = lock_order(db, order_id)
    if order.payment_mode != 'paypal_sandbox' or not order.paypal_order_id:
        db.commit()
        raise HTTPException(409, 'No PayPal order to replace')
    require_payable(order)
    capture_op = db.scalar(select(ProviderOperation).where(ProviderOperation.order_id == order_id,
                                                          ProviderOperation.kind == 'CAPTURE'))
    if order.payment_status != 'CREATED' or capture_op or order.paypal_capture_id:
        db.commit()
        raise HTTPException(409, 'A capture may exist; reconcile instead of starting a new payment')
    old = order.paypal_order_id
    db.commit()
    data = await paypal.get_order(old)
    if not isinstance(data, dict) or data.get('id') != old or data.get('status') not in RESTARTABLE:
        raise HTTPException(409, 'PayPal order is not abandoned; resume it instead')
    order = lock_order(db, order_id)
    if order.paypal_order_id != old or order.payment_status != 'CREATED':
        db.commit()
        raise HTTPException(409, 'Payment state changed; refresh')
    op = db.scalar(select(ProviderOperation).where(ProviderOperation.order_id == order_id,
                                                  ProviderOperation.kind == 'CREATE'))
    if op.state != 'COMPLETED' or op.attempts >= 5:
        db.commit()
        raise HTTPException(409, 'Cannot start another PayPal order for this reservation')
    # A new, stable request id for the replacement order; the old order is retired, never reused.
    op.attempts += 1
    op.request_id = f'c{op.attempts}-{order.id}'[:38]
    op.state, op.provider_id, op.lease_until = 'IN_FLIGHT', None, utcnow() + timedelta(seconds=120)
    op.created_at = utcnow()  # fresh idempotency window for the new request id
    kw = create_kwargs(db, order, op.request_id)
    event(db, order, 'payment.provider_abandoned', {'provider_order_id': old, 'provider_status': data.get('status')},
          key=f'{order_id}:abandoned:{old}')
    order.paypal_order_id = None
    order.payment_status = 'CREATING'
    attempt = db.scalar(select(PaymentAttempt).where(PaymentAttempt.order_id == order_id))
    if attempt:
        attempt.provider_order_id, attempt.state = None, 'CREATING'
    schedule_reconcile(db, order)
    db.commit()
    try:
        created = await paypal.create_order(order, **kw)
        return record_created(db, order_id, created, kw)
    except Exception as exc:
        uncertain(db, order_id, 'CREATE', exc)
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(502, 'PayPal create uncertain; reconciliation queued') from exc


def apply_capture(db, order, data):
    # A delayed completed-capture event must never resurrect a refund/reversal.
    if order.payment_status in ('REFUND_PENDING', 'REFUNDED', 'REVERSED', 'PROVIDER_REVIEW_REQUIRED'):
        return order
    capture_id = parse_capture(data, order)
    if order.payment_status == 'CAPTURED':
        if order.paypal_capture_id != capture_id:
            raise HTTPException(409, 'Provider capture identity changed')
        return order
    # Atomic savepoint prevents a multi-item partial inventory decrement if a
    # later item has a missing/corrupt hold. The provider capture is still kept.
    order.paypal_capture_id = capture_id
    db.flush()
    try:
        with db.begin_nested():
            commit_inventory(db, order)
    except HTTPException:
        order.payment_status = 'RECONCILIATION_REQUIRED'
        event(db, order, 'payment.capture_without_inventory', {'capture_id': capture_id})
        schedule_reconcile(db, order)
        db.commit()
        raise
    order.payment_status = 'CAPTURED'
    order.status = 'PAID'
    attempt = db.scalar(select(PaymentAttempt).where(PaymentAttempt.order_id == order.id))
    if attempt:
        attempt.capture_id = capture_id
        attempt.state = 'CAPTURED'
    op = db.scalar(select(ProviderOperation).where(ProviderOperation.order_id == order.id,
                                                  ProviderOperation.kind == 'CAPTURE'))
    if op:
        op.state = 'COMPLETED'
        op.provider_id = capture_id
        op.lease_until = None
    event(db, order, 'payment.captured', {'capture_id': capture_id})
    return order


async def capture_payment(db, order_id):
    order = lock_order(db, order_id)
    if order.payment_status == 'CAPTURED' and order.payment_mode == 'paypal_sandbox':
        return order
    require_payable(order)
    if not order.paypal_order_id or order.payment_mode != 'paypal_sandbox':
        raise HTTPException(409, 'No PayPal order')
    if order.payment_status != 'CREATED':
        raise HTTPException(409, 'Capture state uncertain; reconcile before retrying')
    claim_operation(db, order, 'CAPTURE')
    event(db, order, 'payment.approved', {'provider_order_id': order.paypal_order_id},
          key=f'{order.id}:approved:{order.paypal_order_id}')
    order.payment_status = 'CAPTURING'
    schedule_reconcile(db, order)
    provider_id = order.paypal_order_id
    db.commit()
    try:
        data = await paypal.capture_order(provider_id, order_id)
        order = lock_order(db, order_id)
        apply_capture(db, order, data)
        db.commit()
        return order
    except Exception as exc:
        uncertain(db, order_id, 'CAPTURE', exc)
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(502, 'PayPal capture uncertain; reconciliation queued') from exc


async def hydrate_refund_response(db, order_id, data):
    """Preserve a successful write's identity before verifying its full resource."""
    provider_id = data.get('id') if isinstance(data, dict) else None
    if not isinstance(provider_id, str) or not provider_id or len(provider_id) > 80:
        raise HTTPException(409, 'Refund response has no valid resource identity')
    order = lock_order(db, order_id)
    refund = db.scalar(select(Refund).where(Refund.order_id == order_id))
    if not refund:
        raise HTTPException(409, 'No refund intent; operator reconciliation required')
    if refund.provider_refund_id and refund.provider_refund_id != provider_id:
        raise HTTPException(409, 'Provider refund identity mismatch')
    refund.provider_refund_id = provider_id
    order.paypal_refund_id = provider_id
    op = db.scalar(select(ProviderOperation).where(ProviderOperation.order_id == order_id,
                                                 ProviderOperation.kind == 'REFUND'))
    if op:
        op.state, op.provider_id, op.lease_until, op.last_error = 'COMPLETED', provider_id, None, None
    db.commit()
    if not data.get('amount'):
        data = await paypal.get_refund(provider_id)
    return data


def apply_refund(db, order, data):
    if order.payment_status == 'REFUNDED':
        return order
    refund = db.scalar(select(Refund).where(Refund.order_id == order.id))
    if not refund:
        raise HTTPException(409, 'No refund intent; operator reconciliation required')
    if not data.get('id') or data.get('status') not in ('COMPLETED', 'PENDING'):
        raise HTTPException(409, 'Refund status uncertain')
    if refund.provider_refund_id and data['id'] != refund.provider_refund_id:
        raise HTTPException(409, 'Provider refund identity mismatch')
    if money_cents(data.get('amount'), order.currency) != refund.amount_cents:
        raise HTTPException(409, 'Provider refund amount mismatch')
    refund.provider_refund_id = data['id']
    refund.state = data['status']
    order.paypal_refund_id = data['id']
    order.payment_status = 'REFUNDED' if data['status'] == 'COMPLETED' else 'REFUND_PENDING'
    if order.payment_status == 'REFUNDED':
        restock(db, order)
        order.status = 'CANCELLED'
        attempt = db.scalar(select(PaymentAttempt).where(PaymentAttempt.order_id == order.id))
        if attempt:
            attempt.state = 'REFUNDED'
        event(db, order, 'payment.refunded', {'refund_id': data['id']})
    else:
        schedule_reconcile(db, order)
    op = db.scalar(select(ProviderOperation).where(ProviderOperation.order_id == order.id,
                                                  ProviderOperation.kind == 'REFUND'))
    if op:
        op.state = 'COMPLETED'
        op.provider_id = data['id']
        op.lease_until = None
    return order


async def refund_payment(db, order_id, principal=None):
    order = lock_order(db, order_id)
    if order.payment_status == 'REFUNDED':
        return order
    if order.status == 'COLLECTED':
        raise HTTPException(409, 'Collected orders require a separate return workflow')
    if order.payment_status == 'REFUND_PENDING':
        # Public retries are read-only. The worker reconciles pending writes.
        return order
    if order.payment_status != 'CAPTURED' and not (
            order.payment_status == 'RECONCILIATION_REQUIRED' and order.paypal_capture_id):
        raise HTTPException(409, 'No verified captured payment to refund')
    if order.payment_mode == 'demo' and demo_mode():
        order.payment_status = 'REFUNDED'
        restock(db, order)
        order.status = 'CANCELLED'
        event(db, order, 'payment.demo_refunded')
        db.commit()
        return order
    if order.payment_mode != 'paypal_sandbox' or not order.paypal_capture_id:
        raise HTTPException(409, 'Unsupported payment refund path')
    claim_operation(db, order, 'REFUND')
    db.add(Refund(id=guid('rf'), order_id=order.id, capture_id=order.paypal_capture_id,
                  amount_cents=order.amount_cents, currency=order.currency))
    order.payment_status = 'REFUND_PENDING'
    event(db, order, 'payment.refund_requested')
    schedule_reconcile(db, order)
    capture_id = order.paypal_capture_id
    db.commit()
    try:
        data = await paypal.refund_capture(capture_id, order_id)
        data = await hydrate_refund_response(db, order_id, data)
        order = lock_order(db, order_id)
        apply_refund(db, order, data)
        audit(db, principal or 'worker', 'payment.refund', order.id)
        db.commit()
        return order
    except Exception as exc:
        uncertain(db, order_id, 'REFUND', exc)
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(502, 'PayPal refund uncertain; reconciliation queued') from exc


async def reconcile_payment(db, order_id):
    order = lock_order(db, order_id)
    if order.payment_status in ('REFUNDED', 'REVERSED', 'PROVIDER_REVIEW_REQUIRED'):
        db.commit()
        return order
    operations = list(db.scalars(select(ProviderOperation).where(ProviderOperation.order_id == order_id)))
    if any(op.lease_until and op.lease_until > utcnow() for op in operations):
        db.commit()
        raise HTTPException(409, 'Provider operation still in flight')
    provider_id, refund_id = order.paypal_order_id, order.paypal_refund_id
    pending_refund = order.payment_status == 'REFUND_PENDING'
    capture_id = order.paypal_capture_id
    if not provider_id:
        op = next((op for op in operations if op.kind == 'CREATE'), None)
        if not op:
            db.commit()
            raise HTTPException(409, 'No provider order')
        # Replay create with the SAME key even after local expiry, so the ID
        # can be recovered before the quarantined hold is released.
        claim_operation(db, order, 'CREATE')
        db.commit()
        try:
            kw = create_kwargs(db, order, op.request_id if op.request_id != ('create-' + order.id)[:38] else None)
            data = await paypal.create_order(order, **kw)
            if not data.get('id'):
                raise HTTPException(502, 'Missing recovered provider order')
            order = lock_order(db, order_id)
            order.paypal_order_id = data['id']
            order.payment_status = 'CREATED'
            op = db.scalar(select(ProviderOperation).where(ProviderOperation.order_id == order_id,
                                                          ProviderOperation.kind == 'CREATE'))
            op.state, op.provider_id, op.lease_until = 'COMPLETED', data['id'], None
            attempt = db.scalar(select(PaymentAttempt).where(PaymentAttempt.order_id == order_id))
            if attempt:
                attempt.provider_order_id, attempt.state = data['id'], 'CREATED'
            db.commit()
            return await reconcile_payment(db, order_id)
        except Exception as exc:
            uncertain(db, order_id, 'CREATE', exc)
            raise
    if pending_refund and not refund_id:
        # Idempotent replay recovers a lost refund response; it cannot create a
        # second logical refund. Keep the intent and use the original order ID.
        claim_operation(db, order, 'REFUND')
    db.commit()
    try:
        if pending_refund:
            if refund_id:
                data = await paypal.get_refund(refund_id)
            else:
                data = await paypal.refund_capture(capture_id, order_id)
                data = await hydrate_refund_response(db, order_id, data)
            order = lock_order(db, order_id)
            apply_refund(db, order, data)
        else:
            data = await paypal.get_order(provider_id)
            order = lock_order(db, order_id)
            if order.payment_status in ('REFUND_PENDING', 'REFUNDED', 'REVERSED', 'PROVIDER_REVIEW_REQUIRED'):
                db.commit()
                return order
            if data.get('id') != provider_id:
                raise HTTPException(409, 'Provider order identity mismatch')
            if data.get('status') == 'COMPLETED':
                apply_capture(db, order, data)
            elif data.get('status') in ('CREATED', 'SAVED', 'PAYER_ACTION_REQUIRED', 'APPROVED', 'VOIDED'):
                op = db.scalar(select(ProviderOperation).where(ProviderOperation.order_id == order_id,
                                                              ProviderOperation.kind == 'CAPTURE'))
                if op:
                    # Capture writes may have succeeded but not be visible yet.
                    # Retain the hold and retry readback; never release it on a
                    # nonterminal provider read or send a second capture here.
                    order.payment_status = 'RECONCILIATION_REQUIRED'
                    schedule_reconcile(db, order)
                else:
                    order.payment_status = 'CREATED'
            else:
                raise HTTPException(409, 'Unknown provider state; reconciliation required')
        db.commit()
        if order.payment_status == 'CREATED' and order.hold_expires_at <= utcnow():
            expire_order(db, order.id)
        return order
    except Exception as exc:
        if pending_refund and not refund_id:
            uncertain(db, order_id, 'REFUND', exc)
        else:
            db.rollback()
        raise


def cancel_order(db, order_id, principal):
    order = lock_order(db, order_id)
    if order.status == 'CANCELLED' and order.payment_status == 'CANCELLED':
        return order
    if order.payment_status not in ('NOT_STARTED', 'EXPIRED') or order.status not in ('RESERVED', 'EXPIRED'):
        raise HTTPException(409, 'Payment may exist; use merchant cancellation/refund workflow')
    release_inventory(db, order)
    release_booking(db, order)
    order.status, order.payment_status = 'CANCELLED', 'CANCELLED'
    event(db, order, 'order.cancelled')
    audit(db, principal, 'order.cancelled', order.id)
    db.commit()
    return order


def fulfil_order(db, order_id, status, principal, proof=''):
    order = lock_order(db, order_id)
    if order.payment_status != 'CAPTURED':
        raise HTTPException(409, 'Only captured, unrefunded orders can be fulfilled')
    allowed = {'PAID': ['ACCEPTED'], 'ACCEPTED': ['PREPARING'],
               'PREPARING': ['READY'], 'READY': ['COLLECTED']}
    if order.status == status:
        return order
    if status not in allowed.get(order.status, []):
        raise HTTPException(409, f'Invalid {order.status} → {status} transition; use refund for cancellation')
    order.status = status
    db.add(FulfilmentProof(id=guid('proof'), order_id=order.id, state=status,
                          actor=principal.subject, proof=proof))
    event(db, order, 'fulfilment.' + status.lower())
    audit(db, principal, 'fulfilment.' + status.lower(), order.id)
    db.commit()
    return order


def confirm_pickup(db, order_id, principal):
    """Shopper confirms they collected a READY order. The store still records READY; this only closes the loop."""
    order = lock_order(db, order_id)
    if order.status == 'COLLECTED':
        return order
    if order.payment_status != 'CAPTURED':
        raise HTTPException(409, 'Only paid orders can be confirmed as collected')
    if order.status != 'READY':
        raise HTTPException(409, 'The store has not marked this order ready yet')
    order.status = 'COLLECTED'
    db.add(FulfilmentProof(id=guid('proof'), order_id=order.id, state='COLLECTED',
                          actor=principal.subject, proof='Confirmed by shopper'))
    event(db, order, 'fulfilment.collected_by_buyer')
    audit(db, principal, 'fulfilment.collected_by_buyer', order.id)
    db.commit()
    return order


def book_pickup(db, order_id, slot_id, principal):
    order = lock_order(db, order_id)
    if order.status in ('CANCELLED', 'EXPIRED', 'COLLECTED') or order.payment_status in ('REFUND_PENDING', 'REFUNDED', 'REVERSED', 'PROVIDER_REVIEW_REQUIRED'):
        raise HTTPException(409, 'Order cannot be booked for pickup')
    if order.status == 'RESERVED' and order.hold_expires_at <= utcnow():
        raise HTTPException(409, 'Reservation expired')
    slot = db.get(PickupSlot, slot_id)
    if not slot or slot.merchant_id != order.merchant_id or (order.location_id and slot.location_id != order.location_id):
        raise HTTPException(409, 'Pickup slot belongs to a different merchant or branch')
    if slot.start_at <= utcnow():
        raise HTTPException(409, 'Pickup slot has already started')
    booking = db.scalar(select(PickupBooking).where(PickupBooking.order_id == order.id))
    if booking and booking.active and booking.slot_id == slot_id:
        return order
    # Lock involved slots in a consistent order, including rescheduling.
    ids = sorted({slot_id} | ({booking.slot_id} if booking and booking.active else set()))
    for sid in ids:
        db.execute(update(PickupSlot).where(PickupSlot.id == sid).values(booked_count=PickupSlot.booked_count))
    changed = db.execute(update(PickupSlot).where(PickupSlot.id == slot_id,
        PickupSlot.booked_count < PickupSlot.capacity).values(booked_count=PickupSlot.booked_count + 1))
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, 'Pickup slot is full')
    release_booking(db, order)
    if booking:
        booking.slot_id, booking.active = slot_id, True
    else:
        db.add(PickupBooking(id=guid('book'), order_id=order.id, slot_id=slot_id))
    order.location_id = slot.location_id
    event(db, order, 'pickup.booked', {'slot_id': slot_id}, f'{order.id}:pickup:{slot_id}:{order.version}')
    audit(db, principal, 'pickup.booked', order.id, slot_id)
    db.commit()
    return order
