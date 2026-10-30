from __future__ import annotations

import json
import math
import os
import re
import httpx
import logging
import time as clock
from contextlib import asynccontextmanager
from sqlalchemy import text, inspect
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import desc, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import commerce, llm, paypal
from .access import accessible_merchant_ids, merchant_role, require_merchant_access
from .auth import Principal, current_principal, require_role
from .commerce import ReserveInput, audit, expire_holds, guid, iso, opening, parse_capture
from .database import Base, SessionLocal, db_session, engine
from .models import (Audit, FulfilmentProof, Merchant, MerchantLocation,
    MerchantMembership, Order, PickupBooking, PickupSlot, Product, ProviderWebhook,
    Refund, Review, StaffInvitation, utcnow)
from .models import OutboxJob, CanonicalProduct, Notification
from .limits import allowed as request_allowed
from .demo_photos import apply_demo_photos
from .demo_catalogue import seed_expanded_demo
from .demo_orders import seed_demo_basket, seed_demo_orders
from .demo_pickup import seed_demo_pickup
from .demo_backfill import seed_demo_backfill
from .routing import capabilities as routing_capabilities, router as routing_router
from . import placement, ipgeo, plans, paypal_billing  # noqa: F401  (registers billing tables for create_all)
from . import site_access


@asynccontextmanager
async def lifespan(application):
    if commerce.demo_mode():
        Base.metadata.create_all(engine)
        from .assistant.history import ensure_surface_column
        ensure_surface_column(engine)
        seed_demo()
    elif engine.dialect.name != 'postgresql' and os.getenv('PAYFOUND_TESTING') != '1':
        raise RuntimeError('Authenticated staging requires a PostgreSQL DATABASE_URL; use scripts/dev.py --demo for local synthetic data')
    yield

app = FastAPI(title='PayFound API', version='0.2.0', lifespan=lifespan,
              description='Local-first commerce with durable reservation and payment reconciliation.')


# Registered before CORS so CORS wraps it: preflights pass, and a 401 still carries CORS headers the browser can read.
@app.middleware('http')
async def site_access_gate(request: Request, call_next):
    """With SITE_ACCESS_KEY set, every API call needs the token from POST /api/access in x-pf-access."""
    if (site_access.required() and request.method != 'OPTIONS' and not site_access.is_open(request.url.path)
            and not site_access.valid(request.headers.get(site_access.HEADER))):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=401, content={'detail': 'Access key required', 'code': 'access_required'},
                            headers={site_access.HEADER: 'required'})
    return await call_next(request)


app.add_middleware(CORSMiddleware,
    allow_origins=os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(','),
    allow_credentials=True, allow_methods=['*'], allow_headers=['*'], expose_headers=['x-pf-placement', 'x-pf-cell', 'X-Request-ID', 'x-pf-access'])


@app.middleware('http')
async def local_demo_only(request: Request, call_next):
    trace = guid('req')
    started = clock.monotonic()
    if request.url.path.startswith('/api/') and request.url.path not in ('/api/health', '/api/ready'):
        if not request_allowed('ip', request.client.host if request.client else 'unknown'):
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=429, content={'detail': 'Request rate limit exceeded'},
                                headers={'Retry-After': '60', 'X-Request-ID': trace})
    if commerce.demo_mode() and request.client and request.client.host not in {'127.0.0.1', '::1', 'localhost', 'testclient'}:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=403, content={'detail': 'Demo mode is restricted to localhost'})
    if commerce.demo_mode():
        hosts = {'localhost', '127.0.0.1', '::1'}
        if os.getenv('PAYFOUND_TESTING') == '1':
            hosts.add('testserver')
        if request.url.hostname not in hosts:
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=403, content={'detail': 'Demo mode requires a loopback host'}, headers={'X-Request-ID': trace})
    response = await call_next(request)
    response.headers['X-Request-ID'] = trace
    logging.getLogger('payfound.http').info('request id=%s method=%s path=%s status=%s latency_ms=%s',
        trace, request.method, request.url.path, response.status_code, round((clock.monotonic() - started) * 1000))
    return response


_PLACEMENT_PATHS = ('/api/products', '/api/merchants', '/api/merchant/', '/api/catalogue', '/api/assistant', '/api/routing',
                    '/api/intelligence', '/api/orders', '/api/online', '/api/demo/placement')


@app.middleware('http')
async def demo_placement(request: Request, call_next):
    """Resolve the viewer's demo-store layout (request-scoped; the database is never modified)."""
    anchor = tz = layout = None
    path = request.url.path
    if commerce.demo_mode() and path.startswith(_PLACEMENT_PATHS):
        anchor = placement.parse_anchor(request.headers.get('x-pf-anchor'))
        tz = placement.parse_timezone(request.headers.get('x-pf-timezone'))
        if anchor:
            # The placement endpoint waits for the whole compute budget; data requests wait briefly, then see the original layout
            # and are told so via x-pf-placement: pending, which makes the client re-fetch once the cell is ready.
            layout = await placement.layout_for(anchor, placement.full_wait_s() if path == '/api/demo/placement' else None)
    tokens = placement.set_request(anchor, tz, layout)
    try:
        response = await call_next(request)
    finally:
        placement.reset_request(tokens)
    if anchor:
        response.headers['x-pf-placement'] = layout.mode if layout else 'pending'
        response.headers['x-pf-cell'] = '%.2f,%.2f' % placement.snap(anchor)
    return response


@app.get('/api/demo/placement')
def demo_placement_state():
    """How the demo stores are laid out for this viewer (relocated around the anchor, or the original San Francisco set)."""
    anchor, layout = placement.current_anchor(), placement.current_layout()
    if not anchor:
        return {'mode': 'original', 'cell': None, 'reason': 'no_anchor', 'anchor': None, 'default_origin': list(placement.SF_CENTRE)}
    if layout is None:
        return {'mode': 'original', 'cell': None, 'reason': 'pending', 'anchor': list(anchor), 'default_origin': list(placement.SF_CENTRE)}
    return {**layout.public(), 'anchor': list(anchor), 'default_origin': list(placement.default_origin())}


@app.get('/api/demo/ip-anchor')
async def demo_ip_anchor(request: Request):
    """City-level default area from the caller's IP (2 dp, memory-cached, never stored). 204 when unknown."""
    from fastapi.responses import Response
    found = await ipgeo.lookup(ipgeo.client_ip(request)) if commerce.demo_mode() else None
    if not found:
        return Response(status_code=204)
    placement.warm((found['latitude'], found['longitude']))
    return found


@app.post('/api/demo/placement/reset')
def demo_placement_reset(request: Request):
    """Demo-only, loopback-only: forget cached layouts (used to simulate a cold server)."""
    if not commerce.demo_mode() or not request.client or request.client.host not in {'127.0.0.1', '::1', 'localhost', 'testclient'}:
        raise HTTPException(403, 'Not available')
    placement.clear_cache()
    return {'ok': True}


def dist(lat, lon, lat2, lon2):
    a = math.sin(math.radians(lat2 - lat) / 2) ** 2 + math.cos(math.radians(lat)) * math.cos(math.radians(lat2)) * math.sin(math.radians(lon2 - lon) / 2) ** 2
    return round(6371 * 2 * math.asin(min(1, math.sqrt(a))), 1)


def location_json(location):
    return {'id': location.id, 'merchant_id': location.merchant_id, 'name': location.name,
        'address': location.address, 'latitude': location.latitude, 'longitude': location.longitude,
        'timezone': location.timezone, 'hours': json.loads(location.hours),
        'special_hours': json.loads(location.special_hours), 'operational_status': location.operational_status,
        'phone': location.phone, 'active': location.active}


