"""Merchant plans: what a business gets, its listing and sales limits, and PayFound's platform fee on top of PayPal's."""
from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

from sqlalchemy import DateTime, String, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from .access import require_merchant_access
from .auth import Principal, current_principal
from .commerce import audit
from .database import Base, db_session
from .models import Merchant, Order, Product, utcnow


@dataclass(frozen=True)
class Plan:
    id: str
    name: str
    monthly_cents: int
    listing_limit: int | None
    monthly_sales_cents: int | None  # captured sales per calendar month; None = unlimited
    platform_fee_bps: int           # PayFound fee in basis points, charged on top of PayPal processing
    pos_registers: int | None
    features: tuple[str, ...] = field(default_factory=tuple)


PLANS: dict[str, Plan] = {p.id: p for p in [
    Plan('free', 'Free', 0, 15, 5_000_00, 250, 1, (
        'Up to 15 active listings', 'Up to $5,000 captured sales a month', 'PayFound platform fee 2.5%',
        'Reserve, pay and pickup scheduling', 'PayPal sandbox payments to your own account',
        'Basic POS: 1 register, sales and card payments', 'Orders, messages and review replies', '7-day analytics')),
    Plan('pro', 'Pro', 4900, 300, 50_000_00, 150, 3, (
        'Up to 300 active listings', 'Up to $50,000 captured sales a month', 'PayFound platform fee 1.5%',
        'Everything in Free', 'POS: 3 registers with live stock sync', 'Demand forecast and pickup capacity',
        '90-day analytics and saved reports', 'Inventory count sheet and low-stock alerts')),
    Plan('diamond', 'Diamond', 19900, None, None, 75, None, (
        'Unlimited listings and sales', 'PayFound platform fee 0.75%', 'Everything in Pro',
        'POS: unlimited registers, API and signed webhooks', 'Assistant reports and custom analytics',
        'Priority placement in local discovery', 'Priority support')),
]}
DEFAULT_PLAN = 'free'


class BusinessSubscription(Base):
    __tablename__ = 'business_subscriptions'
    owner_subject: Mapped[str] = mapped_column(String(160), primary_key=True)
    plan_id: Mapped[str] = mapped_column(String(24), nullable=False, default=DEFAULT_PLAN)
    billing_note: Mapped[str] = mapped_column(String(160), nullable=False, default='')
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


def plan_for(db: Session, owner_subject: str | None) -> Plan:
    row = db.get(BusinessSubscription, owner_subject) if owner_subject else None
    return PLANS.get(row.plan_id if row else DEFAULT_PLAN, PLANS[DEFAULT_PLAN])


def owned_merchant_ids(db: Session, owner_subject: str | None) -> list[str]:
    if not owner_subject:
        return []
    return list(db.scalars(select(Merchant.id).where(Merchant.owner_subject == owner_subject)))


def usage(db: Session, owner_subject: str | None) -> dict:
    ids = owned_merchant_ids(db, owner_subject)
    if not ids:
        return {'active_listings': 0, 'month_sales_cents': 0}
    listings = db.scalar(select(func.count()).select_from(Product).where(Product.merchant_id.in_(ids), Product.active.is_(True))) or 0
    now = utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    sales = db.scalar(select(func.coalesce(func.sum(Order.amount_cents), 0)).where(
        Order.merchant_id.in_(ids), Order.payment_status == 'CAPTURED', Order.created_at >= month_start)) or 0
    return {'active_listings': int(listings), 'month_sales_cents': int(sales)}


def listing_block(db: Session, merchant: Merchant) -> str | None:
    """A message when the account's plan does not allow another active listing; None when it may add one."""
    plan = plan_for(db, merchant.owner_subject)
    if plan.listing_limit is None:
        return None
    if usage(db, merchant.owner_subject)['active_listings'] >= plan.listing_limit:
        return f'The {plan.name} plan allows {plan.listing_limit} active listings. Upgrade in Plan to add more.'
    return None


router = APIRouter()


def _plan_json(plan: Plan) -> dict:
    return {'id': plan.id, 'name': plan.name, 'monthly_cents': plan.monthly_cents, 'listing_limit': plan.listing_limit,
            'monthly_sales_cents': plan.monthly_sales_cents, 'platform_fee_bps': plan.platform_fee_bps,
            'pos_registers': plan.pos_registers, 'features': list(plan.features)}


@router.get('/merchants/{merchant_id}/subscription')
def get_subscription(merchant_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = require_merchant_access(db, p, merchant_id)
    plan = plan_for(db, merchant.owner_subject)
    return {'plan': _plan_json(plan), 'usage': usage(db, merchant.owner_subject),
            'plans': [_plan_json(x) for x in PLANS.values()], 'billing_note': 'Demo billing: plan changes take effect immediately and nothing is charged.'}


class PlanChange(BaseModel):
    plan_id: str = Field(max_length=24)


@router.post('/merchants/{merchant_id}/subscription')
def change_subscription(merchant_id: str, body: PlanChange, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = require_merchant_access(db, p, merchant_id, 'manager')
    if body.plan_id not in PLANS:
        raise HTTPException(400, 'Unknown plan')
    if not merchant.owner_subject:
        raise HTTPException(409, 'This business has no owner account to hold a plan')
    row = db.get(BusinessSubscription, merchant.owner_subject)
    if row is None:
        row = BusinessSubscription(owner_subject=merchant.owner_subject)
        db.add(row)
    row.plan_id = body.plan_id
    row.changed_at = utcnow()
    row.billing_note = 'demo'
    audit(db, p, 'subscription.changed', merchant_id, body.plan_id)
    db.commit()
    return get_subscription(merchant_id, db, p)
