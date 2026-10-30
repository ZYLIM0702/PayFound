"""Shared, fresh tenant authorization for commerce, connectors and intelligence."""
import os
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from .auth import Principal
from .models import Merchant, MerchantMembership

ROLE_LEVEL = {'staff': 1, 'manager': 2, 'owner': 3}


def merchant_role(db: Session, principal: Principal, merchant: Merchant) -> str | None:
    if principal.role == 'admin':
        return 'owner'
    if (os.getenv('DEMO_MODE', 'false').lower() == 'true'
            and principal.subject == 'demo-merchant' and merchant.id == 'm1'):
        return 'owner'
    membership = db.scalar(select(MerchantMembership).where(
        MerchantMembership.merchant_id == merchant.id,
        MerchantMembership.subject == principal.subject))
    # An explicit revoked membership takes precedence over legacy ownership.
    if membership:
        return membership.role if membership.active else None
    return 'owner' if merchant.owner_subject == principal.subject else None


def accessible_merchant_ids(db: Session, principal: Principal) -> list[str]:
    if principal.role == 'admin':
        return list(db.scalars(select(Merchant.id).order_by(Merchant.id)))
    ids = set(db.scalars(select(MerchantMembership.merchant_id).where(
        MerchantMembership.subject == principal.subject, MerchantMembership.active.is_(True))))
    ids.update(db.scalars(select(Merchant.id).where(Merchant.owner_subject == principal.subject)))
    if os.getenv('DEMO_MODE', 'false').lower() == 'true' and principal.subject == 'demo-merchant':
        ids.add('m1')
    return [mid for mid in sorted(ids) if (m := db.get(Merchant, mid)) and merchant_role(db, principal, m)]


def require_merchant_access(db: Session, principal: Principal, merchant_id: str,
                            minimum_role: str = 'staff') -> Merchant:
    if minimum_role not in ROLE_LEVEL:
        raise ValueError('Unknown minimum merchant role')
    merchant = db.get(Merchant, merchant_id)
    role = merchant_role(db, principal, merchant) if merchant else None
    if not role or ROLE_LEVEL.get(role, 0) < ROLE_LEVEL[minimum_role]:
        raise HTTPException(403, 'Not authorized for this merchant')
    return merchant
