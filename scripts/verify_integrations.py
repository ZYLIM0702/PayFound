"""Targeted, opt-in integration probes. Outputs only non-secret evidence."""
import argparse
import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'apps/api'))
from app import config, paypal
from app.intelligence import channel3
import httpx


async def run(args):
    result = {'checked_at': datetime.now(timezone.utc).isoformat()}
    if paypal.configured():
        try:
            data = await paypal.call('GET', '/v1/catalogs/products?page_size=1&page=1')
            result['paypal_oauth_read'] = {'status': 'passed', 'products_returned': len(data.get('products', [])), 'environment': 'sandbox'}
        except Exception as exc:
            result['paypal_oauth_read'] = {'status': 'failed', 'error_type': type(exc).__name__, 'detail': getattr(exc, 'detail', '')}
    else:
        result['paypal_oauth_read'] = {'status': 'unconfigured'}
    if args.channel3:
        try:
            data = await channel3.search('USB-C 65W charger')
            result['channel3_search'] = {'status': 'passed' if data['enabled'] else 'unconfigured', 'offers_returned': len(data['offers']), 'online_only': True}
        except Exception as exc:
            result['channel3_search'] = {'status': 'failed', 'error_type': type(exc).__name__, 'detail': getattr(exc, 'detail', '')}
    url = os.getenv('SUPABASE_JWKS_URL')
    if url:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url)
            result['supabase_jwks'] = {'status': 'passed' if response.is_success else 'failed', 'http_status': response.status_code,
                                       'key_count': len(response.json().get('keys', [])) if response.is_success else 0}
    if args.paypal_create:
        async with httpx.AsyncClient(base_url='http://127.0.0.1:8000/api', timeout=40) as client:
            public = (await client.get('/config')).json()
            if not public.get('demo_mode') or not public.get('paypal_sandbox_enabled'):
                raise RuntimeError('Sandbox create probe requires the local demo stack with PayPal configured')
            headers = {'x-demo-role': 'consumer'}
            reserved = await client.post('/orders/reserve', headers=headers,
                json={'product_id': 'p1', 'quantity': 1, 'idempotency_key': 'sandbox-probe-' + uuid.uuid4().hex})
            reserved.raise_for_status()
            order = reserved.json()
            made = await client.post(f"/orders/{order['id']}/paypal/create", headers=headers)
            result['paypal_application_create'] = {'status': 'passed' if made.is_success else 'failed', 'http_status': made.status_code,
                'local_order_id': order['id'], 'provider_order_id': made.json().get('id'),
                'capture': 'not attempted; sandbox buyer approval required'}
    result['remaining_configuration'] = [name for name in ('DATABASE_URL', 'LLM_MODEL', 'LLM_API_KEY', 'SHOPIFY_CLIENT_ID', 'SHOPIFY_CLIENT_SECRET') if not os.getenv(name)]
    path = ROOT / 'docs/evidence/integrations.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel3', action='store_true', help='Perform one catalog search using configured credits')
    parser.add_argument('--paypal-create', action='store_true', help='Create one sandbox order through the local app, without capture')
    asyncio.run(run(parser.parse_args()))
