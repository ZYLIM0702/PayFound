"""Analytics report pack, report cards, assistant build_report/save_report."""
import json

from sqlalchemy import select

from app.database import SessionLocal
from app.intelligence.models import MerchantReportCard
from tests.test_assistant import call, events, post, results, script, talk


def pack(client, headers, days=30, mid='m1'):
    return client.get(f'/api/merchant/report-pack?merchant_id={mid}&days={days}', headers=headers)


def test_pack_scoping(client, merchant, consumer):
    assert pack(client, merchant).status_code == 200
    assert pack(client, merchant, mid='m2').status_code == 404
    assert pack(client, merchant, mid='nope').status_code == 404
    assert pack(client, consumer).status_code == 403
    assert client.get('/api/merchant/report-cards/preview?merchant_id=m2', headers=merchant).status_code == 404


def test_default_pack_has_every_section_for_m1(client, merchant):
    from app.database import engine
    from app.demo_backfill import seed_demo_backfill
    from app.demo_catalogue import seed_expanded_demo
    from app.demo_orders import seed_demo_orders
    from app.demo_pickup import seed_demo_pickup
    if engine.dialect.name != 'sqlite':
        import pytest
        pytest.skip('Demo backfill is local-only')
    with SessionLocal() as db:
        seed_expanded_demo(db, force=True)
        seed_demo_orders(db, force=True)
        seed_demo_pickup(db)
        seed_demo_backfill(db, force=True)
        db.commit()
    body = pack(client, merchant, days=90).json()
    assert body['sections'] == ['summary', 'sales_trend', 'categories', 'branches', 'top_products', 'funnel', 'stock_health', 'pickup', 'recommendations']
    s = body['summary']
    assert s['by_currency'] and s['by_currency'][0]['captured_amount_cents'] > 0 and s['by_currency'][0]['average_basket_cents'] > 0
    assert s['pickup_completion_pct'] is not None and s['orders_in_range'] > 100
    assert body['categories'] and body['branches'] and body['top_products']['by_units'] and body['top_products']['by_revenue']
    f = body['funnel']
    assert f['reserved'] >= f['paid'] >= f['collected'] > 0
    assert any(len(rows) == 90 for rows in body['sales_trend']['by_currency'].values())
    assert body['stock_health']['in_stock'] + body['stock_health']['low'] + body['stock_health']['out'] + body['stock_health']['stale'] > 0
    assert body['pickup']['by_branch'] and 'slots' in body['pickup'] and body['recommendations']  # slots are present in the live demo DB; pickup seeding is gated in tests


def test_numbers_are_per_currency_and_make_no_profit_claims(client, merchant):
    body = pack(client, merchant).json()
    text = json.dumps(body).lower()
    assert 'not profit' in body['note'].lower()
    for word in ('profit', 'margin'):
        assert word not in text.replace('not profit, margin or bank settlement', '').replace('not profit', '')
    # every money row carries its own currency; none is a cross-currency total
    assert all('currency' in r for r in body['categories'] + body['branches'])
    card = client.get('/api/merchant/report-cards/preview?merchant_id=m1&kind=sales&days=30', headers=merchant).json()
    assert card['kind'] == 'sales' and card['note'] == body['note']
    metric_labels = [m['label'] for sec in card['sections'] for m in sec['metrics']]
    assert any('USD' in label for label in metric_labels)


def test_card_validation_and_focus(client, merchant):
    r = client.get('/api/merchant/report-cards/preview?merchant_id=m1&kind=bogus', headers=merchant)
    assert r.status_code == 422
    full = client.get('/api/merchant/report-cards/preview?merchant_id=m1&kind=full&days=7', headers=merchant).json()
    assert {s['id'] for s in full['sections']} >= {'summary', 'sales_mix', 'top_products', 'funnel', 'stock', 'pickup', 'recommendations'}
    for sec in full['sections']:
        for chart in sec['charts']:
            assert all(len(s['values']) == len(chart['labels']) for s in chart['series'])


