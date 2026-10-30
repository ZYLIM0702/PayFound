"""Merchant report pack: the numbers behind the Analytics page, the PDF export and the assistant's build_report tool."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import Principal, require_role
from .database import db_session
from .merchant_overview import DEAD, DEFAULT_LOW_STOCK, _items, _lines, _local, _primary, _tz, build_analytics, scope
from .models import Merchant, MerchantLocation, Order, PickupSlot, Product, utcnow

router = APIRouter(tags=['Merchant reports'])
NOTE = 'Recorded captured payment amounts per currency (simulated in demo). Not profit, margin or bank settlement.'
SECTIONS = ('summary', 'sales_trend', 'categories', 'branches', 'top_products', 'funnel', 'stock_health', 'pickup', 'recommendations')
PREPARED = ('PREPARING', 'READY', 'COLLECTED')


def _by_currency(rows: dict) -> list[dict]:
    return [{'currency': c, **v} for c, v in sorted(rows.items())]


def build_report_pack(db: Session, merchant: Merchant, days: int = 30, threshold: int = DEFAULT_LOW_STOCK, now: datetime | None = None) -> dict:
    now = now or utcnow()
    base = build_analytics(db, merchant, days, threshold, now)
    location = _primary(db, merchant.id)
    tz = _tz(location)
    start_day = _local(now, tz).date() - timedelta(days=days - 1)
    products = {p.id: p for p in db.scalars(select(Product).where(Product.merchant_id == merchant.id))}
    names = {pid: p.name for pid, p in products.items()}
    branch_names = {loc.id: loc.name for loc in db.scalars(select(MerchantLocation).where(MerchantLocation.merchant_id == merchant.id, MerchantLocation.active.is_(True)))}
    orders = [o for o in db.scalars(select(Order).where(Order.merchant_id == merchant.id).order_by(Order.created_at))
              if _local(o.created_at, tz).date() >= start_day]
    items = _items(db, orders)

    funnel = defaultdict(int)
    cur: dict[str, dict] = defaultdict(lambda: {'amount_cents': 0, 'orders': 0})
    cat_branch: dict[tuple, int] = defaultdict(int)
    cat: dict[tuple, dict] = defaultdict(lambda: {'amount_cents': 0, 'units': 0, 'orders': 0})
    branch: dict[tuple, dict] = defaultdict(lambda: {'amount_cents': 0, 'orders': 0, 'collected': 0})
    prod: dict[tuple, dict] = defaultdict(lambda: {'units': 0, 'amount_cents': 0})
    by_hour = [0] * 24
    collected_hours = [0] * 24
    for o in orders:
        funnel['reserved'] += 1
        if o.payment_status in ('CAPTURED', 'REFUNDED'):
            funnel['paid'] += 1
        if o.status in PREPARED:
            funnel['prepared'] += 1
        if o.status == 'COLLECTED':
            funnel['collected'] += 1
            collected_hours[_local(o.created_at, tz).hour] += 1
        for key, status in (('cancelled', 'CANCELLED'), ('refunded', 'REFUNDED'), ('expired', 'EXPIRED')):
            if o.status == status:
                funnel[key] += 1
        bname = branch_names.get(o.location_id, 'Main branch') if o.location_id else 'Main branch'
        if o.status in DEAD or o.payment_status != 'CAPTURED':
            continue
        by_hour[_local(o.created_at, tz).hour] += 1
        cur[o.currency]['amount_cents'] += o.amount_cents
        cur[o.currency]['orders'] += 1
        b = branch[(bname, o.currency)]
        b['amount_cents'] += o.amount_cents
        b['orders'] += 1
        b['collected'] += o.status == 'COLLECTED'
        for pid, name, q, unit in _lines(o, items, names):
            cat_branch[(bname, products[pid].category if pid in products else 'Other', o.currency)] += q * unit
            c = cat[(products[pid].category if pid in products else 'Other', o.currency)]
            c['amount_cents'] += q * unit
            c['units'] += q
            c['orders'] += 1
            p = prod[(name, o.currency)]
            p['units'] += q
            p['amount_cents'] += q * unit

    summary_cur = []
    for c, v in sorted(cur.items()):
        summary_cur.append({'currency': c, 'captured_amount_cents': v['amount_cents'], 'orders': v['orders'], 'average_basket_cents': v['amount_cents'] // v['orders'] if v['orders'] else 0})
    paid_live = funnel['paid'] - funnel['refunded']
    completion = round(100 * funnel['collected'] / paid_live) if paid_live > 0 else None
    health = base['stock_health']
    attention = health['low'] + health['out']
    categories = sorted(({'category': k[0], 'currency': k[1], **v} for k, v in cat.items()), key=lambda r: (-r['amount_cents'], r['category']))
    branches = sorted(({'branch': k[0], 'currency': k[1], **v} for k, v in branch.items()), key=lambda r: (-r['amount_cents'], r['branch']))
    top = sorted(({'name': k[0], 'currency': k[1], **v} for k, v in prod.items()), key=lambda r: (-r['units'], r['name']))[:10]
    top_rev = sorted(({'name': k[0], 'currency': k[1], **v} for k, v in prod.items()), key=lambda r: (-r['amount_cents'], r['name']))[:10]

    # scheduled pickup capacity by branch and local hour (window: 2 days back to 7 days ahead, as the pickup calendar holds)
    cells: dict[tuple, list] = defaultdict(lambda: [0, 0])
    lo = now - timedelta(days=2)
    for s in db.scalars(select(PickupSlot).where(PickupSlot.merchant_id == merchant.id, PickupSlot.start_at >= lo, PickupSlot.start_at < now + timedelta(days=8))):
        cell = cells[(branch_names.get(s.location_id, 'Branch'), _local(s.start_at, tz).hour)]
        cell[0] += s.capacity
        cell[1] += s.booked_count
    slot_cells = [{'branch': b, 'hour': h, 'capacity': v[0], 'booked': v[1], 'utilisation_pct': round(100 * v[1] / v[0]) if v[0] else 0} for (b, h), v in sorted(cells.items())]
    cap, booked = sum(c['capacity'] for c in slot_cells), sum(c['booked'] for c in slot_cells)

    trend = {c: [{'date': r['date'], 'amount_cents': r['amount_cents'], 'orders': r['orders']} for r in rows] for c, rows in base['revenue'].items()}
    recs = recommendations(base, funnel, top, completion, summary_cur)
    return {
        'merchant_id': merchant.id, 'store_name': merchant.name, 'days': days, 'timezone': str(tz), 'generated_at': now.isoformat() + 'Z',
        'start_date': start_day.isoformat(), 'end_date': _local(now, tz).date().isoformat(), 'note': NOTE, 'sections': list(SECTIONS),
        'summary': {'by_currency': summary_cur, 'orders_in_range': len(orders), 'pickup_completion_pct': completion,
                    'stock_attention_count': attention, 'out_of_stock': health['out'], 'low_stock': health['low'], 'stale_stock': health['stale']},
        'sales_trend': {'by_currency': trend},
        'categories': categories, 'branches': branches,
        'category_by_branch': [{'branch': k[0], 'category': k[1], 'currency': k[2], 'amount_cents': v} for k, v in sorted(cat_branch.items())], 'top_products': {'by_units': top, 'by_revenue': top_rev},
        'funnel': {**{k: funnel.get(k, 0) for k in ('reserved', 'paid', 'prepared', 'collected', 'cancelled', 'refunded', 'expired')}},
        'stock_health': {**health, 'attention': base['low_stock'] + base['stale_stock']},
        'pickup': {'collected_by_hour': [{'hour': h, 'orders': n} for h, n in enumerate(collected_hours)],
                   'orders_by_hour': [{'hour': h, 'orders': n} for h, n in enumerate(by_hour)],
                   'by_branch': [{'branch': r['branch'], 'currency': r['currency'], 'collected': r['collected'], 'orders': r['orders']} for r in branches],
                   'slots': slot_cells, 'slot_capacity': cap, 'slot_booked': booked, 'slot_utilisation_pct': round(100 * booked / cap) if cap else None},
        'recommendations': recs, 'alerts': base['alerts'],
    }


def recommendations(base: dict, funnel, top, completion, summary_cur) -> list[dict]:
    out = []
    for a in base['alerts'][:4]:
        out.append({'title': a['title'], 'detail': a['detail'], 'to': a['to'], 'action': a['action']})
    if funnel['refunded'] and funnel['paid'] and funnel['refunded'] / funnel['paid'] > 0.02:
        out.append({'title': f"{funnel['refunded']} refunded orders in this range", 'detail': 'Review refunded orders for a repeating product or pickup issue.', 'to': '/merchant/orders', 'action': 'Open orders'})
    if completion is not None and completion < 90:
        out.append({'title': f'Pickup completion is {completion}%', 'detail': 'Some paid orders were not collected yet; check pickup windows and reminders.', 'to': '/merchant/pickup', 'action': 'Check pickup'})
    if top:
        out.append({'title': f"{top[0]['name']} sells best", 'detail': f"{top[0]['units']} units in this range. Keep it above your low-stock level.", 'to': '/merchant/inventory', 'action': 'Open inventory'})
    if not out:
        out.append({'title': 'Nothing needs attention', 'detail': 'Stock, orders and pickups look healthy for this range.', 'to': '/merchant/overview', 'action': 'Back to overview'})
    return out[:6]


@router.get('/merchant/report-pack')
def report_pack(merchant_id: str = Query(max_length=48), days: int = Query(30, ge=1, le=90), low_stock_threshold: int = Query(DEFAULT_LOW_STOCK, ge=0, le=100),
                db: Session = Depends(db_session), p: Principal = Depends(require_role('merchant', 'admin'))):
    return build_report_pack(db, scope(db, p, merchant_id), days, low_stock_threshold)
