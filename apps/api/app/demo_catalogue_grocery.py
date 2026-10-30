"""Idempotent, offline seeding of the fictional grocery / fresh-food demo stores (m14-m40)."""
from datetime import datetime, time, timedelta, timezone
from functools import lru_cache
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import select

from .models import Merchant, MerchantLocation, PickupSlot, Product, utcnow

TZ = 'America/Los_Angeles'
SLOT_DAYS = 7


@lru_cache(maxsize=1)
def grocery_data():
    return json.loads(Path(__file__).with_name('demo_catalogue_grocery.json').read_text())


def _slot_windows(periods):
    """Hourly pickup windows (start_hour, end_hour) for a day's opening periods."""
    out = []
    for period in periods:
        a = int(period['start'][:2]) * 60 + int(period['start'][3:])
        b = int(period['end'][:2]) * 60 + int(period['end'][3:])
        if a == 0 and b == 1440:
            a, b = 360, 1320  # 24-hour stores offer pickup 06:00-22:00
        elif b <= a:
            b = 1440  # overnight period: offer the evening part
        for start in range(a - a % 60, b - 59, 60):
            out.append((start, start + 60))
    return out[:14]


def seed_grocery_demo(db):
    data = grocery_data()
    zone = ZoneInfo(TZ)
    have_merchants = set(db.scalars(select(Merchant.id)))
    have_locations = set(db.scalars(select(MerchantLocation.id)))
    for store in data['merchants']:
        main = store['branches'][0]
        if store['id'] not in have_merchants:
            db.add(Merchant(id=store['id'], slug=store['slug'], name=store['name'], category=store['category'],
                description=store['description'] + ' Fictional store for the PayFound demo.', address=main['address'],
                latitude=main['latitude'], longitude=main['longitude'], hours=store['hours_label'], logo_emoji=store['emoji'],
                fulfillment_minutes=store['fulfillment_minutes'], verified=store['verified'], owner_subject='demo-merchant'))
    db.flush()
    for store in data['merchants']:
        for branch in store['branches']:
            if branch['id'] not in have_locations:
                db.add(MerchantLocation(id=branch['id'], merchant_id=store['id'], name=branch['name'], address=branch['address'],
                    latitude=branch['latitude'], longitude=branch['longitude'], timezone=TZ, hours=json.dumps(store['hours'])))
    db.flush()
    have_products = set(db.scalars(select(Product.id).where(Product.id.like('g%'))))
    now = utcnow()
    off = data['source']['open_food_facts']
    new_products = []
    by_id = {item['id']: item for item in data['products']}

    def metadata_for(item):
        metadata = {'demo_catalogue': True, 'catalogue_key': 'grocery:' + item['key'], 'unit': item['unit'],
                    'fresh': item['fresh'], 'catalogue_attributes': {'Unit': item['unit']}}
        if item['fresh']:
            metadata['shelf_life_hours'] = item['shelf_life_hours']
        if item.get('image_kind'):  # 'photo' = Open Food Facts front image (CC BY-SA); 'illustration' = generated tile
            metadata['image'] = {'kind': item['image_kind'], 'credits_url': '/image-credits.html#open-food-facts'}
        if item.get('off_code'):
            metadata['open_food_facts'] = {'code': item['off_code'], 'category': item['off_category'], 'licence': 'ODbL 1.0',
                                           'credits_url': '/image-credits.html#open-food-facts'}
        return metadata

    # Catalogue-version upgrade: refresh descriptive identity of already-seeded rows when the shipped catalogue changed.
    # Stock, holds, prices edited by merchants and freshness timestamps are never touched.
    for product in db.scalars(select(Product).where(Product.id.in_(list(have_products)))):
        item = by_id.get(product.id)
        if not item or product.inventory_source != 'synthetic_local':
            continue
        if (product.name, product.image_url, product.category) != (item['name'], item.get('image_url'), item['category']):
            if product.name != item['name']:
                product.price_cents, product.sku = item['price_cents'], item['sku']
            product.name, product.description, product.category = item['name'], item['description'], item['category']
            product.image_url, product.image_emoji = item.get('image_url'), item['emoji']
            old = json.loads(product.source_metadata or '{}')
            product.source_metadata = json.dumps({**metadata_for(item), 'comparison_count': old.get('comparison_count', 1)})
    for product in db.scalars(select(Product).where(Product.id.in_(list(have_products - set(by_id))))):
        product.active = False  # retired by a newer catalogue version (kept so past orders stay valid)
    for item in data['products']:
        if item['id'] in have_products:
            continue
        observed = now - timedelta(minutes=item['stock_age_minutes'])
        metadata = metadata_for(item)
        new_products.append(Product(id=item['id'], merchant_id=item['merchant_id'], location_id=item['location_id'],
            name=item['name'], description=item['description'], sku=item['sku'], category=item['category'],
            price_cents=item['price_cents'], quantity=item['quantity'], synthetic=True, supports_reservation=True,
            image_url=item.get('image_url'), image_emoji=item['emoji'], inventory_source='synthetic_local',
            availability_state='likely_available' if item['quantity'] > 0 else 'unavailable',
            stock_updated_at=observed, source_observed_at=observed, source_metadata=json.dumps(metadata)))
    db.add_all(new_products)
    db.flush()
    # Counts of offers per shared catalogue key (for the "same item in N stores" comparison).
    keys = {}
    for item in data['products']:
        keys[item['key']] = keys.get(item['key'], 0) + 1
    for product in db.scalars(select(Product).where(Product.id.in_(list(by_id)))):
        meta = json.loads(product.source_metadata)
        if meta.get('catalogue_key') and meta.get('comparison_count') != keys[meta['catalogue_key'][len('grocery:'):]]:
            meta['comparison_count'] = keys[meta['catalogue_key'][len('grocery:'):]]
            product.source_metadata = json.dumps(meta)
    # Pickup slots for the next SLOT_DAYS days at every branch (top-up only; never edits existing rows).
    today = datetime.now(zone).date()
    horizon_start = datetime.combine(today, time.min, tzinfo=zone).astimezone(timezone.utc).replace(tzinfo=None)
    have_slots = set(db.execute(select(PickupSlot.location_id, PickupSlot.start_at).where(
        PickupSlot.location_id.like('loc-m%'), PickupSlot.start_at >= horizon_start)).all())
    now_local = datetime.now(zone)
    for store in data['merchants']:
        for bi, branch in enumerate(store['branches']):
            for offset in range(SLOT_DAYS):
                day = today + timedelta(days=offset)
                for start, end in _slot_windows(store['hours'].get(str(day.weekday()), [])):
                    s_local = datetime.combine(day, time(start // 60, start % 60), tzinfo=zone)
                    if s_local <= now_local:
                        continue
                    s_utc = s_local.astimezone(timezone.utc).replace(tzinfo=None)
                    if (branch['id'], s_utc) in have_slots:
                        continue
                    seed = sum(map(ord, branch['id'])) + start + offset * 7
                    capacity = 4 + seed % 5
                    db.add(PickupSlot(id=f"slot-{branch['id']}-{day:%m%d}{start // 60:02d}", merchant_id=store['id'],
                        location_id=branch['id'], start_at=s_utc, end_at=s_utc + timedelta(minutes=end - start), capacity=capacity,
                        booked_count=(seed // 3) % capacity if seed % 4 == 0 else 0))
    db.flush()
    return {'products': len(new_products), 'attribution': off['attribution']}
