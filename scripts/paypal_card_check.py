"""One opt-in sandbox fixture-card confirmation, app capture and app refund."""
import argparse
import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import uuid
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'apps/api'))
from app import config, paypal


async def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true', required=True)
    parser.parse_args()
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'environment': 'sandbox',
              'path': 'sandbox_fixture_card_confirmation', 'status': 'running',
              'capture': 'not_attempted', 'refund': 'not_attempted'}
    local_id = None
    try:
        assert os.getenv('PAYPAL_ENV', 'sandbox') == 'sandbox'
        async with httpx.AsyncClient(base_url='http://127.0.0.1:8000/api', timeout=90) as api:
            public = (await api.get('/config')).json()
            assert public['demo_mode'] and public['paypal_sandbox_enabled'] and public['paypal_environment'] == 'sandbox'
            product = (await api.get('/products', params={'ids': 'p1'})).json()[0]
            assert product['synthetic'] and product['currency'] == 'USD'
            if product['available_quantity'] < 1:
                (await api.patch('/merchant/products/p1/stock', headers={'x-demo-role': 'merchant'}, json={'quantity': 9})).raise_for_status()
            made = await api.post('/orders/reserve', headers={'x-demo-role': 'consumer'}, json={
                'product_id': 'p1', 'quantity': 1, 'buyer_name': 'Sandbox fixture card test',
                'idempotency_key': 'paypal-card-test-' + uuid.uuid4().hex})
            made.raise_for_status()
            order = made.json()
            local_id = order['id']
            report.update(local_order_id=local_id, amount_cents=order['amount_cents'], currency=order['currency'])
            created = await api.post(f'/orders/{local_id}/paypal/create', headers={'x-demo-role': 'consumer'})
            created.raise_for_status()
            provider_id = created.json()['id']
            report['provider_order_id'] = provider_id
            token = await paypal.access_token()
            async with httpx.AsyncClient(timeout=30, follow_redirects=False) as remote:
                confirmed = await remote.post(paypal.BASE + f'/v2/checkout/orders/{provider_id}/confirm-payment-source',
                    headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json',
                             'PayPal-Request-Id': ('confirm-' + local_id)[:38]},
                    json={'payment_source': {'card': {'number': '4111111111111111', 'expiry': '2027-12',
                                                     'name': 'Test Buyer', 'security_code': '123'}}})
                data = confirmed.json()
                report['confirmation_http_status'] = confirmed.status_code
                if not confirmed.is_success:
                    report.update(status='blocked', confirmation_name=data.get('name'),
                        confirmation_issues=[x.get('issue') for x in data.get('details', []) if isinstance(x, dict)],
                        debug_id=data.get('debug_id'))
                    return
                report['provider_status_after_confirmation'] = data.get('status')
                if data.get('status') == 'PAYER_ACTION_REQUIRED':
                    report.update(status='blocked', detail='Sandbox fixture card requires a payer/3DS interaction')
                    return
                if data.get('status') == 'COMPLETED':
                    captured = await api.post(f'/orders/{local_id}/paypal/reconcile', headers={'x-demo-role': 'consumer'})
                    report['capture_path'] = 'provider_complete_then_application_readback'
                else:
                    captured = await api.post(f'/orders/{local_id}/paypal/capture', headers={'x-demo-role': 'consumer'})
                    report['capture_path'] = 'application_capture_endpoint'
                report['capture_http_status'] = captured.status_code
                if not captured.is_success:
                    report.update(status='failed', detail=captured.json().get('detail', 'Capture failed'))
                    return
                assert captured.json()['payment_status'] == 'CAPTURED'
                report['capture'] = 'confirmed_by_application'
                readback = await paypal.get_order(provider_id)
                captures = readback['purchase_units'][0]['payments']['captures']
                assert len(captures) == 1 and captures[0]['status'] == 'COMPLETED'
                assert captures[0]['amount'] == {'currency_code': 'USD', 'value': f"{order['amount_cents'] / 100:.2f}"}
                report['provider_capture_id'] = captures[0]['id']
                repeated = await api.post(f'/orders/{local_id}/paypal/capture', headers={'x-demo-role': 'consumer'})
                assert repeated.is_success and repeated.json()['payment_status'] == 'CAPTURED'
                check = await paypal.get_order(provider_id)
                assert len(check['purchase_units'][0]['payments']['captures']) == 1
                report['capture_idempotency'] = 'passed'
                refund = await api.post(f'/orders/{local_id}/refund', headers={'x-demo-role': 'merchant'})
                report['refund_http_status'] = refund.status_code
                refund.raise_for_status()
                report['refund'] = refund.json()['payment_status']
                if report['refund'] == 'REFUND_PENDING':
                    for _ in range(6):
                        await asyncio.sleep(3)
                        polled = await api.post(f'/orders/{local_id}/paypal/reconcile', headers={'x-demo-role': 'consumer'})
                        if polled.is_success and polled.json()['payment_status'] == 'REFUNDED':
                            report['refund'] = 'REFUNDED'
                            break
                if report['refund'] == 'REFUNDED':
                    repeated = await api.post(f'/orders/{local_id}/refund', headers={'x-demo-role': 'merchant'})
                    assert repeated.is_success and repeated.json()['payment_status'] == 'REFUNDED'
                    report['refund_idempotency'] = 'passed'
                report['status'] = 'passed' if report['refund'] == 'REFUNDED' else 'pending_refund'
    except Exception as exc:
        # No raw HTTP responses, headers, OAuth tokens or test PAN in evidence.
        report.update(status='failed', error_type=type(exc).__name__)
    finally:
        if local_id:
            try:
                async with httpx.AsyncClient(base_url='http://127.0.0.1:8000/api', timeout=15) as api:
                    final = (await api.get(f'/orders/{local_id}', headers={'x-demo-role': 'consumer'})).json()
                    report['final_order_status'] = final.get('status')
                    report['final_payment_status'] = final.get('payment_status')
            except Exception:
                pass
        (ROOT / 'docs/evidence/paypal-card-check.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    asyncio.run(run())
    status = json.loads((ROOT / 'docs/evidence/paypal-card-check.json').read_text())['status']
    sys.exit(0 if status == 'passed' else 2 if status in ('blocked', 'pending_refund') else 1)
