from datetime import date, datetime, timedelta

from app import forecast_drivers as fd
from app import merchant_overview as mo
from app.database import SessionLocal
from app.models import Merchant, PickupSlot

TODAY = date(2026, 10, 24)


def weather(rain=5, temp=18, days=7, rainy=()):
    return {'source': 'test', 'days': [{'date': (TODAY + timedelta(days=i)).isoformat(), 'summary': 'Rain' if i in rainy else 'Clear', 'code': 63 if i in rainy else 0,
                                        'temp_max_c': temp, 'rain_chance_pct': 100 if i in rainy else rain} for i in range(days)]}


def build(w=None, today=TODAY):
    with SessionLocal() as db:
        return mo.build_forecast(db, db.get(Merchant, 'm1'), w or weather(), today=today)


def test_new_keys_present_and_deterministic(client):
    a, b = build(), build()
    assert a == b
    for key in ('summary', 'daily', 'drivers', 'branches', 'calendar', 'stock_cover', 'pickup_outlook', 'scenarios', 'method_note', 'confidence'):
        assert key in a
    assert {d['id'] for d in a['drivers']} >= {'rain', 'weekday', 'payday', 'holiday', 'events', 'stock', 'pickup', 'promotions'}
    assert all(d['confidence'] in ('observed', 'modelled', 'demo', 'not_modelled') and len(d['effect_pct']) == 7 for d in a['drivers'])
    assert len(a['branches']) in (0, 2, 3) and (not a['branches'] or abs(sum(b['share_pct'] for b in a['branches']) - 100) <= 2)
    assert a['calendar']['demo'] is True and 'Demo calendar' in a['calendar']['note']


def test_scoping_other_store_is_404(client, merchant, monkeypatch):
    async def _fetch(lat, lng, **kw):
        return weather()
    monkeypatch.setattr(mo, 'fetch_daily_weather', _fetch)
    ok = client.get('/api/merchant/forecast?merchant_id=m1', headers=merchant)
    assert ok.status_code == 200 and 'drivers' in ok.json()
    assert client.get('/api/merchant/forecast?merchant_id=m2', headers=merchant).status_code == 404


def test_rain_driver_lowers_outdoor_and_shows_in_drivers(client):
    dry, wet = build(weather()), build(weather(rainy=(1,)))
    rain_dry = next(d for d in dry['drivers'] if d['id'] == 'rain')
    rain_wet = next(d for d in wet['drivers'] if d['id'] == 'rain')
    assert rain_dry['effect_pct'][1] == 0 and rain_wet['effect_pct'][1] != 0
    assert wet['summary']['rain_days'] == 1 and dry['summary']['rain_days'] == 0
    assert mo.rain_factor(100, 'Garden') == 0.7 and mo.rain_factor(100, 'Grocery') > 1
    scenario = next(s for s in wet['scenarios']['items'] if s['id'] == 'no_rain')
    assert scenario['delta_units_7d'] != 0 and scenario['days'] == [(TODAY + timedelta(days=1)).isoformat()]
    assert next(s for s in dry['scenarios']['items'] if s['id'] == 'no_rain')['delta_units_7d'] == 0


def test_payday_window_lifts_discretionary_more_than_essentials():
    assert fd.country_for('Asia/Kuala_Lumpur') == 'MY' and fd.country_for('Asia/Singapore') == 'SG' and fd.country_for('America/Los_Angeles', 37.7, -122.4) == 'US'
    assert fd.country_for('Europe/Paris') == 'INTL'
    payday = date(2026, 10, 31)
    assert fd.payday_position(payday, 'SG')[0] == 0
    f0, _ = fd.payday_factor(payday, 'SG', False)
    f2, _ = fd.payday_factor(payday + timedelta(days=2), 'SG', False)
    f5, why5 = fd.payday_factor(payday + timedelta(days=5), 'SG', False)
    assert f0 > f2 > 1.0 and f5 == 1.0 and why5 is None
    assert 1.0 < fd.payday_factor(payday, 'SG', True)[0] < f0
    assert fd.payday_factor(payday - timedelta(days=2), 'SG', False)[0] < 1.0
    assert fd.payday_position(date(2026, 10, 25), 'MY')[0] == 0 and fd.payday_position(date(2026, 10, 15), 'US')[0] == 0


def test_payday_shows_up_in_forecast_when_in_window(client):
    f = build(today=date(2026, 10, 31))
    day0 = f['demand_index'][0]['days'][0]
    assert day0['payday_factor'] > 1 and day0['payday_reason'] == 'Payday today'
    assert next(d for d in f['drivers'] if d['id'] == 'payday')['effect_pct'][0] > 0


