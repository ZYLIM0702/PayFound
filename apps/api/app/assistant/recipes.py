"""Recipe-to-basket planning. Pure functions over a `fetch(keyword, category)` callable so they are testable without HTTP."""
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Callable

RECIPES_PATH = Path(__file__).resolve().parent.parent / 'recipes.json'
FOOD_CATEGORIES = ('Groceries', 'Fresh produce', 'Meat & seafood', 'Dairy & eggs', 'Bakery')


@lru_cache(maxsize=1)
def load() -> list[dict]:
    return json.loads(RECIPES_PATH.read_text(encoding='utf-8'))['recipes']


def names() -> list[str]:
    return [r['name'] for r in load()]


def find(text: str) -> dict | None:
    """Best recipe for free text: alias/name phrase hit, longest phrase wins."""
    t = re.sub(r'[^a-z0-9 ]+', ' ', text.lower())
    t = f' {re.sub(chr(32) + "+", " ", t)} '
    best, best_len = None, 0
    for r in load():
        for phrase in [r['name'], *r['aliases']]:
            p = re.sub(r'[^a-z0-9 ]+', ' ', phrase.lower()).strip()
            if f' {p} ' in t and len(p) > best_len:
                best, best_len = r, len(p)
    return best


def _qty(q: float, base: int, servings: int) -> float:
    return q * servings / max(base, 1)


def _fmt(q: float, unit: str) -> str:
    if unit in ('whole', 'cloves', 'slices'):
        q = math.ceil(q - 1e-9)
    s = f'{q:.2f}'.rstrip('0').rstrip('.') if q != int(q) else str(int(q))
    return f'{s} {unit}'.strip()


def _name_has(name: str, keyword: str) -> bool:
    return re.search(r'(?<![a-z])' + re.escape(keyword.lower()), name.lower()) is not None


def match_ingredient(ing: dict, fetch: Callable[[str, str], list[dict]]) -> list[dict]:
    """In-stock catalogue rows for one ingredient (all stores), cheapest first per store."""
    seen: dict[str, dict] = {}
    for kw in ing['keywords']:
        for row in fetch(kw, ing['category']):
            name = row['name']
            if not row.get('in_stock') or row.get('available_quantity', 0) < 1:
                continue
            if row.get('category') not in FOOD_CATEGORIES or not _name_has(name, kw):
                continue
            if any(x in name.lower() for x in ing.get('exclude', [])):
                continue
            seen.setdefault(row['id'], row)
    return sorted(seen.values(), key=lambda r: (r['price_cents'], r.get('distance_km') or 0))


def build_plan(recipe: dict, servings: int, fetch: Callable[[str, str], list[dict]], view: Callable[[dict], dict], now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    servings = max(1, min(int(servings or recipe['base_servings']), 12))
    base = recipe['base_servings']
    lines, per_store = [], {}
    for ing in recipe['ingredients']:
        line = {'name': ing['name'], 'quantity': _fmt(_qty(ing['qty'], base, servings), ing['unit']), 'pantry': ing['pantry'], 'optional': ing['optional']}
        if ing['pantry']:
            lines.append(line)
            continue
        rows = match_ingredient(ing, fetch)
        line['_rows'] = rows
        for row in rows:
            store = per_store.setdefault(row['merchant_id'], {'rows': {}, 'name': row.get('merchant_name'), 'slug': row.get('merchant_slug'),
                                                              'distance': row.get('distance_km') or 0, 'is_open': row.get('is_open')})
            best = store['rows'].get(ing['name'])
            if best is None or row['price_cents'] < best['price_cents']:
                store['rows'][ing['name']] = row
        lines.append(line)
    needed = [i for i in recipe['ingredients'] if not i['pantry']]

    def score(item):
        mid, s = item
        req = sum(1 for i in needed if i['name'] in s['rows'] and not i['optional'])
        opt = sum(1 for i in needed if i['name'] in s['rows'] and i['optional'])
        return (-req, -opt, not s['is_open'], s['distance'], mid)
    ranked = sorted(per_store.items(), key=score)
    best_id, best = (ranked[0] if ranked else (None, None))

    add, extras, missing_here, elsewhere = [], [], [], []
    for line, ing in zip(lines, recipe['ingredients']):
        rows = line.pop('_rows', [])
        if ing['pantry']:
            continue
        mine = best['rows'].get(ing['name']) if best else None
        if mine:
            line['match'] = view(mine) | {'merchant_id': mine['merchant_id']}
            (extras if ing['optional'] else add).append({'product_id': mine['id'], 'quantity': 1, 'for': ing['name']})
        else:
            line['match'] = None
            if rows:
                other = rows[0]
                elsewhere.append({'ingredient': ing['name'], 'store': other.get('merchant_name'), 'product': other['name'], 'optional': ing['optional']})
            if not ing['optional']:
                missing_here.append(ing['name'])
    total_cents = sum(best['rows'][a['for']]['price_cents'] for a in add) if best else 0
    currency = next((r['currency'] for r in best['rows'].values()), 'USD') if best else None
    plan = {
        'found': True, 'recipe_id': recipe['id'], 'dish': recipe['name'], 'servings': servings, 'time': recipe['time'], 'prep_steps': recipe['prep'],
        'checked_at': now.isoformat(timespec='seconds'),
        'ingredients': lines,
        'best_store': None if not best else {
            'id': best_id, 'slug': best['slug'], 'name': best['name'], 'distance_km': best['distance'], 'is_open': best['is_open'],
            'items_in_stock': len(add), 'items_needed': sum(1 for i in needed if not i['optional']),
            'estimated_total': f'{currency} {total_cents // 100}.{total_cents % 100:02d}', 'estimated_total_cents': total_cents},
        'add_to_basket': add, 'optional_extras': extras,
        'missing_here': missing_here, 'available_at_other_stores': elsewhere,
        'pantry_check': [f"{l['name']} ({l['quantity']})" for l in lines if l['pantry']],
        'proposal_only': True,
        'note': 'Proposal only: the shopper adds items to the basket by clicking. One pack per ingredient; check pack sizes against the quantities. '
                'Stock is as listed by the store at each item\'s stock_updated_at, not a verified shelf count. All items are from one store.',
    }
    if not best:
        plan['note'] = 'None of the ingredients are listed in stock nearby right now.'
    return plan


def suggest_pickup(slots: list[dict], fulfillment_minutes: int | None, now: datetime | None = None) -> dict | None:
    """First published pickup slot with room that starts after the store's usual prep time. Read-only suggestion."""
    now = now or datetime.now(timezone.utc)
    earliest = now + timedelta(minutes=max(fulfillment_minutes or 20, 15))
    for s in sorted(slots, key=lambda x: x['start_at']):
        start = datetime.fromisoformat(s['start_at'].replace('Z', '+00:00'))
        if start >= earliest and s.get('remaining', 0) > 0:
            return {'start_at': s['start_at'], 'end_at': s['end_at'], 'slots_left': s['remaining'], 'earliest_possible': earliest.isoformat(timespec='minutes'),
                    'note': 'Suggestion only. The shopper picks the pickup time at reservation.'}
    return None
