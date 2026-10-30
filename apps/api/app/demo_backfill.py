"""Demo-only history for Northside Electronics (m1): ~36 extra products and ~90 days of past orders."""
from __future__ import annotations
import json
import math
import os
import random
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import insert, select

from .models import Merchant, MerchantLocation, Order, OrderItem, Product, utcnow

MERCHANT = 'm1'
MARKER = 'bf-000001'
DAYS = 90
TZ = ZoneInfo('America/Los_Angeles')
TILE = '/images/products/pos-demo-%s.webp'  # illustrated tiles shipped with the POS simulator
# (key, name, category, price_cents, quantity, stock_age_minutes, emoji, tile)
PRODUCTS = [
    ('usbc100', 'USB-C 100W cable 1 m', 'Cables', 1999, 34, 40, '➰', 'cable'),
    ('usbc240', 'USB-C 240W braided cable 2 m', 'Cables', 2499, 21, 130, '➰', 'cable'),
    ('hdmi21', 'HDMI 2.1 cable 2 m', 'Cables', 1799, 19, 300, '➰', 'cable'),
    ('dp14', 'DisplayPort 1.4 cable 1.5 m', 'Cables', 1699, 12, 1500, '➰', 'cable'),
    ('ethcat6', 'Cat 6 Ethernet cable 3 m', 'Cables', 999, 41, 90, '➰', 'cable'),
    ('aux35', '3.5 mm audio cable 1.2 m', 'Cables', 699, 26, 4300, '➰', 'cable'),
    ('gan65', '65W GaN wall charger', 'Charging', 3499, 17, 25, '🔋', 'wireless'),
    ('car30', '30W dual-port car charger', 'Charging', 1799, 14, 600, '🔋', 'wireless'),
    ('pad15', '15W Qi charging pad', 'Charging', 1999, 23, 210, '🔋', 'wireless'),
    ('travel', 'Travel charger with 4 ports', 'Charging', 2799, 9, 2900, '🔋', 'wireless'),
    ('bank20', 'Power bank 20,000mAh', 'Charging', 4999, 6, 55, '🔋', 'wireless'),
    ('earbuds', 'Wireless earbuds ANC', 'Audio', 5999, 15, 15, '🎧', 'headphones'),
    ('buds_s', 'True wireless earbuds', 'Audio', 2999, 28, 340, '🎧', 'headphones'),
    ('gaming', 'Gaming headset with mic', 'Audio', 4499, 8, 780, '🎧', 'headphones'),
    ('bar', 'Compact soundbar 60W', 'Audio', 8999, 4, 1900, '🔊', 'speaker'),
    ('speaker2', 'Waterproof Bluetooth speaker', 'Audio', 3999, 11, 120, '🔊', 'speaker'),
    ('mic', 'USB condenser microphone', 'Audio', 5499, 7, 3600, '🎙️', 'speaker'),
    ('plug2', 'Smart plug 2-pack', 'Smart home', 1999, 31, 35, '💡', 'lamp'),
    ('bulb4', 'Smart LED bulb 4-pack', 'Smart home', 2999, 16, 180, '💡', 'lamp'),
    ('strip', 'Smart power strip 4 outlets', 'Smart home', 3499, 10, 520, '💡', 'lamp'),
    ('sensor', 'Wi-Fi temperature sensor', 'Smart home', 1799, 13, 5000, '🌡️', 'lamp'),
    ('cam', 'Indoor security camera 2K', 'Smart home', 3999, 5, 70, '📷', 'lamp'),
    ('lightstrip', 'LED light strip 5 m', 'Smart home', 2299, 0, 8000, '💡', 'lamp'),
    ('webcam', 'Webcam 1080p', 'Electronics', 3999, 12, 95, '📷', 'stand'),
    ('monitor', 'Portable monitor 15.6 in', 'Electronics', 15999, 3, 240, '🖥️', 'stand'),
    ('mouse', 'Wireless mouse', 'Electronics', 1999, 25, 150, '🖱️', 'keyboard'),
    ('mousepad', 'Large desk mat', 'Accessories', 1999, 22, 700, '🖱️', 'stand'),
    ('sleeve14', 'Laptop sleeve 14 in', 'Accessories', 2499, 18, 410, '💻', 'stand'),
    ('sleeve16', 'Laptop sleeve 16 in', 'Accessories', 2799, 14, 410, '💻', 'stand'),
    ('phonestand', 'Adjustable phone stand', 'Accessories', 1299, 29, 60, '📱', 'stand'),
    ('screen', 'Tempered glass screen protector 2-pack', 'Accessories', 999, 45, 3100, '📱', 'stand'),
    ('ssd1tb', 'Portable SSD 1 TB', 'Storage', 8999, 9, 45, '💾', 'hub'),
    ('ssd500', 'Portable SSD 500 GB', 'Storage', 5499, 13, 45, '💾', 'hub'),
    ('flash128', 'USB flash drive 128 GB', 'Storage', 1499, 38, 200, '💾', 'hub'),
    ('sd256', 'microSD card 256 GB', 'Storage', 2299, 24, 1100, '💾', 'hub'),
    ('reader', 'USB-C card reader', 'Storage', 1299, 17, 2600, '💾', 'hub'),
    ('enclosure', 'NVMe SSD enclosure', 'Storage', 2999, 8, 900, '💾', 'hub'),
]
FIRST = ['Ava', 'Noah', 'Mia', 'Liam', 'Zoe', 'Ethan', 'Isla', 'Lucas', 'Nora', 'Owen', 'Maya', 'Leo', 'Ruby', 'Finn',
         'Ivy', 'Jude', 'Tessa', 'Caleb', 'Priya', 'Arjun', 'Hana', 'Kenji', 'Sofia', 'Mateo', 'Amara', 'Tomas']
