from __future__ import annotations

import hashlib
import time
from datetime import timedelta
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from .. import llm
from ..auth import Principal, current_principal
from ..database import db_session
from ..models import Merchant, Order, Product, utcnow
from . import channel3
from .catalog import extract, iso, location_for, product_dto, search_local
from .models import AgentRun
from .reports import consent_granted, merchant_scope
from .schemas import (AgentInput, FreshnessOutput, HoursOutput, InventoryOutput, MerchantToolInput,
                      NumericOutput, PickupOutput, ProductList, ProductReferences, SearchInput)

router = APIRouter()

# These are the schemas actually used by ToolSession, not descriptive labels.
TOOLS = {
    'search_local_products': ('consumer', SearchInput, ProductList, 'Read active local listings with extracted constraints.'),
    'check_store_hours': ('consumer', ProductReferences, HoursOutput, 'Read stored schedules; opening status can be unknown.'),
    'explain_stock_freshness': ('consumer', ProductReferences, FreshnessOutput, 'Read source timestamps, never assert live stock.'),
    'recommend_pickup': ('consumer', ProductReferences, PickupOutput, 'Suggest listed products; merchant stock confirmation required.'),
    'handoff_checkout': ('consumer', ProductReferences, PickupOutput, 'Return a human-confirmed checkout handoff; no order or payment writes.'),
    'detect_low_stock': ('merchant', MerchantToolInput, InventoryOutput, 'Read low-stock inventory for one authorized merchant.'),
    'suggest_stock_checks': ('merchant', MerchantToolInput, InventoryOutput, 'Read stale/unknown stock for one authorized merchant.'),
    'explain_orders': ('merchant', MerchantToolInput, NumericOutput, 'Read aggregate order counts; no customer identities.'),
    'report_revenue': ('merchant', MerchantToolInput, NumericOutput, 'Read recorded captured amounts separately by currency, not profit or settlement.'),
}


class ToolSession:
    def __init__(self):
        self.used: list[str] = []
        self.calls: list[dict] = []
        self.started = time.monotonic()

    def run(self, name: str, arguments: dict, implementation: Callable):
        if len(self.used) >= 8 or time.monotonic() - self.started > 5:
            raise HTTPException(503, 'Agent tool execution budget exceeded')
        _, inputs, outputs, _ = TOOLS[name]
        args = inputs.model_validate(arguments)
        result = outputs.model_validate(implementation(args)).model_dump()
        self.used.append(name)
        self.calls.append({'name': name, 'arguments': args.model_dump(mode='json'), 'result': result})
        return result


@router.get('/agents/tools')
def agent_tools():
    groups = {'consumer': [], 'merchant': []}
    for name, (role, inputs, outputs, description) in TOOLS.items():
        groups[role].append({'name': name, 'description': description, 'read_only': True,
                             'input_schema': inputs.model_json_schema(), 'output_schema': outputs.model_json_schema()})
    return {**groups, 'max_tool_calls': 8,
            'payments': 'Explicit human checkout required. No capture, refund, stock-write or role-mutation tool.'}


def _persist(db, principal, merchant_id, role, products, tools, inference, started) -> dict:
    mode = 'llm-grounded' if inference.answer else 'deterministic-tool-baseline'
    usage = {'input_tokens': inference.input_tokens, 'output_tokens': inference.output_tokens,
             'estimated_cost_usd': inference.estimated_cost_usd,
             'reserved_cost_usd': inference.reserved_cost_usd, 'usage_estimated': inference.usage_estimated,
             'latency_ms': max(0, int((time.monotonic() - started) * 1000))}
    run = AgentRun(merchant_id=merchant_id, principal_key=hashlib.sha256(principal.subject.encode()).hexdigest(),
                   role=role, mode=mode, status=inference.status, tools=tools,
                   product_count=len(products), **usage)
    db.add(run)
    db.commit()
    return {'run_id': run.id, 'mode': mode, 'ai_status': inference.status, 'usage': usage}


def _llm_products(products):
    # Product names are untrusted data. Exclude addresses, SKUs, descriptions, metadata and identities.
    return [{'id': p['id'], 'name': p['name'], 'price_cents': p['price_cents'], 'currency': p['currency'],
             'freshness': p['freshness'], 'stock_updated_at': p['stock_updated_at']} for p in products]


