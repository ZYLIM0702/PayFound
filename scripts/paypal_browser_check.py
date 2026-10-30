"""Opt-in real sandbox wallet test. Credentials never enter logs or arguments."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlparse
import uuid

import httpx
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'apps/api'))
from app import config

LOCAL = 'http://127.0.0.1:8000/api'
WEB = 'http://127.0.0.1:5173'
PAYPAL = 'https://api-m.sandbox.paypal.com'


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true', required=True)
    parser.add_argument('--inspect', action='store_true', help='Inspect SDK and popup without entering login credentials')
    args = parser.parse_args()
    email = os.getenv('PAYPAL_SANDBOX_BUYER_EMAIL') or os.getenv('PAYPAL_BUYER_EMAIL') or os.getenv('PAYPAL_SANDBOX_EMAIL', '')
    password = (os.getenv('PAYPAL_SANDBOX_BUYER_PASSWORD') or os.getenv('PAYPAL_SANDBOX_BUYER_EMAIL_PASSWORD')
                or os.getenv('PAYPAL_BUYER_PASSWORD') or os.getenv('PAYPAL_SANDBOX_EMAIL_PASSWORD', ''))
    client_id = os.getenv('PAYPAL_CLIENT_ID', '')
    secret = os.getenv('PAYPAL_CLIENT_SECRET', '')
    redactions = [value for value in (email, password, secret, os.getenv('PAYPAL_ACCESS_TOKEN', '')) if value]
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'environment': 'sandbox',
              'status': 'running', 'buyer_credentials_present': bool(email and password),
              'sdk_button': 'not_checked', 'capture': 'not_attempted', 'refund': 'not_attempted',
              'stages': [], 'provider_requests': [], 'page_errors': []}
    order_id = None

    def redact(value):
        text = str(value)
        for item in redactions:
            text = text.replace(item, '[redacted]')
        return text

    def summary(page):
        host = urlparse(page.url).hostname
        return {'host': host, 'path': urlparse(page.url).path,
                'inputs': page.locator('input:visible').evaluate_all("els => els.map(e => ({type:e.type,name:e.name,id:e.id}))"),
                'buttons': [redact(x)[:100] for x in page.get_by_role('button').all_text_contents()][:25]}

    def official_frame(context):
        for page in reversed(context.pages):
            for frame in reversed(page.frames):
                host = urlparse(frame.url).hostname or ''
                if host == 'sandbox.paypal.com' or host.endswith('.sandbox.paypal.com'):
                    return page, frame
        return None, None

    try:
        assert os.getenv('PAYPAL_ENV', 'sandbox') == 'sandbox', 'Sandbox environment required'
        with httpx.Client(base_url=LOCAL, timeout=40) as api:
            settings = api.get('/config').json()
            assert settings['demo_mode'] and settings['paypal_sandbox_enabled'] and settings['paypal_environment'] == 'sandbox', 'Configured local sandbox stack required'
            product = api.get('/products', params={'ids': 'p1'}).json()[0]
            assert product['synthetic'], 'Only synthetic local inventory may be used'
            if product['available_quantity'] < 1:
                api.patch('/merchant/products/p1/stock', headers={'x-demo-role': 'merchant'}, json={'quantity': 9}).raise_for_status()
            reserved = api.post('/orders/reserve', headers={'x-demo-role': 'consumer'}, json={
                'product_id': 'p1', 'quantity': 1, 'buyer_name': 'Sandbox automated test',
                'idempotency_key': 'paypal-wallet-test-' + uuid.uuid4().hex})
            reserved.raise_for_status()
            order = reserved.json()
            order_id = order['id']
            report.update(local_order_id=order_id, amount_cents=order['amount_cents'], currency=order['currency'])

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(viewport={'width': 1440, 'height': 1000})

                def sandbox_only(route):
                    host = urlparse(route.request.url).hostname or ''
                    if host in {'www.paypal.com', 'paypal.com', 'api.paypal.com', 'api-m.paypal.com'}:
                        report['stages'].append({'blocked_live_host': host})
                        route.abort()
                    else:
                        route.continue_()

                context.route('**/*', sandbox_only)
                page = context.new_page()
                page.on('pageerror', lambda error: report['page_errors'].append(redact(error.message)[:600]))

                def provider_response(response):
                    host = urlparse(response.url).hostname or ''
                    if 'paypal' in host and response.status >= 400:
                        report['provider_requests'].append({'host': host, 'path': urlparse(response.url).path, 'status': response.status})

                context.on('response', provider_response)
                page.goto(f'{WEB}/checkout/{order_id}', wait_until='domcontentloaded')
                page.get_by_role('heading', name='Checkout', exact=True).wait_for(timeout=30000)
                # The official high-level React component renders this v6 custom element.
                button = page.locator('paypal-button').first
                try:
                    button.wait_for(state='visible', timeout=45000)
                except Exception:
                    report.update(status='blocked', sdk_button='unavailable', detail='SDK payment method did not render')
                    report['local_page'] = {'alerts': [redact(x) for x in page.get_by_role('alert').all_text_contents()],
                                            'payment_text': redact(page.locator('main').inner_text())[:2500]}
                    return
                report['sdk_button'] = 'rendered'
                page.screenshot(path=str(ROOT / 'docs/evidence/paypal-sdk-checkout.png'), full_page=True)
                button.click(timeout=15000)
                provider_id = None
                for _ in range(30):
                    order = api.get(f'/orders/{order_id}', headers={'x-demo-role': 'consumer'}).json()
                    provider_id = order.get('paypal_order_id')
                    if provider_id:
                        break
                    page.wait_for_timeout(500)
                report['provider_order_id'] = provider_id
                for _ in range(30):
                    popup, frame = official_frame(context)
                    if frame:
                        break
                    page.wait_for_timeout(500)
                else:
                    report.update(status='blocked', detail='SDK click did not open a sandbox approval document')
                    report['local_page'] = {'alerts': [redact(x) for x in page.get_by_role('alert').all_text_contents()]}
                    return
                popup.wait_for_load_state('domcontentloaded')
                report['stages'].append({'approval_document': summary(frame)})
                if provider_id and client_id and secret:
                    with httpx.Client(timeout=25) as remote:
                        token_response = remote.post(PAYPAL + '/v1/oauth2/token', auth=(client_id, secret), data={'grant_type': 'client_credentials'})
                        token_response.raise_for_status()
                        token = token_response.json()['access_token']
                        redactions.append(token)
                        found = remote.get(PAYPAL + '/v2/checkout/orders/' + provider_id, headers={'Authorization': 'Bearer ' + token})
                        found.raise_for_status()
                        payee = found.json().get('purchase_units', [{}])[0].get('payee', {})
                        seller_email = payee.get('email_address', '')
                        if seller_email:
                            redactions.append(seller_email)
                        report['buyer_login_matches_seller'] = bool(email and seller_email and email.casefold() == seller_email.casefold())
                        if report['buyer_login_matches_seller']:
                            report.update(status='blocked', detail='The provided sandbox login is the seller receiving this purchase; a distinct buyer account is required')
                            return
                if args.inspect:
                    report.update(status='inspected', detail='SDK and approval document inspected; no login submitted')
                    return
                if not email or not password:
                    report.update(status='blocked', detail='Sandbox buyer login credentials are not configured')
                    return

                submitted_email, submitted_password, approved = False, False, False
                for _ in range(18):
                    order = api.get(f'/orders/{order_id}', headers={'x-demo-role': 'consumer'}).json()
                    if order.get('payment_status') == 'CAPTURED':
                        report['capture'] = 'confirmed_by_application'
                        break
                    popup, frame = official_frame(context)
                    if not frame:
                        page.wait_for_timeout(1000)
                        continue
                    host = urlparse(frame.url).hostname or ''
                    assert host == 'sandbox.paypal.com' or host.endswith('.sandbox.paypal.com'), 'Refusing non-sandbox login'
                    visible_text = frame.locator('body').inner_text(timeout=5000)
                    if re.search(r'captcha|confirm you.re not a robot|security challenge|enter.*(?:code|one.time)|verify your identity', visible_text, re.I):
                        report.update(status='blocked', detail='Sandbox account requires an interactive security/verification step')
                        return
                    if re.search(r'pay yourself|logged in.*seller|logging in.*seller|seller.*account.*purchase', visible_text, re.I):
                        report.update(status='blocked', detail='PayPal rejected the seller account as the buyer')
                        return
                    emails = frame.locator('input[type="email"]:visible, input#email:visible, input[name="login_email"]:visible')
                    passwords = frame.locator('input[type="password"]:visible')
                    if emails.count() and not submitted_email:
                        emails.first.fill(email)
                        submitted_email = True
                        report['stages'].append('sandbox_email_submitted')
                    if passwords.count() and not submitted_password:
                        passwords.first.fill(password)
                        submitted_password = True
                        report['stages'].append('sandbox_password_submitted')
                    if submitted_password and not approved:
                        login = frame.get_by_role('button', name=re.compile(r'^(Log In|Log in|Sign In|Sign in)$'))
                        if login.count() and login.first.is_visible():
                            login.first.click()
                            page.wait_for_timeout(1500)
                            continue
                    if not submitted_password:
                        next_button = frame.get_by_role('button', name=re.compile(r'^(Next|Continue)$'))
                        if next_button.count() and next_button.first.is_visible():
                            next_button.first.click()
                            page.wait_for_timeout(1000)
                            continue
                    confirmation = frame.get_by_role('button', name=re.compile(r'^(Agree (?:&|and) Pay|Pay Now|Pay now|Complete Purchase|Complete purchase|Pay)$'))
                    if submitted_password and confirmation.count() and confirmation.first.is_visible():
                        expected = f"{order['amount_cents'] / 100:.2f}"
                        if expected not in visible_text:
                            report.update(status='blocked', detail='Approval document did not expose the expected sandbox total')
                            return
                        confirmation.first.click()
                        approved = True
                        report['stages'].append('approval_submit_clicked')
                    page.wait_for_timeout(1000)
                else:
                    report.update(status='blocked', detail='Sandbox approval did not complete within the bounded test window')
                    if popup and not popup.is_closed():
                        report['approval_document'] = summary(popup)
                        alerts = popup.get_by_role('alert').all_text_contents()
                        report['approval_alerts'] = [redact(x)[:600] for x in alerts]
                    return

                # Repeats exercise the application's idempotency boundary, not a new payment.
                captured = api.post(f'/orders/{order_id}/paypal/capture', headers={'x-demo-role': 'consumer'})
                captured.raise_for_status()
                assert captured.json()['payment_status'] == 'CAPTURED'
                report['capture_idempotency'] = 'passed'
                refunded = api.post(f'/orders/{order_id}/refund', headers={'x-demo-role': 'merchant'})
                refunded.raise_for_status()
                state = refunded.json()['payment_status']
                report['refund'] = state
                if state == 'REFUND_PENDING':
                    for _ in range(6):
                        time.sleep(3)
                        readback = api.post(f'/orders/{order_id}/paypal/reconcile', headers={'x-demo-role': 'consumer'})
                        if readback.is_success and readback.json()['payment_status'] == 'REFUNDED':
                            report['refund'] = 'REFUNDED'
                            break
                if report['refund'] == 'REFUNDED':
                    again = api.post(f'/orders/{order_id}/refund', headers={'x-demo-role': 'merchant'})
                    assert again.is_success and again.json()['payment_status'] == 'REFUNDED'
                    report['refund_idempotency'] = 'passed'
                report['status'] = 'passed' if report['refund'] == 'REFUNDED' else 'pending_refund'
                browser.close()
    except Exception as exc:
        report.update(status='failed', error_type=type(exc).__name__, detail=redact(exc)[:2000])
    finally:
        # Retain genuine test journals and original provider operation identities.
        # An unpaid provider order is allowed to expire via the actual worker.
        if order_id:
            try:
                with httpx.Client(base_url=LOCAL, timeout=10) as api:
                    final = api.get(f'/orders/{order_id}', headers={'x-demo-role': 'consumer'}).json()
                    report['final_order_status'] = final.get('status')
                    report['final_payment_status'] = final.get('payment_status')
            except Exception:
                pass
        path = ROOT / 'docs/evidence/paypal-browser-check.json'
        path.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    run()
    status = json.loads((ROOT / 'docs/evidence/paypal-browser-check.json').read_text())['status']
    sys.exit(0 if status in ('passed', 'inspected') else 2 if status in ('blocked', 'pending_refund') else 1)