LAST = ['Archer', 'Bennett', 'Calloway', 'Dalton', 'Ellison', 'Foster', 'Garrity', 'Hollis', 'Ibarra', 'Jensen', 'Kwan',
        'Lindqvist', 'Marlow', 'Nakamura', 'Okafor', 'Pellegrino', 'Quincy', 'Rowan', 'Sato', 'Thorne', 'Underhill']
WEEKDAY = [0.80, 0.90, 0.95, 1.00, 1.18, 1.50, 1.28]
HOUR_WEIGHT = {8: 1, 9: 2, 10: 3, 11: 4, 12: 8, 13: 7, 14: 4, 15: 3, 16: 4, 17: 6, 18: 7, 19: 5, 20: 3, 21: 1}
# (days ago start, days ago end, categories or None for store-wide, discount, demand boost)
PROMOS = [(64, 58, {'Audio'}, 0.15, 1.5), (40, 35, {'Charging', 'Cables'}, 0.10, 1.4), (13, 9, None, 0.12, 1.35)]


def _enabled(force: bool) -> bool:
    if os.getenv('DEMO_MODE', 'false').lower() != 'true':
        return False
    return force or os.getenv('PAYFOUND_TESTING') != '1'


def seed_demo_backfill(db, force: bool = False) -> dict:
    """Add the extra m1 products and ~90 days of order history. Returns counts (zeros when skipped)."""
    out = {'products': 0, 'orders': 0}
    if not _enabled(force) or db.get_bind().dialect.name != 'sqlite':
        return out
    merchant = db.get(Merchant, MERCHANT)
    main = db.get(MerchantLocation, 'loc-' + MERCHANT)
    if not merchant or not main:
        return out
    out['products'] = _seed_products(db)
    if db.get(Order, MARKER):
        return out
    out['orders'] = _seed_orders(db)
    return out


def _seed_products(db) -> int:
    now = utcnow()
    have = set(db.scalars(select(Product.id).where(Product.id.like('bf-p-%'))))
    added = 0
    for key, name, category, price, qty, age, emoji, tile in PRODUCTS:
        pid = 'bf-p-' + key
        if pid in have:
            continue
        observed = now - timedelta(minutes=age)
        stale = age > 2880
        db.add(Product(id=pid, merchant_id=MERCHANT, location_id='loc-' + MERCHANT, name=name,
            description=f'{name}. Fictional demo item with sample price and stock.', sku='BF-' + key.upper(),
            category=category, price_cents=price, quantity=qty, synthetic=True, supports_reservation=True,
            image_url=TILE % tile, image_emoji=emoji, inventory_source='synthetic_local',
            availability_state='unavailable' if qty == 0 else ('uncertain' if stale else 'likely_available'),
            stock_updated_at=observed, source_observed_at=observed,
            source_metadata=json.dumps({'demo_catalogue': True, 'catalogue_key': 'backfill:' + key, 'comparison_count': 1,
                                        'image': {'kind': 'illustration'}, 'catalogue_attributes': {'Demo': 'Illustrated tile'}})))
        added += 1
    db.flush()
    return added


def _round_price(cents: float) -> int:
    return max(199, int(round(cents / 10.0)) * 10)