def _shop_reply(products, selected=None):
    if not products:
        return ('No local listing matched the extracted constraints. Try a product name or SKU. '
                'Online results, when available, do not verify local stock. Checkout needs your confirmation.')
    selected_ids = [claim.product_id for claim in selected.products] if selected else [p['id'] for p in products]
    by_id = {p['id']: p for p in products}
    lines = []
    for pid in selected_ids:
        p = by_id[pid]
        money = f"{p['currency']} {p['price_cents'] // 100}.{p['price_cents'] % 100:02d}"
        stamp = p['stock_updated_at'] or 'unknown source time'
        lines.append(f"{p['name']} at {p['merchant_name']}: {money}; inventory {p['freshness']}, source update {stamp}.")
    return ' '.join(lines) + (' Listed stock is uncertain, not a verified shelf count or a guaranteed hold. '
                             'Ask the store to confirm stock and pickup before travelling. Payment needs your explicit checkout confirmation.')


async def run_shop(body: AgentInput, db: Session, p: Principal) -> tuple[dict, ToolSession]:
    started = time.monotonic()
    channel3.rate_limit(p, 'agent')
    try:
        args = extract(body)
    except ValidationError:
        raise HTTPException(422, 'Extracted constraints exceed supported search bounds') from None
    session = ToolSession()
    result = session.run('search_local_products', args.model_dump(), lambda a: search_local(db, a))
    products = result['products']
    ids = {'product_ids': [p['id'] for p in products]}
    session.run('check_store_hours', ids, lambda _: {'stores': [
        {'product_id': x['id'], 'merchant_id': x['merchant_id'], 'hours': x['hours'],
         'is_open': x['is_open'], 'basis': 'Stored schedule/operational override; not verified presence.'} for x in products]})
    session.run('explain_stock_freshness', ids, lambda _: {'inventory': [
        {'product_id': x['id'], 'freshness': x['freshness'], 'stock_updated_at': x['stock_updated_at'],
         'verified_local_stock': False} for x in products]})
    session.run('recommend_pickup', ids, lambda a: {'product_ids': a.product_ids})
    inference = await llm.infer({'products': _llm_products(products), 'numeric_facts': {'match_count': len(products)}}, 'consumer')
    online = None
    if not products:
        # Product entities only; never send raw user text or merchant analytics to the catalog provider.
        if args.terms:
            channel3.rate_limit(p)
            try:
                online = await channel3.search(' '.join(args.terms))
            except HTTPException as exc:
                online = channel3.envelope(channel3.configured(), status='unavailable', error_code=exc.status_code)
        else:
            online = channel3.envelope(channel3.configured(), status='query_required')
    meta = _persist(db, p, None, 'consumer', products, session.used, inference, started)
    return {**meta, 'tools_used': session.used, 'reply': _shop_reply(products, inference.answer),
            'products': products, 'low_stock': [], 'stale': [],
            'requires_user_confirmation_for_payment': True,
            'constraints': args.model_dump(exclude_none=True), 'truncated': result['truncated'],
            'online': online, 'online_offers': online['offers'] if online else []}, session