def test_holiday_calendar_is_demo_and_country_aware():
    my = fd.calendar_entries('MY', date(2026, 11, 1), date(2026, 11, 30))
    us = fd.calendar_entries('US', date(2026, 11, 1), date(2026, 11, 30))
    assert any(r['name'] == 'Deepavali' for r in my) and not any(r['name'] == 'Deepavali' for r in us)
    assert any(r['name'] == 'Thanksgiving' for r in us) and all(r['demo'] for r in my + us)
    assert any(r['name'] == 'Black Friday' for r in my)  # international dates apply everywhere
    assert fd.holiday_factor([{'effect_pct': -25, 'name': 'Christmas Day'}], False)[0] == 0.75
    assert fd.holiday_factor([{'effect_pct': -25, 'name': 'Christmas Day'}], True)[0] > 0.75


def test_stock_out_suppression_is_not_low_demand():
    window = 28
    # Sold 2/day on days 10..27, then nothing for 10 days because it ran out.
    series = [0] * 10 + [2] * 18
    out = fd.product_rate(series, 0, 0.5, window)
    instock = fd.product_rate(series, 5, 0.5, window)
    assert out['suppressed_days'] == 10 and instock['suppressed_days'] == 0
    assert out['rate'] > instock['rate'] and out['rate'] > out['naive_rate']
    assert all(v == out['rate'] for v in out['clean_series'][:10]) and out['clean_series'][10:] == [2] * 18
    # A single quiet day is not evidence of a stock-out.
    assert fd.product_rate([0, 3, 3] + [3] * 25, 0, 0.5, window)['suppressed_days'] == 0
    # Never sold and unavailable: whole window is suppressed, falls back to the prior.
    never = fd.product_rate([0] * window, 0, 0.5, window)
    assert never['suppressed_days'] == window and abs(never['rate'] - 0.5 * 7 / 7) < 1e-9


def test_forecast_reports_stock_cover_and_note(client):
    with SessionLocal() as db:
        p = next(x for x in db.query(mo.Product).filter_by(merchant_id='m1', active=True))
        p.quantity, p.hold_quantity = 0, 0
        db.commit()
    f = build()
    cover = f['stock_cover']
    assert 'Do not reorder on stock-out-suppressed demand' in cover['note']
    assert cover['categories'] and all({'days_of_cover', 'out_of_stock_products', 'suppressed_days', 'status'} <= set(c) for c in cover['categories'])
    assert any(c['out_of_stock_products'] for c in cover['categories'])  # demo store has out-of-stock products
    assert all(p['headline'] and p['reason'] for p in f['prep'])


def test_pickup_capacity_flag():
    assert fd.pickup_flag(50, 100) == 'ok' and fd.pickup_flag(90, 100) == 'tight' and fd.pickup_flag(100, 100) == 'capped' and fd.pickup_flag(5, 0) == 'none'


def test_pickup_outlook_flags_a_capped_day(client):
    with SessionLocal() as db:
        db.query(PickupSlot).filter(PickupSlot.merchant_id == 'm1').delete()
        loc = db.query(mo.MerchantLocation).filter_by(merchant_id='m1').order_by(mo.MerchantLocation.created_at, mo.MerchantLocation.id).first()
        # Tomorrow (local noon, store tz is America/Los_Angeles): one tiny slot, fully booked. The day after: plenty of room.
        tomorrow = datetime.combine(TODAY + timedelta(days=1), datetime.min.time()).replace(hour=19)
        db.add(PickupSlot(id='cap-a', merchant_id='m1', location_id=loc.id, start_at=tomorrow, end_at=tomorrow + timedelta(hours=1), capacity=2, booked_count=2))
        later = tomorrow + timedelta(days=1)
        db.add(PickupSlot(id='cap-b', merchant_id='m1', location_id=loc.id, start_at=later, end_at=later + timedelta(hours=1), capacity=500, booked_count=1))
        db.commit()
        out = mo.build_forecast(db, db.get(Merchant, 'm1'), weather(), today=TODAY)['pickup_outlook']
    days = {d['date']: d for d in out['days']}
    t1, t2, t3 = (TODAY + timedelta(days=i) for i in (1, 2, 3))
    assert days[t1.isoformat()]['flag'] == 'capped' and days[t1.isoformat()]['free'] == 0 and 'capped' in days[t1.isoformat()]['note']
    assert days[t2.isoformat()]['flag'] == 'ok'
    assert days[t3.isoformat()]['flag'] == 'none'
    assert out['risk_days'] >= 2