def store_json(merchant, db):
    reviews = list(db.scalars(select(Review).where(Review.merchant_id == merchant.id, Review.visible.is_(True))))
    locations = list(db.scalars(select(MerchantLocation).where(MerchantLocation.merchant_id == merchant.id)
                               .order_by(MerchantLocation.created_at, MerchantLocation.id)))
    primary = next((x for x in locations if x.active), None)
    return {'id': merchant.id, 'slug': merchant.slug, 'name': merchant.name,
        'description': merchant.description, 'category': merchant.category, 'address': merchant.address,
        'latitude': merchant.latitude, 'longitude': merchant.longitude, 'phone': merchant.phone,
        'hours': merchant.hours, 'is_open': opening(merchant, primary), 'status_override': merchant.status_override,
        'fulfillment_minutes': merchant.fulfillment_minutes, 'verified': merchant.verified,
        'emoji': merchant.logo_emoji, 'rating': round(sum(x.rating for x in reviews) / len(reviews), 1) if reviews else None,
        'review_count': len(reviews), 'locations': [location_json(x) for x in locations],
        'location_id': primary.id if primary else None, 'location_name': primary.name if primary else None,
        'timezone': primary.timezone if primary else None}


def product_json(product, db=None, origin=None):
    metadata = json.loads(product.source_metadata or '{}')
    fresh = bool(product.stock_updated_at and utcnow() - product.stock_updated_at < timedelta(minutes=15))
    available = max(0, product.quantity - product.hold_quantity)
    state = product.availability_state
    if not product.active or available == 0:
        state = 'unavailable'
    elif not fresh and state != 'unavailable':
        state = 'uncertain'
    result = {'id': product.id, 'merchant_id': product.merchant_id, 'name': product.name,
        'description': product.description, 'category': product.category, 'sku': product.sku,
        'price_cents': product.price_cents, 'currency': product.currency, 'quantity': product.quantity,
        'available_quantity': available, 'stock_updated_at': iso(product.stock_updated_at),
        'image_emoji': product.image_emoji, 'in_stock': product.active and available > 0,
        'active': product.active, 'freshness': 'fresh' if fresh else 'stale',
        'location_id': product.location_id, 'location_name': None, 'availability_state': state,
        'inventory_source': product.inventory_source, 'source': product.inventory_source,
        'source_product_id': product.source_product_id, 'source_version': product.source_version,
        'source_updated_at': iso(product.source_updated_at), 'source_observed_at': iso(product.source_observed_at),
        'synthetic': product.synthetic, 'supports_reservation': product.supports_reservation,
        'checkout_mode': metadata.get('checkout_mode', 'payfound'),
        'checkout_connection_id': metadata.get('connection_id'),
        'image_url': product.image_url,
        'comparison_count': metadata.get('comparison_count', 1),
        'perishable': bool(metadata.get('fresh')), 'shelf_life_hours': metadata.get('shelf_life_hours'),
        'unit': metadata.get('unit'),
        'canonical_product_id': product.canonical_product_id,
        'requires_merchant_confirmation': not (commerce.demo_mode() and product.synthetic),
        'provenance': {'source': product.inventory_source, 'synthetic': product.synthetic,
                       'source_version': product.source_version}}
    if db:
        canonical = db.get(CanonicalProduct, product.canonical_product_id) if product.canonical_product_id else None
        result.update(brand=canonical.brand if canonical else metadata.get('catalogue_brand'), gtin=canonical.gtin if canonical else None)
        merchant = db.get(Merchant, product.merchant_id)
        location = db.get(MerchantLocation, product.location_id) if product.location_id else None
        if merchant:
            result.update({'merchant_name': merchant.name, 'merchant_slug': merchant.slug,
                'merchant_address': location.address if location else merchant.address,
                'latitude': location.latitude if location else merchant.latitude,
                'longitude': location.longitude if location else merchant.longitude,
                'is_open': opening(merchant, location), 'location_name': location.name if location else None,
                'distance_km': dist(origin[0], origin[1], location.latitude if location else merchant.latitude,
                                    location.longitude if location else merchant.longitude) if origin else None})
    return result


def slot_json(slot):
    return {'id': slot.id, 'merchant_id': slot.merchant_id, 'location_id': slot.location_id,
        'start_at': iso(slot.start_at), 'end_at': iso(slot.end_at), 'capacity': slot.capacity,
        'remaining': slot.capacity - slot.booked_count}


class ProductInput(BaseModel):
    location_id: str
    name: str = Field(min_length=2, max_length=180)
    sku: str = Field(min_length=1, max_length=90)
    description: str = Field(default='', max_length=10000)
    category: str = Field(default='Retail', max_length=90)
    price_cents: int = Field(gt=0, le=100000000, strict=True)
    currency: str = Field(default='USD', pattern='^[A-Z]{3}$')
    quantity: int = Field(default=0, ge=0, le=100000, strict=True)
    gtin: str | None = Field(default=None, pattern=r'^(?:\d{8}|\d{12}|\d{13}|\d{14})$')
    brand: str = Field(default='', max_length=100)
    image_url: str | None = Field(default=None, max_length=2000, pattern='^https://[^\\s]+$')

    @field_validator('gtin')
    @classmethod
    def gtin_checksum(cls, value):
        if value and (sum(int(n) * (3 if i % 2 == 0 else 1) for i, n in enumerate(reversed(value[:-1]))) + int(value[-1])) % 10:
            raise ValueError('GTIN checksum is invalid')
        return value


