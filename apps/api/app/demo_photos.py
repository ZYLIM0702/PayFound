"""Reviewed photo metadata for owned synthetic demo products only."""
from functools import lru_cache
import json
import os
from pathlib import Path

from .models import Product

ORIGINAL_DESCRIPTIONS = {
    'p1': 'Compact 65W fast charger for laptops and phones.',
    'p2': 'Braided 100W-rated charging cable.',
    'p3': 'USB-C portable battery with charge indicator.',
    'p4': 'Quiet multi-device mouse.', 'p5': '24-bit interchangeable tool set.',
    'p6': 'Steel jaw wrench for plumbing repairs.',
    'p7': 'Rechargeable 400-lumen magnetic work light.',
    'p8': 'Industrial 50m repair tape.', 'p9': 'Everyday complete dog food, 2kg bag.',
    'p10': 'Clumping low-dust litter.', 'p11': 'Leak-proof portable pet drinking bottle.',
    'p12': 'Weatherproof front and rear light set.',
    'p13': 'Patch, lever, and mini pump combination.',
    'p14': 'Ventilated certified commuter helmet.',
}


@lru_cache(maxsize=1)
def catalogue():
    return json.loads(Path(__file__).with_name('demo_photos.json').read_text())['products']


def apply_demo_photos(db):
    if os.getenv('DEMO_MODE', 'false').lower() != 'true' or db.get_bind().dialect.name != 'sqlite':
        return 0
    updated = 0
    for photo in catalogue():
        product = db.get(Product, photo['id'])
        image_url = '/images/products/' + photo['id'] + '.webp'
        if not product or not product.synthetic or product.merchant_id != photo['merchant_id']:
            continue
        if product.inventory_source not in ('synthetic_local', 'pos_simulator'):
            continue
        # Preserve user-edited listings and merchant-supplied imagery. Never
        # reset price, quantities, holds, freshness, SKU or financial journals.
        if product.name not in (photo['previous_name'], photo['name']) or product.image_url not in (None, '', image_url):
            continue
        product.name, product.image_url = photo['name'], image_url
        original_description = ORIGINAL_DESCRIPTIONS.get(photo['id'], 'Fictional retail item for the PayFound POS simulator.')
        if product.description in (original_description, photo['description']):
            product.description = photo['description']
        metadata = json.loads(product.source_metadata or '{}')
        metadata['photo'] = {'source': photo.get('source', 'Amazon Berkeley Objects'),
            'item_id': photo.get('item_id'), 'image_id': photo.get('image_id'),
            'credits_url': '/image-credits.html#' + photo['id']}
        product.source_metadata = json.dumps(metadata)
        updated += 1
    return updated
