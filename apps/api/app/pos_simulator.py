"""Local software POS and a fault-tolerant bridge to synthetic PayFound stock."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from typing import Literal
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from . import commerce, database
from .access import require_merchant_access
from .auth import Principal, require_role
from .database import db_session
from .models import MerchantLocation, Order, OutboxJob, PickupSlot, Product, utcnow
from .demo_photos import apply_demo_photos

router = APIRouter(prefix='/pos-simulator', tags=['Local POS simulator'])


def stamp():
    return datetime.now(timezone.utc).isoformat()


def enabled():
    if not commerce.demo_mode() or database.engine.dialect.name != 'sqlite':
        raise HTTPException(404, 'POS simulator is available only in the local SQLite demo')


@contextmanager
def journal(merchant_id):
    enabled()
    path = os.getenv('POS_SIMULATOR_DATABASE', str(Path(__file__).resolve().parents[1] / 'pos_simulator.db'))
    with sqlite3.connect(path, timeout=30, isolation_level=None) as source:
        source.execute('CREATE TABLE IF NOT EXISTS registers (merchant_id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        source.execute('BEGIN IMMEDIATE')
        try:
            row = source.execute('SELECT payload FROM registers WHERE merchant_id = ?', (merchant_id,)).fetchone()
            state = json.loads(row[0]) if row else {
                'connected': False, 'online': True, 'catalog': [], 'receipts': [], 'events': [],
                'last_synced_at': None, 'merchant_id': merchant_id}
            yield state
            source.execute('INSERT INTO registers (merchant_id, payload) VALUES (?, ?) '
                           'ON CONFLICT(merchant_id) DO UPDATE SET payload=excluded.payload',
                           (merchant_id, json.dumps(state)))
            source.commit()
        except BaseException:
            source.rollback()
            raise


def log(state, kind, direction, summary, *, event_id=None, deltas=None, receipt_id=None):
    event = {'id': event_id or 'posevt_' + uuid.uuid4().hex[:24], 'kind': kind, 'direction': direction,
             'summary': summary, 'status': 'QUEUED' if deltas else 'ACKNOWLEDGED', 'created_at': stamp(),
             'deltas': deltas or {}, 'receipt_id': receipt_id, 'error': None}
    # Never discard unacknowledged mutations when trimming diagnostic history.
    state['events'] = [e for e in state['events'] if e['status'] != 'ACKNOWLEDGED'] + [
        e for e in state['events'] if e['status'] == 'ACKNOWLEDGED'][-199:]
    state['events'].append(event)
    return event


def pull(db, state):
    if any(e['status'] != 'ACKNOWLEDGED' for e in state['events']):
        return  # Do not overwrite unacknowledged source stock with a snapshot.
    rows = db.scalars(select(Product).where(Product.merchant_id == state['merchant_id'],
        Product.synthetic.is_(True), Product.active.is_(True), Product.currency == 'USD').order_by(Product.id).limit(200))
    catalog = [{'id': p.id, 'name': p.name, 'sku': p.sku, 'category': p.category, 'price_cents': p.price_cents,
        'currency': p.currency, 'quantity': p.quantity, 'reserved': p.hold_quantity,
        'image_emoji': p.image_emoji, 'image_url': p.image_url, 'location_id': p.location_id} for p in rows]
    changed = catalog != state['catalog']
    state['catalog'], state['last_synced_at'] = catalog, stamp()
    if changed:
        log(state, 'catalog.refreshed', 'platform_to_pos', f'{len(catalog)} products and available stock refreshed')


def sync(db, state, principal):
    if not state['online']:
        raise HTTPException(409, 'Resume the platform bridge before syncing')
    for event in state['events']:
        if event['status'] == 'ACKNOWLEDGED':
            continue
        key = 'pos-simulator:' + event['id']
        acknowledged = db.scalar(select(OutboxJob).where(OutboxJob.dedupe_key == key))
        if not acknowledged:
            try:
                for product_id, delta in sorted(event['deltas'].items()):
                    changed = db.execute(update(Product).where(Product.id == product_id,
                        Product.merchant_id == state['merchant_id'], Product.synthetic.is_(True), Product.active.is_(True),
                        Product.quantity + delta >= Product.hold_quantity,
                        Product.quantity + delta <= 100000).values(quantity=Product.quantity + delta, stock_updated_at=utcnow()))
                    if changed.rowcount != 1:
                        raise HTTPException(409, 'Platform stock changed or is held for an online order; resolve the hold/count and retry')
                receipt = next((r for r in state['receipts'] if r['id'] == event['receipt_id']), None)
                db.add(OutboxJob(id=commerce.guid('posack'), kind='pos_simulator_ack', state='DONE', dedupe_key=key,
                    payload=json.dumps({'simulated': True, 'merchant_id': state['merchant_id'],
                                        'event_id': event['id'], 'receipt': receipt})))
                commerce.audit(db, principal, 'simulator.pos_synced', event['id'], 'Synthetic inventory only; no payment processed')
                db.commit()
            except HTTPException as exc:
                db.rollback()
                event['status'], event['error'] = 'NEEDS_REVIEW', exc.detail
                for receipt in state['receipts']:
                    if receipt['id'] == event['receipt_id']:
                        receipt['sync_status'] = 'NEEDS_REVIEW'
                break  # Preserve source sequence; later deltas must not pass it.
        event['status'], event['error'], event['acknowledged_at'] = 'ACKNOWLEDGED', None, stamp()
        for receipt in state['receipts']:
            if receipt['id'] == event['receipt_id']:
                receipt['sync_status'] = 'ACKNOWLEDGED'
    pull(db, state)


def _iso(value):
    return value.replace(tzinfo=timezone.utc).isoformat() if value else None


def live(db, merchant_id):
    """Read-only snapshot of the SAME store data the merchant workspace uses."""
    from .pos_plugin.models import PosConnection
    now = utcnow()
    products = list(db.scalars(select(Product).where(Product.merchant_id == merchant_id,
        Product.active.is_(True)).order_by(Product.name).limit(300)))
    locations = {l.id: l.name for l in db.scalars(select(MerchantLocation).where(MerchantLocation.merchant_id == merchant_id))}
    names = {x.id: x.name for x in products}
    orders = list(db.scalars(select(Order).where(Order.merchant_id == merchant_id).order_by(Order.created_at.desc()).limit(40)))
    captured = list(db.scalars(select(Order).where(Order.merchant_id == merchant_id,
        Order.payment_status == 'CAPTURED', Order.status != 'CANCELLED')))

    def kind(o):
        if o.payment_status == 'CAPTURED' and o.status != 'CANCELLED':
            return 'paid'
        if o.status in ('CANCELLED', 'EXPIRED') or o.hold_released or o.hold_expires_at <= now:
            return 'closed'
        return 'reservation'
    slots = list(db.scalars(select(PickupSlot).where(PickupSlot.merchant_id == merchant_id,
        PickupSlot.end_at >= now).order_by(PickupSlot.start_at).limit(8)))
    plugin = db.scalar(select(PosConnection).where(PosConnection.merchant_id == merchant_id,
        PosConnection.status != 'disconnected').order_by(PosConnection.created_at.desc()))
    return {
        'server_time': _iso(now),
        'products': [{'id': x.id, 'name': x.name, 'sku': x.sku, 'category': x.category, 'price_cents': x.price_cents,
            'currency': x.currency, 'quantity': x.quantity, 'held': x.hold_quantity,
            'available': max(0, x.quantity - x.hold_quantity), 'branch': locations.get(x.location_id, ''),
            'source': x.inventory_source, 'image_url': x.image_url, 'updated_at': _iso(x.stock_updated_at)} for x in products],
        'orders': [{'id': o.id, 'kind': kind(o), 'product_name': names.get(o.product_id) or o.product_id,
            'buyer_name': o.buyer_name, 'quantity': o.quantity, 'amount_cents': o.amount_cents, 'currency': o.currency,
            'status': o.status, 'payment_status': o.payment_status, 'branch': locations.get(o.location_id, ''),
            'hold_expires_at': _iso(o.hold_expires_at), 'created_at': _iso(o.created_at)} for o in orders],
        'captured_cents': sum(o.amount_cents for o in captured), 'captured_count': len(captured),
        'reservation_count': sum(kind(o) == 'reservation' for o in orders),
        'pickup_slots': [{'id': s.id, 'branch': locations.get(s.location_id, ''), 'start_at': _iso(s.start_at),
            'end_at': _iso(s.end_at), 'capacity': s.capacity, 'booked': s.booked_count} for s in slots],
        'plugin': {'name': plugin.name, 'mode': plugin.mode, 'status': plugin.status, 'last_synced_at': _iso(plugin.last_synced_at),
            'last_error': plugin.last_error} if plugin else None,
    }


def view(db, state, merchant):
    result = json.loads(json.dumps(state))
    for item in result['catalog']:
        product = db.get(Product, item['id'], populate_existing=True)
        item['platform_quantity'] = product.quantity if product else None
        item['platform_reserved'] = product.hold_quantity if product else None
        item['available_quantity'] = max(0, item['quantity'] - item['reserved'])
    result['events'] = sorted(result['events'], key=lambda e: e['created_at'], reverse=True)
    result['receipts'] = list(reversed(result['receipts']))
    result['live'] = live(db, merchant.id)
    result.update(merchant_name=merchant.name, merchant_slug=merchant.slug, currency='USD', simulated=True,
        pending_count=sum(e['status'] != 'ACKNOWLEDGED' for e in state['events']),
        conflict_count=sum(e['status'] == 'NEEDS_REVIEW' for e in state['events']))
    return result


def access(db, principal, merchant_id, role='staff'):
    enabled()
    return require_merchant_access(db, principal, merchant_id, role)


# A small, explicitly fictional retail extension for the default demo merchant.
FIXTURES = [
    ('headphones', 'Studio wireless headphones', 'Audio', 7990, 14, '🎧'),
    ('speaker', 'Pocket Bluetooth speaker', 'Audio', 4990, 8, '🔊'),
    ('hub', '7-in-1 USB-C hub', 'Accessories', 5490, 11, '🔌'),
    ('keyboard', 'Compact wireless keyboard', 'Accessories', 6990, 6, '⌨️'),
    ('stand', 'Aluminium laptop stand', 'Accessories', 3490, 18, '💻'),
    ('wireless', 'Magnetic wireless charger', 'Charging', 2990, 12, '🔋'),
    ('cable', 'Braided lightning cable', 'Cables', 1490, 22, '➰'),
    ('lamp', 'Minimal desk light', 'Accessories', 4490, 5, '💡'),
]


@router.get('/state')
def state(merchant_id: str = Query(max_length=48), db: Session = Depends(db_session), p: Principal = Depends(require_role('merchant', 'admin'))):
    merchant = access(db, p, merchant_id)
    with journal(merchant_id) as source:
        if source['connected'] and source['online']:
            pull(db, source)
        return view(db, source, merchant)


@router.post('/connect')
def connect(merchant_id: str = Query(max_length=48), db: Session = Depends(db_session), p: Principal = Depends(require_role('merchant', 'admin'))):
    merchant = access(db, p, merchant_id, 'manager')
    with journal(merchant_id) as source:
        if not source['connected']:
            location = db.scalar(select(MerchantLocation).where(MerchantLocation.merchant_id == merchant_id,
                MerchantLocation.active.is_(True)).order_by(MerchantLocation.id))
            if merchant_id == 'm1' and location:
                for key, name, category, price, quantity, emoji in FIXTURES:
                    product_id = 'pos-demo-' + key
                    if not db.get(Product, product_id):
                        db.add(Product(id=product_id, merchant_id=merchant_id, location_id=location.id, name=name,
                            description='Fictional retail item for the PayFound POS simulator.', sku='SIM-' + key.upper(),
                            category=category, price_cents=price, quantity=quantity, synthetic=True, image_emoji=emoji,
                            inventory_source='pos_simulator', supports_reservation=True, availability_state='merchant_confirmed',
                            source_metadata=json.dumps({'simulated': True, 'created_by': 'pos_simulator'})))
                db.flush()
                apply_demo_photos(db)
                commerce.audit(db, p, 'simulator.pos_connected', merchant_id, 'Fictional retail library; no Zettle connection')
                db.commit()
            source['connected'] = True
            pull(db, source)
        return view(db, source, merchant)


class ConnectionInput(BaseModel):
    online: bool


@router.patch('/connection')
def connection(body: ConnectionInput, merchant_id: str = Query(max_length=48), db: Session = Depends(db_session), p: Principal = Depends(require_role('merchant', 'admin'))):
    merchant = access(db, p, merchant_id, 'manager')
    with journal(merchant_id) as source:
        source['online'] = body.online
        if source['online'] and source['connected']:
            sync(db, source, p)
        return view(db, source, merchant)


@router.post('/sync')
def synchronize(merchant_id: str = Query(max_length=48), db: Session = Depends(db_session), p: Principal = Depends(require_role('merchant', 'admin'))):
    merchant = access(db, p, merchant_id)
    with journal(merchant_id) as source:
        sync(db, source, p)
        return view(db, source, merchant)


class Line(BaseModel):
    product_id: str = Field(min_length=1, max_length=48)
    quantity: int = Field(ge=1, le=10)


class SaleInput(BaseModel):
    items: list[Line] = Field(min_length=1, max_length=30)
    discount_kind: Literal['percent', 'fixed'] = 'percent'
    discount_value: int = Field(default=0, ge=0, le=1000000)  # basis points or cents
    payment_method: Literal['card', 'cash'] = 'card'
    outcome: Literal['approved', 'declined'] = 'approved'
    idempotency_key: str = Field(min_length=8, max_length=100)


@router.post('/sales')
def sale(body: SaleInput, merchant_id: str = Query(max_length=48), db: Session = Depends(db_session), p: Principal = Depends(require_role('merchant', 'admin'))):
    merchant = access(db, p, merchant_id)
    fingerprint = hashlib.sha256(json.dumps(body.model_dump(), sort_keys=True).encode()).hexdigest()
    receipt_id = 'pos_' + hashlib.sha256((merchant_id + ':' + body.idempotency_key).encode()).hexdigest()[:28]
    with journal(merchant_id) as source:
        if not source['connected']:
            raise HTTPException(409, 'Connect the demo register first')
        previous = next((r for r in source['receipts'] if r['id'] == receipt_id), None)
        # Recover even when the platform commit succeeded but source ack was lost.
        ack = db.scalar(select(OutboxJob).where(OutboxJob.dedupe_key == 'pos-simulator:' + receipt_id))
        previous = previous or (json.loads(ack.payload).get('receipt') if ack else None)
        if previous:
            if previous['fingerprint'] != fingerprint:
                raise HTTPException(409, 'Idempotency key belongs to another sale')
            if not any(r['id'] == receipt_id for r in source['receipts']):
                previous['sync_status'] = 'ACKNOWLEDGED'
                source['receipts'].append(previous)
                pull(db, source)
            return {'receipt': previous, 'state': view(db, source, merchant), 'duplicate': True}
        if len(source['receipts']) >= 2000 or sum(e['status'] != 'ACKNOWLEDGED' for e in source['events']) >= 100:
            raise HTTPException(409, 'Simulator journal limit reached; synchronize queued events before continuing')
        if source['online']:
            sync(db, source, p)
        if any(e['status'] == 'NEEDS_REVIEW' for e in source['events']):
            raise HTTPException(409, 'Resolve the stock conflict before taking another simulated sale')
        catalog = {item['id']: item for item in source['catalog']}
        lines, subtotal, seen, locations = [], 0, set(), set()
        for item in body.items:
            product = catalog.get(item.product_id)
            if not product or item.product_id in seen:
                raise HTTPException(422, 'Use unique products from this register library')
            if product['quantity'] - product['reserved'] < item.quantity:
                raise HTTPException(409, 'Not enough available simulator stock')
            seen.add(item.product_id)
            locations.add(product['location_id'])
            lines.append({'product_id': item.product_id, 'name': product['name'], 'sku': product['sku'],
                          'unit_price_cents': product['price_cents'], 'quantity': item.quantity})
            subtotal += product['price_cents'] * item.quantity
        if len(locations) > 1:
            raise HTTPException(422, 'A counter sale must belong to one branch')
        if body.discount_kind == 'percent' and body.discount_value > 10000:
            raise HTTPException(422, 'Percentage discount cannot exceed 100%')
        discount = (subtotal * body.discount_value + 5000) // 10000 if body.discount_kind == 'percent' else body.discount_value
        if discount >= subtotal or subtotal > 2147483647:
            raise HTTPException(422, 'Sale total must be positive and within the supported amount')
        receipt = {'id': receipt_id, 'number': f'POS-{len(source["receipts"]) + 1:05d}', 'created_at': stamp(),
            'items': lines, 'subtotal_cents': subtotal, 'discount_cents': discount, 'total_cents': subtotal - discount,
            'currency': 'USD', 'payment_method': body.payment_method, 'simulated': True, 'fingerprint': fingerprint,
            'sync_status': 'NOT_APPLICABLE' if body.outcome == 'declined' else 'QUEUED',
            'status': 'DECLINED' if body.outcome == 'declined' else 'COMPLETED'}
        source['receipts'].append(receipt)
        if body.outcome == 'declined':
            log(source, 'payment.declined', 'pos_local', 'Simulated decline; no inventory or platform effects')
        else:
            deltas = {item.product_id: -item.quantity for item in body.items}
            for product_id, delta in deltas.items():
                catalog[product_id]['quantity'] += delta
            log(source, 'sale.completed', 'pos_to_platform', f'{receipt["number"]} · {sum(i.quantity for i in body.items)} items sold',
                event_id=receipt_id, deltas=deltas, receipt_id=receipt_id)
            if source['online']:
                sync(db, source, p)
        return {'receipt': receipt, 'state': view(db, source, merchant), 'duplicate': False}


class StockInput(BaseModel):
    product_id: str = Field(min_length=1, max_length=48)
    quantity: int = Field(ge=0, le=100000)


@router.post('/stock-count')
def stock_count(body: StockInput, merchant_id: str = Query(max_length=48), db: Session = Depends(db_session), p: Principal = Depends(require_role('merchant', 'admin'))):
    merchant = access(db, p, merchant_id, 'manager')
    with journal(merchant_id) as source:
        if not source['connected']:
            raise HTTPException(409, 'Connect the demo register first')
        if source['online']:
            sync(db, source, p)
        if any(e['status'] != 'ACKNOWLEDGED' for e in source['events']):
            raise HTTPException(409, 'Synchronize pending sales before recording a new count')
        product = next((item for item in source['catalog'] if item['id'] == body.product_id), None)
        if not product or body.quantity < product['reserved']:
            raise HTTPException(409, 'Count cannot remove stock reserved by a platform shopper')
        delta = body.quantity - product['quantity']
        if delta:
            product['quantity'] = body.quantity
            log(source, 'stock.counted', 'pos_to_platform', f'{product["name"]}: count recorded as {body.quantity}',
                deltas={body.product_id: delta})
            if source['online']:
                sync(db, source, p)
        return view(db, source, merchant)
