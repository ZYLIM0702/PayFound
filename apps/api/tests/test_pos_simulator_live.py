"""Live store data on the POS simulator state endpoint: merchant scoping and real catalogue/orders."""
import pytest

from app.database import SessionLocal, engine
from app.models import Product


@pytest.fixture
def pos(client, merchant, monkeypatch, tmp_path):
    if engine.dialect.name != 'sqlite':
        pytest.skip('The POS simulator intentionally requires the local SQLite demo')
    monkeypatch.setenv('POS_SIMULATOR_DATABASE', str(tmp_path / 'register.db'))
    assert client.post('/api/pos-simulator/connect?merchant_id=m1', headers=merchant).status_code == 200
    return client, merchant


def test_state_carries_live_store_data(pos):
    client, merchant = pos
    live = client.get('/api/pos-simulator/state?merchant_id=m1', headers=merchant).json()['live']
    assert live['server_time'] and live['products']
    with SessionLocal() as db:
        stock = db.get(Product, 'p1')
        row = next(p for p in live['products'] if p['id'] == 'p1')
        assert row['quantity'] == stock.quantity and row['price_cents'] == stock.price_cents
        assert row['available'] == stock.quantity - stock.hold_quantity
    assert all(p['id'] for p in live['orders']) and isinstance(live['pickup_slots'], list)


def test_live_reflects_stock_change_on_next_poll(pos):
    client, merchant = pos
    body = {'items': [{'product_id': 'p1', 'quantity': 1}], 'idempotency_key': 'live-sale-0001'}
    before = next(p for p in client.get('/api/pos-simulator/state?merchant_id=m1', headers=merchant).json()['live']['products'] if p['id'] == 'p1')
    assert client.post('/api/pos-simulator/sales?merchant_id=m1', headers=merchant, json=body).status_code == 200
    after = next(p for p in client.get('/api/pos-simulator/state?merchant_id=m1', headers=merchant).json()['live']['products'] if p['id'] == 'p1')
    assert after['quantity'] == before['quantity'] - 1


def test_other_store_is_not_readable(pos):
    client, merchant = pos
    other = client.get('/api/pos-simulator/state?merchant_id=m-does-not-exist', headers=merchant)
    assert other.status_code in (403, 404)
    assert client.get('/api/pos-simulator/state?merchant_id=m1', headers={'x-demo-role': 'consumer'}).status_code in (401, 403)
