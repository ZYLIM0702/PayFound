"""Merchant overview: analytics from real merchant data and a deterministic DEMO forecast."""
from __future__ import annotations

import asyncio
import json
import math
import time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .access import merchant_role
from .assistant.weather import CODES
from .auth import Principal, require_role
from .commerce import opening
from . import forecast_drivers as fd
from .database import db_session
from .models import Merchant, MerchantLocation, Order, OrderItem, PickupSlot, Product, Review, utcnow

router = APIRouter(tags=['Merchant overview'])
DEFAULT_LOW_STOCK = 3
STALE_AFTER = timedelta(hours=24)
DEAD = ('CANCELLED', 'EXPIRED', 'REFUNDED')
EVENTS_FILE = Path(__file__).with_name('demo_events.json')
FOOTFALL_BOOST = {'low': 0.05, 'medium': 0.12, 'high': 0.22, 'very_high': 0.35}
EVENT_RADIUS_KM = 3.0
LABEL = 'Demo forecast · generated for demonstration, not an AI model output'


def scope(db: Session, p: Principal, merchant_id: str) -> Merchant:
    """Merchant for this principal or 404 (never reveals whether another store exists)."""
    merchant = db.get(Merchant, merchant_id)
    if not merchant or not merchant_role(db, p, merchant):
        raise HTTPException(404, 'Store not found')
    return merchant


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    a = math.sin(math.radians(lat2 - lat1) / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.asin(min(1, math.sqrt(a)))


def low_threshold(product, default: int = DEFAULT_LOW_STOCK) -> int:
    """Per-product override lives in source_metadata.low_stock_at; otherwise the default."""
    try:
        value = json.loads(product.source_metadata or '{}').get('low_stock_at')
        return int(value) if value is not None and int(value) >= 0 else default
    except (ValueError, TypeError):
        return default


def stock_state(product, default: int = DEFAULT_LOW_STOCK, now: datetime | None = None) -> str:
    now = now or utcnow()
    available = max(0, product.quantity - product.hold_quantity)
    if available == 0:
        return 'out'
    if available <= low_threshold(product, default):
        return 'low'
    if not product.stock_updated_at or now - product.stock_updated_at > STALE_AFTER:
        return 'stale'
    return 'in_stock'


def _tz(location) -> ZoneInfo:
    try:
        return ZoneInfo(location.timezone) if location else ZoneInfo('UTC')
    except Exception:  # noqa: BLE001 - unknown tz name falls back to UTC
        return ZoneInfo('UTC')


def _local(dt: datetime, tz: ZoneInfo) -> datetime:
    return dt.replace(tzinfo=timezone.utc).astimezone(tz)


def _primary(db, merchant_id):
    return db.scalar(select(MerchantLocation).where(MerchantLocation.merchant_id == merchant_id, MerchantLocation.active.is_(True))
                     .order_by(MerchantLocation.created_at, MerchantLocation.id))


def _items(db, orders):
    """order id -> [(product_id, name, qty, unit_price_cents)] from order_items, falling back to the order row."""
    ids = [o.id for o in orders]
    out: dict[str, list] = defaultdict(list)
    if ids:
        for it in db.scalars(select(OrderItem).where(OrderItem.order_id.in_(ids))):
            out[it.order_id].append((it.product_id, it.product_name, it.quantity, it.unit_price_cents))
    return out


def _lines(order, items, names):
    return items.get(order.id) or [(order.product_id, names.get(order.product_id, 'Item'), order.quantity, order.amount_cents // max(1, order.quantity))]


def hours_today(location, now: datetime | None = None) -> str:
    if not location:
        return 'Hours not set'
    try:
        local = (now or datetime.now(timezone.utc)).astimezone(_tz(location))
        special = json.loads(location.special_hours or '{}')
        periods = special.get(local.date().isoformat(), json.loads(location.hours or '{}').get(str(local.weekday()), []))
    except Exception:  # noqa: BLE001
        return 'Hours not set'
    return ', '.join(f"{x['start']}–{x['end']}" for x in periods) if periods else 'Closed today'


def store_block(db, merchant) -> dict:
    reviews = list(db.scalars(select(Review.rating).where(Review.merchant_id == merchant.id, Review.visible.is_(True))))
    locations = list(db.scalars(select(MerchantLocation).where(MerchantLocation.merchant_id == merchant.id, MerchantLocation.active.is_(True))))
    primary = _primary(db, merchant.id)
    return {'id': merchant.id, 'name': merchant.name, 'slug': merchant.slug, 'is_open': opening(merchant, primary), 'status_override': merchant.status_override,
            'branch_count': len(locations), 'hours_today': hours_today(primary), 'rating': round(sum(reviews) / len(reviews), 1) if reviews else None,
            'review_count': len(reviews), 'verified': merchant.verified, 'timezone': primary.timezone if primary else 'UTC'}


def build_analytics(db: Session, merchant: Merchant, days: int = 30, threshold: int = DEFAULT_LOW_STOCK, now: datetime | None = None) -> dict:
    now = now or utcnow()
    location = _primary(db, merchant.id)
    tz = _tz(location)
    today = _local(now, tz).date()
    start_day = today - timedelta(days=days - 1)
    products = list(db.scalars(select(Product).where(Product.merchant_id == merchant.id)))
    names = {p.id: p.name for p in products}
    orders = list(db.scalars(select(Order).where(Order.merchant_id == merchant.id).order_by(Order.created_at)))
    items = _items(db, orders)

    day_keys = [start_day + timedelta(days=i) for i in range(days)]
    revenue: dict[str, dict[date, list]] = defaultdict(lambda: {d: [0, 0] for d in day_keys})
    hours = [0] * 24
    qty: dict[str, int] = defaultdict(int)
    rev: dict[str, int] = defaultdict(int)
    for o in orders:
        if o.status in DEAD:
            continue
        local = _local(o.created_at, tz)
        if local.date() < start_day:
            continue
        hours[local.hour] += 1
        if o.payment_status == 'CAPTURED':
            bucket = revenue[o.currency][local.date()]
            bucket[0] += o.amount_cents
            bucket[1] += 1
            for pid, name, q, unit in _lines(o, items, names):
                qty[name] += q
                rev[name] += q * unit
    revenue_out = {cur: [{'date': d.isoformat(), 'amount_cents': v[0], 'orders': v[1]} for d, v in sorted(series.items())] for cur, series in revenue.items()}
    currency = products[0].currency if products else 'USD'
    if not revenue_out:
        revenue_out[currency] = [{'date': d.isoformat(), 'amount_cents': 0, 'orders': 0} for d in day_keys]
    top = lambda m: [{'name': n, 'value': v} for n, v in sorted(m.items(), key=lambda kv: (-kv[1], kv[0]))[:6]]  # noqa: E731

    health = {'in_stock': 0, 'low': 0, 'out': 0, 'stale': 0}
    low_rows, stale_rows = [], []
    for p in products:
        if not p.active:
            continue
        state = stock_state(p, threshold, now)
        health[state] += 1
        row = {'id': p.id, 'name': p.name, 'available': max(0, p.quantity - p.hold_quantity), 'threshold': low_threshold(p, threshold), 'state': state}
        if state in ('low', 'out'):
            low_rows.append(row)
        elif state == 'stale':
            stale_rows.append({**row, 'updated_at': p.stock_updated_at.isoformat() + 'Z' if p.stock_updated_at else None})
    low_rows.sort(key=lambda r: (r['available'], r['name']))

    slot_days: dict[date, list] = defaultdict(lambda: [0, 0])
    horizon = datetime.combine(today + timedelta(days=7), datetime.min.time())
    for s in db.scalars(select(PickupSlot).where(PickupSlot.merchant_id == merchant.id, PickupSlot.start_at >= datetime.combine(today - timedelta(days=2), datetime.min.time()),
                                                 PickupSlot.start_at < horizon)):
        b = slot_days[_local(s.start_at, tz).date()]
        b[0] += s.capacity
        b[1] += s.booked_count
    pickup = [{'date': d.isoformat(), 'capacity': v[0], 'booked': v[1], 'utilisation_pct': round(100 * v[1] / v[0]) if v[0] else 0} for d, v in sorted(slot_days.items())]

    awaiting = [o for o in orders if o.confirmation_status == 'PENDING' and o.status == 'RESERVED']
    to_prepare = [o for o in orders if o.status in ('PAID', 'ACCEPTED') and o.payment_status == 'CAPTURED']
    alerts = build_alerts(low_rows, stale_rows, awaiting, to_prepare, names)
    return {'merchant_id': merchant.id, 'days': days, 'timezone': str(tz), 'currency': currency, 'store': store_block(db, merchant),
            'revenue': revenue_out, 'revenue_note': 'Recorded captured payment amounts (simulated in demo). Not profit.',
            'orders_by_hour': [{'hour': h, 'orders': n} for h, n in enumerate(hours)],
            'top_by_quantity': top(qty), 'top_by_revenue': top(rev), 'currency_for_revenue': currency,
            'stock_health': {**health, 'threshold': threshold}, 'low_stock': low_rows, 'stale_stock': stale_rows,
            'pickup_utilisation': pickup, 'awaiting_confirmation': len(awaiting), 'to_prepare': len(to_prepare), 'alerts': alerts}


def build_alerts(low_rows, stale_rows, awaiting, to_prepare, names) -> list[dict]:
    out = []
    out_of_stock = [r for r in low_rows if r['state'] == 'out']
    if out_of_stock:
        out.append({'id': 'out', 'kind': 'stock', 'severity': 'high', 'count': len(out_of_stock), 'title': f"{len(out_of_stock)} product{'s' if len(out_of_stock) != 1 else ''} out of stock",
                    'detail': ', '.join(r['name'] for r in out_of_stock[:3]), 'to': '/merchant/inventory', 'action': 'Open inventory',
                    'ask': f"Which products are out of stock ({', '.join(r['name'] for r in out_of_stock[:3])}) and what should I reorder first?"})
    low_only = [r for r in low_rows if r['state'] == 'low']
    if low_only:
        out.append({'id': 'low', 'kind': 'stock', 'severity': 'high' if any(r['available'] <= 1 for r in low_only) else 'medium', 'count': len(low_only),
                    'title': f"{len(low_only)} product{'s' if len(low_only) != 1 else ''} low on stock", 'detail': ', '.join(f"{r['name']} ({r['available']})" for r in low_only[:3]),
                    'to': '/merchant/inventory', 'action': 'Record count', 'ask': f"These products are low on stock: {', '.join(r['name'] for r in low_only[:4])}. How much should I reorder?"})
    if awaiting:
        out.append({'id': 'confirm', 'kind': 'orders', 'severity': 'high', 'count': len(awaiting), 'title': f"{len(awaiting)} order{'s' if len(awaiting) != 1 else ''} waiting for your confirmation",
                    'detail': 'Confirm you hold the stock before the reservation expires', 'to': '/merchant/orders', 'action': 'Review orders',
                    'ask': f"I have {len(awaiting)} reservation(s) waiting for stock confirmation. How should I handle them?"})
    if to_prepare:
        out.append({'id': 'prepare', 'kind': 'orders', 'severity': 'medium', 'count': len(to_prepare), 'title': f"{len(to_prepare)} paid order{'s' if len(to_prepare) != 1 else ''} to prepare",
                    'detail': 'Paid and waiting to be accepted or packed', 'to': '/merchant/orders', 'action': 'Prepare orders',
                    'ask': f"I have {len(to_prepare)} paid order(s) to prepare. What should I pack first?"})
    if stale_rows:
        out.append({'id': 'stale', 'kind': 'stock', 'severity': 'low', 'count': len(stale_rows), 'title': f"{len(stale_rows)} product{'s' if len(stale_rows) != 1 else ''} with stale stock counts",
                    'detail': 'Not updated for over 24 hours, so shoppers see lower confidence', 'to': '/merchant/inventory', 'action': 'Refresh counts',
                    'ask': f"{len(stale_rows)} products have stock counts older than 24 hours. Which should I recount first?"})
    return out


def load_events(path: Path = EVENTS_FILE) -> list[dict]:
    return json.loads(path.read_text(encoding='utf-8'))['events']


def events_between(events: list[dict], start: date, end: date, lat: float, lng: float, radius_km: float = EVENT_RADIUS_KM) -> list[dict]:
    """Event occurrences with start<=date<=end within radius_km of (lat, lng); repeating events are expanded."""
    found = []
    for e in events:
        km = haversine_km(lat, lng, e['lat'], e['lng'])
        if km > radius_km:
            continue
        first = date.fromisoformat(e['date'])
        span = (date.fromisoformat(e['end_date']) - first).days if e.get('end_date') else 0
        step = int(e.get('repeat_days') or 0)
        if step:
            k = max(0, math.ceil(((start - timedelta(days=span)) - first).days / step))
            cursor = first + timedelta(days=k * step)
        else:
            cursor = first
        while cursor <= end:
            for offset in range(span + 1):
                day = cursor + timedelta(days=offset)
                if start <= day <= end:
                    found.append({'id': e['id'], 'name': e['name'], 'type': e['type'], 'date': day.isoformat(), 'start': e.get('start'), 'end': e.get('end'),
                                  'footfall': e['footfall'], 'distance_km': round(km, 1), 'boosts': e.get('boosts', [])})
            if not step:
                break
            cursor += timedelta(days=step)
    return sorted(found, key=lambda x: (x['date'], x['start'] or '', x['id']))


def event_factor(events_on_day: list[dict], category: str) -> tuple[float, str | None]:
    boost, top = 0.0, None
    for e in events_on_day:
        proximity = max(0.4, 1 - e['distance_km'] / (EVENT_RADIUS_KM * 1.5))
        gain = FOOTFALL_BOOST.get(e['footfall'], 0.05) * proximity * (1.0 if category in e['boosts'] else 0.35)
        if top is None or gain > top[0]:
            top = (gain, e['name'])
        boost += gain
    return round(1 + min(boost, 0.6), 3), top[1] if top else None


_WX: dict[tuple[float, float], tuple[float, dict]] = {}
RAINY = {51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99}


async def fetch_daily_weather(lat: float, lng: float, *, transport=None) -> dict:
    """7-day Open-Meteo daily forecast, cached 30 min (failures cached 2 min). Never raises."""
    key = (round(lat, 2), round(lng, 2))
    hit = _WX.get(key)
    if hit and time.monotonic() < hit[0]:
        return hit[1]
    try:
        async with httpx.AsyncClient(timeout=1.2, transport=transport) as client:
            r = await client.get('https://api.open-meteo.com/v1/forecast', params={'latitude': key[0], 'longitude': key[1], 'timezone': 'auto', 'forecast_days': 7,
                                 'daily': 'weather_code,temperature_2m_max,precipitation_probability_max'})
            r.raise_for_status()
            d = r.json()['daily']
        result = {'source': 'Open-Meteo', 'days': [{'date': t, 'summary': CODES.get(d['weather_code'][i], 'Unknown'), 'code': d['weather_code'][i],
                  'temp_max_c': d['temperature_2m_max'][i], 'rain_chance_pct': (d.get('precipitation_probability_max') or [None] * 9)[i]} for i, t in enumerate(d['time'])]}
        ttl = 1800
    except Exception:  # noqa: BLE001 - weather is optional; the forecast degrades to a neutral factor
        result, ttl = {'source': 'unavailable', 'days': []}, 120
    _WX[key] = (time.monotonic() + ttl, result)
    return result


OUTDOOR = {'Sports & cycling', 'Garden', 'Outdoor'}
ESSENTIALS = {'Hardware', 'Pet essentials', 'Grocery', 'Pharmacy'}


def rain_factor(rain_chance_pct: float | None, category: str) -> float:
    """Walk-in demand multiplier for rain. Below 40% chance nothing changes."""
    if rain_chance_pct is None or rain_chance_pct < 40:
        return 1.0
    p = (rain_chance_pct - 40) / 60
    if category in OUTDOOR:
        return round(1 - 0.3 * p, 3)
    if category in ESSENTIALS:
        return round(1 + 0.1 * p, 3)
    return round(1 - 0.1 * p, 3)


def heat_factor(temp_max_c: float | None, category: str) -> float:
    if temp_max_c is None or temp_max_c < 28:
        return 1.0
    p = min(1.0, (temp_max_c - 28) / 8)
    return round(1 + (0.2 if category in ('Grocery', 'Beverages') else -0.08 if category in OUTDOOR else 0.0) * p, 3)


def weather_factor(day: dict | None, category: str) -> tuple[float, str | None]:
    if not day:
        return 1.0, None
    f = rain_factor(day.get('rain_chance_pct'), category) * heat_factor(day.get('temp_max_c'), category)
    if f == 1.0:
        return 1.0, None
    why = f"{day['summary'].lower()} ({day['rain_chance_pct']}% rain)" if rain_factor(day.get('rain_chance_pct'), category) != 1.0 else f"hot day ({round(day['temp_max_c'])}°C)"
    return round(f, 3), why


def baseline_rate(product_id: str) -> float:
    """Stable demo prior (units/day) so thin demo history still gives a readable forecast."""
    return 0.4 + (sum(ord(c) for c in product_id) % 6) * 0.15


def _locations(db, merchant_id) -> list:
    return list(db.scalars(select(MerchantLocation).where(MerchantLocation.merchant_id == merchant_id, MerchantLocation.active.is_(True))
                           .order_by(MerchantLocation.created_at, MerchantLocation.id)))


def _wd(iso: str) -> str:
    return date.fromisoformat(iso).strftime('%A')


def _direction(effects: list[float]) -> str:
    if not any(abs(e) >= 0.5 for e in effects):
        return 'none'
    ups, downs = any(e >= 0.5 for e in effects), any(e <= -0.5 for e in effects)
    return 'mixed' if ups and downs else 'up' if ups else 'down'


def _mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def build_forecast(db: Session, merchant: Merchant, weather: dict, today: date | None = None, events: list[dict] | None = None, window: int = 28) -> dict:
    locations = _locations(db, merchant.id)
    location = locations[0] if locations else None
    lat = location.latitude if location else merchant.latitude
    lng = location.longitude if location else merchant.longitude
    tz = _tz(location)
    now = utcnow()
    today = today or _local(now, tz).date()
    horizon = [today + timedelta(days=i) for i in range(7)]
    country = fd.country_for(location.timezone if location else None, lat, lng)
    cal_rows = fd.calendar_entries(country, today, today + timedelta(days=30))
    cal_by_day: dict[str, list[dict]] = defaultdict(list)
    for r in cal_rows:
        cal_by_day[r['date']].append(r)
    events = load_events() if events is None else events
    near = events_between(events, today, horizon[-1], lat, lng)
    wx_days = {d['date']: d for d in weather.get('days', [])}
    products = [p for p in db.scalars(select(Product).where(Product.merchant_id == merchant.id)) if p.active]
    names = {p.id: p.name for p in products}
    orders = [o for o in db.scalars(select(Order).where(Order.merchant_id == merchant.id)) if o.status not in DEAD]
    items = _items(db, orders)
    primary_id = location.id if location else None
    by_product: dict[str, list[int]] = defaultdict(lambda: [0] * window)
    branch_units: dict[str | None, int] = defaultdict(int)
    order_days: list[date] = []
    orders_in_window = 0
    for o in orders:
        local_day = _local(o.created_at, tz).date()
        age = (today - local_day).days
        if 0 <= age < window:
            orders_in_window += 1
            order_days.append(local_day)
            for pid, _, q, _ in _lines(o, items, names):
                by_product[pid][age] += q
                branch_units[o.location_id or primary_id] += q

    # Per-product rate, with stock-out days excluded rather than counted as low demand.
    rates: dict[str, dict] = {}
    for p in products:
        available = max(0, p.quantity - p.hold_quantity)
        rates[p.id] = fd.product_rate(by_product.get(p.id, [0] * window), available, baseline_rate(p.id), window)

    categories = sorted({p.category for p in products})
    cat_units: dict[str, list[float]] = {c: [0.0] * window for c in categories}
    for p in products:
        for age, u in enumerate(rates[p.id]['clean_series']):
            cat_units[p.category][age] += u

    def trend_of(series: list[float]) -> float:
        recent, prior = sum(series[:7]) / 7, sum(series[7:]) / max(1, window - 7)
        if recent + prior == 0:
            return 1.0
        return round(max(0.7, min(1.4, (recent + 0.3) / (prior + 0.3))), 3)

    dow, dow_source = fd.weekday_curve(order_days, [today - timedelta(days=i) for i in range(window)])
    index = []
    for c in categories:
        t = trend_of(cat_units[c])
        essential = c in ESSENTIALS
        row = {'category': c, 'trend_factor': t, 'days': []}
        for d in horizon:
            wf, wwhy = weather_factor(wx_days.get(d.isoformat()), c)
            ef, ewhy = event_factor([e for e in near if e['date'] == d.isoformat()], c)
            hf, hwhy = fd.holiday_factor(cal_by_day.get(d.isoformat(), []), essential)
            pf, pwhy = fd.payday_factor(d, country, essential)
            wk = dow[d.weekday()]
            row['days'].append({'date': d.isoformat(), 'demand_index': round(100 * t * wf * ef * wk * hf * pf), 'weather_factor': wf, 'event_factor': ef,
                                'weekday_factor': wk, 'holiday_factor': hf, 'payday_factor': pf, 'weather_reason': wwhy, 'event_reason': ewhy,
                                'holiday_reason': hwhy, 'payday_reason': pwhy})
        index.append(row)
    cat_days = {r['category']: r for r in index}

    prep, risks, suppressed_products = [], [], []
    cat_rate: dict[str, float] = defaultdict(float)
    cat_exp7: dict[str, float] = defaultdict(float)
    cat_avail: dict[str, int] = defaultdict(int)
    units_by_day = [0.0] * 7
    product_exp7: dict[str, float] = {}
    for p in sorted(products, key=lambda x: x.id):
        pr = rates[p.id]
        rate = pr['rate']
        row = cat_days[p.category]
        mult = [d['demand_index'] / 100 for d in row['days']]
        expected_3 = rate * sum(mult[:3])
        expected_7 = rate * sum(mult)
        product_exp7[p.id] = expected_7
        for i, m in enumerate(mult):
            units_by_day[i] += rate * m
        available = max(0, p.quantity - p.hold_quantity)
        cat_rate[p.category] += rate
        cat_exp7[p.category] += expected_7
        cat_avail[p.category] += available
        suggested = max(0, math.ceil(expected_3 * 1.25) - available)
        gains = {'weather': sum(d['weather_factor'] - 1 for d in row['days']), 'event': sum(d['event_factor'] - 1 for d in row['days']),
                 'trend': (row['trend_factor'] - 1) * 7, 'payday': sum(d['payday_factor'] - 1 for d in row['days']),
                 'holiday': sum(d['holiday_factor'] - 1 for d in row['days'])}
        driver, gain = max(gains.items(), key=lambda kv: (abs(kv[1]), kv[0]))
        day_name, label = '', ''
        if abs(gain) < 0.05:  # nothing stands out: fall back to the weekday curve
            peak = max(row['days'], key=lambda d: d['weekday_factor'])
            driver, day_name = 'weekday', _wd(peak['date'])
            label, reason = ('Weekend peak' if peak['weekday_factor'] > 1.1 else 'Busy day'), f"Weekday: {day_name} is the busiest day of the week for this store"
        elif driver == 'weather':
            top_day = max(row['days'], key=lambda d: abs(d['weather_factor'] - 1))
            day_name = _wd(top_day['date'])
            rainy = rain_factor((wx_days.get(top_day['date']) or {}).get('rain_chance_pct'), p.category) != 1.0
            label = 'Rain' if rainy else 'Heat'
            reason = f"Weather: {top_day['weather_reason']} on {date.fromisoformat(top_day['date']).strftime('%a')}"
        elif driver == 'event':
            top_day = max(row['days'], key=lambda d: d['event_factor'])
            day_name, label = _wd(top_day['date']), 'Event'
            reason = f"Event: {top_day['event_reason']} on {date.fromisoformat(top_day['date']).strftime('%a')}"
        elif driver == 'payday':
            top_day = max(row['days'], key=lambda d: abs(d['payday_factor'] - 1))
            day_name, label = _wd(top_day['date']), 'Payday'
            reason = f"Payday: {top_day['payday_reason']} ({date.fromisoformat(top_day['date']).strftime('%a')})"
        elif driver == 'holiday':
            top_day = max(row['days'], key=lambda d: abs(d['holiday_factor'] - 1))
            day_name, label = _wd(top_day['date']), top_day['holiday_reason'] or 'Holiday'
            reason = f"Holiday: {top_day['holiday_reason']} on {date.fromisoformat(top_day['date']).strftime('%a')} (demo calendar)"
        else:
            driver = 'trend'
            up = row['trend_factor'] > 1
            label = 'Rising sales' if up else 'Falling sales' if row['trend_factor'] < 1 else 'Steady sales'
            reason = f"Trend: sales {'up' if up else 'down' if row['trend_factor'] < 1 else 'steady'} vs the previous weeks"
        cover = round(available / (expected_7 / 7), 1) if expected_7 > 0 else None
        if suggested > 0:
            prep.append({'product_id': p.id, 'product': p.name, 'category': p.category, 'suggested_quantity': suggested, 'available': available,
                         'expected_next_3_days': round(expected_3, 1), 'driver': driver, 'reason': reason,
                         'headline': f"{label}{' ' + day_name if day_name else ''}: +{suggested} {p.name}",
                         'note': (f"{pr['suppressed_days']} out-of-stock days were not counted as low demand." if pr['suppressed_days'] else None)})
        if pr['suppressed_days']:
            suppressed_products.append({'product_id': p.id, 'product': p.name, 'category': p.category, 'suppressed_days': pr['suppressed_days'],
                                        'rate_per_day': round(rate, 2), 'naive_rate_per_day': round(pr['naive_rate'], 2)})
        if available == 0 or (cover is not None and cover < 3):
            risks.append({'product_id': p.id, 'product': p.name, 'available': available, 'days_of_cover': cover,
                          'severity': 'high' if available == 0 or (cover is not None and cover < 1.5) else 'medium',
                          'reason': 'Out of stock' if available == 0 else f"About {cover} days of cover at the forecast pace"})
    prep.sort(key=lambda r: (-r['suggested_quantity'], r['product']))
    risks.sort(key=lambda r: (r['available'], r['product']))
    suppressed_products.sort(key=lambda r: (-r['suppressed_days'], r['product']))

    cover_rows = []
    for c in categories:
        in_cat = [p for p in products if p.category == c]
        out = [p.name for p in in_cat if max(0, p.quantity - p.hold_quantity) == 0]
        supp = sum(rates[p.id]['suppressed_days'] for p in in_cat)
        cov = round(cat_avail[c] / (cat_exp7[c] / 7), 1) if cat_exp7[c] > 0 else None
        status = 'out' if len(out) == len(in_cat) and in_cat else 'low' if out or (cov is not None and cov < 3) else 'ok'
        cover_rows.append({'category': c, 'products': len(in_cat), 'available_units': cat_avail[c], 'expected_units_7d': round(cat_exp7[c], 1), 'days_of_cover': cov,
                           'out_of_stock_products': out, 'suppressed_days': supp, 'status': status,
                           'note': ('Sales dropped while out of stock. Reorder on normal demand, not on the quiet days.' if supp else None)})
    cover_rows.sort(key=lambda r: ({'out': 0, 'low': 1, 'ok': 2}[r['status']], r['days_of_cover'] if r['days_of_cover'] is not None else 999, r['category']))
    stock_cover = {'categories': cover_rows, 'suppressed_products': suppressed_products[:8],
                   'note': 'Do not reorder on stock-out-suppressed demand: days when a product was out of stock are left out of the demand rate, so a stock-out is never read as low demand.'}

    weights = {c: cat_rate[c] or 1e-9 for c in categories}
    daily = []
    for i, d in enumerate(horizon):
        idx = _mean_weighted([(cat_days[c]['days'][i]['demand_index'], weights[c]) for c in categories]) if categories else 100
        daily.append({'date': d.isoformat(), 'weekday': _wd(d.isoformat()), 'demand_index': round(idx), 'expected_units': round(units_by_day[i], 1)})
    opd = (orders_in_window + 2.0 * 7) / (window + 7)  # orders/day, thin history blended with a demo prior of 2/day

    slot_rows: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
    lo = datetime.combine(today - timedelta(days=1), datetime.min.time())
    hi = datetime.combine(today + timedelta(days=8), datetime.min.time())
    for s in db.scalars(select(PickupSlot).where(PickupSlot.merchant_id == merchant.id, PickupSlot.start_at >= lo, PickupSlot.start_at < hi)):
        b = slot_rows[(s.location_id, _local(s.start_at, tz).date().isoformat())]
        b[0] += s.capacity
        b[1] += s.booked_count
    pickup_days = []
    for i, d in enumerate(horizon):
        iso = d.isoformat()
        cap = sum(v[0] for (loc, day), v in slot_rows.items() if day == iso)
        booked = sum(v[1] for (loc, day), v in slot_rows.items() if day == iso)
        wx = wx_days.get(iso) or {}
        rain_p = max(0.0, ((wx.get('rain_chance_pct') or 0) - 40) / 60)
        modelled = round(opd * daily[i]['demand_index'] / 100 * (1 + 0.15 * rain_p))
        expected = max(booked, modelled)
        flag = fd.pickup_flag(expected, cap)
        pickup_days.append({'date': iso, 'weekday': d.strftime('%a'), 'slots_capacity': cap, 'booked': booked, 'free': max(0, cap - booked), 'expected_orders': expected,
                            'rain_uplift_pct': round(15 * rain_p), 'flag': flag, 'orders_over_capacity': max(0, expected - cap) if cap else expected,
                            'note': ('No pickup slots published, so pickup sales are capped at zero.' if flag == 'none' else
                                     f"Expected {expected} orders vs {cap} slots: sales will be capped by pickup capacity." if flag == 'capped' else
                                     f"Slots are nearly full ({expected} expected of {cap}). Open more slots." if flag == 'tight' else None)})
    pickup = {'days': pickup_days, 'risk_days': sum(1 for d in pickup_days if d['flag'] in ('tight', 'capped', 'none')),
              'note': 'Expected orders = recent orders per day x demand index (rain shifts a little more demand to pickup). Booked slots are real; the rest is modelled.'}

    branches = []
    if len(locations) > 1:
        total_units = sum(branch_units.get(l.id, 0) for l in locations) or 0
        for l in locations:
            share = branch_units.get(l.id, 0) / total_units if total_units else 1 / len(locations)
            branches.append({'location_id': l.id, 'name': l.name, 'units_28d': branch_units.get(l.id, 0), 'share_pct': round(100 * share),
                             'expected_units': [round(u * share, 1) for u in units_by_day], 'expected_units_7d': round(sum(units_by_day) * share, 1),
                             'pickup_capacity_7d': sum(v[0] for (loc, day), v in slot_rows.items() if loc == l.id and day in {x.isoformat() for x in horizon}),
                             'pickup_booked_7d': sum(v[1] for (loc, day), v in slot_rows.items() if loc == l.id and day in {x.isoformat() for x in horizon})})

    seen_ranges, ahead = set(), []
    for r in cal_rows:
        key = (r['name'], r['range_start'])
        if key not in seen_ranges:
            seen_ranges.add(key)
            ahead.append(r)
    paydays_ahead = [d for d in fd.paydays_in(country, today, today + timedelta(days=30)) if today <= d <= today + timedelta(days=30)]
    cal_horizon = []
    for d in horizon:
        since, to_next = fd.payday_position(d, country)
        cal_horizon.append({'date': d.isoformat(), 'days_since_payday': since, 'days_to_payday': to_next,
                            'holidays': [r['name'] for r in cal_by_day.get(d.isoformat(), [])],
                            'payday_label': fd.payday_factor(d, country, False)[1]})
    within14 = today + timedelta(days=14)
    calendar = {'country': country, 'country_name': fd.COUNTRY_NAMES[country], 'demo': True, 'note': fd.CALENDAR_NOTE, 'payday_rule': f"Demo payday rule: {fd.COUNTRY_PAYDAYS[country]}.",
                'entries': [r for r in ahead if r['range_start'] <= within14.isoformat() or r['date'] <= within14.isoformat()][:10],
                'paydays': [d.isoformat() for d in paydays_ahead][:4], 'horizon': cal_horizon,
                'ahead_days': 14, 'ahead_count': sum(1 for r in ahead if r['date'] <= within14.isoformat()) + sum(1 for d in paydays_ahead if d <= within14)}

    def effect(fn) -> list[float]:
        return [round(_mean((fn(c, i) - 1) * 100 for c in categories), 1) for i in range(7)]
    t0 = wx_days.get(horizon[0].isoformat()) or {}
    wx_ok = bool(wx_days)
    rain_p0 = max(0.0, ((t0.get('rain_chance_pct') or 0) - 40) / 60)
    rain_eff = effect(lambda c, i: rain_factor((wx_days.get(horizon[i].isoformat()) or {}).get('rain_chance_pct'), c))
    heat_eff = effect(lambda c, i: heat_factor((wx_days.get(horizon[i].isoformat()) or {}).get('temp_max_c'), c))
    dow_eff = effect(lambda c, i: dow[horizon[i].weekday()])
    pay_eff = effect(lambda c, i: cat_days[c]['days'][i]['payday_factor'])
    hol_eff = effect(lambda c, i: cat_days[c]['days'][i]['holiday_factor'])
    ev_eff = effect(lambda c, i: cat_days[c]['days'][i]['event_factor'])
    tr_eff = effect(lambda c, i: cat_days[c]['trend_factor'])
    out_now = [p for p in products if max(0, p.quantity - p.hold_quantity) == 0]
    t0pick = pickup_days[0]
    since0, to0 = fd.payday_position(horizon[0], country)
    hol_today = [r['name'] for r in cal_by_day.get(horizon[0].isoformat(), [])]
    ev_today = [e for e in near if e['date'] == horizon[0].isoformat()]

    def drv(id_, name, value, eff, confidence, summary, ask, data=None):
        return {'id': id_, 'name': name, 'today_value': value, 'effect_pct': eff, 'avg_effect_pct': round(_mean(eff), 1),
                'peak_effect_pct': max(eff, key=abs) if eff else 0.0, 'direction': _direction(eff), 'confidence': confidence, 'summary': summary, 'data': data, 'ask': ask}
    drivers = [
        drv('rain', 'Rain', (f"Rain {t0.get('rain_chance_pct')}%: lowers outdoor categories by up to {round(30 * rain_p0)}%" if rain_p0 > 0 else
                             f"Rain {t0.get('rain_chance_pct')}%: no effect below 40%" if t0.get('rain_chance_pct') is not None else 'Weather unavailable: neutral'),
            rain_eff, 'modelled' if wx_ok else 'demo', 'Heavy rain cuts walk-ins for outdoor and discretionary items (up to 30% / 10%), lifts essentials (up to 10%) and shifts orders to pickup.',
            'How does rain change my sales and pickups this week?', 'Open-Meteo forecast; effect size is a demo assumption'),
        drv('heat', 'Heat', (f"{round(t0['temp_max_c'])}°C: lifts cold drinks and grocery" if (t0.get('temp_max_c') or 0) >= 28 else
                             f"{round(t0['temp_max_c'])}°C: no effect below 28°C" if t0.get('temp_max_c') is not None else 'Weather unavailable: neutral'),
            heat_eff, 'modelled' if wx_ok else 'demo', 'Hot days raise grocery and drinks up to 20% and soften outdoor categories.', 'How should I prepare for hot days?', 'Open-Meteo forecast; effect size is a demo assumption'),
        drv('weekday', 'Day of week', f"{_wd(horizon[0].isoformat())}: {round((dow[horizon[0].weekday()] - 1) * 100):+d}% vs an average day", dow_eff, 'observed' if dow_source == 'observed' else 'modelled',
            'Weekends and Fridays are busier; early week is quiet. Blended with your own order history once there are 30+ orders.' if dow_source == 'observed' else 'Weekends and Fridays are busier; early week is quiet. Typical neighbourhood curve (needs 30+ orders to learn your own).',
            'Which days of the week are busiest for my store?', 'Your orders by weekday' if dow_source == 'observed' else 'Typical weekday curve'),
        drv('payday', 'Payday and month-end', (f"{'Payday today' if since0 == 0 else f'{since0} days after payday'}: discretionary spend up to +10%" if since0 is not None and since0 <= 3 else
                                              f"{to0} days to payday: spend slightly tighter" if to0 is not None and to0 <= 3 else
                                              f"Next payday in {to0} days" if to0 is not None else 'No payday in range'), pay_eff, 'demo',
            'The first days after payday lift discretionary spending (up to +10%); the last days before it are a little tighter. Payday dates follow a demo rule for the country.',
            'How do paydays and month-end affect my sales?', fd.CALENDAR_NOTE),
        drv('holiday', 'Holidays and seasons', (', '.join(hol_today) + ' today' if hol_today else (f"Next: {ahead[0]['name']} on {_wd(ahead[0]['date'])[:3]} {ahead[0]['date'][5:]}" if ahead else 'None in the demo calendar')),
            hol_eff, 'demo', 'Public holidays can shut or surge local footfall; school holidays and festive seasons lift family shopping. Dates are a demo calendar.',
            'Which holidays or festive periods are coming up and how should I prepare?', fd.CALENDAR_NOTE),
        drv('events', 'Local events', (f"{len(ev_today)} nearby today: {ev_today[0]['name']}" if ev_today else f"{len(near)} in the next 7 days within {int(EVENT_RADIUS_KM)} km" if near else 'No events within 3 km'),
            ev_eff, 'demo', 'Markets, sports fixtures and festivals pull crowds; nearby events add up to +60% for the categories they boost.',
            'Which nearby events matter most for my store this week?', 'Fictional demo events feed'),
        drv('trend', 'Recent sales trend', f"{'Up' if _mean(cat_days[c]['trend_factor'] for c in categories) > 1.02 else 'Down' if _mean(cat_days[c]['trend_factor'] for c in categories) < 0.98 else 'Steady'} vs the previous 3 weeks" if categories else 'No sales yet',
            tr_eff, 'observed', 'Last 7 days of units against the 3 weeks before, per category, capped at +40% / -30%. Stock-out days are not counted as low demand.',
            'Why are my recent sales trending this way?', 'Your orders, last 28 days'),
        drv('stock', 'Stock availability', (f"{len(out_now)} product{'s' if len(out_now) != 1 else ''} out of stock: sales on them are capped at zero" if out_now else 'Everything is available'), [0.0] * 7, 'observed',
            'A product that is out of stock cannot sell. PayFound leaves those days out of the demand rate and raises prep on normal demand instead.',
            'Which out-of-stock products should I reorder first?', 'Your inventory counts'),
        drv('pickup', 'Pickup capacity', (f"{t0pick['free']} of {t0pick['slots_capacity']} slots free today" if t0pick['slots_capacity'] else 'No pickup slots published today'), [0.0] * 7, 'observed',
            'Sales can only be collected in published pickup slots. Flags days where expected orders approach or exceed capacity.', 'Do I have enough pickup slots this week?', 'Your pickup slots'),
        drv('promotions', 'Promotions and price changes', 'No promotion data in PayFound yet', [0.0] * 7, 'not_modelled',
            'Discount days commonly lift units. We do not hold promotion schedules, so the baseline excludes them. See the scenario panel for a demo what-if.',
            'Should I run a promotion this week and on what?', 'Not available'),
        drv('traffic', 'Traffic and commute', 'No traffic or roadworks feed connected', [0.0] * 7, 'not_modelled',
            'Roadworks, jams and transit disruption change footfall and parking. Not observed or modelled here.', 'How could roadworks or traffic affect my store?', 'Not available'),
    ]

    def cat_total(c: str, factor=lambda i: 1.0, days=range(7)) -> float:
        return sum(cat_rate[c] * cat_days[c]['days'][i]['demand_index'] / 100 * factor(i) for i in days)
    base_total = sum(units_by_day)
    scenarios = []
    rain_days = [i for i, d in enumerate(horizon) if rain_factor((wx_days.get(d.isoformat()) or {}).get('rain_chance_pct'), 'x') != 1.0]
    delta_rain = 0.0
    for c in categories:
        for i in rain_days:
            rf = rain_factor((wx_days.get(horizon[i].isoformat()) or {}).get('rain_chance_pct'), c)
            delta_rain += cat_rate[c] * cat_days[c]['days'][i]['demand_index'] / 100 * (1 / rf - 1)
    scenarios.append({'id': 'no_rain', 'title': 'If the rain is cancelled', 'assumption': 'Rain factors set to 1.0 on every rainy day; everything else unchanged.',
                      'days': [horizon[i].isoformat() for i in rain_days], 'delta_units_7d': round(delta_rain, 1), 'delta_pct': round(100 * delta_rain / base_total, 1) if base_total else 0.0,
                      'summary': ('No rain is forecast above 40%, so nothing would change.' if not rain_days else
                                  f"About {abs(round(delta_rain))} {'more' if delta_rain >= 0 else 'fewer'} unit{'s' if abs(round(delta_rain)) != 1 else ''} over {len(rain_days)} rainy day{'s' if len(rain_days) != 1 else ''}: outdoor categories recover, essentials ease."),
                      'extra_prep': [], 'ask': 'If the rain stays away, how should I change my stock plan this week?'})
    if categories:
        top_c = max(categories, key=lambda c: (cat_exp7[c], c))
        quiet = sorted(range(7), key=lambda i: (cat_days[top_c]['days'][i]['demand_index'], i))[:2]
        lift = 0.18
        delta_promo = cat_total(top_c, lambda i: lift if i in quiet else 0.0)
        top_products = sorted([p for p in products if p.category == top_c], key=lambda p: (-product_exp7[p.id], p.id))[:3]
        extra = []
        for p in top_products:
            units = math.ceil(sum(rates[p.id]['rate'] * cat_days[top_c]['days'][i]['demand_index'] / 100 * lift for i in quiet))
            avail = max(0, p.quantity - p.hold_quantity)
            extra.append({'product_id': p.id, 'product': p.name, 'extra_units': units, 'available': avail, 'short': avail < product_exp7[p.id] + units})
        scenarios.append({'id': 'promo_top', 'title': f"If you run a promotion on {top_c}", 'assumption': f"Demo assumption: +{round(lift * 100)}% units on the 2 quietest days for {top_c}, no cannibalisation.",
                          'days': [horizon[i].isoformat() for i in sorted(quiet)], 'delta_units_7d': round(delta_promo, 1), 'delta_pct': round(100 * delta_promo / base_total, 1) if base_total else 0.0,
                          'summary': f"About {round(delta_promo)} more unit{'s' if round(delta_promo) != 1 else ''} over {' and '.join(_wd(horizon[i].isoformat()) for i in sorted(quiet))}. {sum(1 for x in extra if x['short'])} of the top {len(extra)} products would need restocking first.",
                          'extra_prep': extra, 'ask': f"Should I run a promotion on {top_c} on {' and '.join(_wd(horizon[i].isoformat()) for i in sorted(quiet))}?"})
    scenario_block = {'label': 'Demo scenarios: simple what-ifs with fixed assumptions, not predictions', 'baseline_units_7d': round(base_total, 1), 'items': scenarios}

    risk = weather_risk(weather, horizon)
    insights = build_insights(index, prep, risks, near, risk, horizon, calendar=calendar, pickup=pickup, suppressed=suppressed_products, daily=daily)
    avg7 = round(_mean(d['demand_index'] for d in daily)) if daily else 100
    rain_count = sum(1 for d in horizon if (wx_days.get(d.isoformat()) or {}).get('rain_chance_pct') is not None and wx_days[d.isoformat()]['rain_chance_pct'] >= 40)
    summary = {'demand_index_today': daily[0]['demand_index'] if daily else 100, 'demand_index_avg_7d': avg7,
               'peak_day': max(daily, key=lambda d: (d['demand_index'], d['date']))['date'] if daily else None,
               'rain_days': rain_count, 'events_nearby': len(near), 'calendar_ahead': calendar['ahead_count'], 'pickup_risk_days': pickup['risk_days'],
               'out_of_stock_products': len(out_now), 'suppressed_products': len(suppressed_products)}
    confidence = {'level': 'demo', 'parts': [
        {'name': 'Weather forecast', 'status': 'observed' if wx_ok else 'unavailable', 'detail': 'Open-Meteo daily forecast. Effect sizes are demo assumptions.' if wx_ok else 'Weather could not be loaded, so weather factors are neutral.'},
        {'name': 'Your sales history', 'status': 'observed', 'detail': f"{orders_in_window} orders in the last {window} days. Thin history is blended with a demo prior."},
        {'name': 'Stock and pickup slots', 'status': 'observed', 'detail': 'Current counts and published slots. Stock-out days are excluded from demand.'},
        {'name': 'Weekday curve', 'status': dow_source, 'detail': 'Typical curve, blended with your own once you have 30+ orders.'},
        {'name': 'Holidays and paydays', 'status': 'demo', 'detail': fd.CALENDAR_NOTE},
        {'name': 'Local events', 'status': 'demo', 'detail': 'Fictional demo events feed.'},
        {'name': 'Promotions and traffic', 'status': 'not_modelled', 'detail': 'No data in PayFound yet.'}]}
    method_note = ("Each category starts at 100 (a normal day) and is multiplied by its recent sales trend, the weather (rain, heat), the day of the week, "
                   "how close payday is, demo holidays and nearby events. Days when a product was out of stock are left out so a stock-out is never read as low demand. "
                   "Prep quantities cover 3 days of expected sales plus a 25% buffer, minus what you hold. This is explainable arithmetic with fixed assumptions, "
                   "not a trained AI model, and it calls no LLM.")
    return {'label': LABEL, 'merchant_id': merchant.id, 'generated_for': today.isoformat(),
            'method': 'demand index = 100 x recent-sales trend x weather x local events x weekday x payday x holidays (100 = a normal day)',
            'method_note': method_note, 'confidence': confidence,
            'weather': {'source': weather.get('source'), 'days': weather.get('days', [])}, 'events': near, 'demand_index': index,
            'prep': prep[:10], 'stock_risks': risks[:8], 'insights': insights, 'weather_risk': risk,
            'summary': summary, 'daily': daily, 'drivers': drivers, 'branches': branches, 'calendar': calendar, 'stock_cover': stock_cover,
            'pickup_outlook': pickup, 'scenarios': scenario_block}


def _mean_weighted(pairs) -> float:
    total = sum(w for _, w in pairs)
    return sum(v * w for v, w in pairs) / total if total else 100.0


def weather_risk(weather: dict, horizon: list[date]) -> dict | None:
    """First day in the next 3 where rain or heat is likely to change pickup."""
    for d in weather.get('days', [])[:3]:
        if (d.get('rain_chance_pct') or 0) >= 60 or (d.get('code') in RAINY and (d.get('rain_chance_pct') or 0) >= 40):
            return {'id': 'weather', 'kind': 'weather', 'severity': 'medium', 'count': 1, 'date': d['date'], 'title': f"Rain expected {date.fromisoformat(d['date']).strftime('%A')} ({d['rain_chance_pct']}%)",
                    'detail': 'Expect fewer walk-ins and more pickup orders; keep a dry handover spot ready', 'to': '/merchant/pickup', 'action': 'Check pickup slots',
                    'ask': f"Rain is forecast on {d['date']} ({d['rain_chance_pct']}% chance). How will it affect pickups and what should I prepare?"}
        if (d.get('temp_max_c') or 0) >= 30:
            return {'id': 'weather', 'kind': 'weather', 'severity': 'medium', 'count': 1, 'date': d['date'], 'title': f"Hot day {date.fromisoformat(d['date']).strftime('%A')} ({round(d['temp_max_c'])}°C)",
                    'detail': 'Heat can delay pickups; keep perishable orders cool', 'to': '/merchant/pickup', 'action': 'Check pickup slots',
                    'ask': f"It will reach {round(d['temp_max_c'])}°C on {d['date']}. How should I adjust pickups and stock?"}
    return None


def build_insights(index, prep, risks, near, risk, horizon, calendar=None, pickup=None, suppressed=None, daily=None) -> list[dict]:
    out = []
    peak = max(((r['category'], d) for r in index for d in r['days']), key=lambda x: (x[1]['demand_index'], x[0]), default=None)
    if peak:
        day = date.fromisoformat(peak[1]['date']).strftime('%A')
        why = peak[1]['event_reason'] or peak[1]['holiday_reason'] or peak[1]['weather_reason'] or peak[1]['payday_reason'] or 'the recent sales trend and the weekday pattern'
        out.append({'title': f"{peak[0]} demand peaks on {day}", 'body': f"Demand index {peak[1]['demand_index']} (100 is normal), mostly from {why}.",
                    'ask': f"Explain why {peak[0]} demand is forecast to peak on {day} and what I should do to prepare."})
    if pickup:
        bad = [d for d in pickup['days'] if d['flag'] in ('capped', 'tight')]
        if bad:
            d = max(bad, key=lambda x: (x['expected_orders'] - x['slots_capacity'], x['date']))
            out.append({'title': f"Pickup slots {'will run out' if d['flag'] == 'capped' else 'are nearly full'} on {_wd(d['date'])}",
                        'body': f"About {d['expected_orders']} orders expected against {d['slots_capacity']} slots. Open more slots so sales are not capped.",
                        'ask': f"Pickup capacity looks tight on {d['date']} ({d['expected_orders']} expected vs {d['slots_capacity']} slots). How many slots should I add?"})
    if calendar:
        pay = next((h for h in calendar['horizon'] if h['payday_label'] and ('after' in h['payday_label'] or h['payday_label'] == 'Payday today')), None)
        hol = next((h for h in calendar['horizon'] if h['holidays']), None)
        if hol:
            out.append({'title': f"{hol['holidays'][0]} on {_wd(hol['date'])}", 'body': 'From the demo calendar. Holidays change footfall; plan staffing and stock around it.',
                        'ask': f"{hol['holidays'][0]} falls on {hol['date']}. How will it affect my sales and what should I prepare?"})
        elif pay:
            out.append({'title': 'Payday boosts the next few days', 'body': f"{pay['payday_label']}: discretionary spend is typically higher in the first days after payday.",
                        'ask': 'It is just after payday. Which products should I push or stock up on?'})
    if near:
        e = max(near, key=lambda x: (FOOTFALL_BOOST.get(x['footfall'], 0), x['name']))
        out.append({'title': f"{e['name']} on {date.fromisoformat(e['date']).strftime('%A')}", 'body': f"{e['footfall'].replace('_', ' ').capitalize()} footfall expected {e['distance_km']} km away. Stock related items and staff the counter.",
                    'ask': f"The event '{e['name']}' is {e['distance_km']} km from my store on {e['date']}. How should I prepare?"})
    if risk:
        out.append({'title': risk['title'], 'body': risk['detail'], 'ask': risk['ask']})
    if suppressed:
        s0 = suppressed[0]
        out.append({'title': f"{s0['product']} sold less only because it ran out", 'body': f"{s0['suppressed_days']} out-of-stock days are not counted as low demand, so reorder on the normal pace of about {s0['rate_per_day']} a day.",
                    'ask': f"{s0['product']} has been out of stock for {s0['suppressed_days']} days. How much should I reorder without being misled by the quiet days?"})
    if prep:
        p = prep[0]
        out.append({'title': f"Prepare {p['suggested_quantity']} more {p['product']}", 'body': f"{p['reason']}. You have {p['available']} available.",
                    'ask': f"Why should I prepare {p['suggested_quantity']} more {p['product']}? {p['reason']}."})
    if risks:
        out.append({'title': f"{len(risks)} product{'s' if len(risks) != 1 else ''} at risk of running out", 'body': ', '.join(r['product'] for r in risks[:3]) + '.',
                    'ask': f"These products may run out soon: {', '.join(r['product'] for r in risks[:4])}. What should I reorder and when?"})
    return out[:6]


@router.get('/merchant/analytics')
def analytics(merchant_id: str = Query(max_length=48), days: int = Query(30, ge=1, le=90), low_stock_threshold: int = Query(DEFAULT_LOW_STOCK, ge=0, le=100),
              db: Session = Depends(db_session), p: Principal = Depends(require_role('merchant', 'admin'))):
    return build_analytics(db, scope(db, p, merchant_id), days, low_stock_threshold)


@router.get('/merchant/forecast')
async def forecast(merchant_id: str = Query(max_length=48), db: Session = Depends(db_session), p: Principal = Depends(require_role('merchant', 'admin'))):
    merchant = scope(db, p, merchant_id)
    location = _primary(db, merchant.id)
    lat, lng = (location.latitude, location.longitude) if location else (merchant.latitude, merchant.longitude)
    weather = await asyncio.wait_for(fetch_daily_weather(lat, lng), 2.0)
    return build_forecast(db, merchant, weather)
