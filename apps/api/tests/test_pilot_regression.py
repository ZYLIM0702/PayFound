import asyncio
import threading
import uuid
from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app import commerce, paypal, worker
from app.database import SessionLocal
from app.main import app
from app.models import Order, OutboxJob, PickupSlot, Product, utcnow


def reserve(client, headers, **body):
    body.setdefault('idempotency_key', uuid.uuid4().hex)
    return client.post('/api/orders/reserve', headers=headers, json=body)


def paypal_capture(order_id, amount):
    return {'id': 'pp-' + order_id, 'status': 'COMPLETED', 'purchase_units': [
        {'payments': {'captures': [{'id': 'cap-' + order_id, 'status': 'COMPLETED',
         'amount': {'currency_code': 'USD', 'value': amount}}]}}]}


def test_basket_total_and_conflicting_idempotency_are_server_authoritative(client, consumer):
    key = uuid.uuid4().hex
    made = reserve(client, consumer, items=[{'product_id': 'p2', 'quantity': 2}, {'product_id': 'p1', 'quantity': 1}], idempotency_key=key)
    assert made.status_code == 201, made.text
    order = made.json()
    assert order['amount_cents'] == 2 * 1599 + 3999
    assert {(item['product_id'], item['amount_cents']) for item in order['items']} == {('p1', 3999), ('p2', 3198)}
    conflict = reserve(client, consumer, items=[{'product_id': 'p1', 'quantity': 1}, {'product_id': 'p2', 'quantity': 1}], idempotency_key=key)
    assert conflict.status_code == 409
    assert client.get('/api/orders/' + order['id'], headers=consumer).json()['amount_cents'] == 7197


def test_last_unit_competition_never_oversells_with_threaded_clients(client, consumer):
    # Each call builds its own TestClient and therefore uses a separate request DB session.
    client.patch('/api/merchant/products/p4/stock', headers={'x-demo-role': 'merchant'}, json={'quantity': 1})
    barrier = threading.Barrier(100)
    statuses = []
    lock = threading.Lock()

    def contender():
        with TestClient(app) as local:
            barrier.wait()
            response = reserve(local, consumer, product_id='p4', quantity=1)
        with lock:
            statuses.append(response.status_code)

    threads = [threading.Thread(target=contender) for _ in range(100)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=35)
    assert len(statuses) == 100
    assert statuses.count(201) == 1
    assert set(statuses) <= {201, 409}
    with SessionLocal() as db:
        product = db.get(Product, 'p4')
        held = list(db.scalars(select(Order).where(Order.product_id == 'p4', Order.status == 'RESERVED')))
        assert product.quantity == 1 and product.hold_quantity == 1 and len(held) == 1


def test_provider_timeout_is_quarantined_and_expiry_worker_does_not_release_hold(client, consumer, monkeypatch):
    monkeypatch.setenv('PAYPAL_CLIENT_ID', 'test-client')
    monkeypatch.setenv('PAYPAL_CLIENT_SECRET', 'test-secret')
    oid = reserve(client, consumer, product_id='p1').json()['id']

    async def timeout(_):
        raise TimeoutError()

    monkeypatch.setattr(paypal, 'create_order', timeout)
    assert client.post(f'/api/orders/{oid}/paypal/create', headers=consumer).status_code == 502
    with SessionLocal() as db:
        order = db.get(Order, oid)
        order.hold_expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    assert asyncio.run(worker.tick(connectors=False))['processed'] >= 1
    with SessionLocal() as db:
        order, product = db.get(Order, oid), db.get(Product, 'p1')
        assert order.payment_status == 'RECONCILIATION_REQUIRED'
        assert order.status == 'RESERVED' and product.hold_quantity == 1


def test_provider_capture_refund_are_exact_idempotent_and_pending_blocks_fulfilment(client, consumer, merchant, monkeypatch):
    monkeypatch.setenv('PAYPAL_CLIENT_ID', 'test-client')
    monkeypatch.setenv('PAYPAL_CLIENT_SECRET', 'test-secret')
    order = reserve(client, consumer, product_id='p1').json()
    oid, seen = order['id'], []

    async def create(received):
        assert received.amount_cents == 3999
        return {'id': 'pp-' + oid}

    async def capture(provider_id, received_id):
        assert (provider_id, received_id) == ('pp-' + oid, oid)
        return paypal_capture(oid, '39.99')

    async def refund(capture_id, received_id):
        seen.append((capture_id, received_id))
        return {'id': 'refund-' + oid, 'status': 'PENDING', 'amount': {'currency_code': 'USD', 'value': '39.99'}}

    monkeypatch.setattr(paypal, 'create_order', create)
    monkeypatch.setattr(paypal, 'capture_order', capture)
    monkeypatch.setattr(paypal, 'refund_capture', refund)
    assert client.post(f'/api/orders/{oid}/paypal/create', headers=consumer).status_code == 200
    assert client.post(f'/api/orders/{oid}/paypal/capture', headers=consumer).json()['payment_status'] == 'CAPTURED'
    first = client.post(f'/api/orders/{oid}/refund', headers=merchant)
    assert first.status_code == 200 and first.json()['payment_status'] == 'REFUND_PENDING'
    assert client.post(f'/api/orders/{oid}/refund', headers=merchant).json()['payment_status'] == 'REFUND_PENDING'
    assert seen == [('cap-' + oid, oid)]
    assert client.post(f'/api/orders/{oid}/fulfilment', headers=merchant, json={'status': 'ACCEPTED'}).status_code == 409
    with SessionLocal() as db:
        current = db.get(Order, oid)
        commerce.apply_capture(db, current, paypal_capture(oid, '39.99'))
        db.commit()
        assert db.get(Order, oid).payment_status == 'REFUND_PENDING'


def test_expired_hold_releases_stock_and_pickup_reschedule_moves_capacity(client, consumer, merchant):
    order = reserve(client, consumer, product_id='p4').json()
    with SessionLocal() as db:
        held = db.get(Order, order['id'])
        held.hold_expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    asyncio.run(worker.tick(connectors=False))
    assert client.get('/api/orders/' + order['id'], headers=consumer).json()['status'] == 'EXPIRED'
    start = (utcnow() + timedelta(hours=2)).isoformat() + 'Z'
    end = (utcnow() + timedelta(hours=3)).isoformat() + 'Z'
    slot1 = client.post('/api/merchant/pickup-slots', headers=merchant, json={'merchant_id': 'm1', 'location_id': 'loc-m1', 'start_at': start, 'end_at': end, 'capacity': 1}).json()
    slot2 = client.post('/api/merchant/pickup-slots', headers=merchant, json={'merchant_id': 'm1', 'location_id': 'loc-m1', 'start_at': (utcnow() + timedelta(hours=4)).isoformat() + 'Z', 'end_at': (utcnow() + timedelta(hours=5)).isoformat() + 'Z', 'capacity': 1}).json()
    active = reserve(client, consumer, product_id='p1').json()['id']
    assert client.post(f'/api/orders/{active}/pickup', headers=consumer, json={'slot_id': slot1['id']}).status_code == 200
    assert client.post(f'/api/orders/{active}/pickup', headers=consumer, json={'slot_id': slot2['id']}).status_code == 200
    with SessionLocal() as db:
        assert (db.get(PickupSlot, slot1['id']).booked_count, db.get(PickupSlot, slot2['id']).booked_count) == (0, 1)


def test_production_rejects_forged_demo_headers(client, monkeypatch):
    monkeypatch.setenv('DEMO_MODE', 'false')
    response = client.get('/api/admin/overview', headers={'x-demo-role': 'admin'})
    assert response.status_code == 401
