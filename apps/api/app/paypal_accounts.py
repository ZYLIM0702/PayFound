"""Merchant PayPal sandbox account setup, shopper PayPal details, and merchant payment history."""
from __future__ import annotations
import json
import re
import time
from collections import defaultdict, deque
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from . import paypal
from .access import merchant_role, ROLE_LEVEL
from .auth import Principal, current_principal
from .connectors.security import ConnectorError, decrypt, encrypt
from .database import Base, db_session
from .models import Merchant, Order, PaymentEvent, utcnow

router = APIRouter(tags=['paypal-accounts'])
EMAIL = re.compile(r'^[^@\s]{1,64}@[^@\s]{1,120}\.[^@\s]{2,24}$')
CLIENT_ID = re.compile(r'^[A-Za-z0-9_\-]{10,160}$')
PAYPAL_ID = re.compile(r'^[A-Z0-9]{10,20}$')


class MerchantPayPalAccount(Base):
    __tablename__ = 'merchant_paypal_accounts'
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(160), nullable=False)
    secret_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    secret_hint: Mapped[str] = mapped_column(String(12), nullable=False, default='')
    receiving_email: Mapped[str] = mapped_column(String(190), nullable=False)
    paypal_merchant_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default='saved')  # saved|verified|failed
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_by: Mapped[str] = mapped_column(String(160), nullable=False, default='')
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class ShopperPayPalDetail(Base):
    """Per-user PayPal sandbox payer label. Email only, encrypted; no passwords, tokens or cards."""
    __tablename__ = 'shopper_paypal_details'
    owner_subject: Mapped[str] = mapped_column(String(160), primary_key=True)
    email_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    paypal_merchant_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class PaypalSandboxAccount(Base):
    """Pool of PayPal sandbox receiving accounts. Email and a display label only; never passwords or cards."""
    __tablename__ = 'paypal_sandbox_accounts'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    email: Mapped[str] = mapped_column(String(190), nullable=False, unique=True)
    display_label: Mapped[str] = mapped_column(String(120), nullable=False, default='')
    country: Mapped[str] = mapped_column(String(2), nullable=False, default='US')
    account_type: Mapped[str] = mapped_column(String(16), nullable=False, default='BUSINESS')
    assigned_to_subject: Mapped[str | None] = mapped_column(String(160), nullable=True)
    assigned_to_merchant_id: Mapped[str | None] = mapped_column(ForeignKey('merchants.id'), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class PaypalDemoPayment(Base):
    """Clearly labelled 'Sandbox demo' payment rows derived from demo orders. Not PayPal transactions."""
    __tablename__ = 'paypal_demo_payments'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), nullable=False, index=True)
    order_id: Mapped[str | None] = mapped_column(String(48), nullable=True)
    provider: Mapped[str] = mapped_column(String(24), nullable=False, default='paypal_sandbox')
    stage: Mapped[str] = mapped_column(String(24), nullable=False)  # captured | refunded | created
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    reference: Mapped[str] = mapped_column(String(64), nullable=False)  # SBX-DEMO-... never a PayPal id
    demo_seeded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


_hits: dict[str, deque] = defaultdict(deque)


def throttle(key: str, limit: int = 10, window: int = 60) -> None:
    now = time.monotonic()
    q = _hits[key]
    while q and q[0] < now - window:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(429, 'Too many PayPal setup requests. Wait a minute and try again.')
    q.append(now)


def _iso(v):
    return v.isoformat() + 'Z' if v else None


def mask_email(email: str) -> str:
    local, _, domain = email.partition('@')
    return f'{local[:1]}***@{domain}'


def mask_id(value: str | None) -> str | None:
    return None if not value else (value[:3] + '…' + value[-3:] if len(value) > 8 else '…' + value[-2:])


def seal(value: dict) -> str:
    try:
        return encrypt(value)
    except ConnectorError:
        raise HTTPException(503, 'Credential encryption is not configured on this server')


def unseal(value: str) -> dict:
    try:
        return decrypt(value)
    except ConnectorError:
        raise HTTPException(503, 'Stored PayPal credentials cannot be decrypted')


def merchant_or_404(db: Session, p: Principal, merchant_id: str, minimum: str = 'staff') -> tuple[Merchant, str]:
    merchant = db.get(Merchant, merchant_id)
    role = merchant_role(db, p, merchant) if merchant else None
    if not role:
        raise HTTPException(404, 'Store not found')
    if ROLE_LEVEL.get(role, 0) < ROLE_LEVEL[minimum]:
        raise HTTPException(403, 'Only the store owner can change PayPal settings')
    return merchant, role


def payee_for(db: Session, merchant_id: str) -> dict | None:
    """Orders v2 purchase_units.payee for the store's own sandbox account, else None (platform seller)."""
    acct = db.get(MerchantPayPalAccount, merchant_id)
    if not acct:
        pooled = assignment_for(db, merchant_id)
        return {'email_address': pooled.email} if pooled else None
    if acct.paypal_merchant_id:
        return {'merchant_id': acct.paypal_merchant_id}
    return {'email_address': acct.receiving_email}


