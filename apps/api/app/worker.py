"""Durable DB jobs: run `python -m app.worker`, or `--once` for a bounded tick."""
import argparse
import asyncio
from datetime import timedelta
import json
import logging
import signal
import uuid

from fastapi import HTTPException
from sqlalchemy import or_, select, update

from . import commerce
from .database import SessionLocal
from .models import Order, OutboxJob, ProviderWebhook, Notification, utcnow
from .connectors.service import process_connector_jobs
from .pos_plugin.service import process_pos_jobs
from .intelligence import models as intelligence_models

logger = logging.getLogger('payfound.worker')


def claim(db):
    due = or_(OutboxJob.state == 'PENDING',
              (OutboxJob.state == 'RUNNING') & (OutboxJob.lease_until < utcnow()))
    candidates = list(db.scalars(select(OutboxJob.id).where(due, OutboxJob.available_at <= utcnow())
                                .order_by(OutboxJob.available_at, OutboxJob.id).limit(10)))
    for jid in candidates:
        token = uuid.uuid4().hex
        result = db.execute(update(OutboxJob).where(OutboxJob.id == jid, due,
            OutboxJob.available_at <= utcnow()).values(state='RUNNING', lease_token=token,
            lease_until=utcnow() + timedelta(minutes=3), attempts=OutboxJob.attempts + 1))
        db.commit()
        if result.rowcount == 1:
            return db.get(OutboxJob, jid, populate_existing=True), token
    return None, None


async def process_webhook(db, event_id):
    event = db.get(ProviderWebhook, event_id)
    if not event or not event.verified or event.processed_at:
        return
    data = json.loads(event.payload)
    resource = data.get('resource', {})
    from .paypal_billing import handle_subscription_event
    if handle_subscription_event(db, str(data.get('event_type', '')), resource):
        event.processed_at = utcnow()
        db.commit()
        return
    provider_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
    capture_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('capture_id')
    if not capture_id:
        from .paypal import BASE
        prefix = BASE + '/v2/payments/captures/'
        capture_id = next((link['href'][len(prefix):] for link in resource.get('links', [])
            if isinstance(link, dict) and link.get('rel') == 'up' and str(link.get('href', '')).startswith(prefix)), None)
    dispute_captures = [t.get('seller_transaction_id') for t in resource.get('disputed_transactions', []) if isinstance(t, dict)]
    order = db.scalar(select(Order).where(or_(
        Order.paypal_order_id == provider_id if provider_id else False,
        Order.paypal_capture_id == capture_id if capture_id else False,
        Order.paypal_capture_id == resource.get('id', ''),
        Order.paypal_capture_id.in_(dispute_captures),
        Order.paypal_refund_id == resource.get('id', ''))))
    if not order:
        # Keep a verified unmatched event visible to operators; it might be an
        # external merchant action or arrive before create returns locally.
        raise HTTPException(409, 'Webhook has no matching local payment yet')
    if event.event_type in ('PAYMENT.CAPTURE.REVERSED', 'CUSTOMER.DISPUTE.CREATED', 'PAYMENT.CAPTURE.REFUNDED') and order.payment_status not in ('REFUNDED', 'REFUND_PENDING', 'REVERSED'):
        # External financial actions stop handover. Do not infer a full refund,
        # restitution, or a physical return from a generic provider event.
        order = commerce.lock_order(db, order.id)
        if order.payment_status not in ('REFUNDED', 'REFUND_PENDING', 'REVERSED'):
            order.payment_status = 'PROVIDER_REVIEW_REQUIRED'
            commerce.event(db, order, 'payment.provider_review_required', {'provider_event_id': event.id})
        event.processed_at = utcnow()
        db.commit()
        return
    await commerce.reconcile_payment(db, order.id)
    event = db.get(ProviderWebhook, event_id)
    event.processed_at = utcnow()
    db.commit()


async def tick(max_jobs=20, connectors=True):
    completed = 0
    with SessionLocal() as db:
        commerce.expire_holds(db)
        for _ in range(max_jobs):
            job, token = claim(db)
            if job is None:
                break
            jid, kind, payload = job.id, job.kind, json.loads(job.payload)
            error, repeat = None, False
            try:
                if kind == 'expire':
                    commerce.expire_order(db, payload['order_id'])
                elif kind == 'reconcile':
                    order = db.get(Order, payload['order_id'])
                    if order and order.payment_mode == 'paypal_sandbox':
                        order = await commerce.reconcile_payment(db, order.id)
                        repeat = order.payment_status in ('CREATING', 'CAPTURING', 'RECONCILIATION_REQUIRED', 'REFUND_PENDING')
                elif kind == 'order_invoice':
                    from .paypal_billing import sync_order_invoice
                    await sync_order_invoice(db, payload['order_id'])
                elif kind == 'paypal_webhook':
                    await process_webhook(db, payload['event_id'])
                elif kind == 'domain_event':
                    order = db.get(Order, payload['order_id'])
                    if order:
                        for audience in ('buyer', 'merchant'):
                            exists = db.scalar(select(Notification.id).where(Notification.order_id == order.id,
                                Notification.event_type == payload['event_type'], Notification.audience == audience))
                            if not exists:
                                db.add(Notification(id=commerce.guid('notice'), order_id=order.id, merchant_id=order.merchant_id,
                                    audience=audience, buyer_subject=order.buyer_subject if audience == 'buyer' else None,
                                    event_type=payload['event_type'], message=commerce.event_message(payload['event_type'])))
                        db.commit()
                else:
                    raise ValueError('Unknown job kind')
            except Exception as exc:
                db.rollback()
                error = type(exc).__name__
                logger.warning('job_failed job_id=%s kind=%s error=%s', jid, kind, error)
            job = db.get(OutboxJob, jid, populate_existing=True)
            if job and job.lease_token == token:
                retry = bool(error or repeat)
                state = ('FAILED' if job.attempts >= 12 else 'PENDING') if retry else 'DONE'
                db.execute(update(OutboxJob).where(OutboxJob.id == jid, OutboxJob.lease_token == token)
                    .values(state=state, last_error=error, lease_until=None, lease_token=None,
                            available_at=utcnow() + timedelta(seconds=min(1800, 5 * 2 ** min(job.attempts, 8)))))
                db.commit()
                completed += 1
        if connectors:
            await process_connector_jobs(db)
            await process_pos_jobs(db)
    return {'processed': completed}


async def run(once=False):
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)
    while not stop.is_set():
        try:
            result = await tick()
            if once:
                print(json.dumps(result))
        except Exception:
            logger.exception('worker_tick_failed')
            if once:
                raise
        if once:
            return
        try:
            await asyncio.wait_for(stop.wait(), timeout=5)
        except TimeoutError:
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run(parser.parse_args().once))
