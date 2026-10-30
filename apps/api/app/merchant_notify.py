"""In-app merchant notifications: every active staff member is told when a reservation needs preparing."""
from __future__ import annotations
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, desc, func, select, update
from sqlalchemy.orm import Mapped, Session, mapped_column

from .access import accessible_merchant_ids, require_merchant_access
from .auth import Principal, current_principal
from .database import Base, db_session
from .models import Merchant, MerchantMembership, Order, utcnow

router = APIRouter(tags=['merchant-notifications'])
EVENT_RESERVED = 'reservation'


class MerchantNotification(Base):
    __tablename__ = 'merchant_notifications'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), index=True)
    recipient_subject: Mapped[str] = mapped_column(String(160), index=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), index=True)
    event_type: Mapped[str] = mapped_column(String(40), default=EVENT_RESERVED)
    message: Mapped[str] = mapped_column(String(300))
    seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __table_args__ = (UniqueConstraint('order_id', 'event_type', 'recipient_subject', name='uq_merchant_notification'),)


def staff_subjects(db: Session, merchant: Merchant) -> list[str]:
    rows = list(db.scalars(select(MerchantMembership).where(MerchantMembership.merchant_id == merchant.id)))
    subjects = {m.subject for m in rows if m.active}
    revoked = {m.subject for m in rows if not m.active}
    if merchant.owner_subject and merchant.owner_subject not in revoked:
        subjects.add(merchant.owner_subject)
    if os.getenv('DEMO_MODE', 'false').lower() == 'true' and merchant.id == 'm1':
        subjects.add('demo-merchant')
    return sorted(subjects)


def notify_reservation(db: Session, order: Order, items) -> None:
    """Add (not commit) one notification per active staff member. `items` are OrderItem rows."""
    merchant = db.get(Merchant, order.merchant_id)
    if not merchant:
        return
    what = ', '.join(f'{i.quantity} × {i.product_name}' for i in items)
    message = f'New reservation: {what} for {order.buyer_name} (pickup today) — please prepare'[:300]
    for subject in staff_subjects(db, merchant):
        if db.scalar(select(MerchantNotification.id).where(MerchantNotification.order_id == order.id,
                MerchantNotification.event_type == EVENT_RESERVED, MerchantNotification.recipient_subject == subject)):
            continue
        db.add(MerchantNotification(id='mnote_' + uuid.uuid4().hex[:24], merchant_id=merchant.id,
            recipient_subject=subject, order_id=order.id, event_type=EVENT_RESERVED, message=message))


def _merchant_ids(db, p, merchant_id):
    if merchant_id:
        require_merchant_access(db, p, merchant_id)
        return [merchant_id]
    return accessible_merchant_ids(db, p)


def _iso(v):
    return v.isoformat() + 'Z' if v else None


@router.get('/merchant/notifications')
def list_notifications(merchant_id: str | None = None, db: Session = Depends(db_session),
                       p: Principal = Depends(current_principal)):
    mids = _merchant_ids(db, p, merchant_id)
    base = (MerchantNotification.recipient_subject == p.subject) & MerchantNotification.merchant_id.in_(mids)
    # Reservations that already expired or were cancelled no longer need preparing, so they do not inflate the badge.
    unread = db.scalar(select(func.count()).select_from(MerchantNotification).join(Order, Order.id == MerchantNotification.order_id)
        .where(base, MerchantNotification.seen_at.is_(None), Order.status.notin_(('EXPIRED', 'CANCELLED', 'REFUNDED'))))
    rows = db.execute(select(MerchantNotification, Order).join(Order, Order.id == MerchantNotification.order_id)
        .where(base).order_by(desc(MerchantNotification.created_at)).limit(50)).all()
    return {'unread': unread, 'notifications': [{'id': n.id, 'merchant_id': n.merchant_id, 'order_id': n.order_id,
        'event_type': n.event_type, 'message': n.message, 'seen_at': _iso(n.seen_at), 'created_at': _iso(n.created_at),
        'order_status': o.status, 'payment_status': o.payment_status, 'buyer_name': o.buyer_name,
        'quantity': o.quantity} for n, o in rows]}


@router.post('/merchant/notifications/{notification_id}/read')
def read_notification(notification_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    mids = accessible_merchant_ids(db, p)
    changed = db.execute(update(MerchantNotification).where(MerchantNotification.id == notification_id,
        MerchantNotification.recipient_subject == p.subject, MerchantNotification.merchant_id.in_(mids),
        MerchantNotification.seen_at.is_(None)).values(seen_at=utcnow()))
    if not changed.rowcount:
        exists = db.scalar(select(MerchantNotification.id).where(MerchantNotification.id == notification_id,
            MerchantNotification.recipient_subject == p.subject, MerchantNotification.merchant_id.in_(mids)))
        if not exists:
            raise HTTPException(404, 'Notification not found')
    db.commit()
    return {'ok': True}