@app.post('/api/merchant/products', status_code=201)
def create_product(body: ProductInput, merchant_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = require_merchant_access(db, p, merchant_id, 'manager')
    blocked = plans.listing_block(db, merchant)
    if blocked:
        raise HTTPException(402, blocked)
    location = db.get(MerchantLocation, body.location_id)
    if not location or location.merchant_id != merchant_id or not location.active:
        raise HTTPException(409, 'Choose an active merchant branch')
    canonical = db.scalar(select(CanonicalProduct).where(CanonicalProduct.gtin == body.gtin)) if body.gtin else None
    if body.gtin and not canonical:
        canonical = CanonicalProduct(id=guid('canonical'), gtin=body.gtin, name=body.name, brand=body.brand, category=body.category)
        db.add(canonical)
        db.flush()
    product = Product(id=guid('p'), merchant_id=merchant_id, **body.model_dump(exclude={'gtin', 'brand'}),
        canonical_product_id=canonical.id if canonical else None,
        inventory_source='merchant_manual', synthetic=False, availability_state='likely_available' if body.quantity else 'unavailable')
    db.add(product)
    try:
        audit(db, p, 'catalog.product_created', product.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'SKU already exists at this branch') from None
    return product_json(product, db)


def order_json(order, db):
    merchant = db.get(Merchant, order.merchant_id)
    location = db.get(MerchantLocation, order.location_id) if order.location_id else None
    items = commerce.order_items(db, order)
    booking = db.scalar(select(PickupBooking).where(PickupBooking.order_id == order.id, PickupBooking.active.is_(True)))
    slot = db.get(PickupSlot, booking.slot_id) if booking else None
    proofs = list(db.scalars(select(FulfilmentProof).where(FulfilmentProof.order_id == order.id).order_by(FulfilmentProof.created_at)))
    return {'id': order.id, 'merchant_id': order.merchant_id, 'merchant_name': merchant.name if merchant else '',
        'merchant_slug': merchant.slug if merchant else '', 'product_id': order.product_id,
        'product_name': next((x.product_name for x in items if x.product_id == order.product_id), ''),
        'quantity': order.quantity, 'amount_cents': order.amount_cents, 'currency': order.currency,
        'status': order.status, 'payment_status': order.payment_status, 'payment_mode': order.payment_mode,
        'paypal_order_id': order.paypal_order_id, 'hold_expires_at': iso(order.hold_expires_at),
        'created_at': iso(order.created_at), 'buyer_name': order.buyer_name,
        'can_review': order.status == 'COLLECTED' and not db.scalar(select(Review.id).where(Review.order_id == order.id)),
        'location_id': order.location_id, 'location_name': location.name if location else None,
        'confirmation_status': order.confirmation_status, 'confirmed_at': iso(order.confirmed_at),
        'hold_guarantee': 'synthetic_local' if order.payment_mode == 'demo' else (
            'merchant_confirmation' if order.confirmed_by else 'synthetic_local' if commerce.demo_mode() and all(
                db.get(Product, x.product_id).synthetic for x in items) else 'none'),
        'items': [{'product_id': x.product_id, 'product_name': x.product_name, 'sku': x.sku,
                   'image_url': product.image_url if (product := db.get(Product, x.product_id)) else None,
                   'quantity': x.quantity, 'unit_price_cents': x.unit_price_cents,
                   'amount_cents': x.quantity * x.unit_price_cents} for x in items],
        'pickup_window': slot_json(slot) if slot else None,
        'fulfilment_proof': [{'state': x.state, 'actor': x.actor, 'proof': x.proof,
                              'created_at': iso(x.created_at)} for x in proofs]}


def can_manage(principal, merchant, db=None):
    if not merchant:
        return False
    if db is not None:
        return bool(merchant_role(db, principal, merchant))
    # Legacy helper retained for callers; new code must pass the DB session.
    return principal.role == 'admin' or merchant.owner_subject == principal.subject


def guard_order(principal, order, db, buyer_only=False):
    if not order:
        raise HTTPException(404, 'Order not found')
    if order.buyer_subject == principal.subject or principal.role == 'admin':
        return
    if not buyer_only and order.merchant_id in accessible_merchant_ids(db, principal):
        return
    raise HTTPException(403, 'Order belongs to another account')


def select_merchant(db, principal, merchant_id=None, minimum_role='staff'):
    mids = accessible_merchant_ids(db, principal)
    selected = merchant_id or (principal.merchant_id if principal.merchant_id in mids else mids[0] if len(mids) == 1 else None)
    if not selected:
        raise HTTPException(403 if not mids else 422, 'Select an authorized merchant_id')
    return require_merchant_access(db, principal, selected, minimum_role)


class StatusUpdate(BaseModel):
    status: Literal['ACCEPTED', 'PREPARING', 'READY', 'COLLECTED', 'CANCELLED']
    proof: str = Field(default='', max_length=500)


class StockUpdate(BaseModel):
    quantity: int = Field(ge=0, le=100000, strict=True)


class MerchantStatus(BaseModel):
    status: Literal['auto', 'open', 'closed']


class ReviewInput(BaseModel):
    order_id: str
    rating: int = Field(ge=1, le=5)
    body: str = Field(default='', max_length=1500)


class ModerationInput(BaseModel):
    visible: bool


def valid_timezone(value):
    try:
        ZoneInfo(value)
    except (ValueError, ZoneInfoNotFoundError):
        raise ValueError('Use a valid IANA timezone')
    return value


def valid_hours(value, special=False):
    for key, periods in value.items():
        if special:
            date.fromisoformat(key)
        elif key not in {str(x) for x in range(7)}:
            raise ValueError('Hours keys must be weekday numbers 0..6 (Monday..Sunday)')
        if periods is None and special:
            continue
        if not isinstance(periods, list) or len(periods) > 10:
            raise ValueError('Hours must be lists of start/end periods')
        for period in periods:
            if not isinstance(period, dict) or set(period) != {'start', 'end'}:
                raise ValueError('Hours periods require start and end')
            for field, value in period.items():
                if not isinstance(value, str) or not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d|24:00', value) or (field == 'start' and value == '24:00'):
                    raise ValueError('Use HH:MM times (24:00 only as end)')
            if period['start'] == period['end']:
                raise ValueError('A period needs different start/end times')
    return value


class OnboardInput(BaseModel):
    name: str = Field(min_length=2, max_length=130)
    slug: str = Field(min_length=2, max_length=150, pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
    category: str = Field(default='Retail', max_length=80)
    address: str = Field(min_length=2, max_length=250)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str = 'UTC'
    _timezone = field_validator('timezone')(valid_timezone)


class ProfilePatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=130)
    description: str | None = Field(default=None, max_length=5000)
    category: str | None = Field(default=None, max_length=80)
    address: str | None = Field(default=None, max_length=250)
    phone: str | None = Field(default=None, max_length=80)
    hours: str | None = Field(default=None, max_length=100)
    fulfillment_minutes: int | None = Field(default=None, ge=0, le=1440)


class LocationInput(BaseModel):
    name: str = Field(default='Main branch', min_length=1, max_length=130)
    address: str = Field(min_length=2, max_length=250)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str = 'UTC'
    hours: dict = Field(default_factory=dict)
    special_hours: dict = Field(default_factory=dict)
    operational_status: Literal['auto', 'open', 'closed', 'delayed'] = 'auto'
    phone: str = Field(default='', max_length=80)
    active: bool = True
    _timezone = field_validator('timezone')(valid_timezone)
    _hours = field_validator('hours')(valid_hours)

    @field_validator('special_hours')
    @classmethod
    def special(cls, value):
        return valid_hours(value, True)


class LocationPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=130)
    address: str | None = Field(default=None, min_length=2, max_length=250)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    timezone: str | None = None
    hours: dict | None = None
    special_hours: dict | None = None
    operational_status: Literal['auto', 'open', 'closed', 'delayed'] | None = None
    phone: str | None = Field(default=None, max_length=80)
    active: bool | None = None


class StaffInput(BaseModel):
    subject: str | None = Field(default=None, min_length=1, max_length=160)
    email: str | None = Field(default=None, min_length=3, max_length=254, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    role: Literal['manager', 'staff'] = 'staff'


class SlotInput(BaseModel):
    merchant_id: str
    location_id: str
    start_at: datetime
    end_at: datetime
    capacity: int = Field(ge=1, le=10000, strict=True)


class BookingInput(BaseModel):
    slot_id: str


@app.get('/api/health')
def health():
    return {'ok': True, 'service': 'payfound-api', 'time': iso(utcnow())}


@app.get('/api/ready')
def ready(db: Session = Depends(db_session)):
    try:
        db.execute(text('SELECT 1'))
        if not inspect(engine).has_table('orders'):
            raise HTTPException(503, 'Database schema not migrated')
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, 'Database not ready') from None
    return {'ok': True, 'database': engine.dialect.name, 'demo_mode': commerce.demo_mode()}


@app.get('/api/config')
def config():
    return {'demo_mode': commerce.demo_mode(),
        'paypal_sandbox_enabled': paypal.configured() and os.getenv('PAYPAL_ENV', 'sandbox') == 'sandbox',
        'paypal_client_id': os.getenv('PAYPAL_CLIENT_ID', '') if paypal.configured() else None,
        'paypal_environment': 'sandbox', 'channel3_enabled': bool(os.getenv('CHANNEL3_API_KEY')),
        'remote_ai_enabled': llm.enabled(), 'ag_studio_enabled': bool(os.getenv('AG_STUDIO_LICENSE_KEY')),
        'supabase_auth_enabled': bool(os.getenv('SUPABASE_JWKS_URL')),
        'supabase_url': os.getenv('SUPABASE_PROJECT_URL', ''),
        'supabase_publishable_key': os.getenv('SUPABASE_PUBLISHABLE_KEY', ''),
        'routing': routing_capabilities(),
        'features': {'merchant_direct_settlement': 'requires approved partner onboarding',
                     'online_checkout': 'opt-in external provider only', 'basket': True,
                     'merchant_confirmation': True, 'durable_worker': True}}


