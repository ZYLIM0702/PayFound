"""Busy, clearly synthetic pickup schedule for the demo merchant calendar."""
from __future__ import annotations
import hashlib
import os
import random
import re
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select

from .models import (FulfilmentProof, Merchant, MerchantLocation, Order, OrderItem, PickupBooking, PickupSlot, Product, utcnow)

PAST_DAYS = 1
FUTURE_DAYS = 7
EXTRA_BRANCHES = {'m1': [('loc-m1-b2', 'Northside Electronics Marina', '2 Marina Blvd, San Francisco, CA', 37.8057, -122.4375),
                         ('loc-m1-b3', 'Northside Electronics Mission Bay', '1200 4th St, San Francisco, CA', 37.7706, -122.3896)]}
LINKED_MERCHANTS = {'m1': 44, 'm2': 6, 'm3': 6, 'm4': 6, 'm14': 8}
BUYERS = ['Aisha K.', 'Ben T.', 'Carla M.', 'Dev P.', 'Elena R.', 'Farid S.', 'Grace L.', 'Hugo B.', 'Ines C.', 'Jon W.', 'Kira N.', 'Leo D.']
FOOD = ('grocery', 'greengrocer', 'bakery', 'dairy', 'butcher', 'restaurant', 'convenience')


def _demo_zone(fallback: str) -> ZoneInfo:
    """Business hours are authored in the demo viewer's wall clock: DEMO_PICKUP_TZ, else this machine's zone, else the branch zone."""
    names = [os.getenv('DEMO_PICKUP_TZ', '')]
    try:
        names.append(os.path.realpath('/etc/localtime').split('zoneinfo/')[-1])
    except OSError:
        pass
    for name in names + [fallback]:
        try:
            if name:
                return ZoneInfo(name)
        except Exception:
            continue
    return ZoneInfo('UTC')


def _capacity_base(category: str) -> int:
    c = category.lower()
    if any(w in c for w in FOOD): return 10
    if 'pharmacy' in c: return 6
    if 'hardware' in c: return 3
    if any(w in c for w in ('electronics', 'home', 'household')): return 4
    return 5


def _hours(merchant: Merchant) -> tuple[int, int]:
    """Pickup desk hours in minutes from midnight. 24h shops staff the desk 08:00-20:00."""
    times = re.findall(r'(\d{2}):(\d{2})', merchant.hours or '')
    if len(times) < 2: return 8 * 60, 20 * 60
    start, end = int(times[0][0]) * 60 + int(times[0][1]), int(times[1][0]) * 60 + int(times[1][1])
    if end <= start: end = 23 * 60 + 30  # closes after midnight: clip to the evening
    return start, min(end, 24 * 60)


def _demand(minute: int, weekday: int) -> float:
    """Share of capacity that tends to be booked: lunch and after-work peaks, broad weekend midday."""
    h = minute / 60
    bump = lambda centre, width, height: height * max(0.0, 1 - abs(h - centre) / width)
    if weekday >= 5:
        return 0.18 + bump(12.5, 3.5, 0.72) + bump(16.5, 1.5, 0.25)
    return 0.12 + bump(12.5, 1.4, 0.70) + bump(17.8, 1.7, 0.80) + bump(9.0, 1.0, 0.18)


def _branches(db, merchant_ids=None):
    for mid, extras in EXTRA_BRANCHES.items():
        for lid, name, address, lat, lon in extras:
            m = db.get(Merchant, mid)
            if m and not db.get(MerchantLocation, lid):
                main = db.get(MerchantLocation, 'loc-' + mid)
                db.add(MerchantLocation(id=lid, merchant_id=mid, name=name, address=address, latitude=lat, longitude=lon,
                                        timezone=main.timezone if main else 'America/Los_Angeles', hours=main.hours if main else '{}'))
    db.flush()
    return list(db.scalars(select(MerchantLocation).where(MerchantLocation.active.is_(True), MerchantLocation.id.like('loc-m%')).order_by(MerchantLocation.id)))


