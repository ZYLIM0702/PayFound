import pytest
from sqlalchemy import select

from app.database import SessionLocal
from app.demo_orders import SHOPPER, seed_demo_orders
from app.models import Order, OrderItem, Product


def reserve(client, headers, pid='p1', key='acct-key-0001'):
    r = client.post('/api/orders/reserve', headers=headers, json={'product_id': pid, 'quantity': 1, 'idempotency_key': key})
    assert r.status_code == 201, r.text
    return r.json()


def test_wishlist_crud_and_ownership(client, consumer, merchant):
    assert client.get('/api/me/wishlist', headers=consumer).json() == {'items': []}
    r = client.post('/api/me/wishlist', headers=consumer, json={'product_id': 'p1'})
    assert r.status_code == 201 and r.json()['product_id'] == 'p1'
    assert r.json()['saved_price_cents'] == r.json()['price_cents'] and not r.json()['price_dropped']
    again = client.post('/api/me/wishlist', headers=consumer, json={'product_id': 'p1'})
    assert again.json()['id'] == r.json()['id']
    assert len(client.get('/api/me/wishlist', headers=consumer).json()['items']) == 1
    # another subject sees nothing and cannot delete it
    assert client.get('/api/me/wishlist', headers=merchant).json()['items'] == []
    assert client.delete('/api/me/wishlist/p1', headers=merchant).status_code == 404
    assert len(client.get('/api/me/wishlist', headers=consumer).json()['items']) == 1
    assert client.post('/api/me/wishlist', headers=consumer, json={'product_id': 'nope'}).status_code == 404
    assert client.delete('/api/me/wishlist/p1', headers=consumer).status_code == 200
    assert client.get('/api/me/wishlist', headers=consumer).json()['items'] == []
    assert client.get('/api/me/wishlist', headers={'x-demo-role': 'bogus'}).status_code == 401


def test_wishlist_price_drop_and_back_in_stock(client, consumer):
    client.post('/api/me/wishlist', headers=consumer, json={'product_id': 'p1'})
    with SessionLocal() as db:
        p = db.get(Product, 'p1')
        saved = p.price_cents
        p.price_cents = saved - 100
        p.quantity = 5
        db.commit()
    item = client.get('/api/me/wishlist', headers=consumer).json()['items'][0]
    assert item['price_dropped'] and item['saved_price_cents'] == saved and not item['back_in_stock']


def test_delivery_request_owner_only(client, consumer, merchant):
    order = reserve(client, consumer)
    body = {'provider_id': 'lalamove', 'address': '12 Market Street, Springfield', 'notes': 'Leave at door'}
    url = f"/api/orders/{order['id']}/delivery-request"
    assert client.post(url, headers=merchant, json=body).status_code == 403
    assert client.post('/api/orders/missing/delivery-request', headers=consumer, json=body).status_code == 404
    assert client.post(url, headers=consumer, json={**body, 'provider_id': 'bogus'}).status_code == 422
    r = client.post(url, headers=consumer, json=body)
    assert r.status_code == 201 and r.json()['status'] == 'requested' and r.json()['demo'] is True
    assert client.post(url, headers=consumer, json=body).status_code == 409
    mine = client.get('/api/me/delivery-requests', headers=consumer).json()['requests']
    assert [x['order_id'] for x in mine] == [order['id']]
    assert client.get('/api/me/delivery-requests', headers=merchant).json()['requests'] == []
    assert client.delete(url, headers=merchant).status_code == 403
    assert client.delete(url, headers=consumer).json()['status'] == 'cancelled'
    # the order itself is untouched (no payment or stock change)
    assert client.get(f"/api/orders/{order['id']}", headers=consumer).json()['status'] == 'RESERVED'


def test_delivery_rejected_for_finished_orders(client, consumer):
    order = reserve(client, consumer)
    assert client.post(f"/api/orders/{order['id']}/cancel", headers=consumer).status_code in (200, 201)
    r = client.post(f"/api/orders/{order['id']}/delivery-request", headers=consumer,
                    json={'provider_id': 'lalamove', 'address': '12 Market Street'})
    assert r.status_code == 409


def test_coupons_are_read_only_and_informational(client, consumer):
    data = client.get('/api/me/coupons', headers=consumer).json()
    assert {c['code'] for c in data['coupons']} == {'FRESH10', 'FIRSTPICK', 'FOODWEEK'}
    assert data['applies_at_checkout'] is False
    assert client.post('/api/me/coupons', headers=consumer, json={}).status_code == 405


def test_profile_roundtrip_is_per_user(client, consumer, merchant):
    body = {'display_name': 'Sam', 'addresses': [{'label': 'Home', 'line1': '1 Main St', 'city': 'X', 'postal': '1'}],
            'notifications': {'promotions': True, 'junk': True}}
    saved = client.put('/api/me/profile', headers=consumer, json=body).json()
    assert saved['addresses'][0]['id'] and saved['notifications'] == {'order_updates': True, 'price_drops': True, 'promotions': True}
    assert client.get('/api/me/profile', headers=consumer).json()['display_name'] == 'Sam'
    assert client.get('/api/me/profile', headers=merchant).json()['addresses'] == []


def test_my_reviews_lists_only_own(client, consumer, merchant):
    seed_demo_orders_for_test()
    mine = client.get('/api/me/reviews', headers=consumer).json()['reviews']
    assert len(mine) >= 4 and all(r['id'].startswith('demo-rev') for r in mine)
    assert client.get('/api/me/reviews', headers=merchant).json()['reviews'] == []


def seed_demo_orders_for_test():
    with SessionLocal() as db:
        n = seed_demo_orders(db, force=True)
        db.commit()
    return n


def test_demo_orders_are_varied_idempotent_and_demo_only(client, consumer):
    assert client.get('/api/orders', headers=consumer).json() == []
    assert seed_demo_orders_for_test() == 16
    assert seed_demo_orders_for_test() == 0
    orders = client.get('/api/orders', headers=consumer).json()
    assert len(orders) == 16
    assert len({o['status'] for o in orders}) >= 6
    assert {'COLLECTED', 'READY', 'PREPARING', 'CANCELLED', 'REFUNDED', 'EXPIRED'} <= {o['status'] for o in orders}
    sigs = set()
    with SessionLocal() as db:
        for o in db.scalars(select(Order).where(Order.buyer_subject == SHOPPER)):
            items = tuple(sorted((i.product_id, i.quantity) for i in db.scalars(select(OrderItem).where(OrderItem.order_id == o.id))))
            sigs.add((o.merchant_id, items, o.amount_cents))
    assert len(sigs) == 16
    assert len({o['amount_cents'] for o in orders}) >= 10
    assert len({o['merchant_id'] for o in orders}) >= 3
    assert any(o['payment_mode'] == 'paypal_sandbox' for o in orders)
    assert len(client.get('/api/me/wishlist', headers=consumer).json()['items']) == 5
    assert client.get('/api/orders', headers={'x-demo-role': 'merchant'}).json() != orders


def test_demo_orders_not_seeded_outside_demo_mode(client, monkeypatch):
    monkeypatch.setenv('DEMO_MODE', 'false')
    with SessionLocal() as db:
        assert seed_demo_orders(db, force=True) == 0