def _seed_orders(db) -> int:
    rng = random.Random(20261023)
    now = utcnow()
    products = list(db.scalars(select(Product).where(Product.merchant_id == MERCHANT, Product.active.is_(True),
        Product.currency == 'USD', Product.price_cents > 0).order_by(Product.id)))
    locs = list(db.scalars(select(MerchantLocation).where(MerchantLocation.merchant_id == MERCHANT,
        MerchantLocation.active.is_(True)).order_by(MerchantLocation.id)))
    if not products or not locs:
        return 0
    loc_ids = [l.id for l in locs]
    loc_w = [0.55] + [0.45 / max(1, len(locs) - 1)] * (len(locs) - 1) if len(locs) > 1 else [1.0]
    # Per-product popularity (cheap items sell more) and a one-off price change somewhere in the window.
    info = {}
    for p in products:
        pop = (1.0 / math.sqrt(p.price_cents / 2000.0)) * rng.uniform(0.5, 1.6)
        change = None
        if rng.random() < 0.5:
            change = (rng.randint(18, 75), rng.choice([0.90, 0.93, 0.95, 1.06, 1.08, 1.12]))  # days ago, new/old ratio
        info[p.id] = (p, pop, change)
    buyers = [(f'demo-buyer-{i:02d}', f'{rng.choice(FIRST)} {rng.choice(LAST)}') for i in range(1, 71)]
    today = datetime.now(TZ).date()
    orders, items = [], []
    seq = 0
    for back in range(DAYS, -1, -1):
        day = today - timedelta(days=back)
        trend = 1.0 + 0.40 * (DAYS - back) / DAYS
        promo = next((pr for pr in PROMOS if pr[1] <= back <= pr[0]), None)
        lam = 13.0 * trend * WEEKDAY[day.weekday()] * (promo[4] if promo else 1.0) * rng.lognormvariate(0, 0.18)
        n = max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))
        weights = []
        for p, pop, _ in info.values():
            boost = 2.2 if promo and (promo[2] is None or p.category in promo[2]) else 1.0
            weights.append(pop * boost)
        plist = [v[0] for v in info.values()]
        hours = list(HOUR_WEIGHT)
        hw = [HOUR_WEIGHT[h] * (1.3 if day.weekday() >= 5 and 11 <= h <= 16 else 1.0) for h in hours]
        for _ in range(n):
            local = datetime(day.year, day.month, day.day, rng.choices(hours, hw)[0], rng.randint(0, 59), rng.randint(0, 59), tzinfo=TZ)
            created = local.astimezone(timezone.utc).replace(tzinfo=None)
            if created >= now - timedelta(minutes=30):
                continue
            seq += 1
            oid = f'bf-{seq + 0:06d}'
            nlines = rng.choices([1, 2, 3], [70, 25, 5])[0]
            picked: list[Product] = []
            while len(picked) < nlines:
                cand = rng.choices(plist, weights)[0]
                if cand not in picked:
                    picked.append(cand)
            lines = []
            for p in picked:
                _, _, change = info[p.id]
                factor = 1.0
                if change and back > change[0]:
                    factor = 1.0 / change[1]  # price before the change
                if promo and (promo[2] is None or p.category in promo[2]):
                    factor *= 1 - promo[3]
                unit = p.price_cents if factor == 1.0 else _round_price(p.price_cents * factor)
                lines.append((p, rng.choices([1, 2, 3], [74, 20, 6])[0], unit))
            total = sum(u * q for _, q, u in lines)
            r = rng.random()
            if r < 0.015:
                status, pay = 'REFUNDED', 'REFUNDED'
            elif r < 0.03:
                status, pay = 'CANCELLED', 'NOT_STARTED'
            elif r < 0.045:
                status, pay = 'EXPIRED', 'EXPIRED'
            else:
                status, pay = 'COLLECTED', 'CAPTURED'
            paid = pay in ('CAPTURED', 'REFUNDED')
            updated = created + timedelta(minutes=rng.randint(25, 240)) if paid else created + timedelta(minutes=rng.randint(5, 25))
            if status == 'REFUNDED':
                updated = created + timedelta(days=rng.randint(1, 4), minutes=rng.randint(0, 600))
            updated = min(updated, now)
            subject, name = rng.choice(buyers)
            orders.append(dict(id=oid, merchant_id=MERCHANT, location_id=rng.choices(loc_ids, loc_w)[0],
                product_id=lines[0][0].id, quantity=lines[0][1], amount_cents=total, currency='USD',
                buyer_subject=subject, buyer_name=name, status=status, payment_status=pay, payment_mode='demo',
                hold_expires_at=created + timedelta(minutes=20), hold_released=True, inventory_committed=status == 'COLLECTED',
                inventory_restocked=status == 'REFUNDED', confirmation_status='CONFIRMED', version=0,
                idempotency_key=oid, created_at=created, updated_at=updated))
            for p, q, unit in lines:
                items.append(dict(id=f'{oid}-{p.id}'[:48], order_id=oid, product_id=p.id, product_name=p.name,
                                  sku=p.sku, quantity=q, unit_price_cents=unit))
    if orders:
        # Marker (bf-000001) must exist even when the first generated slot was skipped.
        orders.sort(key=lambda o: o['created_at'])
        remap = {o['id']: f'bf-{i:06d}' for i, o in enumerate(orders, 1)}
        for o in orders:
            o['id'] = o['idempotency_key'] = remap[o['id']]
        for it in items:
            oid = remap[it['order_id']]
            suffix = it['id'][len(it['order_id']):]
            it['order_id'], it['id'] = oid, f'{oid}{suffix}'[:48]
        db.execute(insert(Order), orders)
        db.execute(insert(OrderItem), items)
        db.flush()
    return len(orders)
