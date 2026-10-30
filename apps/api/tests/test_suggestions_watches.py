"""Queue-aware pickup, stock-up drafts, competitor prices and price watches. Channel3 is always mocked."""
from datetime import timedelta

import pytest

from app import suggestions
from app.database import SessionLocal
from app.intelligence import channel3
from app.models import MerchantLocation, PickupSlot, Product, utcnow
from app.plans import BusinessSubscription
from app.suggestions import OnlinePriceCache, PriceWatch

CONSUMER2 = {'x-demo-role': 'consumer'}


@pytest.fixture()
def online(monkeypatch):
    """Mock Channel3: every product has one offer at state['cents'] (None = no offers). Counts calls."""
    state = {'cents': 1000, 'calls': 0, 'configured': True}

    async def fake_search(q, page_token=None, **kw):
        state['calls'] += 1
        offers = [] if state['cents'] is None else [{'price': state['cents'] / 100, 'currency': 'USD', 'merchant': 'shop.example', 'url': 'https://shop.example/x'}]
        return {'enabled': True, 'offers': offers}
    monkeypatch.setattr(channel3, 'search', fake_search)
    monkeypatch.setattr(channel3, 'configured', lambda: state['configured'])
    return state


def set_plan(plan_id):
    with SessionLocal() as db:
        db.merge(BusinessSubscription(owner_subject='demo-merchant', plan_id=plan_id))
        db.commit()


def test_pickup_suggestions_sorted_by_booked_share(client, consumer):
    with SessionLocal() as db:
        loc = db.query(MerchantLocation).filter_by(merchant_id='m1').first()
        base = utcnow().replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=2)
        for i, (cap, booked) in enumerate([(10, 8), (10, 2), (4, 4), (10, 5), (5, 0), (10, 9), (10, 6)]):
            db.add(PickupSlot(id=f'qs{i}', merchant_id='m1', location_id=loc.id, start_at=base + timedelta(minutes=30 * i),
                              end_at=base + timedelta(minutes=30 * i + 30), capacity=cap, booked_count=booked))
        db.commit()
        tz_day = (base.replace(tzinfo=__import__('datetime').timezone.utc).astimezone(__import__('zoneinfo').ZoneInfo(loc.timezone))).date()
    r = client.get(f'/api/pickup-suggestions?merchant_id=m1&day={tz_day}', headers=consumer)
    assert r.status_code == 200
    got = r.json()['suggestions']
    assert [s['slot_id'] for s in got] == ['qs4', 'qs1', 'qs3', 'qs6', 'qs0']  # full slot excluded, top 5, emptiest first
    assert got[0]['queue_estimate_minutes'] == 0 and got[2]['queue_estimate_minutes'] == 5 and got[0]['remaining'] == 5
    assert 'generated_at' in r.json()
    assert client.get('/api/pickup-suggestions?merchant_id=nope&day=2026-01-01', headers=consumer).status_code == 404


def test_stock_up_flags_and_draft_email(client, merchant):
    with SessionLocal() as db:
        db.add(Product(id='zz1', merchant_id='m1', name='Scarce Widget', sku='ZZ1', price_cents=500, quantity=0))
        db.add(Product(id='zz2', merchant_id='m1', name='Plentiful Widget', sku='ZZ2', price_cents=500, quantity=100000))
        db.commit()
    r = client.post('/api/merchants/m1/stock-up', json={'days': 7}, headers=merchant)
    assert r.status_code == 200
    body = r.json()
    covers = [i['days_cover'] for i in body['items']]
    assert covers == sorted(covers)
    by = {i['product_id']: i for i in body['items']}
    assert by['zz1']['flagged'] and by['zz1']['suggested_order_qty'] > 0
    assert not by['zz2']['flagged'] and by['zz2']['suggested_order_qty'] == 0
    mail = body['supplier_email']
    assert mail['status'] == 'DRAFT' and 'Scarce Widget' in mail['body'] and 'Plentiful Widget' not in mail['body']
    assert mail['body'].rstrip().endswith('Northside Electronics')
    assert client.post('/api/merchants/m1/stock-up', json={'days': 15}, headers=merchant).status_code == 422
    assert client.post('/api/merchants/m1/stock-up', json={}, headers={'x-demo-role': 'consumer'}).status_code == 403


