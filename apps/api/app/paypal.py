"""Sandbox REST adapter: bounded I/O, cached OAuth, stable operation identities."""
import asyncio
import hashlib
import json
import logging
import os
import time
from decimal import Decimal
from urllib.parse import quote
import httpx
from fastapi import HTTPException

BASE = 'https://api-m.sandbox.paypal.com'
logger = logging.getLogger('payfound.paypal')
_tokens = {}
_transport = None


def configured():
    return bool(os.getenv('PAYPAL_CLIENT_ID') and os.getenv('PAYPAL_CLIENT_SECRET'))


def api_base():
    if os.getenv('PAYPAL_ENV', 'sandbox') != 'sandbox':
        raise HTTPException(503, 'PayPal sandbox configuration required')
    return BASE


async def access_token():
    if not configured():
        raise HTTPException(503, 'PayPal sandbox credentials not configured')
    key = hashlib.sha256((os.environ['PAYPAL_CLIENT_ID'] + ':' + os.environ['PAYPAL_CLIENT_SECRET']).encode()).hexdigest()
    cached = _tokens.get(key)
    if cached and cached[1] > time.monotonic():
        return cached[0]
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=False, transport=_transport) as client:
            response = await client.post(api_base() + '/v1/oauth2/token',
                auth=(os.environ['PAYPAL_CLIENT_ID'], os.environ['PAYPAL_CLIENT_SECRET']),
                data={'grant_type': 'client_credentials'})
        if response.status_code != 200:
            raise HTTPException(502, 'PayPal sandbox authentication failed')
        data = response.json()
        token, ttl = data['access_token'], min(int(data['expires_in']), 28800)
        _tokens.clear()
        _tokens[key] = (token, time.monotonic() + max(0, ttl - 60))
        return token
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        raise HTTPException(502, 'PayPal authentication unavailable') from exc


async def call(method, path, payload=None, request_id=None, prefer=None):
    token = await access_token()
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    if request_id:
        headers['PayPal-Request-Id'] = request_id[:38]
    if prefer:
        headers['Prefer'] = prefer
    try:
        async with httpx.AsyncClient(timeout=25, follow_redirects=False, transport=_transport) as client:
            for attempt in range(3):
                response = await client.request(method, api_base() + path, json=payload, headers=headers)
                if response.status_code != 429 or attempt == 2:
                    break
                # Only rate-limit responses are automatically replayed. Transport
                # failures enter the durable readback path, never a blind retry.
                await asyncio.sleep(0.5 * (2 ** attempt))
        data = response.json() if response.content else {}
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(502, 'PayPal network state uncertain; reconcile before retrying') from exc
    if response.status_code >= 400:
        debug_id = str(data.get('debug_id', ''))[:100]
        issues = {x.get('issue') for x in data.get('details', []) if isinstance(x, dict)}
        logger.warning('provider_error status=%s debug_id=%s', response.status_code, debug_id)
        payee_bad = bool(issues & {'PAYEE_ACCOUNT_INVALID', 'PAYEE_ACCOUNT_RESTRICTED', 'PAYEE_ACCOUNT_LOCKED_OR_CLOSED', 'INVALID_PAYEE'})
        message = ('Funding instrument declined; choose another method' if 'INSTRUMENT_DECLINED' in issues else
                   "This store's PayPal receiving account was not accepted by PayPal sandbox. The store owner should check it in Settings."
                   if payee_bad else 'PayPal rejected the operation; reconciliation may be required')
        raise HTTPException(422 if issues & {'INSTRUMENT_DECLINED'} or payee_bad else 502, message,
                            headers={'X-PayPal-Debug-Id': debug_id} if debug_id else None)
    return data


async def verify_credentials(client_id, client_secret):
    """Fetch (and discard) a sandbox OAuth token for a merchant-supplied app. Returns True/False only."""
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=False, transport=_transport) as client:
            response = await client.post(api_base() + '/v1/oauth2/token', auth=(client_id, client_secret),
                                         data={'grant_type': 'client_credentials'})
        return response.status_code == 200 and bool(response.json().get('access_token'))
    except (httpx.HTTPError, ValueError, AttributeError):
        raise HTTPException(502, 'PayPal sandbox unreachable; try again')


async def create_order(order, payee=None, request_id=None):
    unit = {'reference_id': order.id, 'custom_id': order.id,
            'amount': {'currency_code': order.currency, 'value': str((Decimal(order.amount_cents) / 100).quantize(Decimal('.01')))},
            'description': 'PayFound merchant pickup — sandbox'}
    if payee:  # the store's own sandbox receiving account (merchant_id or email_address)
        unit['payee'] = dict(payee)
    elif getattr(order, 'expected_payee_id', None):
        unit['payee'] = {'merchant_id': order.expected_payee_id}
    return await call('POST', '/v2/checkout/orders', {'intent': 'CAPTURE', 'purchase_units': [unit]},
                      request_id or 'create-' + order.id)


async def capture_order(provider_id, order_id):
    return await call('POST', f'/v2/checkout/orders/{quote(provider_id, safe="")}/capture', {}, 'capture-' + order_id)


async def get_order(provider_id):
    return await call('GET', f'/v2/checkout/orders/{quote(provider_id, safe="")}')


async def refund_capture(capture_id, order_id):
    return await call('POST', f'/v2/payments/captures/{quote(capture_id, safe="")}/refund', {}, 'refund-' + order_id,
                      prefer='return=representation')


async def get_refund(refund_id):
    return await call('GET', f'/v2/payments/refunds/{quote(refund_id, safe="")}')


async def verify_webhook(payload, headers, raw_body=None):
    wid = os.getenv('PAYPAL_WEBHOOK_ID', '')
    if not wid:
        raise HTTPException(503, 'PayPal webhook ID missing; cannot verify')
    fields = {name: headers.get('paypal-' + name.replace('_', '-')) for name in
              ('transmission_id', 'transmission_time', 'cert_url', 'auth_algo', 'transmission_sig')}
    if not all(fields.values()):
        raise HTTPException(401, 'Missing PayPal verification headers')
    # The postback API accepts the webhook_event object. Keep the original body
    # in the verified inbox; do not reconstruct it for local signature checks.
    event = json.loads(raw_body) if raw_body is not None else payload
    result = await call('POST', '/v1/notifications/verify-webhook-signature',
                        {**fields, 'webhook_id': wid, 'webhook_event': event},
                        'verify-' + hashlib.sha256(fields['transmission_id'].encode()).hexdigest()[:30])
    if result.get('verification_status') != 'SUCCESS':
        raise HTTPException(401, 'PayPal signature verification failed')
    return True