def seed_demo_pickup(db, force: bool = False) -> int:
    """Add pickup windows for every demo branch (yesterday to +7 days). Returns the number of windows created."""
    if os.getenv('DEMO_MODE', 'false').lower() != 'true' or db.get_bind().dialect.name != 'sqlite':
        return 0
    if not force and os.getenv('PAYFOUND_TESTING') == '1':
        return 0
    merchants = {m.id: m for m in db.scalars(select(Merchant))}
    locations = _branches(db)
    now = utcnow()
    created = 0
    for loc in locations:
        merchant = merchants.get(loc.merchant_id)
        if not merchant:
            continue
        zone = _demo_zone(loc.timezone or 'America/Los_Angeles')
        today = datetime.now(zone).date()
        open_min, close_min = _hours(merchant)
        step = 15 if any(w in merchant.category.lower() for w in ('restaurant', 'bakery')) else 30
        base = _capacity_base(merchant.category)
        scale = {'b2': 0.8, 'b3': 0.65}.get(loc.id.rsplit('-', 1)[-1], 1.0)
        first = datetime.combine(today - timedelta(days=PAST_DAYS), time.min, tzinfo=zone).astimezone(timezone.utc).replace(tzinfo=None)
        last = datetime.combine(today + timedelta(days=FUTURE_DAYS + 1), time.min, tzinfo=zone).astimezone(timezone.utc).replace(tzinfo=None)
        existing = [(s.start_at, s.end_at) for s in db.scalars(select(PickupSlot).where(
            PickupSlot.location_id == loc.id, PickupSlot.end_at > first, PickupSlot.start_at < last))]
        for offset in range(-PAST_DAYS, FUTURE_DAYS + 1):
            day: date = today + timedelta(days=offset)
            rng = random.Random(f'{loc.id}:{day.isoformat()}')
            day_factor = rng.uniform(0.75, 1.15) * (1.1 if day.weekday() >= 5 else 1.0)
            for minute in range(open_min, close_min - step + 1, step):
                s_utc = datetime.combine(day, time(minute // 60, minute % 60), tzinfo=zone).astimezone(timezone.utc).replace(tzinfo=None)
                e_utc = s_utc + timedelta(minutes=step)
                if any(s < e_utc and e > s_utc for s, e in existing):
                    continue
                capacity = max(2, round(base * scale * (1.4 if _demand(minute, day.weekday()) > 0.7 else 1.0) + rng.choice([-1, 0, 0, 1])))
                fill = _demand(minute, day.weekday()) * day_factor * rng.uniform(0.7, 1.35) * 1.3
                if offset > 3: fill *= 0.8
                if offset == -1: fill = min(1.0, fill * 1.1)
                booked = min(capacity, max(0, round(fill * capacity)))
                if rng.random() < 0.05: booked = 0
                db.add(PickupSlot(id='dp-' + hashlib.md5(f'{loc.id}|{s_utc:%Y%m%d%H%M}'.encode()).hexdigest()[:24], merchant_id=loc.merchant_id, location_id=loc.id,
                                  start_at=s_utc, end_at=e_utc, capacity=capacity, booked_count=booked))
                created += 1
    db.flush()
    _link_orders(db, now)
    db.flush()
    return created


def _link_orders(db, now: datetime) -> None:
    """Order pickups for the calendar: real demo Order rows booked into seeded windows of the main branch."""
    if db.get(Order, 'demo-pk-m1-001'):
        return
    for mid, count in LINKED_MERCHANTS.items():
        loc = db.get(MerchantLocation, 'loc-' + mid)
        products = list(db.scalars(select(Product).where(Product.merchant_id == mid, Product.location_id == 'loc-' + mid,
                                                           Product.active.is_(True), Product.price_cents > 0, Product.currency == 'USD').order_by(Product.id)))
        if not loc or len(products) < 2:
            continue
        branch_ids = [loc.id] + [b[0] for b in EXTRA_BRANCHES.get(mid, [])]
        rng = random.Random(f'orders:{mid}')
        chosen = []
        for lid in branch_ids:
            slots = list(db.scalars(select(PickupSlot).where(PickupSlot.location_id == lid, PickupSlot.id.like('dp-%'),
                PickupSlot.booked_count > 0).order_by(PickupSlot.start_at)))
            taken = {b for b in db.scalars(select(PickupBooking.slot_id).where(PickupBooking.slot_id.in_([x.id for x in slots])))} if slots else set()
            free = [x for x in slots if x.id not in taken]
            chosen += rng.sample(free, min(count // len(branch_ids) + (1 if lid == loc.id else 0), len(free)))
        for n, slot in enumerate(sorted(chosen, key=lambda s: s.start_at), 1):
            oid = f'demo-pk-{mid}-{n:03d}'
            lines = [(p, rng.choice([1, 1, 2])) for p in rng.sample(products, rng.choice([1, 2, 2, 3]))]
            total = sum(p.price_cents * q for p, q in lines)
            until = (slot.start_at - now).total_seconds() / 3600
            if slot.end_at <= now: status, pay = 'COLLECTED', 'CAPTURED'
            elif until < 1.5: status, pay = rng.choice(['READY', 'READY', 'PREPARING']), 'CAPTURED'
            elif until < 6: status, pay = rng.choice(['PREPARING', 'ACCEPTED']), 'CAPTURED'
            else: status, pay = rng.choice(['ACCEPTED', 'ACCEPTED', 'RESERVED']), None
            pay = pay or ('CAPTURED' if status == 'ACCEPTED' else 'CREATED')
            created_at = min(now, slot.start_at - timedelta(hours=rng.randint(2, 20)))
            db.add(Order(id=oid, merchant_id=mid, location_id=slot.location_id, product_id=lines[0][0].id, quantity=lines[0][1],
                amount_cents=total, currency='USD', buyer_subject=f'demo-walkin-{mid}-{n}', buyer_name=rng.choice(BUYERS),
                status=status, payment_status=pay, payment_mode='demo', idempotency_key=oid,
                hold_expires_at=now + timedelta(days=1) if status == 'RESERVED' else created_at + timedelta(minutes=20),
                hold_released=status != 'RESERVED', inventory_committed=pay == 'CAPTURED', created_at=created_at, updated_at=created_at))
            db.flush()
            for p, q in lines:
                db.add(OrderItem(id=f'{oid}-{p.id}'[:48], order_id=oid, product_id=p.id, product_name=p.name, sku=p.sku,
                                 quantity=q, unit_price_cents=p.price_cents))
            db.add(PickupBooking(id=f'demo-pkb-{mid}-{n:03d}', order_id=oid, slot_id=slot.id, active=status != 'CANCELLED'))
            chain = ['ACCEPTED', 'PREPARING', 'READY', 'COLLECTED']
            if status in chain:
                steps = chain[:chain.index(status) + 1]
                for k, state in enumerate(steps):
                    at = min(now, created_at + timedelta(minutes=10 + 25 * k + rng.randint(0, 9)))
                    db.add(FulfilmentProof(id=f'{oid}-{state}'[:48], order_id=oid, state=state, actor='demo-merchant',
                                           proof='Demo history', created_at=at))
            if slot.booked_count == 0:
                slot.booked_count = 1
