"""Idempotent, local-only 200-item catalogue and comparable merchant offers, plus the grocery / fresh-food stores."""
from collections import Counter
import json
import os
from pathlib import Path

from .models import Merchant, MerchantLocation, Product, utcnow
from .demo_photos import catalogue


def seed_expanded_demo(db, force=False):
    if os.getenv('DEMO_MODE', 'false').lower() != 'true' or db.get_bind().dialect.name != 'sqlite':
        return
    if not force and (os.getenv('PAYFOUND_TESTING') == '1' or os.getenv('DEMO_EXPANDED_CATALOGUE', 'true').lower() != 'true'):
        return
    data = json.loads(Path(__file__).with_suffix('.json').read_text())
    for store in data['merchants']:
        if not db.get(Merchant, store['id']):
            db.add(Merchant(id=store['id'], slug=store['slug'], name=store['name'], category=store['category'],
                description='Fictional neighborhood retailer for the expanded PayFound demo.', address=store['address'],
                latitude=store['latitude'], longitude=store['longitude'], hours='24 hours', logo_emoji=store['emoji'],
                owner_subject='demo-merchant'))
    db.flush()
    for store in data['merchants']:
        if not db.get(MerchantLocation, 'loc-' + store['id']):
            db.add(MerchantLocation(id='loc-' + store['id'], merchant_id=store['id'], name=store['name'] + ' Main',
                address=store['address'], latitude=store['latitude'], longitude=store['longitude'], timezone='America/Los_Angeles',
                hours=json.dumps({str(day): [{'start':'00:00','end':'24:00'}] for day in range(7)})))
    db.flush()
    base = catalogue()
    from .pos_simulator import FIXTURES
    by_id = {p['id']: p for p in base}
    for key, _, category, price, quantity, emoji in FIXTURES:
        pid = 'pos-demo-' + key
        photo = by_id[pid]
        if not db.get(Product, pid):
            db.add(Product(id=pid, merchant_id='m1', location_id='loc-m1', name=photo['name'], description=photo['description'],
                sku='SIM-' + key.upper(), category=category, price_cents=price, quantity=quantity, synthetic=True,
                image_url='/images/products/' + pid + '.webp', image_emoji=emoji, inventory_source='pos_simulator',
                supports_reservation=True, source_metadata=json.dumps({'created_by':'pos_simulator'})))
    for item in data['products']:
        if not db.get(Product, item['id']):
            db.add(Product(id=item['id'], merchant_id=item['merchant_id'], location_id='loc-' + item['merchant_id'], name=item['name'],
                description=item['description'], sku='CAT-' + item['item_id'], category=item['category'],
                price_cents=item['price_cents'], quantity=item['quantity'], synthetic=True, supports_reservation=True,
                image_url='/images/products/' + item['id'] + '.webp', inventory_source='synthetic_local',
                source_metadata=json.dumps({'demo_catalogue':True, 'catalogue_key':'abo:' + item['item_id'],
                    'catalogue_brand':item['brand'], 'catalogue_attributes':{'Colour':item['color'], 'Material':item['material']},
                    'photo':{'source':'Amazon Berkeley Objects', 'item_id':item['item_id'], 'image_id':item['image_id'],
                             'credits_url':'/image-credits.html#' + item['id']}})))
    db.flush()
    all_base = base + data['products']
    for item in all_base:
        product = db.get(Product, item['id'])
        if not product or not product.synthetic:
            continue
        metadata = json.loads(product.source_metadata or '{}')
        metadata['catalogue_key'] = 'abo:' + item['item_id'] if item.get('item_id') else 'demo-photo:' + item['id']
        metadata['demo_catalogue'] = True
        product.source_metadata = json.dumps(metadata)
    db.flush()
    # Shared catalogue identity represents the SAME sample item, not a fuzzy
    # name match or an invented GTIN. Each merchant keeps its own price/stock.
    for item in all_base[:44]:
        source = db.get(Product, item['id'])
        category = source.category if source.category in data['comparison_stores'] else 'Electronics'
        targets = data['comparison_stores'][category]
        target = next(mid for mid in targets if mid != source.merchant_id)
        pid = 'offer-' + source.id + '-' + target
        if not db.get(Product, pid):
            metadata = json.loads(source.source_metadata)
            metadata['demo_comparison_offer'] = True
            db.add(Product(id=pid, merchant_id=target, location_id='loc-' + target, name=source.name,
                description=source.description, sku=source.sku, category=source.category,
                price_cents=max(1, (source.price_cents * 92 + 50) // 100), quantity=7, synthetic=True,
                supports_reservation=True, image_url=source.image_url, inventory_source='synthetic_local',
                source_metadata=json.dumps(metadata)))
    db.flush()
    from .demo_catalogue_grocery import seed_grocery_demo
    seed_grocery_demo(db)
    counts = Counter(json.loads(p.source_metadata or '{}').get('catalogue_key') for p in db.query(Product).filter(Product.synthetic.is_(True)))
    for product in db.query(Product).filter(Product.synthetic.is_(True)):
        metadata = json.loads(product.source_metadata or '{}')
        if metadata.get('catalogue_key'):
            metadata['comparison_count'] = counts[metadata['catalogue_key']]
            product.source_metadata = json.dumps(metadata)
