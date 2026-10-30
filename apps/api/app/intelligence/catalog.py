"""Deterministic extraction and read-only local catalog tools."""
from __future__ import annotations

import math
import os
import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .. import models as core_models
from ..models import Merchant, Product, utcnow
from .schemas import AgentInput, ProductDTO, SearchInput


STOP = set('i a an the it its my me we our you your please find need want looking look for to of '
           'where can could would should is are do does have has buy get show search nearby near '
           'local locally today some any with and or in at on store stores shop shops product products '
           'recommend something available stock open now cheapest cheap price budget less than '
           'under below over above maximum minimum max min within radius km miles mi dollar dollars '
           'usd eur gbp cad aud cost costs up out only'.split())


def iso(value) -> str | None:
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def distance(lat: float, lon: float, lat2: float, lon2: float) -> float:
    a = (math.sin(math.radians(lat2 - lat) / 2) ** 2 + math.cos(math.radians(lat)) *
         math.cos(math.radians(lat2)) * math.sin(math.radians(lon2 - lon) / 2) ** 2)
    return 6371 * 2 * math.asin(min(1, math.sqrt(a)))


def opening(merchant, location=None) -> bool | None:
    from ..commerce import opening as branch_opening
    return branch_opening(merchant, location)


def product_dto(product: Product, merchant: Merchant, origin=None, location=None) -> dict:
    quantity = product.quantity
    available = max(0, quantity - (product.hold_quantity or 0)) if quantity is not None else None
    stamp = product.stock_updated_at
    naive = stamp.astimezone(timezone.utc).replace(tzinfo=None) if stamp and stamp.tzinfo else stamp
    age = utcnow() - naive if naive else None
    freshness = 'unknown' if age is None or age < timedelta(0) else ('fresh' if age <= timedelta(minutes=15) else 'stale')
    subject = location or merchant
    lat, lon = getattr(subject, 'latitude', None), getattr(subject, 'longitude', None)
    km = distance(*origin, lat, lon) if origin and lat is not None and lon is not None else None
    source = getattr(product, 'source', None) or getattr(product, 'inventory_source', None) or 'local_catalog'
    if not isinstance(source, str):
        source = 'local_catalog'
    data = dict(
        id=product.id, merchant_id=product.merchant_id, name=product.name, description=product.description or '',
        category=product.category, sku=product.sku, price_cents=product.price_cents, currency=product.currency,
        quantity=quantity, available_quantity=available, stock_updated_at=iso(stamp), image_emoji=product.image_emoji,
        in_stock=bool(product.active and available is not None and available > 0), active=product.active,
        freshness=freshness, merchant_name=merchant.name, merchant_slug=merchant.slug,
        merchant_address=getattr(subject, 'address', None) or merchant.address,
        is_open=opening(merchant, location), hours=getattr(subject, 'hours', None) or merchant.hours,
        distance_km=round(km, 3) if km is not None else None,
        location_id=getattr(product, 'location_id', None), source=source[:100],
        source_timestamps={'stock_updated_at': iso(stamp),
                           'source_emitted_at': iso(getattr(product, 'source_emitted_at', None)),
                           'source_observed_at': iso(getattr(product, 'source_observed_at', None))},
        stock_status='unknown' if available is None else ('likely_available' if available > 0 else 'out_of_stock'),
        verified_local_stock=False,
    )
    return ProductDTO.model_validate(data).model_dump()


def location_for(db, product):
    model = getattr(core_models, 'MerchantLocation', None)
    location_id = getattr(product, 'location_id', None)
    location = db.get(model, location_id) if model is not None and location_id else None
    return location if location and location.merchant_id == product.merchant_id else None


