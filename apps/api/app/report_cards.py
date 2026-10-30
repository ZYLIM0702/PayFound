"""Report cards: validated JSON report specs built from the merchant report pack (no new numbers are invented here)."""
from __future__ import annotations

import math
import re
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import Principal, current_principal
from .database import db_session
from .intelligence.models import MerchantReportCard
from .intelligence.reports import merchant_scope
from .merchant_overview import scope
from .intelligence.catalog import iso
from .report_pack import NOTE, build_report_pack

router = APIRouter(tags=['Merchant reports'])
Kind = Literal['full', 'sales', 'products', 'orders', 'stock', 'pickup']
KINDS = ('full', 'sales', 'products', 'orders', 'stock', 'pickup')
TITLES = {'full': 'Store performance report', 'sales': 'Sales report', 'products': 'Products report', 'orders': 'Orders report',
          'stock': 'Stock health report', 'pickup': 'Pickup report'}
MAX_POINTS = 45
_CLEAN = re.compile(r'[^\w \-&.,/()]')


class Metric(BaseModel):
    label: str = Field(max_length=60)
    value: str = Field(max_length=60)
    hint: str | None = Field(default=None, max_length=120)


class Table(BaseModel):
    title: str = Field(max_length=80)
    columns: list[str] = Field(max_length=8)
    rows: list[list[str | int | float]] = Field(max_length=40)

    @field_validator('rows')
    @classmethod
    def _width(cls, rows, info):
        n = len(info.data.get('columns') or [])
        if any(len(r) != n for r in rows):
            raise ValueError('every row must match the columns')
        return rows


class Series(BaseModel):
    name: str = Field(max_length=40)
    values: list[float] = Field(max_length=MAX_POINTS)


class Chart(BaseModel):
    title: str = Field(max_length=80)
    type: Literal['bar', 'line']
    labels: list[str] = Field(max_length=MAX_POINTS)
    series: list[Series] = Field(max_length=3)

    @field_validator('series')
    @classmethod
    def _aligned(cls, series, info):
        n = len(info.data.get('labels') or [])
        if any(len(s.values) != n or any(not math.isfinite(v) for v in s.values) for s in series):
            raise ValueError('series must align with labels and be finite')
        return series


class Section(BaseModel):
    id: str = Field(max_length=24)
    title: str = Field(max_length=80)
    metrics: list[Metric] = Field(default_factory=list, max_length=8)
    tables: list[Table] = Field(default_factory=list, max_length=3)
    charts: list[Chart] = Field(default_factory=list, max_length=3)
    empty: str | None = Field(default=None, max_length=200)


class ReportCard(BaseModel):
    title: str = Field(max_length=120)
    kind: Kind
    days: int = Field(ge=1, le=90)
    merchant_id: str = Field(max_length=48)
    store_name: str = Field(max_length=130)
    start_date: str
    end_date: str
    generated_at: str
    note: str
    sections: list[Section] = Field(min_length=1, max_length=10)


def money(cents: int, cur: str) -> str:
    return f'{cur} {cents / 100:,.2f}'


def clean_focus(focus: str | None) -> str | None:
    text = _CLEAN.sub('', (focus or '')).strip()[:120]
    return text or None


def _bucket(labels: list[str], values: list[float]) -> tuple[list[str], list[float]]:
    if len(labels) <= MAX_POINTS:
        return labels, values
    step = math.ceil(len(labels) / MAX_POINTS)
    return [labels[i] for i in range(0, len(labels), step)], [sum(values[i:i + step]) for i in range(0, len(values), step)]


def _match(focus: str | None, *texts: str) -> bool:
    return not focus or any(focus.lower() in t.lower() for t in texts)


