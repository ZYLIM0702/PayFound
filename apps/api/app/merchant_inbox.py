"""Merchant inbox: read and answer shopper reviews, and list the store's shopper conversations."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from .access import require_merchant_access
from .account_hub import MessageThread, clean_text, thread_json
from .auth import Principal, current_principal
from .commerce import audit
from .database import db_session
from .models import Order, OrderItem, Review, utcnow

router = APIRouter()
MAX_REPLY = 1500


class ReplyInput(BaseModel):
    body: str = Field(max_length=MAX_REPLY + 500)  # length is enforced after sanitising


def _review_json(r: Review, order: Order | None, items: list[dict]) -> dict:
    return {'id': r.id, 'rating': r.rating, 'body': r.body, 'visible': r.visible, 'order_id': r.order_id,
            'buyer_name': order.buyer_name if order else 'Shopper', 'verified_purchase': True, 'products': items,
            'order_date': order.created_at.isoformat() + 'Z' if order and order.created_at else None,
            'reply': r.reply or '', 'replied_at': r.replied_at.isoformat() + 'Z' if r.replied_at else None,
            'created_at': r.created_at.isoformat() + 'Z' if r.created_at else None}


def _items_by_order(db: Session, order_ids: list[str]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    if not order_ids:
        return out
    for item in db.scalars(select(OrderItem).where(OrderItem.order_id.in_(order_ids))):
        out.setdefault(item.order_id, []).append({'product_id': item.product_id, 'name': item.product_name, 'quantity': item.quantity})
    return out


@router.get('/merchants/{merchant_id}/reviews')
def list_reviews(merchant_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    require_merchant_access(db, p, merchant_id)
    rows = db.execute(select(Review, Order).outerjoin(Order, Order.id == Review.order_id)
                      .where(Review.merchant_id == merchant_id).order_by(desc(Review.created_at), Review.id)).all()
    rated = [r.rating for r, _ in rows]
    items = _items_by_order(db, [r.order_id for r, _ in rows])
    return {'average': round(sum(rated) / len(rated), 1) if rated else None, 'count': len(rated),
            'unanswered': sum(1 for r, _ in rows if not r.reply),
            'reviews': [_review_json(r, o, items.get(r.order_id, [])) for r, o in rows]}


@router.post('/merchants/{merchant_id}/reviews/{review_id}/reply')
def reply_review(merchant_id: str, review_id: str, body: ReplyInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    require_merchant_access(db, p, merchant_id)
    review = db.get(Review, review_id)
    if not review or review.merchant_id != merchant_id:
        raise HTTPException(404, 'Review not found')
    review.reply = clean_text(body.body, MAX_REPLY)
    review.replied_at = utcnow()
    audit(db, p, 'review.replied', review.id)
    db.commit()
    order = db.get(Order, review.order_id)
    return _review_json(review, order, _items_by_order(db, [review.order_id]).get(review.order_id, []))


@router.get('/merchants/{merchant_id}/messages')
def list_conversations(merchant_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    require_merchant_access(db, p, merchant_id)
    rows = db.scalars(select(MessageThread).where(MessageThread.merchant_id == merchant_id)
                      .order_by(desc(MessageThread.updated_at), MessageThread.id)).all()
    threads = []
    for t in rows:
        order = db.get(Order, t.order_id) if t.order_id else None
        threads.append({**thread_json(db, t), 'buyer_name': t.buyer_name or (order.buyer_name if order else 'Shopper')})
    total = db.scalar(select(func.count()).select_from(MessageThread).where(MessageThread.merchant_id == merchant_id)) or 0
    return {'threads': threads, 'count': total}