def extract(body: AgentInput) -> SearchInput:
    text = body.message.lower()
    currency = 'GBP' if '£' in text else 'EUR' if '€' in text else next(
        (c.upper() for c in ['usd', 'gbp', 'eur', 'cad', 'aud'] if re.search(r'\b' + c + r'\b', text)), 'USD')
    minimum = maximum = None
    scrubbed = text
    amount = r'(?:[$£€]\s*)?(\d+(?:\.\d{1,2})?)(?:\s*(?:usd|gbp|eur|cad|aud|dollars?))?'
    patterns = [('max', r'\b(?:under|below|less than|up to|at most|max(?:imum)?(?: price)?)\s*' + amount),
                ('min', r'\b(?:over|above|more than|at least|min(?:imum)?(?: price)?)\s*' + amount)]
    for kind, pattern in patterns:
        match = re.search(pattern, scrubbed)
        if match:
            value = int(Decimal(match.group(1)) * 100)
            if kind == 'max':
                maximum = value
            else:
                minimum = value
            scrubbed = scrubbed[:match.start()] + ' ' + scrubbed[match.end():]
    between = re.search(r'\bbetween\s*' + amount + r'\s*(?:and|to|-)\s*' + amount, scrubbed)
    if between:
        minimum, maximum = (int(Decimal(between.group(i)) * 100) for i in (1, 2))
        scrubbed = scrubbed[:between.start()] + ' ' + scrubbed[between.end():]
    radius = body.radius_km
    radius_match = re.search(r'\bwithin\s+(\d+(?:\.\d+)?)\s*(km|kilometers?|mi|miles?)\b', scrubbed)
    if radius_match:
        if radius is None and body.latitude is not None:
            radius = float(radius_match.group(1)) * (1.609344 if radius_match.group(2).startswith('mi') else 1)
        scrubbed = scrubbed[:radius_match.start()] + ' ' + scrubbed[radius_match.end():]
    quantity = 1
    quantity_match = re.search(r'\b(?:need|want|buy|get|find|show)\s+(\d{1,2})\s+', scrubbed)
    if quantity_match:
        quantity = max(1, int(quantity_match.group(1)))
        scrubbed = scrubbed[:quantity_match.start(1)] + scrubbed[quantity_match.end(1):]
    terms = []
    for term in re.findall(r'[a-z0-9]+', scrubbed):
        if term in STOP:
            continue
        if len(term) > 3 and term.endswith('s') and not term.endswith(('ss', 'us')):
            term = term[:-1]
        if term not in terms:
            terms.append(term)
    return SearchInput(terms=terms[:20], merchant_id=body.merchant_id, latitude=body.latitude,
                       longitude=body.longitude, radius_km=radius, min_price_cents=minimum,
                       max_price_cents=maximum, currency=currency if minimum is not None or maximum is not None else None,
                       open_now=bool(re.search(r'\bopen (?:right )?now\b', text)), requested_quantity=quantity)


def search_local(db: Session, args: SearchInput) -> dict:
    if not args.terms or (args.min_price_cents is not None and args.max_price_cents is not None and
                          args.min_price_cents > args.max_price_cents):
        return {'products': [], 'truncated': False}
    stmt = select(Product, Merchant).join(Merchant, Product.merchant_id == Merchant.id).where(Product.active.is_(True))
    if args.merchant_id:
        stmt = stmt.where(Product.merchant_id == args.merchant_id)
    if args.currency:
        stmt = stmt.where(Product.currency == args.currency)
    if args.min_price_cents is not None:
        stmt = stmt.where(Product.price_cents >= args.min_price_cents)
    if args.max_price_cents is not None:
        stmt = stmt.where(Product.price_cents <= args.max_price_cents)
    for term in args.terms:
        # Extracted terms are alphanumeric: no SQL wildcard injection.
        stmt = stmt.where(or_(*(func.lower(column).contains(term) for column in
                               [Product.name, Product.description, Product.category, Product.sku, Merchant.name])))
    rows = db.execute(stmt.order_by(Product.id).limit(201)).all()
    matches = []
    origin = (args.latitude, args.longitude) if args.latitude is not None else None
    for product, merchant in rows[:200]:
        item = product_dto(product, merchant, origin, location_for(db, product))
        if item['available_quantity'] is not None and item['available_quantity'] < args.requested_quantity:
            continue
        if args.open_now and item['is_open'] is not True:
            continue
        if args.radius_km is not None and (item['distance_km'] is None or item['distance_km'] > args.radius_km):
            continue
        matches.append(item)
    matches.sort(key=lambda x: (x['distance_km'] if x['distance_km'] is not None else math.inf,
                                x['price_cents'], x['id']))
    return {'products': matches[:args.limit], 'truncated': len(rows) > 200 or len(matches) > args.limit}
