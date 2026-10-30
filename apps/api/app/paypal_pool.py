"""Demo-only seeder for the PayPal sandbox receiving-account pool and the m1 'Sandbox demo' payment rows."""
from __future__ import annotations
import csv
import hashlib
import os
import re
from datetime import timedelta

from sqlalchemy import select

from .models import Merchant, Order, utcnow
from .paypal_accounts import EMAIL, PaypalDemoPayment, PaypalSandboxAccount, ShopperPayPalDetail, seal

DEFAULT_CSV = '/Users/limziyang/Downloads/paypal_sandbox_20_accounts_randomized.csv'
SHOPPER = 'demo-consumer'
DEMO_MERCHANT = 'm1'
WINDOW_DAYS = 30


def _emails(path: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    try:
        with open(path, newline='', encoding='utf-8-sig') as fh:
            for row in csv.DictReader(fh):
                email = (row.get('primary_email_alias') or '').strip().lower()
                country = (row.get('country_code') or 'US').strip().upper()[:2] or 'US'
                if EMAIL.match(email) and all(email != e for e, _ in out) and (row.get('account_type') or 'BUSINESS').upper() == 'BUSINESS':
                    out.append((email, country))
    except OSError:
        return []
    return out


def _merchant_order(m: Merchant) -> tuple[int, str]:
    found = re.fullmatch(r'm(\d+)', m.id)
    return (int(found.group(1)), m.id) if found else (10**6, m.id)


def seed_paypal_pool(db, force: bool = False) -> dict:
    """Load the pool, assign one account per demo merchant (m1..m40) and the demo shopper. Returns counts only."""
    if os.getenv('DEMO_MODE', 'false').lower() != 'true':
        return {}
    if not force and os.getenv('PAYFOUND_TESTING') == '1':
        return {}
    if not db.get_bind().dialect.name == 'sqlite':
        return {}
    emails = _emails(os.getenv('PAYPAL_SANDBOX_POOL_CSV') or DEFAULT_CSV)
    if not emails:
        return {}
    existing = {a.email: a for a in db.scalars(select(PaypalSandboxAccount))}
    for i, (email, country) in enumerate(emails, 1):
        if email not in existing:
            row = PaypalSandboxAccount(id=f'pps-{i:02d}', email=email, display_label=f'Sandbox business {i:02d}', country=country)
            db.add(row)
            existing[email] = row
    db.flush()
    pool = [existing[e] for e, _ in emails]
    merchants = sorted((m for m in db.scalars(select(Merchant)) if re.fullmatch(r'm\d+', m.id)), key=_merchant_order)[:40]
    assigned = 0
    for merchant in merchants:
        if any(a.assigned_to_merchant_id == merchant.id for a in pool):
            continue
        free = next((a for a in pool if not a.assigned_to_merchant_id), None)
        if free:  # beyond the pool size, remaining merchants keep the platform sandbox seller
            free.assigned_to_merchant_id = merchant.id
            assigned += 1
    # The demo shopper's preferred payer label: the last pool account (never the demo merchant's own receiving account).
    payer = next((a for a in pool if a.assigned_to_subject == SHOPPER), None)
    first_time = payer is None
    if not payer:
        payer = next((a for a in reversed(pool) if a.assigned_to_merchant_id != DEMO_MERCHANT), pool[-1])
        payer.assigned_to_subject = SHOPPER
    db.flush()
    _link_shopper(db, payer, first_time)
    db.commit()
    return {'accounts': len(pool), 'newly_assigned': assigned}


def _link_shopper(db, payer: PaypalSandboxAccount, replace: bool = False) -> None:
    from .account_hub import PaymentMethod, mask_email, _id
    row = db.scalar(select(PaymentMethod).where(PaymentMethod.owner_subject == SHOPPER, PaymentMethod.provider == 'paypal'))
    if row and not replace:
        return  # never overwrite what the shopper chose after the first assignment
    if row:
        row.masked_email, row.status = mask_email(payer.email), 'sandbox_assigned'
    else:
        db.add(PaymentMethod(id=_id('pm'), owner_subject=SHOPPER, provider='paypal', masked_email=mask_email(payer.email), status='sandbox_assigned'))
    try:
        sealed = seal({'email': payer.email})
    except Exception:
        return
    detail = db.get(ShopperPayPalDetail, SHOPPER)
    if not detail:
        db.add(ShopperPayPalDetail(owner_subject=SHOPPER, email_encrypted=sealed))
    elif replace:
        detail.email_encrypted, detail.paypal_merchant_id = sealed, None


def seed_demo_payments(db, force: bool = False) -> int:
    """Label-only 'Sandbox demo' payment rows for m1, derived from its existing demo orders. No stock or reservation writes."""
    if os.getenv('DEMO_MODE', 'false').lower() != 'true':
        return 0
    if not force and os.getenv('PAYFOUND_TESTING') == '1':
        return 0
    if not db.get(Merchant, DEMO_MERCHANT):
        return 0
    since = utcnow() - timedelta(days=WINDOW_DAYS)
    have = set(db.scalars(select(PaypalDemoPayment.id).where(PaypalDemoPayment.merchant_id == DEMO_MERCHANT)))
    made = 0
    orders = db.scalars(select(Order).where(Order.merchant_id == DEMO_MERCHANT, Order.created_at >= since,
        Order.payment_status.in_(('CAPTURED', 'REFUNDED', 'CREATED')), Order.payment_mode != 'paypal_sandbox').order_by(Order.id))
    for o in orders:
        stage = {'CAPTURED': 'captured', 'REFUNDED': 'refunded', 'CREATED': 'created'}[o.payment_status]
        pid = 'dpay-' + o.id
        if pid in have:
            continue
        db.add(PaypalDemoPayment(id=pid, merchant_id=DEMO_MERCHANT, order_id=o.id, stage=stage, amount_cents=o.amount_cents,
                                 currency=o.currency, reference='SBX-DEMO-' + hashlib.sha1(o.id.encode()).hexdigest()[:12].upper(), created_at=o.created_at))
        made += 1
    db.commit()
    return made
