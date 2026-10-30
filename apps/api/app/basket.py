"""Shopper basket stored per signed-in user, so it follows them across browsers and survives a cleared cache."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, delete, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from .auth import Principal, current_principal
from .database import Base, db_session
from .models import Product, utcnow

router = APIRouter(tags=['account'])

MAX_BASKET_UNITS = 30
MAX_PER_PRODUCT = 10


class BasketLine(Base):
    __tablename__ = 'basket_lines'
    owner_subject: Mapped[str] = mapped_column(String(160), primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'), primary_key=True, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class BasketItemIn(BaseModel):
    product_id: str = Field(min_length=1, max_length=48)
    quantity: int = Field(ge=1, le=99)


class BasketIn(BaseModel):
    items: list[BasketItemIn] = Field(default_factory=list, max_length=100)


def basket_json(db: Session, subject: str) -> dict:
    rows = db.scalars(select(BasketLine).where(BasketLine.owner_subject == subject).order_by(BasketLine.position, BasketLine.product_id)).all()
    items = []
    for row in rows:
        product = db.get(Product, row.product_id)
        if product and product.active:
            items.append({'product_id': product.id, 'quantity': row.quantity, 'merchant_id': product.merchant_id, 'location_id': product.location_id})
    return {'items': items}


@router.get('/me/basket')
def get_basket(db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    return basket_json(db, p.subject)


@router.put('/me/basket')
def put_basket(body: BasketIn, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    """Replace the whole basket. Unknown or inactive products and duplicates are dropped; quantities and total units are capped."""
    lines, units = [], 0
    for item in body.items:
        product = db.get(Product, item.product_id)
        if not product or not product.active or any(line[0] == product.id for line in lines):
            continue
        quantity = min(item.quantity, MAX_PER_PRODUCT)
        if units + quantity > MAX_BASKET_UNITS:
            continue
        units += quantity
        lines.append((product.id, quantity))
    db.execute(delete(BasketLine).where(BasketLine.owner_subject == p.subject))
    for position, (product_id, quantity) in enumerate(lines):
        db.add(BasketLine(owner_subject=p.subject, product_id=product_id, quantity=quantity, position=position))
    db.commit()
    return basket_json(db, p.subject)
