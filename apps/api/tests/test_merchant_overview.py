import json
from datetime import date, timedelta

import pytest

from app import merchant_overview as mo
from app.database import SessionLocal
from app.models import Merchant, Product, utcnow

TODAY = date(2026, 10, 24)
WEATHER = {'source': 'test', 'days': [{'date': (TODAY + timedelta(days=i)).isoformat(), 'summary': 'Rain' if i == 1 else 'Clear', 'code': 63 if i == 1 else 0,
                                       'temp_max_c': 18, 'rain_chance_pct': 90 if i == 1 else 5} for i in range(7)]}


def fake_weather(monkeypatch, data=WEATHER):
    async def _fetch(lat, lng, **kw):
        return data
    monkeypatch.setattr(mo, 'fetch_daily_weather', _fetch)


def test_scoping_other_store_is_404(client, merchant, monkeypatch):
    fake_weather(monkeypatch)
    assert client.get('/api/merchant/analytics?merchant_id=m1', headers=merchant).status_code == 200
    assert client.get('/api/merchant/forecast?merchant_id=m1', headers=merchant).status_code == 200
    for path in ('analytics', 'forecast'):
        assert client.get(f'/api/merchant/{path}?merchant_id=m2', headers=merchant).status_code == 404
        assert client.get(f'/api/merchant/{path}?merchant_id=nope', headers=merchant).status_code == 404
        assert client.get(f'/api/merchant/{path}?merchant_id=m1', headers={'x-demo-role': 'consumer'}).status_code == 403


def test_analytics_shape(client, merchant):
    body = client.get('/api/merchant/analytics?merchant_id=m1&days=30', headers=merchant).json()
    assert body['store']['name'] and len(body['orders_by_hour']) == 24
    assert sum(body['stock_health'][k] for k in ('in_stock', 'low', 'out', 'stale')) > 0
    series = next(iter(body['revenue'].values()))
    assert len(series) == 30 and 'Not profit' in body['revenue_note']


def make_product(**kw):
    return Product(id='x', merchant_id='m1', name='X', sku='X', price_cents=100, quantity=kw.pop('quantity', 10), hold_quantity=kw.pop('hold', 0),
                   stock_updated_at=kw.pop('updated', utcnow()), source_metadata=kw.pop('meta', '{}'))


def test_low_stock_threshold_logic():
    assert mo.stock_state(make_product(quantity=3)) == 'low'
    assert mo.stock_state(make_product(quantity=4)) == 'in_stock'
    assert mo.stock_state(make_product(quantity=4, hold=1)) == 'low'
    assert mo.stock_state(make_product(quantity=2, hold=2)) == 'out'
    assert mo.stock_state(make_product(quantity=4), default=5) == 'low'
    assert mo.stock_state(make_product(quantity=8, meta=json.dumps({'low_stock_at': 10}))) == 'low'
    assert mo.stock_state(make_product(quantity=8, updated=utcnow() - timedelta(days=2))) == 'stale'
    assert mo.low_threshold(make_product(meta='not json')) == 3


def test_analytics_threshold_param_changes_alerts(client, merchant):
    base = client.get('/api/merchant/analytics?merchant_id=m1', headers=merchant).json()
    wide = client.get('/api/merchant/analytics?merchant_id=m1&low_stock_threshold=100', headers=merchant).json()
    assert wide['stock_health']['low'] >= base['stock_health']['low']
    assert wide['stock_health']['low'] > 0 and any(a['id'] == 'low' for a in wide['alerts'])
    assert all(a['ask'] and a['to'].startswith('/merchant') for a in wide['alerts'])


def test_events_filtered_by_distance_and_date():
    events = mo.load_events()
    assert len(events) >= 12
    civic = (37.7786, -122.4170)
    near = mo.events_between(events, TODAY, TODAY + timedelta(days=6), *civic)
    assert near and all(e['distance_km'] <= mo.EVENT_RADIUS_KM and TODAY.isoformat() <= e['date'] <= (TODAY + timedelta(days=6)).isoformat() for e in near)
    assert any(e['id'] == 'ev-market-civic' and e['date'] == '2026-10-24' for e in near)
    assert mo.events_between(events, TODAY, TODAY + timedelta(days=6), 40.0, -74.0) == []
    far_future = mo.events_between(events, date(2030, 1, 1), date(2030, 1, 7), *civic)
    assert all(e['date'] >= '2030-01-01' for e in far_future)  # repeating events expand into the window
    multi = mo.events_between(events, date(2026, 10, 27), date(2026, 10, 28), 37.7890, -122.4210)
    assert {e['id'] for e in multi} >= {'ev-school-half'} and {e['date'] for e in multi if e['id'] == 'ev-school-half'} == {'2026-10-27', '2026-10-28'}
    assert mo.events_between(events, TODAY, TODAY, 37.80, -122.40, radius_km=0.01) == []


def test_rain_factor():
    assert mo.rain_factor(10, 'Sports & cycling') == 1.0
    assert mo.rain_factor(None, 'Hardware') == 1.0
    assert mo.rain_factor(100, 'Sports & cycling') == pytest.approx(0.7)
    assert mo.rain_factor(100, 'Hardware') > 1.0
    assert mo.rain_factor(100, 'Electronics') < 1.0
    assert mo.rain_factor(70, 'Electronics') > mo.rain_factor(100, 'Electronics')


def test_forecast_deterministic_and_explainable(client, merchant, monkeypatch):
    with SessionLocal() as db:
        m = db.get(Merchant, 'm1')
        a = mo.build_forecast(db, m, WEATHER, today=TODAY)
        b = mo.build_forecast(db, m, WEATHER, today=TODAY)
    assert a == b and a['label'].startswith('Demo forecast')
    assert len(a['demand_index'][0]['days']) == 7 and 3 <= len(a['insights']) <= 6
    assert a['weather_risk']['date'] == '2026-10-25' and 'Rain' in a['weather_risk']['title']
    assert any(any(d['event_factor'] > 1 for d in r['days']) for r in a['demand_index'])
    rainy = {r['category']: r['days'][1]['weather_factor'] for r in a['demand_index']}
    assert all(f != 1.0 for f in rainy.values())
    assert all(p['reason'] and p['suggested_quantity'] > 0 for p in a['prep'])


def test_forecast_endpoint_degrades_without_weather(client, merchant, monkeypatch):
    fake_weather(monkeypatch, {'source': 'unavailable', 'days': []})
    body = client.get('/api/merchant/forecast?merchant_id=m1', headers=merchant).json()
    assert body['weather_risk'] is None and body['weather']['source'] == 'unavailable'
    assert all(d['weather_factor'] == 1.0 for r in body['demand_index'] for d in r['days'])
