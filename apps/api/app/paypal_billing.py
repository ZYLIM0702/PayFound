"""PayPal sandbox Subscriptions (plan billing) and Invoicing (per-order invoices)."""
from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime
from decimal import Decimal
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Integer, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from . import paypal
from .access import require_merchant_access
from .auth import Principal, current_principal
from .commerce import audit
from .database import Base, db_session
from .models import Merchant, Order, OrderItem, utcnow
from .plans import DEFAULT_PLAN, PLANS, BusinessSubscription

logger = logging.getLogger('payfound.billing')
router = APIRouter()
PRODUCT_NAME = 'PayFound Business'
SUB_STATES = {'APPROVAL_PENDING', 'APPROVED', 'ACTIVE', 'SUSPENDED', 'CANCELLED', 'EXPIRED'}
TERMINAL = {'CANCELLED', 'EXPIRED'}


class BillingPlan(Base):
    __tablename__ = 'billing_plans'
    plan_id: Mapped[str] = mapped_column(String(24), primary_key=True)
    paypal_product_id: Mapped[str] = mapped_column(String(80), nullable=False)
    paypal_plan_id: Mapped[str] = mapped_column(String(80), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default='USD')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class PaypalBusinessSubscription(Base):
    __tablename__ = 'business_subscriptions_paypal'
    owner_subject: Mapped[str] = mapped_column(String(160), primary_key=True)
    paypal_subscription_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(24), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='APPROVAL_PENDING')
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class OrderInvoice(Base):
    __tablename__ = 'order_invoices'
    order_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    paypal_invoice_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='PENDING')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


def _usd(cents: int) -> str:
    return str((Decimal(cents) / 100).quantize(Decimal('.01')))


def _rid(prefix: str, *parts: str) -> str:
    return prefix + hashlib.sha256('|'.join(parts).encode()).hexdigest()[:30]


def _web_base() -> str:
    return (os.getenv('PUBLIC_WEB_URL') or os.getenv('WEB_ORIGIN') or 'http://localhost:5173').rstrip('/')


async def ensure_billing_plan(db: Session, plan_id: str) -> BillingPlan:
    """Create (once) the PayPal catalog product and the monthly plan for a paid local plan."""
    plan = PLANS.get(plan_id)
    if plan is None or plan.monthly_cents <= 0:
        raise HTTPException(400, 'Choose a paid plan')
    row = db.get(BillingPlan, plan_id)
    if row and row.amount_cents == plan.monthly_cents:
        return row
    other = db.scalar(select(BillingPlan).limit(1))
    product_id = other.paypal_product_id if other else None
    if not product_id:
        product = await paypal.call('POST', '/v1/catalogs/products', {
            'name': PRODUCT_NAME, 'description': 'PayFound merchant plan (sandbox)',
            'type': 'SERVICE', 'category': 'SOFTWARE'}, 'prod-payfound-business')
        product_id = product['id']
    created = await paypal.call('POST', '/v1/billing/plans', {
        'product_id': product_id, 'name': f'PayFound {plan.name}', 'status': 'ACTIVE',
        'description': f'PayFound {plan.name} monthly plan',
        'billing_cycles': [{'frequency': {'interval_unit': 'MONTH', 'interval_count': 1}, 'tenure_type': 'REGULAR',
                            'sequence': 1, 'total_cycles': 0,
                            'pricing_scheme': {'fixed_price': {'value': _usd(plan.monthly_cents), 'currency_code': 'USD'}}}],
        'payment_preferences': {'auto_bill_outstanding': True, 'payment_failure_threshold': 2}},
        f'plan-{plan_id}-{plan.monthly_cents}', prefer='return=representation')
    if row is None:
        row = BillingPlan(plan_id=plan_id)
        db.add(row)
    row.paypal_product_id, row.paypal_plan_id = product_id, created['id']
    row.amount_cents, row.currency = plan.monthly_cents, 'USD'
    db.commit()
    return row


class SubscribeBody(BaseModel):
    plan_id: str = Field(max_length=24)


def _approval_link(data: dict) -> str | None:
    for link in data.get('links', []) or []:
        if isinstance(link, dict) and link.get('rel') == 'approve':
            return link.get('href')
    return None


def _owner(merchant: Merchant) -> str:
    if not merchant.owner_subject:
        raise HTTPException(409, 'This business has no owner account to hold a plan')
    return merchant.owner_subject