def test_competitor_prices_402_for_free_200_for_pro(client, merchant, online):
    r = client.get('/api/merchants/m1/competitor-prices', headers=merchant)
    assert r.status_code == 402 and r.json()['detail'] == 'Upgrade to Pro to see online prices'
    assert online['calls'] == 0
    set_plan('pro')
    r = client.get('/api/merchants/m1/competitor-prices', headers=merchant)
    assert r.status_code == 200
    item = r.json()['items'][0]
    assert item['online_cents'] == 1000 and item['retailer'] == 'shop.example' and item['source'] == 'live'
    assert item['difference_cents'] == item['local_cents'] - 1000
    calls = online['calls']
    again = client.get('/api/merchants/m1/competitor-prices', headers=merchant).json()['items'][0]
    assert again['source'] == 'cache' and online['calls'] == calls


def test_competitor_prices_unconfigured_and_failing_lookup(client, merchant, online, monkeypatch):
    set_plan('diamond')
    online['configured'] = False
    items = client.get('/api/merchants/m1/competitor-prices', headers=merchant).json()['items']
    assert items and all(i['source'] == 'unavailable' and i['online_cents'] is None for i in items)
    online['configured'] = True

    async def boom(q, **kw):
        raise RuntimeError('down')
    monkeypatch.setattr(channel3, 'search', boom)
    r = client.get('/api/merchants/m1/competitor-prices', headers=merchant)
    assert r.status_code == 200 and all(i['source'] == 'unavailable' for i in r.json()['items'])


def test_price_watch_statuses_and_drop_rule(client, consumer, online):
    with SessionLocal() as db:
        local = db.get(Product, 'p1').price_cents
    online['cents'] = local + 100
    r = client.post('/api/me/price-watches', json={'product_id': 'p1'}, headers=consumer)
    assert r.status_code == 200 and r.json()['status'] == 'LOCAL_CHEAPER' and r.json()['local_cents'] == local
    assert client.post('/api/me/price-watches', json={'product_id': 'p1'}, headers=consumer).json()['id'] == r.json()['id']
    assert len(client.get('/api/me/price-watches', headers=consumer).json()['items']) == 1

    def expire():
        with SessionLocal() as db:
            row = db.get(OnlinePriceCache, 'p1')
            row.checked_at = utcnow() - timedelta(hours=2)
            db.commit()

    def status():
        expire()
        return client.get('/api/me/price-watches', headers=consumer).json()['items'][0]

    online['cents'] = local - 100  # cheaper online, but not a 10% fall from the baseline
    assert status()['status'] == 'ONLINE_CHEAPER'
    online['cents'] = int((local + 100) * 0.89)  # >10% below the baseline of local+100
    item = status()
    assert item['status'] == 'ONLINE_DEAL_DROPPED' and item['message']
    online['cents'] = None
    assert status()['status'] == 'NO_ONLINE_PRICE'


def test_price_watch_status_boundaries(client, consumer, online):
    online['cents'] = 10000
    assert client.post('/api/me/price-watches', json={'product_id': 'p2'}, headers=consumer).status_code == 200
    with SessionLocal() as db:
        local = db.get(Product, 'p2').price_cents
        w = db.query(PriceWatch).one()
        w.last_online_cents = 10000
        row = db.get(OnlinePriceCache, 'p2')
        row.online_cents = 9000
        row.checked_at = utcnow()
        db.commit()
    assert client.get('/api/me/price-watches', headers=consumer).json()['items'][0]['status'] == 'ONLINE_DEAL_DROPPED'
    with SessionLocal() as db:
        db.get(OnlinePriceCache, 'p2').online_cents = 9100
        db.commit()
    st = client.get('/api/me/price-watches', headers=consumer).json()['items'][0]['status']
    assert st == ('ONLINE_CHEAPER' if 9100 < local else 'LOCAL_CHEAPER')


def test_lookup_limited_to_one_per_hour(client, consumer, online):
    client.post('/api/me/price-watches', json={'product_id': 'p1'}, headers=consumer)
    calls = online['calls']
    for _ in range(3):
        client.get('/api/me/price-watches', headers=consumer)
    assert online['calls'] == calls


def test_shopper_cannot_see_or_delete_other_watches(client, consumer, online, monkeypatch):
    wid = client.post('/api/me/price-watches', json={'product_id': 'p1'}, headers=consumer).json()['id']
    other = {'x-demo-role': 'admin'}
    assert client.get('/api/me/price-watches', headers=other).json()['items'] == []
    assert client.delete(f'/api/me/price-watches/{wid}', headers=other).status_code == 404
    assert len(client.get('/api/me/price-watches', headers=consumer).json()['items']) == 1
    assert client.delete(f'/api/me/price-watches/{wid}', headers=consumer).status_code == 204
    assert client.get('/api/me/price-watches', headers=consumer).json()['items'] == []