def assignment_for(db: Session, merchant_id: str) -> PaypalSandboxAccount | None:
    return db.scalar(select(PaypalSandboxAccount).where(PaypalSandboxAccount.assigned_to_merchant_id == merchant_id))


def account_json(acct: MerchantPayPalAccount | None, role: str = 'owner', assigned: PaypalSandboxAccount | None = None) -> dict:
    if not acct:
        base = {'connected': False, 'can_edit': role == 'owner', 'environment': 'sandbox'}
        if assigned:  # sandbox receiving email only; there is no API secret for an assigned account
            base.update(assigned=True, status='assigned', receiving_email=assigned.email, assigned_label=assigned.display_label)
        return base
    return {'assigned': False, 'connected': True, 'can_edit': role == 'owner', 'environment': 'sandbox',
            'client_id_hint': mask_id(acct.client_id), 'secret_hint': '••••' + acct.secret_hint,
            'receiving_email': mask_email(acct.receiving_email), 'paypal_merchant_id': mask_id(acct.paypal_merchant_id),
            'status': acct.status, 'verified_at': _iso(acct.verified_at), 'updated_at': _iso(acct.updated_at)}


class AccountInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    client_id: str = Field(min_length=10, max_length=160)
    client_secret: str | None = Field(default=None, min_length=10, max_length=300, repr=False)
    receiving_email: str = Field(min_length=5, max_length=190)
    paypal_merchant_id: str | None = Field(default=None, max_length=32)


