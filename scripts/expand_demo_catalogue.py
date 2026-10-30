"""Curate 178 additional, distinct ABO products for the 200-item local demo."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
from pathlib import Path
import re

import httpx

ROOT = Path(__file__).resolve().parents[1]
ABO = 'https://amazon-berkeley-objects.s3.amazonaws.com/'
GROUPS = {
    'Electronics': (40, ['headphone', 'speaker', 'mouse', 'keyboard', 'usb', 'hdmi', 'ethernet', 'microphone', 'camera', 'laptop stand', 'charger', 'power bank', 'monitor', 'tripod', 'battery', 'cable', 'webcam']),
    'Hardware': (28, ['screwdriver', 'wrench', 'socket', 'hammer', 'pliers', 'drill', 'work light', 'extension cord', 'tape measure', 'utility knife', 'hex key', 'clamp', 'ratchet', 'tool', 'safety goggle', 'padlock', 'door handle']),
    'Pet essentials': (20, ['dog bed', 'crate', 'pet carrier', 'litter', 'leash', 'harness', 'pet bowl', 'dog food', 'cat food', 'scratcher', 'pet toy', 'pet', 'dog', 'cat tree']),
    'Sports & cycling': (18, ['yoga', 'dumbbell', 'exercise', 'resistance', 'kettlebell', 'bicycle', 'foam roller', 'jump rope', 'gym', 'fitness', 'basketball', 'sleeping bag', 'camping']),
    'Office supplies': (25, ['pencil', 'stapler', 'shredder', 'binder', 'folder', 'desk organizer', 'marker', 'clipboard', 'scissors', 'notepad', 'notebook', 'copy paper', 'laminator', 'label', 'sticky note', 'writing pen']),
    'Home & living': (47, ['cutting board', 'cookware', 'kettle', 'towel', 'basket', 'lamp', 'mug', 'glass', 'bottle', 'coffee', 'shelf', 'storage', 'pillow', 'blanket', 'rug', 'curtain', 'chair', 'plate', 'utensil', 'cushion', 'frying pan', 'knife', 'saucepan', 'baking', 'kitchen']),
}
MERCHANTS = [
    {'id':'m5','slug':'market-street-tech','name':'Market Street Tech','category':'Electronics','address':'865 Market St, San Francisco, CA','latitude':37.7846,'longitude':-122.4076,'emoji':'💻'},
    {'id':'m6','slug':'soma-gadget-lab','name':'SoMa Gadget Lab','category':'Electronics','address':'680 Folsom St, San Francisco, CA','latitude':37.7848,'longitude':-122.3972,'emoji':'🎧'},
    {'id':'m7','slug':'civic-home-living','name':'Civic Home & Living','category':'Home & living','address':'1150 Market St, San Francisco, CA','latitude':37.7794,'longitude':-122.4149,'emoji':'🪴'},
    {'id':'m8','slug':'hayes-valley-home','name':'Hayes Valley Home','category':'Home & living','address':'460 Hayes St, San Francisco, CA','latitude':37.7767,'longitude':-122.4248,'emoji':'🏡'},
    {'id':'m9','slug':'paper-and-desk','name':'Paper & Desk','category':'Office supplies','address':'500 Sutter St, San Francisco, CA','latitude':37.7893,'longitude':-122.4086,'emoji':'✏️'},
    {'id':'m10','slug':'mission-toolworks','name':'Mission Toolworks','category':'Hardware','address':'2200 Mission St, San Francisco, CA','latitude':37.7612,'longitude':-122.4192,'emoji':'🛠️'},
    {'id':'m11','slug':'cole-valley-pets','name':'Cole Valley Pets','category':'Pet essentials','address':'900 Cole St, San Francisco, CA','latitude':37.7654,'longitude':-122.4498,'emoji':'🐾'},
    {'id':'m12','slug':'active-bay-outdoors','name':'Active Bay Outdoors','category':'Sports & cycling','address':'1550 Bay St, San Francisco, CA','latitude':37.8029,'longitude':-122.4316,'emoji':'🚲'},
    {'id':'m13','slug':'sunset-paper-co','name':'Sunset Paper Co.','category':'Office supplies','address':'1300 9th Ave, San Francisco, CA','latitude':37.7640,'longitude':-122.4663,'emoji':'📓'},
]
STORES = {'Electronics':['m5','m6'], 'Home & living':['m7','m8'], 'Office supplies':['m9','m13'],
          'Hardware':['m10','m2'], 'Pet essentials':['m11','m3'], 'Sports & cycling':['m12','m4']}


def english(values):
    return next((v.get('value', '') for v in values if v.get('language_tag') == 'en_US'), '') if isinstance(values, list) else ''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache-dir', type=Path, required=True)
    args = parser.parse_args()
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    original = json.loads((ROOT / 'apps/api/app/demo_photos.json').read_text())['products']
    old_ids = {p.get('item_id') for p in original}
    old_images = {p.get('image_id') for p in original}

    def shard(i):
        cache = args.cache_dir / f'abo-us-listings-{i:x}.json'
        if cache.exists():
            return json.loads(cache.read_text())
        response = httpx.get(ABO + f'listings/metadata/listings_{i:x}.json.gz', timeout=90)
        response.raise_for_status()
        rows = []
        for line in gzip.decompress(response.content).splitlines():
            item = json.loads(line)
            title = english(item.get('item_name'))
            if item.get('domain_name') != 'amazon.com' or not title or not item.get('main_image_id'):
                continue
            rows.append({'item_id':item['item_id'], 'title':title, 'image_id':item['main_image_id'],
                'brand':english(item.get('brand')), 'color':english(item.get('color')),
                'material':english(item.get('material'))})
        cache.write_text(json.dumps(rows))
        return rows

    items = {}
    with ThreadPoolExecutor(max_workers=4) as workers:
        for rows in workers.map(shard, range(16)):
            for row in rows:
                items[row['item_id']] = row
    image_counts = Counter(row['image_id'] for row in items.values())
    groups = {category: [] for category in GROUPS}
    for row in items.values():
        if row['item_id'] in old_ids or row['image_id'] in old_images or image_counts[row['image_id']] > 2:
            continue
        title = row['title'].lower()
        if re.search(r'\b(bundle|renewed|replacement|refill|case for|cover for|dummy|test|placeholder|refurbish)\b', title) or len(row['title']) > 180:
            continue
        for category, (_, words) in GROUPS.items():
            match = next((word for word in words if word in title), None)
            if match:
                groups[category].append({**row, 'category': category, 'cluster': match})
                break
    chosen, images = [], set(old_images)
    for category, (quota, _) in GROUPS.items():
        clusters = Counter()
        # Stable varied catalogue, with no random substitutions on rerun.
        ordered = sorted(groups[category], key=lambda p: (len(p['title']), p['item_id']))
        for row in ordered:
            if row['image_id'] in images or clusters[row['cluster']] >= 5:
                continue
            chosen.append(row); images.add(row['image_id']); clusters[row['cluster']] += 1
            if sum(p['category'] == category for p in chosen) == quota:
                break
    for category in GROUPS:
        for row in sorted(groups[category], key=lambda p: p['item_id']):
            if len(chosen) >= 178:
                break
            if row['image_id'] not in images:
                chosen.append(row); images.add(row['image_id'])
    assert len(chosen) == 178
    products = []
    counts = Counter()
    for row in chosen:
        sequence = counts[row['category']]
        merchant = STORES[row['category']][sequence % 2]
        counts[row['category']] += 1
        digest = int(hashlib.sha256(row['item_id'].encode()).hexdigest()[:8], 16)
        name = row['title'].replace('AmazonBasics ', '').replace('Amazon Basics ', '').replace('Amazon Brand – ', '').replace('Amazon Brand - ', '')
        products.append({'id':'catalogue-' + row['item_id'].lower(), 'merchant_id':merchant, 'name':name,
            'previous_name':name, 'description':'Reference catalogue item: ' + row['title'] + '. Demo price and stock.',
            'item_id':row['item_id'], 'image_id':row['image_id'], 'source_title':row['title'],
            'category':row['category'], 'brand':row['brand'], 'color':row['color'], 'material':row['material'],
            'price_cents': 990 + (digest % 120) * 100, 'quantity':5 + digest % 25})
    result = {'version':1, 'distinct_items':200, 'merchants':MERCHANTS, 'products':products,
              'comparison_stores':STORES, 'note':'Fictional stores, prices and stock. Licensed ABO catalogue imagery.'}
    (ROOT / 'apps/api/app/demo_catalogue.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'additional_unique_items':len(products), 'total_unique_items':200, 'categories':dict(counts), 'additional_stores':len(MERCHANTS)}, indent=2))


if __name__ == '__main__':
    main()
