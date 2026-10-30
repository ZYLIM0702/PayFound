"""Shopper account area: wishlist, coupons (read-only demo list), reviews, delivery requests, profile."""
from __future__ import annotations
import json
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, desc, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from .auth import Principal, current_principal
from .database import Base, db_session
from .models import Merchant, Order, OrderItem, Product, Review, utcnow

router = APIRouter(tags=['account'])


class WishlistItem(Base):
    __tablename__ = 'wishlist_items'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    owner_subject: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey('products.id'), nullable=False, index=True)
    saved_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    saved_in_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __table_args__ = (UniqueConstraint('owner_subject', 'product_id', name='uq_wishlist_owner_product'),)


class DeliveryRequest(Base):
    __tablename__ = 'delivery_requests'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), nullable=False, index=True)
    owner_subject: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    provider_id: Mapped[str] = mapped_column(String(40), nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    notes: Mapped[str] = mapped_column(String(300), default='')
    status: Mapped[str] = mapped_column(String(20), default='requested')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    __table_args__ = (Index('ix_delivery_order_status', 'order_id', 'status'),)


class AccountProfile(Base):
    __tablename__ = 'account_profiles'
    owner_subject: Mapped[str] = mapped_column(String(160), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(130), default='')
    addresses: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    notifications: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


def _id(prefix: str) -> str:
    return f'{prefix}-{uuid.uuid4().hex[:20]}'


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() + 'Z' if value else None


def _available(p: Product) -> int:
    return max(0, (p.quantity or 0) - (p.hold_quantity or 0))


def wishlist_json(row: WishlistItem, p: Product, db: Session) -> dict:
    merchant = db.get(Merchant, p.merchant_id)
    in_stock = bool(p.active and _available(p) > 0)
    return {'id': row.id, 'product_id': p.id, 'name': p.name, 'merchant_id': p.merchant_id,
        'merchant_name': merchant.name if merchant else '', 'category': p.category, 'currency': p.currency,
        'image_url': p.image_url, 'image_emoji': p.image_emoji, 'active': p.active,
        'price_cents': p.price_cents, 'in_stock': in_stock, 'available_quantity': _available(p),
        'saved_price_cents': row.saved_price_cents, 'saved_in_stock': bool(row.saved_in_stock),
        'price_dropped': p.price_cents < row.saved_price_cents,
        'back_in_stock': in_stock and not row.saved_in_stock, 'created_at': _iso(row.created_at)}


class WishlistInput(BaseModel):
    product_id: str = Field(min_length=1, max_length=48)


@router.get('/me/wishlist')
def get_wishlist(db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    rows = db.scalars(select(WishlistItem).where(WishlistItem.owner_subject == p.subject)
                      .order_by(desc(WishlistItem.created_at), WishlistItem.id)).all()
    items = []
    for row in rows:
        product = db.get(Product, row.product_id)
        if product:
            items.append(wishlist_json(row, product, db))
    return {'items': items}


@router.post('/me/wishlist', status_code=201)
def add_wishlist(body: WishlistInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    product = db.get(Product, body.product_id)
    if not product or not product.active:
        raise HTTPException(404, 'Product not found')
    row = db.scalar(select(WishlistItem).where(WishlistItem.owner_subject == p.subject,
                                               WishlistItem.product_id == product.id))
    if row:
        return wishlist_json(row, product, db)
    count = len(db.scalars(select(WishlistItem.id).where(WishlistItem.owner_subject == p.subject)).all())
    if count >= 200:
        raise HTTPException(409, 'Wishlist is full (200 items)')
    row = WishlistItem(id=_id('wish'), owner_subject=p.subject, product_id=product.id,
                       saved_price_cents=product.price_cents, saved_in_stock=_available(product) > 0)
    db.add(row)
    db.commit()
    return wishlist_json(row, product, db)


@router.delete('/me/wishlist/{product_id}')
def remove_wishlist(product_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    row = db.scalar(select(WishlistItem).where(WishlistItem.owner_subject == p.subject,
                                               WishlistItem.product_id == product_id))
    if not row:
        raise HTTPException(404, 'Not on your wishlist')
    db.delete(row)
    db.commit()
    return {'removed': product_id}


def coupon_list(now: datetime | None = None) -> list[dict]:
    now = now or utcnow()
    return [
        {'code': 'FRESH10', 'title': '10% off grocery and fresh', 'detail': 'Fruit, vegetables, dairy and bakery from neighbourhood grocers.',
         'kind': 'percent', 'value': 10, 'category': 'Grocery / fresh', 'min_spend_cents': 1500, 'expires_at': _iso(now + timedelta(days=21))},
        {'code': 'FIRSTPICK', 'title': '$3 off your first pickup', 'detail': 'One-time welcome offer for new accounts.',
         'kind': 'amount', 'value': 300, 'category': 'Any store', 'min_spend_cents': 1000, 'expires_at': _iso(now + timedelta(days=45))},
        {'code': 'FOODWEEK', 'title': '15% off ready meals', 'detail': 'Hot food and prepared meals during food week.',
         'kind': 'percent', 'value': 15, 'category': 'Ready meals', 'min_spend_cents': 2000, 'expires_at': _iso(now + timedelta(days=6))},
    ]


@router.get('/me/coupons')
def get_coupons(p: Principal = Depends(current_principal)):
    return {'coupons': coupon_list(), 'applies_at_checkout': False,
            'note': 'Demo list. Checkout does not apply discounts yet, so codes are informational only and no price changes.'}


@router.get('/me/reviews')
def my_reviews(db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    rows = db.scalars(select(Review).where(Review.buyer_subject == p.subject).order_by(desc(Review.created_at))).all()
    out = []
    for r in rows:
        order = db.get(Order, r.order_id)
        merchant = db.get(Merchant, r.merchant_id)
        item = db.scalar(select(OrderItem).where(OrderItem.order_id == r.order_id).order_by(OrderItem.product_id))
        out.append({'id': r.id, 'order_id': r.order_id, 'merchant_id': r.merchant_id,
            'merchant_name': merchant.name if merchant else '', 'rating': r.rating, 'body': r.body,
            'product_name': item.product_name if item else '', 'created_at': _iso(r.created_at),
            'visible': r.visible, 'amount_cents': order.amount_cents if order else None})
    return {'reviews': out}


DELIVERY_PROVIDERS = [
    {'id': 'lalamove', 'name': 'Lalamove', 'vehicle': 'Motorbike or van', 'eta': '30-60 min', 'indicative_fee': 'Indicative $4-9'},
    {'id': 'grab-express', 'name': 'Grab Express', 'vehicle': 'Motorbike', 'eta': '25-50 min', 'indicative_fee': 'Indicative $3-7'},
    {'id': 'uber-direct', 'name': 'Uber Direct', 'vehicle': 'Car or bike', 'eta': '35-70 min', 'indicative_fee': 'Indicative $5-10'},
    {'id': 'local-courier', 'name': 'Neighbourhood courier (sample)', 'vehicle': 'Bicycle', 'eta': '45-90 min', 'indicative_fee': 'Indicative $3-5'},
]
DELIVERY_NOTE = ('Demo provider list. Connect a real provider (for example Lalamove, Grab Express or Uber Direct) '
                 'through their API to activate. Requests here are saved locally; no courier is contacted and no money moves.')
DELIVERABLE = {'RESERVED', 'PAID', 'ACCEPTED', 'PREPARING', 'READY'}


class DeliveryInput(BaseModel):
    provider_id: str = Field(min_length=1, max_length=40)
    address: str = Field(min_length=5, max_length=300)
    notes: str = Field(default='', max_length=300)


def delivery_json(d: DeliveryRequest) -> dict:
    provider = next((x for x in DELIVERY_PROVIDERS if x['id'] == d.provider_id), None)
    return {'id': d.id, 'order_id': d.order_id, 'provider_id': d.provider_id,
        'provider_name': provider['name'] if provider else d.provider_id, 'address': d.address, 'notes': d.notes,
        'status': d.status, 'created_at': _iso(d.created_at), 'demo': True,
        'message': 'Quote requested locally. No courier has been contacted.'}


@router.get('/delivery/providers')
def delivery_providers(p: Principal = Depends(current_principal)):
    return {'providers': DELIVERY_PROVIDERS, 'demo': True, 'note': DELIVERY_NOTE}


@router.get('/me/delivery-requests')
def my_delivery_requests(db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    rows = db.scalars(select(DeliveryRequest).where(DeliveryRequest.owner_subject == p.subject)
                      .order_by(desc(DeliveryRequest.created_at))).all()
    return {'requests': [delivery_json(d) for d in rows]}


def _own_order(db: Session, p: Principal, order_id: str) -> Order:
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, 'Order not found')
    if order.buyer_subject != p.subject:
        raise HTTPException(403, 'Order belongs to another account')
    return order


@router.post('/orders/{order_id}/delivery-request', status_code=201)
def request_delivery(order_id: str, body: DeliveryInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    order = _own_order(db, p, order_id)
    if body.provider_id not in {x['id'] for x in DELIVERY_PROVIDERS}:
        raise HTTPException(422, 'Unknown delivery provider')
    if order.status not in DELIVERABLE:
        raise HTTPException(409, 'Delivery can only be requested for orders that are still active')
    if db.scalar(select(DeliveryRequest.id).where(DeliveryRequest.order_id == order.id, DeliveryRequest.status == 'requested')):
        raise HTTPException(409, 'A delivery request is already open for this order')
    row = DeliveryRequest(id=_id('dlv'), order_id=order.id, owner_subject=p.subject, provider_id=body.provider_id,
                          address=body.address.strip(), notes=body.notes.strip(), status='requested')
    db.add(row)
    db.commit()
    return delivery_json(row)


@router.delete('/orders/{order_id}/delivery-request')
def cancel_delivery(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    order = _own_order(db, p, order_id)
    row = db.scalar(select(DeliveryRequest).where(DeliveryRequest.order_id == order.id, DeliveryRequest.status == 'requested'))
    if not row:
        raise HTTPException(404, 'No open delivery request')
    row.status = 'cancelled'
    db.commit()
    return delivery_json(row)


class AddressInput(BaseModel):
    id: str = Field(default='', max_length=48)
    label: str = Field(default='Home', max_length=40)
    line1: str = Field(min_length=3, max_length=200)
    city: str = Field(default='', max_length=80)
    postal: str = Field(default='', max_length=20)


class ProfileInput(BaseModel):
    display_name: str = Field(default='', max_length=130)
    addresses: list[AddressInput] = Field(default_factory=list, max_length=10)
    notifications: dict[str, bool] = Field(default_factory=dict)


DEFAULT_NOTIFICATIONS = {'order_updates': True, 'price_drops': True, 'promotions': False}


def profile_json(row: AccountProfile | None) -> dict:
    return {'display_name': row.display_name if row else '', 'addresses': list(row.addresses or []) if row else [],
            'notifications': {**DEFAULT_NOTIFICATIONS, **(row.notifications or {})} if row else dict(DEFAULT_NOTIFICATIONS)}


@router.get('/me/profile')
def get_profile(db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    return profile_json(db.get(AccountProfile, p.subject))


@router.put('/me/profile')
def put_profile(body: ProfileInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    row = db.get(AccountProfile, p.subject) or AccountProfile(owner_subject=p.subject)
    row.display_name = body.display_name.strip()
    row.addresses = [{**a.model_dump(), 'id': a.id or _id('addr')} for a in body.addresses]
    row.notifications = {k: bool(v) for k, v in body.notifications.items() if k in DEFAULT_NOTIFICATIONS}
    db.add(row)
    db.commit()
    return profile_json(row)