def test_saved_report_ownership(client, merchant, consumer, admin):
    r = client.post('/api/merchant/report-cards', headers=merchant, json={'merchant_id': 'm1', 'name': 'Weekly sales', 'kind': 'sales', 'days': 7})
    assert r.status_code == 201
    rid = r.json()['id']
    assert client.post('/api/merchant/report-cards', headers=merchant, json={'merchant_id': 'm2', 'name': 'x'}).status_code in (403, 404)
    assert client.post('/api/merchant/report-cards', headers=consumer, json={'merchant_id': 'm1', 'name': 'x'}).status_code in (403, 404)
    assert [x['id'] for x in client.get('/api/merchant/report-cards?merchant_id=m1', headers=merchant).json()['reports']] == [rid]
    opened = client.get(f'/api/merchant/report-cards/{rid}', headers=merchant).json()
    assert opened['card']['kind'] == 'sales' and opened['card']['days'] == 7
    assert client.get(f'/api/merchant/report-cards/{rid}', headers=consumer).status_code == 404
    with SessionLocal() as db:   # move the report to another store: the m1 merchant must no longer see or delete it
        row = db.get(MerchantReportCard, rid)
        row.merchant_id = 'm2'
        db.commit()
    assert client.get(f'/api/merchant/report-cards/{rid}', headers=merchant).status_code == 404
    assert client.delete(f'/api/merchant/report-cards/{rid}', headers=merchant).status_code == 404
    with SessionLocal() as db:
        assert db.scalar(select(MerchantReportCard.id).where(MerchantReportCard.id == rid)) == rid


def test_delete_own_report(client, merchant):
    rid = client.post('/api/merchant/report-cards', headers=merchant, json={'merchant_id': 'm1', 'name': 'Tmp'}).json()['id']
    assert client.delete(f'/api/merchant/report-cards/{rid}', headers=merchant).status_code == 204
    assert client.get(f'/api/merchant/report-cards/{rid}', headers=merchant).status_code == 404


def test_build_report_refused_for_shopper(client, consumer, monkeypatch):
    for tool, args in (('build_report', {'kind': 'full'}), ('save_report', {'name': 'x'})):
        script(monkeypatch, call(tool, args), talk())
        evs = events(post(client, consumer, props={'surface': 'merchant', 'merchant_id': 'm1'}))
        res = list(results(evs).values())
        assert not res or res[0].get('error') == 'request_denied'


def test_build_report_for_merchant_own_store_only(client, merchant, monkeypatch):
    script(monkeypatch, call('build_report', {'kind': 'sales', 'days': 30}), talk())
    r = list(results(events(post(client, merchant, props={'merchant_id': 'm1'}))).values())[0]
    assert r['merchant_id'] == 'm1' and r['kind'] == 'sales' and r['sections'] and 'not profit' in r['note'].lower()
    script(monkeypatch, call('build_report', {'kind': 'full'}), talk())
    assert list(results(events(post(client, merchant, props={'merchant_id': 'm2'}))).values())[0]['error'] == 'request_denied'
    script(monkeypatch, call('save_report', {'name': 'From assistant', 'kind': 'stock', 'days': 14}), talk())
    s = list(results(events(post(client, merchant, props={'merchant_id': 'm1'}))).values())[0]
    assert s['saved'] and s['name'] == 'From assistant'
    script(monkeypatch, call('save_report', {'name': 'Nope'}), talk())
    assert list(results(events(post(client, merchant, props={'merchant_id': 'm2'}))).values())[0]['error'] == 'request_denied'
    with SessionLocal() as db:
        assert [r.merchant_id for r in db.scalars(select(MerchantReportCard))] == ['m1']


def test_pack_has_category_by_branch_for_showcase(client, merchant):
    body = pack(client, merchant, days=30).json()
    assert body['category_by_branch'] and all({'branch', 'category', 'currency', 'amount_cents'} <= set(r) for r in body['category_by_branch'])
    assert sum(r['amount_cents'] for r in body['category_by_branch']) == sum(c['amount_cents'] for c in body['categories'])