@router.get('/merchants/{merchant_id}/paypal-account')
def get_account(merchant_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    _, role = merchant_or_404(db, p, merchant_id)
    return account_json(db.get(MerchantPayPalAccount, merchant_id), role, assignment_for(db, merchant_id))


@router.put('/merchants/{merchant_id}/paypal-account')
def save_account(merchant_id: str, body: AccountInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant_or_404(db, p, merchant_id, 'owner')
    throttle(f'save:{p.subject}')
    client_id, email = body.client_id.strip(), body.receiving_email.strip().lower()
    pid = (body.paypal_merchant_id or '').strip().upper() or None
    if not CLIENT_ID.match(client_id):
        raise HTTPException(422, 'Client ID may only contain letters, numbers, - and _')
    if not EMAIL.match(email):
        raise HTTPException(422, 'Enter a valid receiving email')
    if pid and not PAYPAL_ID.match(pid):
        raise HTTPException(422, 'PayPal merchant ID is 10-20 letters/numbers')
    acct = db.get(MerchantPayPalAccount, merchant_id)
    secret = (body.client_secret or '').strip()
    if secret and re.search(r'\s', secret):
        raise HTTPException(422, 'Client secret cannot contain spaces')
    if not secret and not acct:
        raise HTTPException(422, 'Client secret is required')
    if not acct:
        acct = MerchantPayPalAccount(merchant_id=merchant_id)
        db.add(acct)
    if secret:
        acct.secret_encrypted = seal({'client_secret': secret})
        acct.secret_hint = secret[-4:]
    acct.client_id, acct.receiving_email, acct.paypal_merchant_id = client_id, email, pid
    acct.status, acct.verified_at, acct.updated_by, acct.updated_at = 'saved', None, p.subject, utcnow()
    db.commit()
    return account_json(acct)


@router.post('/merchants/{merchant_id}/paypal-account/test')
async def test_account(merchant_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant_or_404(db, p, merchant_id, 'owner')
    throttle(f'test:{p.subject}', 6)
    acct = db.get(MerchantPayPalAccount, merchant_id)
    if not acct:
        raise HTTPException(404, 'No PayPal account saved')
    secret = unseal(acct.secret_encrypted)['client_secret']
    ok = await paypal.verify_credentials(acct.client_id, secret)
    acct.status, acct.verified_at = ('verified', utcnow()) if ok else ('failed', None)
    db.commit()
    return {**account_json(acct), 'ok': ok, 'message': 'Sandbox credentials accepted by PayPal.' if ok else 'PayPal rejected these sandbox credentials.'}


@router.delete('/merchants/{merchant_id}/paypal-account')
def disconnect_account(merchant_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant_or_404(db, p, merchant_id, 'owner')
    throttle(f'save:{p.subject}')
    acct = db.get(MerchantPayPalAccount, merchant_id)
    if acct:
        db.delete(acct)
        db.commit()
    return {'connected': False}


STAGES = {'payment.provider_created': 'created', 'payment.approved': 'approved', 'payment.captured': 'captured',
          'payment.refunded': 'refunded', 'payment.refund_requested': 'refund_pending',
          'payment.provider_abandoned': 'abandoned', 'payment.failed': 'failed',
          'payment.capture_without_inventory': 'failed'}


def stage_of(kind: str) -> str | None:
    if kind in STAGES:
        return STAGES[kind]
    if kind.startswith('payment.') and kind.endswith('_uncertain'):
        return 'failed'
    return None  # demo / unrelated events are not PayPal transactions


def _details(raw: str) -> dict:
    try:
        d = json.loads(raw or '{}')
        return d if isinstance(d, dict) else {}
    except ValueError:
        return {}


DEMO_LABEL = 'Sandbox demo'


@router.get('/merchants/{merchant_id}/payments')
def payment_history(merchant_id: str, stage: str | None = None, limit: int = 100, offset: int = 0,
                    db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant_or_404(db, p, merchant_id)
    limit, offset = max(1, min(limit, 200)), max(0, offset)
    rows = db.execute(select(PaymentEvent, Order).join(Order, Order.id == PaymentEvent.order_id)
        .where(Order.merchant_id == merchant_id, PaymentEvent.event_type.like('payment.%'),
               Order.payment_mode == 'paypal_sandbox')
        .order_by(PaymentEvent.created_at.desc(), PaymentEvent.id)).all()
    items = []
    for ev, order in rows:
        st = stage_of(ev.event_type)
        if not st or (stage and st != stage):
            continue
        d = _details(ev.details)
        items.append({'id': ev.id, 'order_id': order.id, 'event_type': ev.event_type, 'stage': st,
                      'amount_cents': order.amount_cents, 'currency': order.currency,
                      'provider_order_id': d.get('provider_order_id') or order.paypal_order_id,
                      'capture_id': d.get('capture_id') or order.paypal_capture_id if st == 'captured' else None,
                      'payee': d.get('payee'), 'order_status': order.status, 'payment_status': order.payment_status,
                      'demo': False, 'label': None, 'reference': None, 'created_at': _iso(ev.created_at)})
    totals: dict[str, dict] = {}
    for status, currency, count, cents in db.execute(select(Order.payment_status, Order.currency, func.count(), func.sum(Order.amount_cents))
            .where(Order.merchant_id == merchant_id, Order.payment_mode == 'paypal_sandbox')
            .group_by(Order.payment_status, Order.currency)):
        t = totals.setdefault(currency, {'captured_cents': 0, 'refunded_cents': 0, 'pending_cents': 0, 'orders': 0})
        t['orders'] += count
        key = 'captured_cents' if status == 'CAPTURED' else 'refunded_cents' if status == 'REFUNDED' else 'pending_cents'
        t[key] += int(cents or 0)
    # Sandbox demo rows: labelled, never PayPal transactions, kept apart from the live totals.
    demo_rows = db.scalars(select(PaypalDemoPayment).where(PaypalDemoPayment.merchant_id == merchant_id)
                           .order_by(PaypalDemoPayment.created_at.desc(), PaypalDemoPayment.id)).all()
    demo_totals: dict[str, dict] = {}
    daily: dict[tuple[str, str], int] = {}
    for r in demo_rows:
        t = demo_totals.setdefault(r.currency, {'captured_cents': 0, 'refunded_cents': 0, 'pending_cents': 0, 'orders': 0})
        t['orders'] += 1
        t['captured_cents' if r.stage == 'captured' else 'refunded_cents' if r.stage == 'refunded' else 'pending_cents'] += r.amount_cents
        if r.stage == 'captured':
            k = (r.created_at.date().isoformat(), r.currency)
            daily[k] = daily.get(k, 0) + r.amount_cents
        if stage and r.stage != stage:
            continue
        items.append({'id': r.id, 'order_id': r.order_id or '', 'event_type': 'payment.' + r.stage, 'stage': r.stage,
                      'amount_cents': r.amount_cents, 'currency': r.currency, 'provider_order_id': None,
                      'capture_id': None, 'payee': None, 'order_status': '', 'payment_status': r.stage.upper(),
                      'demo': True, 'label': DEMO_LABEL, 'reference': r.reference, 'created_at': _iso(r.created_at)})
    for ev, order in rows:
        if ev.event_type == 'payment.captured':
            k = (ev.created_at.date().isoformat(), order.currency)
            daily[k] = daily.get(k, 0) + order.amount_cents
    items.sort(key=lambda x: (x['created_at'] or '', x['id']), reverse=True)
    acct = db.get(MerchantPayPalAccount, merchant_id)
    pooled = assignment_for(db, merchant_id)
    return {'items': items[offset:offset + limit], 'total': len(items), 'totals': totals, 'demo_totals': demo_totals,
            'daily': [{'day': d, 'currency': c, 'captured_cents': v} for (d, c), v in sorted(daily.items())][-45:],
            'demo_label': DEMO_LABEL, 'payee_account': bool(acct or pooled),
            'payee_email': mask_email(acct.receiving_email if acct else pooled.email) if (acct or pooled) else None,
            'payee_source': 'own_account' if acct else 'assigned_sandbox' if pooled else 'platform',
            'environment': 'sandbox'}

