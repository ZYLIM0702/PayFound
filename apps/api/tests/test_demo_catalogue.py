"""Expanded grocery / fresh-food demo catalogue (stores m14-m40)."""
import json
import time
from datetime import timedelta

import pytest
from sqlalchemy import func, select

from app import placement
from app.database import SessionLocal, engine
from app.demo_catalogue import seed_expanded_demo
from app.demo_catalogue_grocery import grocery_data
from app.models import Merchant, MerchantLocation, PickupSlot, Product, utcnow

FRESH_CATEGORIES = {'Groceries', 'Fresh produce', 'Meat & seafood', 'Bakery', 'Dairy & eggs', 'Ready meals', 'Drinks'}
SF_WORDS = ('SoMa', 'Hayes', 'Cole Valley', 'Mission', 'Marina', 'Haight', 'Castro', 'Sunset', 'Richmond', 'Nob Hill')


@pytest.fixture()
def seeded(client):
    if engine.dialect.name != 'sqlite':
        pytest.skip('Expanded fixture is deliberately local-only')
    with SessionLocal() as db:
        seed_expanded_demo(db, force=True)
        db.commit()
    return client


def test_counts_and_categories(seeded):
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(Merchant)) >= 40
        assert db.scalar(select(func.count()).select_from(Product).where(Product.active.is_(True))) >= 900
        categories = set(db.scalars(select(Product.category).distinct()))
        assert FRESH_CATEGORIES <= categories
    summary = seeded.get('/api/catalogue/summary').json()
    assert summary['stores'] >= 40 and summary['offers'] >= 900 and FRESH_CATEGORIES <= set(summary['categories'])


def test_every_fresh_product_has_shelf_life(seeded):
    with SessionLocal() as db:
        fresh = [p for p in db.scalars(select(Product).where(Product.id.like('g%')))
                 if json.loads(p.source_metadata).get('fresh')]
        assert len(fresh) >= 300
        for p in fresh:
            assert json.loads(p.source_metadata)['shelf_life_hours'] > 0, p.id
    item = seeded.get('/api/products/' + fresh[0].id).json()
    assert item['perishable'] is True and item['shelf_life_hours'] > 0 and item['unit']


def test_stock_freshness_is_a_mix_and_honest(seeded):
    rows = seeded.get('/api/products?limit=1000&radius_km=50&latitude=37.7786&longitude=-122.414').json()
    mine = [p for p in rows if p['id'].startswith('g')]
    states = {p['freshness'] for p in mine}
    assert states == {'fresh', 'stale'}
    for p in mine:
        if p['freshness'] == 'stale' and p['in_stock']:
            assert p['availability_state'] == 'uncertain'  # stale stock is never presented as confirmed


def test_stores_branches_slots_and_hours(seeded):
    data = grocery_data()
    assert len(data['merchants']) == 27
    with SessionLocal() as db:
        for store in data['merchants']:
            merchant = db.get(Merchant, store['id'])
            assert merchant and merchant.verified and merchant.fulfillment_minutes > 0
            assert 1 <= len(store['branches']) <= 3
            n = db.scalar(select(func.count()).select_from(Product).where(Product.merchant_id == store['id'], Product.active.is_(True)))
            assert 15 <= n <= 40, (store['id'], n)
            for branch in store['branches']:
                loc = db.get(MerchantLocation, branch['id'])
                assert loc and loc.timezone == 'America/Los_Angeles' and json.loads(loc.hours)
                assert db.scalar(select(func.count()).select_from(PickupSlot).where(PickupSlot.location_id == branch['id'])) > 0 
        horizon = utcnow() + timedelta(days=6)
        assert db.scalar(select(func.count()).select_from(PickupSlot).where(PickupSlot.start_at > horizon)) > 0
    assert any(s['hours_label'] == '24 hours' for s in data['merchants'])
    assert not any(w in s['name'] for s in data['merchants'] for w in SF_WORDS)


def test_every_demo_store_is_registered_for_placement(seeded):
    data = grocery_data()
    for store in data['merchants']:
        assert store['id'] in placement.DEMO_BY_ID and placement.DEMO_BY_ID[store['id']].slug == store['slug']
        for i, branch in enumerate(store['branches']):
            assert placement.DEMO_BY_LOC[branch['id']].merchant_id == store['id']
    with SessionLocal() as db:
        for mid in db.scalars(select(Merchant.id).where(Merchant.id.like('m%'))):
            assert mid in placement.DEMO_BY_ID, mid
        for lid in db.scalars(select(MerchantLocation.id).where(MerchantLocation.id.like('loc-m%'))):
            assert lid in placement.DEMO_BY_LOC, lid
    assert len(placement.DEMO_STORES) >= 40


def test_attribution_present_when_open_food_facts_used():
    data = grocery_data()
    off = data['source']['open_food_facts']
    assert 'ODbL' in off['attribution'] and 'openfoodfacts.org' in off['url']
    used = [p for p in data['products'] if p.get('off_code')]
    if used:
        assert len(used) >= 100
    html = (placement.Path(__file__).resolve().parents[2] / 'web' / 'public' / 'image-credits.html').read_text()
    assert 'Open Food Facts' in html and 'Open Database Licence' in html


def test_seed_is_idempotent_fast_and_offline(seeded, monkeypatch):
    import socket

    def no_network(*a, **k):
        raise AssertionError('seeding must not use the network')
    monkeypatch.setattr(socket.socket, 'connect', no_network)
    with SessionLocal() as db:
        before = db.scalar(select(func.count()).select_from(Product)), db.scalar(select(func.count()).select_from(PickupSlot))
        started = time.perf_counter()
        seed_expanded_demo(db, force=True)
        db.commit()
        assert time.perf_counter() - started < 3
        after = db.scalar(select(func.count()).select_from(Product)), db.scalar(select(func.count()).select_from(PickupSlot))
    assert before == after


def test_shared_items_compare_across_stores(seeded):
    milk = [p for p in grocery_data()['products'] if p['key'] == 'whole-milk-1-l']
    assert len({p['merchant_id'] for p in milk}) >= 3
    detail = seeded.get('/api/products/' + milk[0]['id'] + '?latitude=37.7786&longitude=-122.414').json()
    assert detail['comparison_count'] >= 3 and len(detail['offers']) >= 2


def test_pos_merchant_and_existing_seed_data_survive(seeded):
    with SessionLocal() as db:
        assert db.get(Merchant, 'm1') is not None
        assert db.scalar(select(func.count()).select_from(Product).where(Product.merchant_id == 'm1')) >= 4
        assert all(db.get(Product, pid) for pid in ('p1', 'p5', 'p9', 'p12'))
        assert db.scalar(select(func.count()).select_from(Merchant)) == len(grocery_data()['merchants']) + 13
    assert len(seeded.get('/api/merchants?limit=1000').json()) >= 40
