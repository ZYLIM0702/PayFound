"""Opt-in real sandbox webhook check using an expiring, private test inbox."""
import argparse
import asyncio
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import uuid

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'apps/api'))
from app import config, paypal

ENTITY = 'payfound-sandbox-test-relay'
PRIVATE = ROOT / 'docs/evidence/paypal-webhook-raw'
STATE = PRIVATE / 'run.json'
EVIDENCE = ROOT / 'docs/evidence/paypal-webhook-check.json'


def now():
    return datetime.now(timezone.utc).isoformat()


def save(state):
    PRIVATE.mkdir(mode=0o700, exist_ok=True)
    PRIVATE.chmod(0o700)
    with os.fdopen(os.open(STATE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as target:
        json.dump(state, target)


def result(state, **changes):
    report = json.loads(EVIDENCE.read_text()) if EVIDENCE.exists() else {}
    if report.get('run_id') != state['run_id']:
        report = {'run_id': state['run_id'], 'environment': 'sandbox', 'started_at': state['started_at']}
    report.update(checked_at=now(), **changes)
    EVIDENCE.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


async def rest(method, table, *, params=None, body=None, prefer=None):
    url = os.environ['SUPABASE_PROJECT_URL'].rstrip('/')
    key = os.getenv('SUPABASE_SECRET_KEY') or os.environ['SUPABASE_SERVICE_ROLE_KEY']
    headers = {'apikey': key, 'Authorization': 'Bearer ' + key}
    if prefer:
        headers['Prefer'] = prefer
    async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
        response = await client.request(method, url + '/rest/v1/' + table, headers=headers, params=params, json=body)
    if not response.is_success:
        raise RuntimeError(f'Private test inbox returned HTTP {response.status_code}')
    return response.json() if response.content else None


async def configure(state, enabled):
    await rest('POST', 'audit_events', body={
        'actor': 'sandbox-test-runner', 'action': 'test.paypal_hook_config', 'entity_id': ENTITY, 'created_at': now(),
        'details': json.dumps({'enabled': enabled, 'nonce_hash': hashlib.sha256(state['nonce'].encode()).hexdigest(),
            'run_id': state['run_id'], 'expires_at': state['expires_at']})})


async def setup():
    if STATE.exists() and not json.loads(STATE.read_text()).get('cleaned_up'):
        raise RuntimeError('An unfinished test exists; verify or cleanup before another setup')
    nonce = secrets.token_urlsafe(32)
    state = {'run_id': uuid.uuid4().hex, 'started_at': now(), 'nonce': nonce,
             'expires_at': (datetime.now(timezone.utc) + timedelta(minutes=45)).isoformat(), 'event_ids': []}
    state['url'] = os.environ['SUPABASE_PROJECT_URL'].rstrip('/') + '/functions/v1/' + ENTITY + '?run=' + nonce
    save(state)
    await configure(state, True)
    async with httpx.AsyncClient(timeout=20) as client:
        missing = await client.post(state['url'].split('?')[0], json={})
        probe = await client.post(state['url'], json={})
    assert missing.status_code == 401 and probe.status_code == 422, 'Test ingress auth probe failed'
    registered = await paypal.call('POST', '/v1/notifications/webhooks', {
        'url': state['url'], 'event_types': [{'name': 'PAYMENT.CAPTURE.COMPLETED'}, {'name': 'PAYMENT.CAPTURE.REFUNDED'}]},
        request_id='hook-' + state['run_id'])
    state['webhook_id'] = registered['id']
    save(state)
    result(state, status='ready', webhook_id=registered['id'], ingress_missing_nonce=missing.status_code,
           ingress_valid_nonce=probe.status_code, expires_at=state['expires_at'])


async def exercise(state):
    assert state.get('webhook_id') and not state.get('payment_attempted'), 'Exercise is one-shot per run'
    state['payment_attempted'] = True
    save(state)
    subprocess.run([sys.executable, str(ROOT / 'scripts/paypal_card_check.py'), '--live'], cwd=ROOT,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, timeout=240)
    payment = json.loads((ROOT / 'docs/evidence/paypal-card-check.json').read_text())
    state['payment'] = payment
    save(state)
    assert payment['status'] == 'passed', 'Inspect sanitized card-check evidence'
    result(state, status='waiting_for_delivery', local_order_id=payment['local_order_id'],
           provider_order_id=payment['provider_order_id'], provider_capture_id=payment['provider_capture_id'],
           capture=payment['capture'], refund=payment['refund'])


async def deliveries(state):
    rows = await rest('GET', 'provider_webhooks', params={
        'select': 'id,payload,event_type', 'received_at': 'gte.' + state['started_at'], 'verified': 'eq.false', 'limit': '100'})
    found = []
    for row in rows:
        envelope = json.loads(row['payload'])
        if envelope.get('run_id') == state['run_id']:
            found.append((row, envelope))
    state['event_ids'] = sorted(set(state['event_ids']) | {row['id'] for row, _ in found})
    save(state)
    return found


async def verify(state, wait_seconds):
    assert state.get('payment', {}).get('status') == 'passed', 'Exercise must pass first'
    deadline = time.monotonic() + wait_seconds
    while True:
        found = await deliveries(state)
        if {row['event_type'] for row, _ in found} >= {'PAYMENT.CAPTURE.COMPLETED', 'PAYMENT.CAPTURE.REFUNDED'}:
            break
        if time.monotonic() >= deadline:
            result(state, status='waiting_for_delivery', received_types=sorted({row['event_type'] for row, _ in found}))
            return False
        await asyncio.sleep(20)

    # Use the running demo's existing database, never a remote database or test
    # fixture. ASGI transport avoids opening demo access beyond loopback.
    database = ROOT / 'apps/api/payfound_demo.db'
    assert database.is_file(), 'Existing local demo database required'
    os.environ.update(DEMO_MODE='true', DATABASE_URL='sqlite:///' + str(database), PAYPAL_WEBHOOK_ID=state['webhook_id'])
    from app.main import app
    from app.database import SessionLocal
    from app.models import Order, Product, ProviderWebhook, OutboxJob
    from app import worker
    from sqlalchemy import select, func

    local_id = state['payment']['local_order_id']
    capture_id = state['payment']['provider_capture_id']
    with SessionLocal() as db:
        order = db.get(Order, local_id)
        assert order and order.paypal_capture_id == capture_id and order.payment_status == 'REFUNDED'
        refund_id = order.paypal_refund_id
        product = db.get(Product, 'p1')
        stock_before = (product.quantity, product.hold_quantity)

    checked = []
    transport = httpx.ASGITransport(app=app, client=('127.0.0.1', 12345))
    async with httpx.AsyncClient(transport=transport, base_url='http://127.0.0.1:8000', timeout=90) as client:
        for row, envelope in found:
            raw = base64.b64decode(envelope['raw_base64'], validate=True)
            event = json.loads(raw)
            expected = capture_id if row['event_type'] == 'PAYMENT.CAPTURE.COMPLETED' else refund_id
            if event.get('resource', {}).get('id') != expected:
                continue
            headers = {**envelope['headers'], 'Content-Type': 'application/json'}
            missing = await client.post('/api/paypal/webhook', content=raw)
            assert missing.status_code == 401
            bad_headers = dict(headers)
            sig = bad_headers['paypal-transmission-sig']
            bad_headers['paypal-transmission-sig'] = ('A' if sig[0] != 'A' else 'B') + sig[1:]
            forged = await client.post('/api/paypal/webhook', content=raw, headers=bad_headers)
            assert forged.status_code == 401, f'Forged signature status {forged.status_code}'
            changed = json.loads(raw)
            changed['resource']['amount']['value'] = '0.01'
            tampered = await client.post('/api/paypal/webhook', json=changed, headers=headers)
            assert tampered.status_code == 401, f'Tampered amount status {tampered.status_code}'
            with SessionLocal() as db:
                assert db.get(ProviderWebhook, row['id']) is None, 'Rejected event must not enter inbox'
            accepted = await client.post('/api/paypal/webhook', content=raw, headers=headers)
            assert accepted.status_code == 200 and accepted.json().get('queued_for_reconciliation')
            replay = await client.post('/api/paypal/webhook', content=raw, headers=headers)
            assert replay.status_code == 200 and replay.json().get('duplicate')
            # Verification must precede duplicate detection, even after acceptance.
            replay_forged = await client.post('/api/paypal/webhook', content=raw, headers=bad_headers)
            assert replay_forged.status_code == 401
            checked.append({'event_id': row['id'], 'event_type': row['event_type'],
                'genuine_signature': 'passed', 'duplicate': 'passed', 'missing_headers_http': missing.status_code,
                'forged_signature_http': forged.status_code, 'tampered_amount_http': tampered.status_code,
                'forged_replay_http': replay_forged.status_code, 'body_sha256': hashlib.sha256(raw).hexdigest()})
        assert len(checked) == 2, 'Expected one matching capture and refund event'
        for _ in range(6):
            await worker.tick(max_jobs=30, connectors=False)
            with SessionLocal() as db:
                if all(db.get(ProviderWebhook, item['event_id']).processed_at for item in checked):
                    break
            await asyncio.sleep(2)
        with SessionLocal() as db:
            for item in checked:
                event = db.get(ProviderWebhook, item['event_id'])
                assert event.verified and event.processed_at
                count = db.scalar(select(func.count()).select_from(OutboxJob).where(
                    OutboxJob.dedupe_key == 'webhook:' + item['event_id']))
                assert count == 1, 'Exactly one reconciliation job per event'
            order = db.get(Order, local_id)
            product = db.get(Product, 'p1')
            assert order.status == 'CANCELLED' and order.payment_status == 'REFUNDED'
            assert stock_before == (product.quantity, product.hold_quantity), 'Webhook replay must not restock twice'
    result(state, status='passed', application_transport='actual FastAPI ASGI handler with live PayPal signature API',
           events=checked, worker_processing='passed', terminal_state_preserved='CANCELLED/REFUNDED',
           stock_replay_effects='none')
    return True


async def cleanup(state):
    await configure(state, False)
    wid = state.get('webhook_id')
    if not wid:
        listing = await paypal.call('GET', '/v1/notifications/webhooks')
        wid = next((item['id'] for item in listing.get('webhooks', []) if item.get('url') == state['url']), None)
    listing = await paypal.call('GET', '/v1/notifications/webhooks')
    if wid and any(item['id'] == wid for item in listing.get('webhooks', [])):
        # A one-shot test deletes only the exact subscription it created.
        await paypal.call('DELETE', '/v1/notifications/webhooks/' + wid)
    found = await deliveries(state)
    for row, _ in found:
        await rest('DELETE', 'provider_webhooks', params={'id': 'eq.' + row['id']})
    async with httpx.AsyncClient(timeout=20) as client:
        retired = await client.post(state['url'], json={})
    assert retired.status_code == 410
    listing = await paypal.call('GET', '/v1/notifications/webhooks')
    assert not any(item['id'] == wid for item in listing.get('webhooks', []))
    state.update(cleaned_up=True)
    state.pop('nonce', None)
    state.pop('url', None)
    save(state)
    result(state, cleanup='passed', temporary_subscription_removed=True, ingress_retired_http=retired.status_code,
           private_transport_rows_removed=len(found))


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', required=True)
    parser.add_argument('action', choices=('setup', 'exercise', 'verify', 'cleanup'))
    parser.add_argument('--wait-seconds', type=int, default=100)
    args = parser.parse_args()
    assert 0 <= args.wait_seconds <= 300
    assert os.getenv('PAYPAL_ENV', 'sandbox') == 'sandbox'
    try:
        if args.action == 'setup':
            await setup()
        else:
            state = json.loads(STATE.read_text())
            if state.get('cleaned_up') and args.action == 'cleanup':
                result(state, cleanup='passed', already_retired=True)
                return 0
            assert not state.get('cleaned_up'), 'Run already retired'
            if args.action == 'exercise':
                await exercise(state)
            elif args.action == 'verify':
                if not await verify(state, args.wait_seconds):
                    return 2
            else:
                await cleanup(state)
        return 0
    except Exception as exc:
        # Exception strings/HTTP URLs can contain nonce, tokens, or provider PII.
        failure = {'action': args.action, 'status': 'failed', 'error_type': type(exc).__name__}
        if isinstance(exc, AssertionError):
            failure['check'] = str(exc)
        print(json.dumps(failure))
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