def build_card(db: Session, merchant, kind: str = 'full', days: int = 30, focus: str | None = None) -> dict:
    if kind not in KINDS:
        raise HTTPException(422, f'kind must be one of {", ".join(KINDS)}')
    focus = clean_focus(focus)
    pack = build_report_pack(db, merchant, days)
    s = pack['summary']
    sections: list[Section] = []
    want = lambda *k: kind == 'full' or kind in k  # noqa: E731

    if want('sales', 'orders'):
        metrics = [m for c in s['by_currency'] for m in (Metric(label=f'Captured ({c["currency"]})', value=money(c['captured_amount_cents'], c['currency']), hint=f'{c["orders"]} captured orders'),
                                                         Metric(label=f'Average basket ({c["currency"]})', value=money(c['average_basket_cents'], c['currency'])))]
        metrics.append(Metric(label='Orders in range', value=str(s['orders_in_range'])))
        if s['pickup_completion_pct'] is not None:
            metrics.append(Metric(label='Pickup completion', value=f'{s["pickup_completion_pct"]}%'))
        charts = []
        for cur, rows in pack['sales_trend']['by_currency'].items():
            labels, vals = _bucket([r['date'][5:] for r in rows], [r['amount_cents'] / 100 for r in rows])
            if any(vals):
                charts.append(Chart(title=f'Daily captured amount ({cur})', type='line', labels=labels, series=[Series(name=cur, values=[round(v, 2) for v in vals])]))
        sections.append(Section(id='summary', title='Summary', metrics=metrics[:8], charts=charts[:2],
                                empty=None if s['by_currency'] else 'No captured orders in this range. Widen the date range or take a first order.'))
    if want('sales'):
        cats = [c for c in pack['categories'] if _match(focus, c['category'])][:12]
        brs = [b for b in pack['branches'] if _match(focus, b['branch'])][:8]
        sections.append(Section(id='sales_mix', title='Sales by category and branch',
                                tables=[t for t in (Table(title='By category', columns=['Category', 'Currency', 'Units', 'Captured amount'], rows=[[c['category'], c['currency'], c['units'], money(c['amount_cents'], c['currency'])] for c in cats]) if cats else None,
                                                    Table(title='By branch', columns=['Branch', 'Currency', 'Orders', 'Captured amount'], rows=[[b['branch'], b['currency'], b['orders'], money(b['amount_cents'], b['currency'])] for b in brs]) if brs else None) if t],
                                charts=[Chart(title='Captured amount by category', type='bar', labels=[c['category'] for c in cats[:8]], series=[Series(name='Amount', values=[round(c['amount_cents'] / 100, 2) for c in cats[:8]])])] if cats else [],
                                empty=None if cats or brs else 'No category or branch sales match this focus.'))
    if want('products', 'sales'):
        rows = [r for r in pack['top_products']['by_units'] if _match(focus, r['name'])][:10]
        sections.append(Section(id='top_products', title='Top products',
                                tables=[Table(title='By units sold', columns=['Product', 'Units', 'Currency', 'Captured amount'], rows=[[r['name'], r['units'], r['currency'], money(r['amount_cents'], r['currency'])] for r in rows])] if rows else [],
                                charts=[Chart(title='Units sold', type='bar', labels=[r['name'][:24] for r in rows[:8]], series=[Series(name='Units', values=[float(r['units']) for r in rows[:8]])])] if rows else [],
                                empty=None if rows else 'No product sales match this focus in the range.'))
    if want('orders'):
        f = pack['funnel']
        sections.append(Section(id='funnel', title='Orders funnel', metrics=[Metric(label=k.capitalize(), value=str(f[k])) for k in ('reserved', 'paid', 'prepared', 'collected', 'cancelled', 'refunded')],
                                charts=[Chart(title='Orders by stage', type='bar', labels=['Reserved', 'Paid', 'Prepared', 'Collected', 'Cancelled', 'Refunded'], series=[Series(name='Orders', values=[float(f[k]) for k in ('reserved', 'paid', 'prepared', 'collected', 'cancelled', 'refunded')])])],
                                empty=None if f['reserved'] else 'No orders in this range.'))
    if want('stock'):
        h = pack['stock_health']
        risk = [r for r in h['attention'] if _match(focus, r['name'])][:12]
        sections.append(Section(id='stock', title='Stock health',
                                metrics=[Metric(label='In stock', value=str(h['in_stock'])), Metric(label='Low', value=str(h['low'])), Metric(label='Out', value=str(h['out'])), Metric(label='Stale count', value=str(h['stale']))],
                                tables=[Table(title='Needs attention', columns=['Product', 'Available', 'State'], rows=[[r['name'], r['available'], r['state']] for r in risk])] if risk else [],
                                empty=None if risk else 'No low, out or stale products. Nothing to recount.'))
    if want('pickup'):
        p = pack['pickup']
        brs = [b for b in p['by_branch'] if _match(focus, b['branch'])][:8]
        hrs = [r for r in p['collected_by_hour'] if 7 <= r['hour'] <= 21]
        metrics = [Metric(label='Pickup completion', value=f'{s["pickup_completion_pct"]}%')] if s['pickup_completion_pct'] is not None else []
        if p['slot_utilisation_pct'] is not None:
            metrics.append(Metric(label='Upcoming slot utilisation', value=f'{p["slot_utilisation_pct"]}%', hint=f'{p["slot_booked"]} of {p["slot_capacity"]} places booked'))
        sections.append(Section(id='pickup', title='Pickup utilisation', metrics=metrics,
                                tables=[Table(title='Collected orders by branch', columns=['Branch', 'Currency', 'Collected', 'Orders'], rows=[[b['branch'], b['currency'], b['collected'], b['orders']] for b in brs])] if brs else [],
                                charts=[Chart(title='Collected orders by hour', type='bar', labels=[f'{r["hour"]:02d}:00' for r in hrs], series=[Series(name='Orders', values=[float(r['orders']) for r in hrs])])] if any(r['orders'] for r in hrs) else [],
                                empty=None if brs or metrics else 'No pickup activity yet. Add pickup windows under Pickup.'))
    if kind == 'full':
        sections.append(Section(id='recommendations', title='Recommendations', tables=[Table(title='Next steps', columns=['Recommendation', 'Detail'], rows=[[r['title'], r['detail']] for r in pack['recommendations']])]))
    title = TITLES[kind] + (f': {focus}' if focus else '')
    card = ReportCard(title=title, kind=kind, days=days, merchant_id=merchant.id, store_name=merchant.name, start_date=pack['start_date'], end_date=pack['end_date'],
                      generated_at=pack['generated_at'], note=NOTE, sections=sections)
    return card.model_dump()