@router.post('/merchants/{merchant_id}/billing/subscribe')
async def subscribe(merchant_id: str, body: SubscribeBody, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = require_merchant_access(db, p, merchant_id, 'manager')
    owner = _owner(merchant)
    if body.plan_id not in PLANS or PLANS[body.plan_id].monthly_cents <= 0:
        raise HTTPException(400, 'Choose a paid plan')
    billing_plan = await ensure_billing_plan(db, body.plan_id)
    row = db.get(PaypalBusinessSubscription, owner)
    prev = row.paypal_subscription_id if row and row.status in TERMINAL else ''
    base = _web_base()
    data = await paypal.call('POST', '/v1/billing/subscriptions', {
        'plan_id': billing_plan.paypal_plan_id,
        'custom_id': merchant_id[:120],
        'subscriber': {'name': {'given_name': 'PayFound', 'surname': (merchant.name or 'Merchant')[:40]}},
        'application_context': {'brand_name': 'PayFound', 'user_action': 'SUBSCRIBE_NOW',
            'shipping_preference': 'NO_SHIPPING', 'return_url': f'{base}/?billing=return', 'cancel_url': f'{base}/?billing=cancel'}},
        _rid('sub-', merchant_id, body.plan_id, prev), prefer='return=representation')
    sub_id, status = data['id'], data.get('status', 'APPROVAL_PENDING')
    if row is None:
        row = PaypalBusinessSubscription(owner_subject=owner)
        db.add(row)
    row.paypal_subscription_id, row.plan_id = sub_id, body.plan_id
    row.status, row.updated_at = status if status in SUB_STATES else 'APPROVAL_PENDING', utcnow()
    audit(db, p, 'billing.subscribe_started', merchant_id, body.plan_id)
    db.commit()
    return {'subscription_id': sub_id, 'status': row.status, 'approval_url': _approval_link(data)}


def apply_status(db: Session, row: PaypalBusinessSubscription, status: str) -> None:
    """Record a PayPal subscription status and move the local plan only on ACTIVE / terminal states."""
    if status not in SUB_STATES:
        return
    row.status, row.updated_at = status, utcnow()
    local = db.get(BusinessSubscription, row.owner_subject)
    if status == 'ACTIVE' and row.plan_id in PLANS:
        if local is None:
            local = BusinessSubscription(owner_subject=row.owner_subject)
            db.add(local)
        local.plan_id, local.billing_note, local.changed_at = row.plan_id, 'paypal_sandbox', utcnow()
    elif status in TERMINAL | {'SUSPENDED'} and local is not None and local.billing_note == 'paypal_sandbox':
        local.plan_id, local.billing_note, local.changed_at = DEFAULT_PLAN, 'paypal_sandbox_ended', utcnow()


@router.get('/merchants/{merchant_id}/billing/subscription')
async def billing_subscription(merchant_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = require_merchant_access(db, p, merchant_id)
    owner = merchant.owner_subject
    local = db.get(BusinessSubscription, owner) if owner else None
    if local is not None and local.billing_note == 'demo-simulated':
        # Demo account only: reported as active without asking PayPal.
        return {'plan': local.plan_id, 'status': 'ACTIVE', 'next_billing_time': None}
    row = db.get(PaypalBusinessSubscription, owner) if owner else None
    if row is None:
        local = db.get(BusinessSubscription, owner) if owner else None
        return {'plan': local.plan_id if local else DEFAULT_PLAN, 'status': 'NONE'}
    data = await paypal.call('GET', f'/v1/billing/subscriptions/{quote(row.paypal_subscription_id, safe="")}')
    apply_status(db, row, data.get('status', row.status))
    db.commit()
    local = db.get(BusinessSubscription, owner)
    out = {'plan': local.plan_id if local else DEFAULT_PLAN, 'status': row.status, 'requested_plan': row.plan_id}
    if row.status == 'APPROVAL_PENDING' and _approval_link(data):
        out['approval_url'] = _approval_link(data)
    nxt = (data.get('billing_info') or {}).get('next_billing_time')
    if nxt:
        out['next_billing_time'] = nxt
    return out


@router.post('/merchants/{merchant_id}/billing/cancel')
async def billing_cancel(merchant_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = require_merchant_access(db, p, merchant_id, 'manager')
    row = db.get(PaypalBusinessSubscription, _owner(merchant))
    if row is None or row.status in TERMINAL:
        raise HTTPException(409, 'No active PayPal subscription to cancel')
    sid = quote(row.paypal_subscription_id, safe='')
    await paypal.call('POST', f'/v1/billing/subscriptions/{sid}/cancel', {'reason': 'Customer request'},
                      _rid('cancel-', row.paypal_subscription_id))
    confirmed = await paypal.call('GET', f'/v1/billing/subscriptions/{sid}')
    if confirmed.get('status') != 'CANCELLED':
        raise HTTPException(502, 'PayPal has not confirmed the cancellation yet; try again shortly')
    apply_status(db, row, 'CANCELLED')
    audit(db, p, 'billing.cancelled', merchant_id, row.plan_id)
    db.commit()
    local = db.get(BusinessSubscription, row.owner_subject)
    return {'plan': local.plan_id if local else DEFAULT_PLAN, 'status': 'CANCELLED'}


SUB_EVENTS = {'BILLING.SUBSCRIPTION.ACTIVATED': 'ACTIVE', 'BILLING.SUBSCRIPTION.CANCELLED': 'CANCELLED',
              'BILLING.SUBSCRIPTION.SUSPENDED': 'SUSPENDED', 'BILLING.SUBSCRIPTION.EXPIRED': 'EXPIRED'}


def handle_subscription_event(db: Session, event_type: str, resource: dict) -> bool:
    """Apply a verified BILLING.SUBSCRIPTION.* webhook. Returns True when the event type is ours."""
    status = SUB_EVENTS.get(event_type)
    if status is None:
        return False
    sid = resource.get('id') if isinstance(resource, dict) else None
    row = db.scalar(select(PaypalBusinessSubscription).where(PaypalBusinessSubscription.paypal_subscription_id == sid)) if sid else None
    if row is not None:
        apply_status(db, row, status)
        db.commit()
    return True


async def sync_order_invoice(db: Session, order_id: str) -> OrderInvoice | None:
    """Create + mark-paid the PayPal sandbox invoice for a captured order. Idempotent; raises on failure so the outbox retries."""
    order = db.get(Order, order_id)
    if order is None or order.payment_status != 'CAPTURED':
        return None
    inv = db.get(OrderInvoice, order_id)
    if order.payment_mode == 'demo':
        if inv is None:
            db.add(OrderInvoice(order_id=order_id, status='DEMO'))
            db.commit()
        return db.get(OrderInvoice, order_id)
    if inv is not None and inv.status in ('PAID', 'DEMO'):
        return inv
    if inv is None:
        inv = OrderInvoice(order_id=order_id, status='PENDING')
        db.add(inv)
        db.commit()
    merchant = db.get(Merchant, order.merchant_id)
    items = list(db.scalars(select(OrderItem).where(OrderItem.order_id == order_id)))
    cur = order.currency or 'USD'
    body = {'detail': {'invoice_number': order_id[:25], 'currency_code': cur,
                       'invoice_date': (order.created_at or utcnow()).strftime('%Y-%m-%d'),
                       'note': 'Paid via PayFound PayPal sandbox checkout'},
            'invoicer': {'business_name': (merchant.name if merchant else 'PayFound merchant')[:300]},
            'primary_recipients': [{'billing_info': {'name': {'given_name': (order.buyer_name or 'Guest')[:140]}}}],
            'items': [{'name': i.product_name[:200], 'quantity': str(i.quantity),
                       'unit_amount': {'currency_code': cur, 'value': _usd(i.unit_price_cents)}} for i in items]}
    if not items:
        raise HTTPException(409, 'Order has no items to invoice')
    if inv.paypal_invoice_id is None:
        created = await paypal.call('POST', '/v2/invoicing/invoices', body, 'inv-' + order_id)
        inv.paypal_invoice_id = created['href'].rstrip('/').rsplit('/', 1)[-1] if created.get('href') else created.get('id')
        inv.status = 'DRAFT'
        db.commit()
    iid = quote(inv.paypal_invoice_id, safe='')
    # Mark SENT without emailing anyone, then record the captured amount as paid.
    await paypal.call('POST', f'/v2/invoicing/invoices/{iid}/send',
                      {'send_to_recipient': False, 'send_to_invoicer': False}, 'invsend-' + order_id)
    await paypal.call('POST', f'/v2/invoicing/invoices/{iid}/payments',
                      {'method': 'OTHER', 'amount': {'currency_code': cur, 'value': _usd(order.amount_cents)},
                       'note': 'PayPal checkout capture'}, 'invpay-' + order_id)
    inv.status = 'PAID'
    db.commit()
    return inv


@router.get('/orders/{order_id}/invoice')
def order_invoice(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    from .main import guard_order  # late import: main imports this module
    order = db.get(Order, order_id)
    guard_order(p, order, db)
    inv = db.get(OrderInvoice, order_id)
    if inv is None and order.payment_status == 'CAPTURED' and order.payment_mode == 'demo':
        inv = OrderInvoice(order_id=order_id, status='DEMO')
        db.add(inv)
        db.commit()
    if inv is None:
        return {'status': 'PENDING'}
    return {'invoice_id': inv.paypal_invoice_id, 'status': inv.status, 'number': order_id[:25]}