@app.get('/api/me')
def me(db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    mids = accessible_merchant_ids(db, p)
    return {'subject': p.subject, 'role': 'admin' if p.role == 'admin' else 'merchant' if mids else 'consumer',
        'merchant_ids': mids, 'memberships': [{'merchant_id': mid, 'merchant_name': db.get(Merchant, mid).name,
            'role': merchant_role(db, p, db.get(Merchant, mid))} for mid in mids]}


def notification_scope(db, principal):
    return or_(Notification.buyer_subject == principal.subject,
               (Notification.audience == 'merchant') & Notification.merchant_id.in_(accessible_merchant_ids(db, principal)))


@app.get('/api/notifications')
def notifications(db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    rows = db.scalars(select(Notification).where(notification_scope(db, p))
        .order_by(desc(Notification.created_at)).limit(100))
    return {'notifications': [{'id': n.id, 'order_id': n.order_id, 'audience': n.audience,
        'message': n.message, 'seen_at': iso(n.seen_at), 'created_at': iso(n.created_at)} for n in rows]}


@app.post('/api/notifications/{notification_id}/read')
def read_notification(notification_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    changed = db.execute(update(Notification).where(Notification.id == notification_id, notification_scope(db, p)).values(seen_at=utcnow()))
    if not changed.rowcount:
        raise HTTPException(404, 'Notification not found')
    db.commit()
    return {'ok': True}


@app.get('/api/merchants')
def merchants(limit: int = Query(200, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(db_session)):
    return [store_json(m, db) for m in db.scalars(select(Merchant).order_by(Merchant.name, Merchant.id).offset(offset).limit(limit))]


@app.get('/api/merchants/{merchant_id}/pickup-slots')
def pickup_slots(merchant_id: str, date: date, location_id: str | None = None,
    view_timezone: str | None = Query(default=None, max_length=80), db: Session = Depends(db_session)):
    merchant = db.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(404, 'Merchant not found')
    query = select(MerchantLocation).where(MerchantLocation.merchant_id == merchant_id, MerchantLocation.active.is_(True))
    if location_id:
        query = query.where(MerchantLocation.id == location_id)
    if view_timezone:
        try:
            valid_timezone(view_timezone)
        except ValueError:
            raise HTTPException(422, 'Use a valid IANA view_timezone') from None
    result = []
    for location in db.scalars(query):
        # The default remains the branch's business day. Calendar clients can
        # explicitly request their own display-day window without relabeling it.
        tz = ZoneInfo(view_timezone or location.timezone)
        start = datetime.combine(date, time.min, tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None)
        end = datetime.combine(date + timedelta(days=1), time.min, tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None)
        result.extend(slot_json(x) for x in db.scalars(select(PickupSlot).where(
            PickupSlot.location_id == location.id, PickupSlot.end_at > start, PickupSlot.start_at < end)))
    return sorted(result, key=lambda x: (x['start_at'], x['id']))


@app.get('/api/merchants/{slug}')
def merchant_detail(slug: str, db: Session = Depends(db_session)):
    merchant = db.scalar(select(Merchant).where(Merchant.slug == slug))
    if not merchant:
        raise HTTPException(404, 'Store not found')
    reviews = db.scalars(select(Review).where(Review.merchant_id == merchant.id, Review.visible.is_(True)).order_by(desc(Review.created_at)))
    return {**store_json(merchant, db), 'products': [product_json(x, db) for x in merchant.products if x.active],
        'reviews': [{'id': r.id, 'rating': r.rating, 'body': r.body, 'created_at': iso(r.created_at),
                     'demo_review': r.buyer_subject.startswith('demo-')} for r in reviews]}


@app.get('/api/products')
def products(q: str = Query(default='', max_length=200), category: str = '', merchant_id: str = '', latitude: float | None = Query(None, ge=-90, le=90),
    longitude: float | None = Query(None, ge=-180, le=180), radius_km: float = Query(100, ge=0, le=20040),
    open_now: bool = False, in_stock: bool = False, location_id: str | None = None,
    ids: str = Query(default='', max_length=1500),
    limit: int = Query(400, ge=1, le=1000), offset: int = Query(0, ge=0), db: Session = Depends(db_session)):
    if latitude is None or longitude is None:
        # Default origin: the viewer's anchor when demo stores are relocated around it, else the original demo centre.
        default = placement.default_origin()
        latitude = default[0] if latitude is None else latitude
        longitude = default[1] if longitude is None else longitude
    statement = select(Product).where(Product.active.is_(True))
    if ids:
        requested = ids.split(',')
        if len(requested) > 30 or any(not re.fullmatch(r'[a-zA-Z0-9_-]{1,48}', value) for value in requested):
            raise HTTPException(422, 'Supply at most 30 valid product IDs')
        statement = statement.where(Product.id.in_(requested))
    if q:
        statement = statement.outerjoin(CanonicalProduct, Product.canonical_product_id == CanonicalProduct.id)
        terms = re.findall(r'\w+', q, flags=re.UNICODE)[:20] or [q]
        for term in terms:
            pattern = '%' + term.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
            statement = statement.where(or_(*(column.ilike(pattern, escape='\\') for column in (
                Product.name, Product.description, Product.category, Product.sku, CanonicalProduct.brand, CanonicalProduct.gtin))))
    if category:
        statement = statement.where(Product.category == category)
    if merchant_id:
        statement = statement.where(Product.merchant_id == merchant_id)
    if location_id:
        statement = statement.where(Product.location_id == location_id)
    out = []
    for product in db.scalars(statement.order_by(Product.id)):
        item = product_json(product, db, (latitude, longitude))
        if item.get('distance_km') is None or item['distance_km'] > radius_km or (open_now and not item['is_open']) or (in_stock and not item['in_stock']):
            continue
        out.append(item)
    out.sort(key=lambda x: (not x['in_stock'], x['distance_km'], x['price_cents'], x['id']))
    return out[offset:offset + limit]


@app.get('/api/catalogue/summary')
def catalogue_summary(db: Session = Depends(db_session)):
    rows = list(db.scalars(select(Product).where(Product.active.is_(True)).limit(10000)))
    keys = {json.loads(p.source_metadata or '{}').get('catalogue_key') or p.canonical_product_id or p.id for p in rows}
    return {'offers': len(rows), 'distinct_products': len(keys), 'stores': len({p.merchant_id for p in rows}),
            'categories': sorted({p.category for p in rows}), 'demo': commerce.demo_mode()}


@app.get('/api/products/{product_id}')
def product_detail(product_id: str, latitude: float | None = Query(None, ge=-90, le=90),
    longitude: float | None = Query(None, ge=-180, le=180), db: Session = Depends(db_session)):
    product = db.get(Product, product_id)
    if not product or not product.active:
        raise HTTPException(404, 'Product not found')
    if (latitude is None) != (longitude is None):
        raise HTTPException(422, 'Supply both origin coordinates')
    origin = (latitude, longitude) if latitude is not None else None
    metadata = json.loads(product.source_metadata or '{}')
    if product.canonical_product_id:
        matches = list(db.scalars(select(Product).where(Product.active.is_(True),
            Product.canonical_product_id == product.canonical_product_id, Product.currency == product.currency).limit(40)))
        basis = 'Shared canonical product identity'
    elif commerce.demo_mode() and product.synthetic and metadata.get('catalogue_key'):
        matches = [p for p in db.scalars(select(Product).where(Product.active.is_(True), Product.synthetic.is_(True),
            Product.currency == product.currency)) if json.loads(p.source_metadata or '{}').get('catalogue_key') == metadata['catalogue_key']][:40]
        basis = 'Same sample catalogue item across demo stores'
    else:
        matches, basis = [product], 'This merchant listing'
    offers = sorted((product_json(p, db, origin) for p in matches), key=lambda x: (not x['in_stock'], x['price_cents'], x['id']))
    merchant = db.get(Merchant, product.merchant_id)
    attributes = metadata.get('catalogue_attributes', {})
    return {**product_json(product, db, origin), 'merchant': store_json(merchant, db), 'offers': offers,
            'comparison_basis': basis, 'attributes': {str(k): str(v)[:300] for k, v in attributes.items() if v},
            'photo_credits_url': metadata.get('photo', {}).get('credits_url', '/image-credits.html')}


@app.post('/api/orders/reserve', status_code=201)
def reserve(body: ReserveInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    return order_json(commerce.reserve(db, p, body), db)


@app.get('/api/orders')
def list_orders(merchant_id: str | None = None, limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0), db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    mids = accessible_merchant_ids(db, p)
    query = select(Order).order_by(desc(Order.created_at), Order.id)
    if merchant_id:
        require_merchant_access(db, p, merchant_id)
        query = query.where(Order.merchant_id == merchant_id)
    elif p.role != 'admin':
        query = query.where(or_(Order.buyer_subject == p.subject, Order.merchant_id.in_(mids)))
    return [order_json(o, db) for o in db.scalars(query.offset(offset).limit(limit))]


@app.get('/api/orders/{order_id}')
def detail_order(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    order = db.get(Order, order_id)
    guard_order(p, order, db)
    return order_json(order, db)


@app.post('/api/orders/{order_id}/confirm')
def confirm_order(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, 'Order not found')
    require_merchant_access(db, p, order.merchant_id)
    return order_json(commerce.confirm_reservation(db, order_id, p), db)


@app.post('/api/orders/{order_id}/mock-pay')
def mock_payment(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    guard_order(p, db.get(Order, order_id), db, buyer_only=True)
    return order_json(commerce.mock_pay(db, order_id, p), db)


@app.post('/api/orders/{order_id}/paypal/create')
async def paypal_create(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    guard_order(p, db.get(Order, order_id), db, buyer_only=True)
    order = await commerce.create_payment(db, order_id)
    return {'id': order.paypal_order_id, 'order': order_json(order, db)}


@app.post('/api/orders/{order_id}/paypal/capture')
async def paypal_capture(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    guard_order(p, db.get(Order, order_id), db, buyer_only=True)
    return order_json(await commerce.capture_payment(db, order_id), db)


@app.post('/api/orders/{order_id}/paypal/resume')
async def paypal_resume(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    guard_order(p, db.get(Order, order_id), db, buyer_only=True)
    result = await commerce.resume_payment(db, order_id)
    return {'action': result['action'], 'provider_status': result['provider_status'], 'order': order_json(result['order'], db)}


@app.post('/api/orders/{order_id}/paypal/restart')
async def paypal_restart(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    guard_order(p, db.get(Order, order_id), db, buyer_only=True)
    order = await commerce.restart_payment(db, order_id)
    return {'id': order.paypal_order_id, 'order': order_json(order, db)}


@app.post('/api/merchants/{merchant_id}/payments/{order_id}/reconcile')
async def merchant_payment_reconcile(merchant_id: str, order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    from .paypal_accounts import merchant_or_404
    merchant_or_404(db, p, merchant_id)
    order = db.get(Order, order_id)
    if not order or order.merchant_id != merchant_id:
        raise HTTPException(404, 'Payment not found')
    if order.payment_mode != 'paypal_sandbox':
        raise HTTPException(409, 'Not a PayPal sandbox payment')
    return order_json(await commerce.reconcile_payment(db, order_id), db)


@app.post('/api/orders/{order_id}/paypal/reconcile')
async def paypal_reconcile(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    guard_order(p, db.get(Order, order_id), db)
    return order_json(await commerce.reconcile_payment(db, order_id), db)


@app.post('/api/orders/{order_id}/fulfilment')
def fulfil(order_id: str, body: StatusUpdate, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, 'Order not found')
    require_merchant_access(db, p, order.merchant_id)
    return order_json(commerce.fulfil_order(db, order_id, body.status, p, body.proof), db)


@app.post('/api/orders/{order_id}/confirm-pickup')
def confirm_pickup(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    guard_order(p, db.get(Order, order_id), db, buyer_only=True)
    return order_json(commerce.confirm_pickup(db, order_id, p), db)


@app.post('/api/orders/{order_id}/cancel')
def cancel_reservation(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    guard_order(p, db.get(Order, order_id), db)
    return order_json(commerce.cancel_order(db, order_id, p), db)


@app.post('/api/orders/{order_id}/refund')
async def refund(order_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, 'Order not found')
    require_merchant_access(db, p, order.merchant_id, 'manager')
    return order_json(await commerce.refund_payment(db, order_id, p), db)


@app.post('/api/orders/{order_id}/pickup')
def book_pickup(order_id: str, body: BookingInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    guard_order(p, db.get(Order, order_id), db)
    return order_json(commerce.book_pickup(db, order_id, body.slot_id, p), db)


@app.post('/api/merchant/onboard', status_code=201)
def onboard(body: OnboardInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = Merchant(id=guid('m'), name=body.name, slug=body.slug, category=body.category,
        address=body.address, latitude=body.latitude, longitude=body.longitude, owner_subject=p.subject)
    db.add(merchant)
    try:
        db.flush()
        db.add(MerchantMembership(id=guid('mem'), merchant_id=merchant.id, subject=p.subject, role='owner'))
        db.add(MerchantLocation(id=guid('loc'), merchant_id=merchant.id, name='Main branch',
            address=body.address, latitude=body.latitude, longitude=body.longitude, timezone=body.timezone,
            hours=json.dumps({str(i): [{'start': '09:00', 'end': '18:00'}] for i in range(7)})))
        audit(db, p, 'merchant.onboarded', merchant.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Merchant slug already in use')
    return store_json(merchant, db)


@app.get('/api/merchant/profile')
def merchant_profile(merchant_id: str | None = None, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    return store_json(select_merchant(db, p, merchant_id), db)


@app.patch('/api/merchant/profile')
def patch_profile(body: ProfilePatch, merchant_id: str | None = None, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = select_merchant(db, p, merchant_id, 'manager')
    for key, value in body.model_dump(exclude_unset=True).items():
        if value is None:
            raise HTTPException(422, 'Profile fields cannot be null')
        setattr(merchant, key, value)
    audit(db, p, 'merchant.profile_updated', merchant.id)
    db.commit()
    return store_json(merchant, db)


@app.get('/api/merchant/locations')
def merchant_locations(merchant_id: str | None = None, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = select_merchant(db, p, merchant_id)
    return [location_json(x) for x in db.scalars(select(MerchantLocation).where(MerchantLocation.merchant_id == merchant.id).order_by(MerchantLocation.id))]


@app.post('/api/merchant/locations', status_code=201)
def create_location(body: LocationInput, merchant_id: str | None = None, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = select_merchant(db, p, merchant_id, 'manager')
    values = body.model_dump()
    values['hours'], values['special_hours'] = json.dumps(body.hours), json.dumps(body.special_hours)
    location = MerchantLocation(id=guid('loc'), merchant_id=merchant.id, **values)
    db.add(location)
    audit(db, p, 'merchant.location_created', location.id)
    db.commit()
    return location_json(location)


@app.patch('/api/merchant/locations/{location_id}')
def patch_location(location_id: str, body: LocationPatch, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    location = db.get(MerchantLocation, location_id)
    if not location:
        raise HTTPException(404, 'Location not found')
    require_merchant_access(db, p, location.merchant_id, 'manager')
    values = body.model_dump(exclude_unset=True)
    try:
        for key, value in values.items():
            if value is None:
                raise ValueError('Location fields cannot be null')
            if key == 'timezone':
                valid_timezone(value)
            if key in ('hours', 'special_hours'):
                valid_hours(value, key == 'special_hours')
                value = json.dumps(value)
            setattr(location, key, value)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    audit(db, p, 'merchant.location_updated', location.id)
    db.commit()
    return location_json(location)


@app.get('/api/merchant/staff')
def list_staff(merchant_id: str | None = None, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = select_merchant(db, p, merchant_id, 'manager')
    members = [{'id': x.id, 'subject': x.subject, 'role': x.role, 'active': x.active, 'merchant_id': x.merchant_id}
        for x in db.scalars(select(MerchantMembership).where(MerchantMembership.merchant_id == merchant.id))]
    invitations = [{'id': x.id, 'email': x.email, 'subject': x.subject, 'role': x.role,
                    'status': x.status, 'expires_at': iso(x.expires_at), 'merchant_id': x.merchant_id}
        for x in db.scalars(select(StaffInvitation).where(StaffInvitation.merchant_id == merchant.id))]
    return {'memberships': members, 'invitations': invitations}


@app.post('/api/merchant/staff', status_code=201)
async def invite_staff(body: StaffInput, merchant_id: str | None = None, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = select_merchant(db, p, merchant_id, 'owner')
    if not body.subject and not body.email:
        raise HTTPException(422, 'An existing subject or email is required')
    delivery = 'subject_invitation' if body.subject else 'pending_auth_integration'
    target_subject = body.subject
    key, base = os.getenv('SUPABASE_SECRET_KEY'), os.getenv('SUPABASE_PROJECT_URL')
    if not target_subject and body.email and key and base and not commerce.demo_mode():
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
                response = await client.post(base.rstrip('/') + '/auth/v1/invite',
                    headers={'apikey': key, 'Authorization': 'Bearer ' + key},
                    params={'redirect_to': os.getenv('PUBLIC_WEB_URL', 'http://localhost:5173').rstrip('/') + '/auth/callback?next=%2Forders'},
                    json={'email': body.email.strip().lower(), 'data': {'payfound_invitation': True}})
            if response.status_code >= 400:
                raise HTTPException(502, 'Auth invitation could not be delivered; invite an existing user by ID')
            target_subject = response.json().get('id')
            if not target_subject:
                raise HTTPException(502, 'Auth invitation returned no user identity')
            delivery = 'supabase_email'
        except httpx.HTTPError:
            raise HTTPException(502, 'Auth invitation service unavailable') from None
    invitation = StaffInvitation(id=guid('invite'), merchant_id=merchant.id,
        subject=target_subject, email=body.email.strip().lower() if body.email else None,
        role=body.role, invited_by=p.subject, expires_at=utcnow() + timedelta(days=7))
    db.add(invitation)
    audit(db, p, 'merchant.staff_invited', invitation.id)
    db.commit()
    return {'id': invitation.id, 'merchant_id': merchant.id, 'role': invitation.role,
            'status': invitation.status, 'expires_at': iso(invitation.expires_at), 'delivery': delivery}


@app.get('/api/me/invitations')
def my_invitations(db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    rows = db.scalars(select(StaffInvitation).where(StaffInvitation.subject == p.subject,
        StaffInvitation.status == 'PENDING', StaffInvitation.expires_at > utcnow()))
    return {'invitations': [{'id': r.id, 'merchant_name': db.get(Merchant, r.merchant_id).name,
                            'role': r.role} for r in rows]}


@app.post('/api/merchant/staff/invitations/{invitation_id}/accept')
def accept_staff(invitation_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    changed = db.execute(update(StaffInvitation).where(StaffInvitation.id == invitation_id,
        StaffInvitation.status == 'PENDING', StaffInvitation.expires_at > utcnow(),
        StaffInvitation.subject == p.subject).values(status='ACCEPTED'))
    # Email-only invites remain pending until server auth administration resolves
    # the existing subject. No user-editable email metadata may grant access.
    if changed.rowcount != 1:
        raise HTTPException(403, 'Invitation does not target this verified subject or has expired')
    invitation = db.get(StaffInvitation, invitation_id, populate_existing=True)
    membership = db.scalar(select(MerchantMembership).where(MerchantMembership.merchant_id == invitation.merchant_id,
                                                            MerchantMembership.subject == p.subject))
    if membership:
        if membership.role == 'owner':
            raise HTTPException(409, 'An invitation cannot change owner membership')
        membership.role, membership.active = invitation.role, True
    else:
        db.add(MerchantMembership(id=guid('mem'), merchant_id=invitation.merchant_id,
                                 subject=p.subject, role=invitation.role))
    audit(db, p, 'merchant.staff_joined', invitation.merchant_id)
    db.commit()
    return {'merchant_id': invitation.merchant_id, 'role': invitation.role, 'status': 'ACCEPTED'}


@app.delete('/api/merchant/staff/{membership_id}')
def revoke_staff(membership_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    membership = db.get(MerchantMembership, membership_id)
    if not membership:
        raise HTTPException(404, 'Membership not found')
    require_merchant_access(db, p, membership.merchant_id, 'owner')
    if membership.role == 'owner':
        raise HTTPException(409, 'Owner transfer requires a separate verified workflow')
    membership.active = False
    audit(db, p, 'merchant.staff_revoked', membership.id)
    db.commit()
    return {'ok': True}


@app.post('/api/merchant/pickup-slots', status_code=201)
def create_pickup_slot(body: SlotInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    require_merchant_access(db, p, body.merchant_id, 'manager')
    location = db.get(MerchantLocation, body.location_id)
    if not location or location.merchant_id != body.merchant_id or not location.active:
        raise HTTPException(409, 'Invalid merchant branch')
    if body.start_at.tzinfo is None or body.end_at.tzinfo is None:
        raise HTTPException(422, 'Pickup times require a timezone offset')
    start = body.start_at.astimezone(timezone.utc).replace(tzinfo=None)
    end = body.end_at.astimezone(timezone.utc).replace(tzinfo=None)
    if start <= utcnow() or end <= start or end - start > timedelta(days=1):
        raise HTTPException(422, 'Pickup window must be future, positive, and at most one day')
    slot = PickupSlot(id=guid('slot'), merchant_id=body.merchant_id, location_id=body.location_id,
                      start_at=start, end_at=end, capacity=body.capacity)
    db.add(slot)
    try:
        audit(db, p, 'pickup.slot_created', slot.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Pickup window already exists')
    return slot_json(slot)


@app.get('/api/merchant/pickup-slots')
def pickup_calendar(start_at: datetime, end_at: datetime, merchant_id: str | None = None,
    db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = select_merchant(db, p, merchant_id)
    if start_at.tzinfo is None or end_at.tzinfo is None:
        raise HTTPException(422, 'Calendar ranges require timezone offsets')
    start = start_at.astimezone(timezone.utc).replace(tzinfo=None)
    end = end_at.astimezone(timezone.utc).replace(tzinfo=None)
    if end <= start or end - start > timedelta(days=400):
        raise HTTPException(422, 'Calendar range must be positive and at most 400 days')
    rows = list(db.scalars(select(PickupSlot).where(PickupSlot.merchant_id == merchant.id,
        PickupSlot.end_at > start, PickupSlot.start_at < end).order_by(PickupSlot.start_at, PickupSlot.id).limit(5001)))
    return {'slots': [slot_json(slot) for slot in rows[:5000]], 'truncated': len(rows) > 5000}


@app.get('/api/merchant/dashboard')
def dashboard(merchant_id: str | None = None, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    mids = accessible_merchant_ids(db, p)
    if merchant_id:
        require_merchant_access(db, p, merchant_id)
        mids = [merchant_id]
    if not mids:
        raise HTTPException(403, 'Merchant membership required')
    prods = list(db.scalars(select(Product).where(Product.merchant_id.in_(mids))))
    orders = list(db.scalars(select(Order).where(Order.merchant_id.in_(mids)).order_by(desc(Order.created_at))))
    captured = [o for o in orders if o.payment_status == 'CAPTURED' and o.status != 'CANCELLED']
    return {'merchant_id': merchant_id or (mids[0] if len(mids) == 1 else None), 'merchant_ids': mids,
        'product_count': len(prods), 'low_stock_count': sum(x.quantity - x.hold_quantity <= 3 for x in prods),
        'revenue_cents': sum(o.amount_cents for o in captured), 'order_count': len(orders),
        'pending_count': sum(o.status in ('PAID', 'ACCEPTED', 'PREPARING', 'READY') and o.payment_status == 'CAPTURED' for o in orders),
        'products': [product_json(x, db) for x in prods], 'orders': [order_json(o, db) for o in orders]}


@app.patch('/api/merchant/products/{product_id}/stock')
def edit_stock(product_id: str, body: StockUpdate, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, 'Product not found')
    require_merchant_access(db, p, product.merchant_id)
    if product.inventory_source in ('shopify', 'woocommerce'):
        raise HTTPException(409, 'Correct connector-authoritative stock at its merchant source, then sync')
    changed = db.execute(update(Product).where(Product.id == product_id, Product.hold_quantity <= body.quantity)
        .values(quantity=body.quantity, stock_updated_at=utcnow(), inventory_source='synthetic_local' if product.synthetic else 'merchant_manual',
                availability_state='likely_available' if body.quantity else 'unavailable'))
    if changed.rowcount != 1:
        raise HTTPException(409, 'Cannot set physical stock below active hold quantity')
    audit(db, p, 'inventory.manual_edit', product.id, json.dumps({'quantity': body.quantity}))
    db.commit()
    return product_json(db.get(Product, product_id, populate_existing=True), db)


@app.patch('/api/merchant/status')
def edit_store_status(body: MerchantStatus, merchant_id: str | None = None, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    merchant = select_merchant(db, p, merchant_id)
    merchant.status_override = body.status
    audit(db, p, 'merchant.status', merchant.id, body.status)
    db.commit()
    return store_json(merchant, db)


@app.post('/api/reviews', status_code=201)
def create_review(body: ReviewInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    order = db.get(Order, body.order_id)
    if not order or order.buyer_subject != p.subject or order.status != 'COLLECTED' or order.payment_status != 'CAPTURED':
        raise HTTPException(403, 'Only the buyer of a collected order can review')
    if db.scalar(select(Review.id).where(Review.order_id == order.id)):
        raise HTTPException(409, 'Order already reviewed')
    review = Review(id=guid('rev'), merchant_id=order.merchant_id, order_id=order.id,
                    buyer_subject=p.subject, rating=body.rating, body=body.body)
    db.add(review)
    try:
        audit(db, p, 'review.created', review.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Order already reviewed')
    return {'id': review.id, 'rating': review.rating, 'body': review.body, 'verified_purchase': True}


@app.get('/api/admin/overview')
def admin(db: Session = Depends(db_session), p: Principal = Depends(require_role('admin'))):
    return {'merchants': [store_json(x, db) for x in db.scalars(select(Merchant))],
        'orders': [order_json(x, db) for x in db.scalars(select(Order).order_by(desc(Order.created_at)))],
        'reviews': [{'id': r.id, 'rating': r.rating, 'body': r.body, 'visible': r.visible, 'merchant_id': r.merchant_id}
                    for r in db.scalars(select(Review))],
        'audit': [{'id': x.id, 'action': x.action, 'actor': x.actor, 'entity_id': x.entity_id, 'created_at': iso(x.created_at)}
                  for x in db.scalars(select(Audit).order_by(desc(Audit.id)).limit(100))]}


@app.get('/api/admin/reconciliation')
def reconciliation_cases(db: Session = Depends(db_session), p: Principal = Depends(require_role('admin'))):
    cases = db.scalars(select(Order).where(Order.payment_status.in_(
        ['RECONCILIATION_REQUIRED', 'CREATING', 'CAPTURING', 'REFUND_PENDING', 'PROVIDER_REVIEW_REQUIRED'])).order_by(Order.updated_at).limit(200))
    failed = db.scalars(select(OutboxJob).where(OutboxJob.state == 'FAILED').order_by(OutboxJob.created_at).limit(100))
    return {'orders': [order_json(o, db) for o in cases], 'failed_jobs': [
        {'id': j.id, 'kind': j.kind, 'attempts': j.attempts, 'last_error': j.last_error} for j in failed]}


@app.post('/api/admin/jobs/{job_id}/retry')
def retry_job(job_id: str, db: Session = Depends(db_session), p: Principal = Depends(require_role('admin'))):
    changed = db.execute(update(OutboxJob).where(OutboxJob.id == job_id, OutboxJob.state == 'FAILED')
        .values(state='PENDING', attempts=0, available_at=utcnow(), last_error=None))
    if changed.rowcount != 1:
        raise HTTPException(409, 'Only a failed job can be retried')
    audit(db, p, 'job.retry', job_id)
    db.commit()
    return {'ok': True}


@app.patch('/api/admin/reviews/{review_id}')
def moderate(review_id: str, body: ModerationInput, db: Session = Depends(db_session), p: Principal = Depends(require_role('admin'))):
    review = db.get(Review, review_id)
    if not review:
        raise HTTPException(404, 'Review not found')
    review.visible = body.visible
    audit(db, p, 'review.moderated', review.id, str(body.visible))
    db.commit()
    return {'id': review.id, 'visible': review.visible}


@app.post('/api/paypal/webhook')
async def paypal_webhook(request: Request, db: Session = Depends(db_session)):
    raw = await request.body()
    if len(raw) > 1024 * 1024:
        raise HTTPException(413, 'Webhook too large')
    try:
        payload = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(400, 'Invalid webhook JSON')
    if not isinstance(payload, dict):
        raise HTTPException(400, 'Webhook must be an object')
    await paypal.verify_webhook(payload, request.headers, raw_body=raw)
    event_id = payload.get('id')
    if not isinstance(event_id, str) or not event_id or len(event_id) > 160:
        raise HTTPException(400, 'Missing or invalid event ID')
    if db.get(ProviderWebhook, event_id):
        return {'ok': True, 'duplicate': True}
    try:
        db.add(ProviderWebhook(id=event_id, event_type=str(payload.get('event_type', ''))[:120],
            payload=raw.decode('utf-8'), verified=True))
        db.flush()
        commerce.enqueue(db, 'paypal_webhook', 'webhook:' + event_id, {'event_id': event_id})
        audit(db, 'paypal-webhook', 'payment.webhook_received', event_id, str(payload.get('event_type', ''))[:120])
        db.commit()
    except IntegrityError:
        db.rollback()
        if db.get(ProviderWebhook, event_id):
            return {'ok': True, 'duplicate': True}
        raise
    return {'ok': True, 'queued_for_reconciliation': True}


SEED_MERCHANTS = [
 ('m1','northside-electronics','Northside Electronics','Electronics','Independent electronics and accessories, with local pickup and practical device advice.','1745 Market St, San Francisco, CA',37.7744,-122.4212,'24 hours','💻'),
 ('m2','mission-hardware','Mission Hardware Co.','Hardware','Tools, household parts and same-day supplies for small repairs.','2798 Mission St, San Francisco, CA',37.7512,-122.4183,'09:00–20:00','🔧'),
 ('m3','bay-pet-supply','Bay Pet Supply','Pet essentials','Independent neighborhood pet shop stocking trusted everyday essentials.','1500 California St, San Francisco, CA',37.7905,-122.4200,'09:00–19:00','🐾'),
 ('m4','city-cycle-shop','City Cycle Shop','Sports & cycling','Bicycle repair essentials, lights, helmets and accessories.','101 Townsend St, San Francisco, CA',37.7791,-122.4050,'10:00–18:00','🚲'),
]
SEED_PRODUCTS = [
 ('p1','m1','USB-C 65W GaN Charger','Compact 65W fast charger for laptops and phones.','Electronics','NE-CH65',3999,9,'🔌'),
 ('p2','m1','USB-C to USB-C 2m Cable','Braided 100W-rated charging cable.','Electronics','NE-CAB2',1599,16,'🔋'),
 ('p3','m1','Portable 10,000mAh Power Bank','USB-C portable battery with charge indicator.','Electronics','NE-PB10',4499,5,'🔋'),
 ('p4','m1','Wireless Bluetooth Mouse','Quiet multi-device mouse.','Electronics','NE-MOUSE',2999,3,'🖱️'),
 ('p5','m2','Precision Screwdriver Kit','24-bit interchangeable tool set.','Hardware','MH-SCR24',2499,13,'🪛'),
 ('p6','m2','Adjustable Wrench 10 in.','Steel jaw wrench for plumbing repairs.','Hardware','MH-WREN10',1899,7,'🔧'),
 ('p7','m2','LED Work Light','Rechargeable 400-lumen magnetic work light.','Hardware','MH-LIGHT',2999,4,'💡'),
 ('p8','m2','Waterproof Duct Tape','Industrial 50m repair tape.','Hardware','MH-TAPE',1099,16,'🧰'),
 ('p9','m3','Dry Dog Food 2kg','Everyday complete dog food, 2kg bag.','Pet essentials','BPS-DOG2',2999,15,'🐕'),
 ('p10','m3','Cat Litter 5kg','Clumping low-dust litter.','Pet essentials','BPS-CAT5',1899,7,'🐈'),
 ('p11','m3','Pet Travel Water Bottle','Leak-proof portable pet drinking bottle.','Pet essentials','BPS-WTR',1699,2,'🐾'),
 ('p12','m4','USB Rechargeable Bike Light','Weatherproof front and rear light set.','Sports & cycling','CC-LIGHT',3499,9,'🚴'),
 ('p13','m4','Bike Tire Repair Kit','Patch, lever, and mini pump combination.','Sports & cycling','CC-REPAIR',2199,5,'🛠️'),
 ('p14','m4','Urban Cycling Helmet','Ventilated certified commuter helmet.','Sports & cycling','CC-HELM',5999,4,'⛑️'),
]


def seed_demo():
    if not commerce.demo_mode():
        return
    with SessionLocal() as db:
        if db.scalar(select(Merchant.id).limit(1)):
            apply_demo_photos(db)
            seed_expanded_demo(db)
            seed_demo_orders(db)
            seed_demo_basket(db)
            seed_demo_pickup(db)
            seed_demo_backfill(db)
            db.commit()
            _seed_paypal(db)
            return
        for mid, slug, name, cat, description, address, lat, lon, hours, icon in SEED_MERCHANTS:
            db.add(Merchant(id=mid, slug=slug, name=name, category=cat, description=description,
                address=address, latitude=lat, longitude=lon, hours=hours, logo_emoji=icon,
                verified=True, owner_subject='demo-merchant' if mid == 'm1' else None))
        db.flush()
        for mid, _, name, _, _, address, lat, lon, hours, _ in SEED_MERCHANTS:
            times = re.findall(r'\d{2}:\d{2}', hours)
            periods = [{'start': times[0], 'end': times[1]}] if times else [{'start': '00:00', 'end': '24:00'}]
            db.add(MerchantLocation(id='loc-' + mid, merchant_id=mid, name=name + ' Main',
                address=address, latitude=lat, longitude=lon, timezone='America/Los_Angeles',
                hours=json.dumps({str(i): periods for i in range(7)})))
        db.add(MerchantMembership(id='demo-membership', merchant_id='m1', subject='demo-merchant', role='owner'))
        db.flush()
        for pid, mid, name, description, cat, sku, price, qty, icon in SEED_PRODUCTS:
            db.add(Product(id=pid, merchant_id=mid, location_id='loc-' + mid, name=name,
                description=description, category=cat, sku=sku, price_cents=price, quantity=qty,
                image_emoji=icon, inventory_source='synthetic_local', synthetic=True,
                availability_state='likely_available', source_observed_at=utcnow()))
        db.flush()
        apply_demo_photos(db)
        seed_expanded_demo(db)
        for i in range(1, 5):
            order = Order(id=f'seed-order-{i}', merchant_id=f'm{i}', location_id=f'loc-m{i}',
                product_id=['p1', 'p5', 'p9', 'p12'][i-1], quantity=1,
                amount_cents=[3999, 2499, 2999, 3499][i-1], currency='USD',
                buyer_subject=f'demo-seed-{i}', buyer_name='Demo shopper', idempotency_key=f'seed-review-{i}',
                status='COLLECTED', payment_status='CAPTURED', payment_mode='demo',
                hold_released=True, inventory_committed=True, hold_expires_at=utcnow())
            db.add(order)
            db.flush()
            db.add(Review(id=f'seed-review-{i}', merchant_id=f'm{i}', order_id=order.id,
                buyer_subject=order.buyer_subject, rating=[5,4,5,4][i-1],
                body=['Helpful pickup and friendly service (sample review).', 'Had the repair kit I needed (sample review).',
                      'Convenient neighborhood shop (sample review).', 'Easy bike-light pickup (sample review).'][i-1]))
        seed_demo_orders(db)
        seed_demo_basket(db)
        seed_demo_pickup(db)
        seed_demo_backfill(db)
        db.commit()
        _seed_paypal(db)


def _seed_paypal(db):
    from .paypal_pool import seed_demo_payments, seed_paypal_pool
    try:
        seed_paypal_pool(db)
        seed_demo_payments(db)
    except Exception:
        db.rollback()
        logging.getLogger('payfound').warning('paypal demo seed skipped')


# Import failures are deployment errors; never silently drop an API surface.
from .connectors import router as connectors_router
from .pos_plugin import router as pos_plugin_router
from .intelligence import router as intelligence_router
from .pos_simulator import router as pos_simulator_router
from .paypal_accounts import router as paypal_accounts_router
app.include_router(site_access.router, prefix='/api')
app.include_router(paypal_accounts_router, prefix='/api')
app.include_router(connectors_router, prefix='/api')
app.include_router(pos_plugin_router, prefix='/api')
app.include_router(intelligence_router, prefix='/api')
from .online.routes import router as online_browse_router
app.include_router(online_browse_router, prefix='/api')
app.include_router(pos_simulator_router, prefix='/api')
app.include_router(routing_router, prefix='/api')
from .account import router as account_router
app.include_router(account_router, prefix='/api')
from .basket import router as basket_router
app.include_router(basket_router, prefix='/api')
from .account_hub import router as account_hub_router
app.include_router(account_hub_router, prefix='/api')
from .merchant_notify import router as merchant_notify_router
app.include_router(merchant_notify_router, prefix='/api')
from .plans import router as plans_router
app.include_router(plans_router, prefix='/api')
from .paypal_billing import router as paypal_billing_router
app.include_router(paypal_billing_router, prefix='/api')
from .merchant_inbox import router as merchant_inbox_router
app.include_router(merchant_inbox_router, prefix='/api')
from .merchant_overview import router as merchant_overview_router
app.include_router(merchant_overview_router, prefix='/api')
from .report_pack import router as report_pack_router
app.include_router(report_pack_router, prefix='/api')
from .report_cards import router as report_cards_router
app.include_router(report_cards_router, prefix='/api')
from .suggestions import router as suggestions_router
app.include_router(suggestions_router, prefix='/api')