class CardSave(BaseModel):
    merchant_id: str | None = Field(default=None, max_length=48)
    name: str = Field(min_length=1, max_length=120)
    kind: Kind = 'full'
    days: int = Field(default=30, ge=1, le=90)
    focus: str | None = Field(default=None, max_length=120)


def saved_json(r: MerchantReportCard) -> dict:
    return {'id': r.id, 'merchant_id': r.merchant_id, 'name': r.name, 'kind': r.kind, 'days': r.days, 'focus': r.focus, 'created_at': iso(r.created_at)}


def save_card(db: Session, mid: str, name: str, kind: str, days: int, focus: str | None, subject: str) -> MerchantReportCard:
    name = _CLEAN.sub('', name).strip()
    if not name:
        raise HTTPException(422, 'Report name is required')
    if kind not in KINDS:
        raise HTTPException(422, f'kind must be one of {", ".join(KINDS)}')
    if len(db.scalars(select(MerchantReportCard.id).where(MerchantReportCard.merchant_id == mid).limit(50)).all()) >= 50:
        raise HTTPException(409, 'Saved report limit reached (50). Delete one first.')
    row = MerchantReportCard(merchant_id=mid, name=name[:120], kind=kind, days=min(max(days, 1), 90), focus=clean_focus(focus), created_by=subject[:160])
    db.add(row)
    db.commit()
    return row


def _owned(db: Session, p: Principal, card_id: str) -> MerchantReportCard:
    row = db.get(MerchantReportCard, card_id) if re.fullmatch(r'[A-Za-z0-9_-]{1,48}', card_id) else None
    if row is None:
        raise HTTPException(404, 'Report not found')
    try:
        scope(db, p, row.merchant_id)
    except HTTPException:
        raise HTTPException(404, 'Report not found') from None
    return row


@router.get('/merchant/report-cards/preview')
def preview(merchant_id: str = Query(max_length=48), kind: Kind = 'full', days: int = Query(30, ge=1, le=90), focus: str | None = Query(default=None, max_length=120),
            db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    return build_card(db, scope(db, p, merchant_id), kind, days, focus)


@router.get('/merchant/report-cards')
def list_cards(merchant_id: str = Query(max_length=48), db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    scope(db, p, merchant_id)
    rows = db.scalars(select(MerchantReportCard).where(MerchantReportCard.merchant_id == merchant_id).order_by(MerchantReportCard.created_at.desc(), MerchantReportCard.id).limit(50)).all()
    return {'reports': [saved_json(r) for r in rows]}


@router.post('/merchant/report-cards', status_code=201)
def create_card(body: CardSave, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    mid = merchant_scope(db, p, body.merchant_id)
    scope(db, p, mid)
    return saved_json(save_card(db, mid, body.name, body.kind, body.days, body.focus, p.subject))


@router.get('/merchant/report-cards/{card_id}')
def open_card(card_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    row = _owned(db, p, card_id)
    return {**saved_json(row), 'card': build_card(db, scope(db, p, row.merchant_id), row.kind, row.days, row.focus)}


@router.delete('/merchant/report-cards/{card_id}', status_code=204)
def delete_card(card_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    row = _owned(db, p, card_id)
    db.delete(row)
    db.commit()
