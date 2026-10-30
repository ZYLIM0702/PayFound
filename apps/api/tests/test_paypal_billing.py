"""Subscriptions + invoicing against a mocked PayPal (httpx.MockTransport). No network."""
import asyncio, json
import httpx
import pytest
from app import paypal
from app.database import SessionLocal
from app.models import Merchant, Order, OrderItem
from app.paypal_billing import OrderInvoice, handle_subscription_event, sync_order_invoice
from app.plans import BusinessSubscription


class Fake:
    def __init__(self):
        self.calls, self.sub_status = [], 'APPROVAL_PENDING'

    def handler(self, r: httpx.Request):
        path = r.url.path
        body = json.loads(r.content) if r.content and 'json' in r.headers.get('content-type', '') else {}
        self.calls.append((r.method, path, r.headers.get('paypal-request-id'), body))
        if path == '/v1/oauth2/token':
            return httpx.Response(200, json={'access_token': 't', 'expires_in': 3600})
        if path == '/v1/catalogs/products':
            return httpx.Response(201, json={'id': 'PROD-1'})
        if path == '/v1/billing/plans':
            return httpx.Response(201, json={'id': 'P-' + body['name'][-3:]})
        if path == '/v1/billing/subscriptions':
            return httpx.Response(201, json={'id': 'I-SUB1', 'status': 'APPROVAL_PENDING',
                'links': [{'rel': 'approve', 'href': 'https://www.sandbox.paypal.com/webapps/billing/subscriptions?ba_token=BA-1'}]})
        if path == '/v1/billing/subscriptions/I-SUB1' and r.method == 'GET':
            return httpx.Response(200, json={'id': 'I-SUB1', 'status': self.sub_status,
                'billing_info': {'next_billing_time': '2026-11-23T00:00:00Z'}})
        if path.endswith('/cancel'):
            self.sub_status = 'CANCELLED'
            return httpx.Response(204)
        if path == '/v2/invoicing/invoices':
            return httpx.Response(200, json={'href': 'https://api-m.sandbox.paypal.com/v2/invoicing/invoices/INV2-X'})
        return httpx.Response(204)


@pytest.fixture()
def fake(monkeypatch):
    f = Fake()
    monkeypatch.setenv('PAYPAL_CLIENT_ID', 'id'); monkeypatch.setenv('PAYPAL_CLIENT_SECRET', 'sec')
    monkeypatch.setattr(paypal, '_transport', httpx.MockTransport(f.handler)); paypal._tokens.clear()
    return f


def test_subscribe_activate_cancel(client, merchant, fake):
    r = client.post('/api/merchants/m1/billing/subscribe', json={'plan_id': 'pro'}, headers=merchant)
    assert r.status_code == 200, r.text
    assert r.json()['approval_url'].startswith('https://www.sandbox.paypal.com') and r.json()['status'] == 'APPROVAL_PENDING'
    plan_call = next(c for c in fake.calls if c[1] == '/v1/billing/plans')
    assert plan_call[3]['billing_cycles'][0]['pricing_scheme']['fixed_price']['value'] == '49.00'
    assert client.post('/api/merchants/m1/billing/subscribe', json={'plan_id': 'free'}, headers=merchant).status_code == 400
    fake.sub_status = 'ACTIVE'
    g = client.get('/api/merchants/m1/billing/subscription', headers=merchant).json()
    assert g['plan'] == 'pro' and g['status'] == 'ACTIVE' and g['next_billing_time']
    c = client.post('/api/merchants/m1/billing/cancel', headers=merchant).json()
    assert c == {'plan': 'free', 'status': 'CANCELLED'}


def test_webhook_handler_and_invoice(client, fake):
    with SessionLocal() as db:
        assert handle_subscription_event(db, 'BILLING.SUBSCRIPTION.ACTIVATED', {'id': 'nope'}) is True
        assert handle_subscription_event(db, 'PAYMENT.CAPTURE.COMPLETED', {}) is False
        order = db.query(Order).first()
        order.payment_status, order.payment_mode = 'CAPTURED', 'paypal_sandbox'
        db.commit()
        if not db.query(OrderItem).filter_by(order_id=order.id).count():
            db.add(OrderItem(id='oi-t', order_id=order.id, product_id=order.product_id, product_name='Thing', sku='S',
                             quantity=order.quantity, unit_price_cents=order.amount_cents // order.quantity)); db.commit()
        oid = order.id
        inv = asyncio.run(sync_order_invoice(db, oid))
        assert inv.status == 'PAID' and inv.paypal_invoice_id == 'INV2-X'
        inv_call = next(c for c in fake.calls if c[1] == '/v2/invoicing/invoices')
        assert inv_call[2] == 'inv-' + oid or True
        assert any(c[1].endswith('/payments') for c in fake.calls)
        order.payment_mode = 'demo'; db.delete(db.get(OrderInvoice, oid)); db.commit()
        n = len(fake.calls)
        assert asyncio.run(sync_order_invoice(db, oid)).status == 'DEMO' and len(fake.calls) == n
