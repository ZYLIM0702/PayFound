"""Queue-aware pickup suggestions, stock-up drafts, competitor price checks and shopper price watches."""
from __future__ import annotations

import asyncio
import math
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from . import forecast_drivers as fd
from . import merchant_overview as mo
from .access import require_merchant_access
from .auth import Principal, current_principal
from .commerce import guid, iso
from .database import Base, db_session
from .intelligence import channel3
from .models import CanonicalProduct, Merchant, MerchantLocation, Order, PickupSlot, Product, utcnow
from .plans import plan_for

router = APIRouter(tags=['Suggestions and price watches'])

CACHE_TTL = timedelta(hours=6)
WATCH_LOOKUP_TTL = timedelta(hours=1)
MAX_LOOKUPS_PER_REQUEST = 25


class OnlinePriceCache(Base):
    __tablename__ = 'online_price_cache'
    product_id: Mapped[str] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
    online_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    retailer: Mapped[str | None] = mapped_column(String(250), nullable=True)
    url: Mapped[str | None] = mapped_column(String(8192), nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)


class PriceWatch(Base):
    __tablename__ = 'price_watches'
    id: Mapped[str] = mapped_column(String(48), primary_key=True)
    buyer_subject: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    merchant_id: Mapped[str] = mapped_column(ForeignKey('merchants.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_online_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_local_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    __table_args__ = (UniqueConstraint('buyer_subject', 'product_id', name='uq_price_watch_buyer_product'),)


@router.get('/pickup-suggestions')
def pickup_suggestions(merchant_id: str = Query(max_length=48), day: date = Query(),
                       db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    """Top 5 pickup slots with room left on `day` (the store's local day, per branch timezone).

    queue_estimate_minutes = round(booked / max(capacity, 1) * 10). It is a simple estimate from the share of the slot
    already booked, not a measured wait time. Slots are ordered by booked share (emptiest first), then start time.
    """
    if not db.get(Merchant, merchant_id):
        raise HTTPException(404, 'Merchant not found')
    rows: list[PickupSlot] = []
    for loc in db.scalars(select(MerchantLocation).where(MerchantLocation.merchant_id == merchant_id, MerchantLocation.active.is_(True))):
        tz = mo._tz(loc)
        start = datetime.combine(day, time.min, tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None)
        end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None)
        rows.extend(db.scalars(select(PickupSlot).where(PickupSlot.location_id == loc.id, PickupSlot.start_at >= start, PickupSlot.start_at < end)))
    open_slots = [s for s in rows if s.capacity - s.booked_count > 0]
    open_slots.sort(key=lambda s: (s.booked_count / max(s.capacity, 1), s.start_at, s.id))
    out = [{'slot_id': s.id, 'start_at': iso(s.start_at), 'end_at': iso(s.end_at), 'capacity': s.capacity, 'booked': s.booked_count,
            'remaining': s.capacity - s.booked_count, 'queue_estimate_minutes': round(s.booked_count / max(s.capacity, 1) * 10)}
           for s in open_slots[:5]]
    return {'suggestions': out, 'generated_at': iso(utcnow())}


class StockUpBody(BaseModel):
    days: int = Field(default=7, ge=1, le=14)


def _daily_rates(db: Session, merchant: Merchant, products: list[Product], window: int = 28) -> dict[str, float]:
    """Units/day per product from the forecast machinery (recent sales, stock-out days excluded, blended with the demo prior)."""
    location = mo._primary(db, merchant.id)
    tz = mo._tz(location)
    today = mo._local(utcnow(), tz).date()
    names = {p.id: p.name for p in products}
    orders = [o for o in db.scalars(select(Order).where(Order.merchant_id == merchant.id)) if o.status not in mo.DEAD]
    items = mo._items(db, orders)
    series: dict[str, list[int]] = defaultdict(lambda: [0] * window)
    for o in orders:
        age = (today - mo._local(o.created_at, tz).date()).days
        if 0 <= age < window:
            for pid, _, q, _ in mo._lines(o, items, names):
                series[pid][age] += q
    return {p.id: fd.product_rate(series.get(p.id, [0] * window), max(0, p.quantity - p.hold_quantity), mo.baseline_rate(p.id), window)['rate']
            for p in products}


def _draft_email(merchant: Merchant, flagged: list[dict], days: int) -> dict:
    lines = [f"- {i['name']} (SKU {i['sku']}): {i['on_hand']} on hand, about {i['projected_units']} expected in {days} days, order {i['suggested_order_qty']}"
             for i in flagged if i['suggested_order_qty'] > 0]
    body = ('Hello,\n\nWe would like to place a restock order for the items below, based on our expected sales over the next '
            f'{days} days.\n\n' + ('\n'.join(lines) if lines else '(No items need reordering right now.)') +
            f'\n\nPlease confirm availability and delivery timing.\n\nThank you,\n{merchant.name}')
    return {'subject': f'Restock order request from {merchant.name}', 'body': body, 'status': 'DRAFT'}


@router.post('/merchants/{merchant_id}/stock-up')
def stock_up(merchant_id: str, body: StockUpBody = StockUpBody(), db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    """Projects demand for the next `days` days and drafts (never sends) a supplier email for products that will sell out."""
    merchant = require_merchant_access(db, p, merchant_id, 'manager')
    today = mo._local(utcnow(), mo._tz(mo._primary(db, merchant.id))).date()
    products = list(db.scalars(select(Product).where(Product.merchant_id == merchant.id, Product.active.is_(True)).order_by(Product.id)))
    rates = _daily_rates(db, merchant, products)
    items = []
    for pr in products:
        rate = rates[pr.id]
        projected = rate * body.days
        cover = pr.quantity / max(rate, 0.01)
        sell_out = today + timedelta(days=int(math.floor(min(cover, 3650))))
        flagged = sell_out <= today + timedelta(days=body.days)
        items.append({'product_id': pr.id, 'name': pr.name, 'sku': pr.sku, 'projected_units': round(projected, 1), 'daily_rate': round(rate, 2),
                      'on_hand': pr.quantity, 'days_cover': round(cover, 1), 'sell_out_date': sell_out.isoformat(), 'flagged': flagged,
                      'suggested_order_qty': max(0, math.ceil(projected * 1.2 - pr.quantity)) if flagged else 0})
    items.sort(key=lambda i: (i['days_cover'], i['name']))
    return {'days': body.days, 'items': items, 'supplier_email': _draft_email(merchant, [i for i in items if i['flagged']], body.days)}


async def lookup_online(name: str, gtin: str | None, currency: str) -> dict | None:
    """Best (cheapest) online offer for a product via the shared Channel3 adapter, or None if nothing matched."""
    result = await channel3.search((name + (' ' + gtin if gtin else ''))[:200])
    if not result.get('enabled'):
        raise RuntimeError('unconfigured')
    offers = [o for o in result.get('offers', []) if o.get('currency') == currency and o.get('price') is not None]
    if not offers:
        return None
    best = min(offers, key=lambda o: o['price'])
    return {'online_cents': int(round(best['price'] * 100)), 'currency': best['currency'], 'retailer': best.get('merchant'), 'url': best.get('url')}


def _gtin(db: Session, product: Product) -> str | None:
    canonical = db.get(CanonicalProduct, product.canonical_product_id) if product.canonical_product_id else None
    return canonical.gtin if canonical else None


async def online_price(db: Session, product: Product, ttl: timedelta, budget: dict | None = None) -> tuple[OnlinePriceCache | None, str]:
    """Cached-or-fresh online price. Returns (row or None, source) with source in cache|live|unavailable. Never raises."""
    row = db.get(OnlinePriceCache, product.id)
    now = utcnow()
    if row and now - row.checked_at < ttl:
        return row, 'cache'
    if not channel3.configured() or (budget is not None and budget['left'] <= 0):
        return (row, 'cache') if row else (None, 'unavailable')
    if budget is not None:
        budget['left'] -= 1
    try:
        found = await lookup_online(product.name, _gtin(db, product), product.currency)
    except Exception:  # noqa: BLE001 - one bad lookup must not fail the request
        return (row, 'cache') if row else (None, 'unavailable')
    # Affiliate offer URLs are never persisted (see intelligence/channel3.py). Only the price and retailer are cached.
    values = (found['online_cents'], found['currency'], found['retailer'], None) if found else (None, None, None, None)
    for attempt in range(2):  # a parallel request may insert the same product first; then update that row instead
        if row is None:
            row = OnlinePriceCache(product_id=product.id)
            db.add(row)
        row.online_cents, row.currency, row.retailer, row.url = values
        row.checked_at = now
        try:
            db.commit()
            return row, 'live'
        except IntegrityError:
            db.rollback()
            row = db.get(OnlinePriceCache, product.id) if attempt == 0 else None
    return None, 'unavailable'


@router.get('/merchants/{merchant_id}/competitor-prices')
async def competitor_prices(merchant_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = require_merchant_access(db, p, merchant_id, 'manager')
    if plan_for(db, merchant.owner_subject).id not in ('pro', 'diamond'):
        raise HTTPException(402, 'Upgrade to Pro to see online prices')
    products = list(db.scalars(select(Product).where(Product.merchant_id == merchant.id, Product.active.is_(True)).order_by(Product.name, Product.id)))
    budget = {'left': MAX_LOOKUPS_PER_REQUEST}
    out = []
    for pr in products:
        row, source = await online_price(db, pr, CACHE_TTL, budget)
        usable = row is not None and row.online_cents is not None and row.currency == pr.currency
        out.append({'product_id': pr.id, 'name': pr.name, 'local_cents': pr.price_cents,
                    'online_cents': row.online_cents if usable else None, 'retailer': row.retailer if usable else None,
                    'url': row.url if usable else None, 'difference_cents': (pr.price_cents - row.online_cents) if usable else None,
                    'checked_at': iso(row.checked_at) if row else None, 'source': source if (usable or source != 'cache') else 'no_match'})
    return {'items': out}


class WatchInput(BaseModel):
    product_id: str = Field(min_length=1, max_length=48)


def _status(local: int, online: int | None, last_online: int | None) -> tuple[str, str]:
    if online is None:
        return 'NO_ONLINE_PRICE', 'No online price found for this item right now.'
    if last_online and online <= last_online * 0.9:
        return 'ONLINE_DEAL_DROPPED', f'The online price fell {round((1 - online / last_online) * 100)}% since you started watching.'
    if online < local:
        return 'ONLINE_CHEAPER', f'Online is ${(local - online) / 100:.2f} cheaper than the local price.'
    return 'LOCAL_CHEAPER', 'The local price is as good as or better than online.'


async def _watch_json(db: Session, w: PriceWatch) -> dict:
    pr = db.get(Product, w.product_id)
    if pr is None:
        return {'id': w.id, 'product_id': w.product_id, 'merchant_id': w.merchant_id, 'name': None, 'local_cents': None, 'online_cents': None,
                'status': 'NO_ONLINE_PRICE', 'message': 'This item is no longer listed.', 'created_at': iso(w.created_at)}
    row, _ = await online_price(db, pr, WATCH_LOOKUP_TTL)
    online = row.online_cents if row is not None and row.currency == pr.currency else None
    status, message = _status(pr.price_cents, online, w.last_online_cents)
    # Baseline for the 10% rule: set once, re-based upward only, so a drop stays visible instead of vanishing on the next read.
    if online is not None and (w.last_online_cents is None or online > w.last_online_cents):
        w.last_online_cents = online
    w.last_local_cents = pr.price_cents
    w.last_checked_at = utcnow()
    db.commit()
    return {'id': w.id, 'product_id': pr.id, 'merchant_id': w.merchant_id, 'name': pr.name, 'local_cents': pr.price_cents, 'online_cents': online,
            'retailer': row.retailer if online is not None else None, 'url': row.url if online is not None else None,
            'status': status, 'message': message, 'created_at': iso(w.created_at), 'last_checked_at': iso(w.last_checked_at)}


@router.post('/me/price-watches')
async def create_price_watch(body: WatchInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    pr = db.get(Product, body.product_id)
    if pr is None or not pr.active:
        raise HTTPException(404, 'Product not found')
    w = db.scalar(select(PriceWatch).where(PriceWatch.buyer_subject == p.subject, PriceWatch.product_id == pr.id))
    if w is None:
        cached = db.get(OnlinePriceCache, pr.id)
        w = PriceWatch(id=guid('pw'), buyer_subject=p.subject, product_id=pr.id, merchant_id=pr.merchant_id, last_local_cents=pr.price_cents,
                       last_online_cents=cached.online_cents if cached else None)
        db.add(w)
        db.commit()
    return await _watch_json(db, w)


@router.get('/me/price-watches')
async def list_price_watches(db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    watches = list(db.scalars(select(PriceWatch).where(PriceWatch.buyer_subject == p.subject).order_by(PriceWatch.created_at, PriceWatch.id)))
    return {'items': [await _watch_json(db, w) for w in watches]}


@router.delete('/me/price-watches/{watch_id}', status_code=204)
def delete_price_watch(watch_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    w = db.get(PriceWatch, watch_id)
    if w is None or w.buyer_subject != p.subject:
        raise HTTPException(404, 'Price watch not found')
    db.delete(w)
    db.commit()