@router.post('/agents/shop')
async def agent_shop(body: AgentInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    return (await run_shop(body, db, p))[0]


def _inventory(db, mid, stale=False):
    now = utcnow()
    condition = or_(Product.stock_updated_at < now - timedelta(minutes=15),
                    Product.stock_updated_at.is_(None), Product.stock_updated_at > now) if stale else (
                        Product.quantity - Product.hold_quantity <= 3)
    where = (Product.merchant_id == mid, Product.active.is_(True), condition)
    total = int(db.scalar(select(func.count()).select_from(Product).where(*where)) or 0)
    products = db.scalars(select(Product).where(*where).order_by(Product.stock_updated_at, Product.id).limit(12)).all()
    merchant = db.get(Merchant, mid)
    return {'products': [product_dto(x, merchant, location=location_for(db, x)) for x in products], 'count': total}


def _order_facts(db, mid):
    rows = db.execute(select(Order.status, func.count()).where(Order.merchant_id == mid).group_by(Order.status)).all()
    # Fixed keys prevent untrusted status strings becoming provider instructions.
    total = sum(int(count) for _, count in rows)
    pending = sum(int(count) for status, count in rows if status in {'PAID', 'ACCEPTED', 'PREPARING', 'READY'})
    return {'numeric_facts': {'order_count': total, 'pending_pickup_count': pending}, 'as_of': iso(utcnow())}


def _revenue_facts(db, mid):
    # Separate currencies and payment states. Never add USD to GBP or call captures net revenue.
    rows = db.execute(select(Order.currency, Order.payment_status, func.sum(Order.amount_cents))
                      .where(Order.merchant_id == mid, Order.payment_status.in_(['CAPTURED', 'REFUNDED']))
                      .group_by(Order.currency, Order.payment_status)).all()
    facts = {}
    for currency, status, amount in rows:
        if len(currency) == 3 and currency.isascii() and currency.isalpha() and currency.isupper():
            prefix = 'recorded_captured_amount_cents_' if status == 'CAPTURED' else 'recorded_refunded_order_amount_cents_'
            facts[prefix + currency] = int(amount or 0)
    return {'numeric_facts': facts, 'as_of': iso(utcnow())}


def _merchant_reply(low, stale, numeric, answer):
    reply = (f"{low['count']} active products are low-stock; {stale['count']} have stale or unknown inventory timestamps. "
             'Prioritize physical stock checks. Listed quantities are not POS-authoritative. ')
    if answer and answer.intent == 'order_summary':
        reply += f"Recorded orders: {numeric['order_count']}; pending pickup: {numeric['pending_pickup_count']}. "
    if answer and answer.intent == 'revenue_summary':
        amounts = [(key.rsplit('_', 1)[1], value) for key, value in numeric.items()
                   if key.startswith('recorded_captured_amount_cents_')]
        reply += 'Recorded captured order amounts: ' + (', '.join(
            f'{currency} {amount // 100}.{amount % 100:02d}' for currency, amount in amounts) if amounts else 'none')
        reply += '. These are order records, not profit, provider reconciliation or bank settlement. '
    return reply + 'No stock, payment, refund or staff-role changes were made.'


def merchant_intent(message: str) -> str:
    text = message.lower()
    return 'revenue_summary' if any(t in text for t in ['revenue', 'sales', 'income']) else (
           'order_summary' if any(t in text for t in ['order', 'pickup']) else 'inventory_review')


async def run_merchant(body: AgentInput, db: Session, p: Principal) -> tuple[dict, ToolSession]:
    started = time.monotonic()
    channel3.rate_limit(p, 'agent')
    mid = merchant_scope(db, p, body.merchant_id)
    session = ToolSession()
    args = {'merchant_id': mid}
    low = session.run('detect_low_stock', args, lambda a: _inventory(db, a.merchant_id))
    stale = session.run('suggest_stock_checks', args, lambda a: _inventory(db, a.merchant_id, stale=True))
    orders = session.run('explain_orders', args, lambda a: _order_facts(db, a.merchant_id))
    revenue = session.run('report_revenue', args, lambda a: _revenue_facts(db, a.merchant_id))
    numeric = {**orders['numeric_facts'], **revenue['numeric_facts'],
               'low_stock_count': low['count'], 'stale_stock_count': stale['count']}
    products = list({x['id']: x for x in low['products'] + stale['products']}.values())[:12]
    intent = merchant_intent(body.message)
    # Consent read immediately before each inference. No customer/order-level data is sent.
    facts = {'products': _llm_products(products), 'numeric_facts': numeric, 'requested_intent': intent}
    inference = await llm.infer(facts, 'merchant', sensitive_authorized=consent_granted(db, mid))
    # Deterministic summaries still honor the extracted intent if inference is disabled.
    selected = inference.answer or llm.GroundedAnswer(intent=intent, products=[], facts=[], actions=[])
    meta = _persist(db, p, mid, 'merchant', products, session.used, inference, started)
    return {**meta, 'merchant_id': mid, 'tools_used': session.used,
            'reply': _merchant_reply(low, stale, numeric, selected), 'products': products,
            'low_stock': low['products'], 'stale': stale['products'], 'facts': numeric,
            'facts_as_of': orders['as_of'], 'low_stock_count': low['count'], 'stale_count': stale['count'],
            'requires_user_confirmation_for_payment': True}, session


@router.post('/agents/merchant')
async def agent_merchant(body: AgentInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    return (await run_merchant(body, db, p))[0]
