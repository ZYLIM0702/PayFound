"""Behavioral tests of the separate POS journal and synthetic platform bridge."""
import pytest
from sqlalchemy import select, func

from app import pos_simulator
from app.database import engine, SessionLocal
from app.models import OutboxJob, Product


@pytest.fixture
def pos(client, merchant, monkeypatch, tmp_path):
    if engine.dialect.name != 'sqlite':
        pytest.skip('The POS simulator intentionally requires the local SQLite demo')
    monkeypatch.setenv('POS_SIMULATOR_DATABASE', str(tmp_path / 'register.db'))
    connected = client.post('/api/pos-simulator/connect?merchant_id=m1', headers=merchant)
    assert connected.status_code == 200
    return client, merchant


def make_sale(client, headers, key='counter-sale-001', **extra):
    body = {'items': [{'product_id': 'p1', 'quantity': 2}], 'discount_kind': 'percent',
            'discount_value': 2000, 'idempotency_key': key, **extra}
    return client.post('/api/pos-simulator/sales?merchant_id=m1', headers=headers, json=body)


def quantity():
    with SessionLocal() as db:
        return db.get(Product, 'p1').quantity


def test_sale_discount_and_duplicate_commit_exactly_once(pos):
    client, merchant = pos
    before = quantity()
    sold = make_sale(client, merchant)
    assert sold.status_code == 200
    receipt = sold.json()['receipt']
    assert receipt['subtotal_cents'] == 7998 and receipt['discount_cents'] == 1600
    assert receipt['total_cents'] == 6398 and receipt['simulated']
    assert receipt['sync_status'] == 'ACKNOWLEDGED' and quantity() == before - 2
    repeated = make_sale(client, merchant)
    assert repeated.status_code == 200 and repeated.json()['duplicate']
    assert quantity() == before - 2
    assert make_sale(client, merchant, discount_value=1000).status_code == 409
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(OutboxJob).where(
            OutboxJob.dedupe_key == 'pos-simulator:' + receipt['id'])) == 1


def test_paused_bridge_queues_then_replays_source_change(pos):
    client, merchant = pos
    before = quantity()
    client.patch('/api/pos-simulator/connection?merchant_id=m1', headers=merchant, json={'online': False}).raise_for_status()
    sold = make_sale(client, merchant).json()
    assert sold['receipt']['sync_status'] == 'QUEUED' and quantity() == before
    assert next(p for p in sold['state']['catalog'] if p['id'] == 'p1')['quantity'] == before - 2
    resumed = client.patch('/api/pos-simulator/connection?merchant_id=m1', headers=merchant, json={'online': True}).json()
    assert resumed['pending_count'] == 0 and quantity() == before - 2
    for _ in range(2):
        assert client.post('/api/pos-simulator/sync?merchant_id=m1', headers=merchant).status_code == 200
    assert quantity() == before - 2


def test_decline_and_invalid_discount_have_no_stock_effects(pos):
    client, merchant = pos
    before = quantity()
    declined = make_sale(client, merchant, outcome='declined').json()
    assert declined['receipt']['status'] == 'DECLINED' and quantity() == before
    assert declined['state']['pending_count'] == 0
    assert make_sale(client, merchant, key='bad-discount', discount_value=10001).status_code == 422
    assert make_sale(client, merchant, key='free-sale-test', discount_value=10000).status_code == 422
    assert quantity() == before


def test_online_hold_conflict_cannot_be_overwritten_by_offline_sale(pos, consumer):
    client, merchant = pos
    before = quantity()
    client.patch('/api/pos-simulator/connection?merchant_id=m1', headers=merchant, json={'online': False})
    assert make_sale(client, merchant).status_code == 200
    held = client.post('/api/orders/reserve', headers=consumer, json={
        'product_id': 'p1', 'quantity': before, 'idempotency_key': 'platform-last-stock', 'buyer_name': 'Demo shopper'})
    assert held.status_code == 201
    conflicted = client.patch('/api/pos-simulator/connection?merchant_id=m1', headers=merchant, json={'online': True}).json()
    assert conflicted['conflict_count'] == 1 and quantity() == before
    assert make_sale(client, merchant, key='blocked-conflict-sale').status_code == 409
    client.post(f'/api/orders/{held.json()["id"]}/cancel', headers=consumer).raise_for_status()
    synced = client.post('/api/pos-simulator/sync?merchant_id=m1', headers=merchant).json()
    assert synced['pending_count'] == 0 and quantity() == before - 2


def test_platform_changes_pull_back_and_source_stock_count_pushes(pos):
    client, merchant = pos
    client.patch('/api/merchant/products/p1/stock', headers=merchant, json={'quantity': 25}).raise_for_status()
    pulled = client.get('/api/pos-simulator/state?merchant_id=m1', headers=merchant).json()
    product = next(p for p in pulled['catalog'] if p['id'] == 'p1')
    assert product['quantity'] == product['platform_quantity'] == 25
    counted = client.post('/api/pos-simulator/stock-count?merchant_id=m1', headers=merchant,
                          json={'product_id': 'p1', 'quantity': 19})
    assert counted.status_code == 200 and quantity() == 19


def test_lost_source_ack_recovery_does_not_repeat_stock_write(pos):
    client, merchant = pos
    before = quantity()
    receipt = make_sale(client, merchant).json()['receipt']
    with pos_simulator.journal('m1') as source:
        event = next(e for e in source['events'] if e['id'] == receipt['id'])
        event['status'] = 'QUEUED'  # Platform committed; source lost the acknowledgement.
        source['receipts'][0]['sync_status'] = 'QUEUED'
    replay = client.post('/api/pos-simulator/sync?merchant_id=m1', headers=merchant)
    assert replay.status_code == 200 and replay.json()['pending_count'] == 0
    assert quantity() == before - 2


def test_simulator_tenant_and_public_mode_boundaries(pos, consumer, monkeypatch):
    client, merchant = pos
    assert client.get('/api/pos-simulator/state?merchant_id=m1', headers=consumer).status_code == 403
    assert client.get('/api/pos-simulator/state?merchant_id=m2', headers=merchant).status_code == 403
    monkeypatch.setenv('DEMO_MODE', 'false')
    # Auth may reject first; either way the source and mutation stay inaccessible.
    assert client.post('/api/pos-simulator/sales?merchant_id=m1', headers=merchant,
                       json={'items': [{'product_id': 'p1', 'quantity': 1}], 'idempotency_key': 'public-mode-sale'}).status_code in (401, 503)


def test_counter_sale_and_platform_buyer_compete_without_oversell(pos, consumer):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    client, merchant = pos
    barrier = Barrier(2)
    def counter():
        barrier.wait()
        return make_sale(client, merchant, key='concurrent-counter-sale').status_code
    def shopper():
        barrier.wait()
        return client.post('/api/orders/reserve', headers=consumer, json={
            'product_id': 'p1', 'quantity': 9, 'idempotency_key': 'concurrent-online-order'}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        counter_task, shopper_task = pool.submit(counter), pool.submit(shopper)
        statuses = (counter_task.result(), shopper_task.result())
    assert statuses in ((200, 409), (409, 201), (200, 201))
    if statuses == (200, 201):
        # The source accepted a simulated payment while the online buyer won
        # platform stock. Surface the conflict instead of overwriting the hold.
        state = client.get('/api/pos-simulator/state?merchant_id=m1', headers=merchant).json()
        assert state['conflict_count'] == 1
        assert state['receipts'][0]['sync_status'] == 'NEEDS_REVIEW'
    with SessionLocal() as db:
        product = db.get(Product, 'p1')
        assert 0 <= product.hold_quantity <= product.quantity
