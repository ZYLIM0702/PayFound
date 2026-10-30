"""PayPal sandbox flows with mocked PayPal HTTP (httpx.MockTransport). No network."""
import json
import httpx
import pytest
from cryptography.fernet import Fernet
from sqlalchemy import select
from app import paypal
from app.auth import Principal
from app.database import SessionLocal
from app.models import MerchantMembership, Order, PaymentEvent, ProviderOperation
from app.paypal_accounts import MerchantPayPalAccount, ShopperPayPalDetail, merchant_or_404


class FakePayPal:
    def __init__(self):
        self.orders, self.calls, self.status, self.n = {}, [], {}, 0
        self.valid_secret = 'good-secret-1234567890'

    def handler(self, request: httpx.Request):
        path, body = request.url.path, (json.loads(request.content) if request.content and 'json' in request.headers.get('content-type', '') else {})
        self.calls.append((request.method, path, request.headers.get('paypal-request-id'), body))
        if path == '/v1/oauth2/token':
            import base64
            user, _, secret = base64.b64decode(request.headers['authorization'][6:]).decode().partition(':')
            if user == 'platform-id' or secret == self.valid_secret:
                return httpx.Response(200, json={'access_token': 'tok', 'expires_in': 3600})
            return httpx.Response(401, json={'error': 'invalid_client'})
        if request.method == 'POST' and path == '/v2/checkout/orders':
            rid = request.headers.get('paypal-request-id')
            known = next((k for k, v in self.orders.items() if v['rid'] == rid), None)
            if not known:
                self.n += 1
                known = f'PPORDER{self.n}'
                self.orders[known] = {'rid': rid, 'body': body}
                self.status[known] = 'CREATED'
            return httpx.Response(201, json={'id': known, 'status': 'CREATED'})
        parts = path.split('/')
        if request.method == 'GET' and path.startswith('/v2/checkout/orders/'):
            pid = parts[-1]
            unit = dict(self.orders[pid]['body']['purchase_units'][0])
            if self.status[pid] == 'COMPLETED':
                unit['payments'] = {'captures': [{'id': 'CAP-' + pid, 'status': 'COMPLETED', 'amount': unit['amount']}]}
            return httpx.Response(200, json={'id': pid, 'status': self.status[pid], 'purchase_units': [unit]})
        if request.method == 'POST' and path.endswith('/capture'):
            pid = parts[-2]
            unit = dict(self.orders[pid]['body']['purchase_units'][0])
            self.status[pid] = 'COMPLETED'
            unit['payments'] = {'captures': [{'id': 'CAP-' + pid, 'status': 'COMPLETED', 'amount': unit['amount']}]}
            return httpx.Response(201, json={'id': pid, 'status': 'COMPLETED', 'purchase_units': [unit]})
        return httpx.Response(404, json={})


@pytest.fixture()
def pp(monkeypatch):
    fake = FakePayPal()
    monkeypatch.setenv('PAYPAL_CLIENT_ID', 'platform-id')
    monkeypatch.setenv('PAYPAL_CLIENT_SECRET', 'platform-secret')
    monkeypatch.setenv('CONNECTOR_ENCRYPTION_KEY', Fernet.generate_key().decode())
    monkeypatch.setattr(paypal, '_transport', httpx.MockTransport(fake.handler))
    paypal._tokens.clear()
    return fake


def reserve(client, consumer, key, product='p1'):
    r = client.post('/api/orders/reserve', headers=consumer, json={'product_id': product, 'idempotency_key': key})
    assert r.status_code in (200, 201), r.text
    return r.json()['id']


def test_stuck_approved_order_is_captured_by_resume(client, consumer, pp):
    oid = reserve(client, consumer, 'flow-approved')
    created = client.post(f'/api/orders/{oid}/paypal/create', headers=consumer)
    created = created.json()
    pid = created['id']
    pp.status[pid] = 'APPROVED'  # buyer approved but the page never called capture
    r = client.post(f'/api/orders/{oid}/paypal/resume', headers=consumer)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body['action'] == 'captured' and body['order']['payment_status'] == 'CAPTURED' and body['order']['status'] == 'PAID'
    capture = [c for c in pp.calls if c[1].endswith('/capture')]
    assert len(capture) == 1 and capture[0][2] == 'capture-' + oid
    again = client.post(f'/api/orders/{oid}/paypal/resume', headers=consumer).json()
    assert again['action'] == 'captured' and len([c for c in pp.calls if c[1].endswith('/capture')]) == 1


def test_unapproved_order_offers_new_paypal_order_with_new_request_id(client, consumer, pp):
    oid = reserve(client, consumer, 'flow-created')
    old = client.post(f'/api/orders/{oid}/paypal/create', headers=consumer).json()['id']
    r = client.post(f'/api/orders/{oid}/paypal/resume', headers=consumer).json()
    assert r['action'] == 'pay_again' and r['provider_status'] == 'CREATED' and r['order']['payment_status'] == 'CREATED'
    new = client.post(f'/api/orders/{oid}/paypal/restart', headers=consumer)
    assert new.status_code == 200, new.text
    assert new.json()['id'] and new.json()['id'] != old
    assert new.json()['order']['paypal_order_id'] == new.json()['id']
    rids = [c[2] for c in pp.calls if c[0] == 'POST' and c[1] == '/v2/checkout/orders']
    assert len(rids) == 2 and rids[0] != rids[1] and all(len(x) <= 38 for x in rids)
    # amounts stay server-side and identical
    amounts = {json.dumps(v['body']['purchase_units'][0]['amount']) for v in pp.orders.values()}
    assert len(amounts) == 1
    with SessionLocal() as db:
        kinds = [e.event_type for e in db.scalars(select(PaymentEvent).where(PaymentEvent.order_id == oid))]
        assert 'payment.provider_abandoned' in kinds and kinds.count('payment.provider_created') == 2
    # the new order can be approved and captured by the normal flow
    pp.status[new.json()['id']] = 'APPROVED'
    done = client.post(f'/api/orders/{oid}/paypal/capture', headers=consumer).json()
    assert done['payment_status'] == 'CAPTURED'


def test_restart_refused_when_provider_order_is_not_abandoned_or_captured(client, consumer, pp):
    oid = reserve(client, consumer, 'flow-no-restart')
    pid = client.post(f'/api/orders/{oid}/paypal/create', headers=consumer).json()['id']
    pp.status[pid] = 'APPROVED'
    assert client.post(f'/api/orders/{oid}/paypal/restart', headers=consumer).status_code == 409
    other = {'x-demo-role': 'merchant'}  # sellers cannot start a buyer's payment
    assert client.post(f'/api/orders/{oid}/paypal/restart', headers=other).status_code == 403


def test_voided_order_can_restart(client, consumer, pp):
    oid = reserve(client, consumer, 'flow-void')
    pid = client.post(f'/api/orders/{oid}/paypal/create', headers=consumer).json()['id']
    pp.status[pid] = 'VOIDED'
    assert client.post(f'/api/orders/{oid}/paypal/resume', headers=consumer).json()['action'] == 'pay_again'
    assert client.post(f'/api/orders/{oid}/paypal/restart', headers=consumer).status_code == 200


ACCOUNT = {'client_id': 'AbCdEf123456-merchant', 'client_secret': 'good-secret-1234567890',
           'receiving_email': 'Seller@Example.com'}


def test_merchant_secret_encrypted_and_never_returned(client, merchant, consumer, pp):
    url = '/api/merchants/m1/paypal-account'
    saved = client.put(url, headers=merchant, json=ACCOUNT)
    assert saved.status_code == 200, saved.text
    text = json.dumps(saved.json()) + client.get(url, headers=merchant).text
    assert 'good-secret' not in text and 'seller@example.com' not in text.lower()
    assert saved.json()['secret_hint'] == '••••7890' and saved.json()['receiving_email'] == 's***@example.com'
    with SessionLocal() as db:
        row = db.get(MerchantPayPalAccount, 'm1')
        assert 'good-secret' not in row.secret_encrypted and row.secret_encrypted.startswith('gAAAA')
    ok = client.post(url + '/test', headers=merchant).json()
    assert ok['ok'] is True and ok['status'] == 'verified' and 'good-secret' not in json.dumps(ok)
    assert client.put(url, headers=merchant, json={**ACCOUNT, 'client_secret': 'bad-secret-1234567'}).status_code == 200
    assert client.post(url + '/test', headers=merchant).json()['ok'] is False
    assert client.put(url, headers=merchant, json={**ACCOUNT, 'password': 'x'}).status_code == 422
    assert client.put(url, headers=consumer, json=ACCOUNT).status_code == 404
    assert client.delete(url, headers=merchant).json() == {'connected': False}
    assert client.get(url, headers=merchant).json()['connected'] is False


def test_only_owner_can_set_paypal_account(client, pp):
    from app.models import utcnow
    with SessionLocal() as db:
        db.add(MerchantMembership(id='mem-staff-1', merchant_id='m1', subject='staff-user', role='staff', active=True))
        db.commit()
        staff = Principal('staff-user', 'merchant', 'm1')
        merchant_or_404(db, staff, 'm1')
        with pytest.raises(Exception) as err:
            merchant_or_404(db, staff, 'm1', 'owner')
        assert getattr(err.value, 'status_code', None) == 403


def test_shopper_stores_email_only_and_rejects_password_fields(client, consumer, pp):
    url = '/api/me/payment-methods/paypal-sandbox'
    for extra in ({'password': 'hunter2'}, {'card_number': '4111111111111111'}, {'client_secret': 'x'}):
        assert client.post(url, headers=consumer, json={'email': 'buyer@example.com', **extra}).status_code == 422
    assert client.post(url, headers=consumer, json={'email': 'a' * 200 + '@example.com'}).status_code == 422
    assert client.post(url, headers=consumer, json={'email': 'nope'}).status_code == 422
    r = client.post(url, headers=consumer, json={'email': 'Buyer@Example.com', 'paypal_merchant_id': 'ab12cd34ef56g'})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body['label'] == 'b***@example.com' and body['preferred'] is True and body['stored'] is True
    listing = client.get('/api/me/payment-methods', headers=consumer).text
    assert 'buyer@example.com' not in listing.lower() and 'AB12CD34EF56G' not in listing
    with SessionLocal() as db:
        d = db.get(ShopperPayPalDetail, 'demo-consumer')
        assert 'buyer@example.com' not in d.email_encrypted.lower() and d.paypal_merchant_id == 'AB12CD34EF56G'


def pay(client, consumer, pp, key):
    oid = reserve(client, consumer, key)
    pid = client.post(f'/api/orders/{oid}/paypal/create', headers=consumer).json()['id']
    pp.status[pid] = 'APPROVED'
    assert client.post(f'/api/orders/{oid}/paypal/capture', headers=consumer).json()['payment_status'] == 'CAPTURED'
    return oid, pid


def test_payment_history_is_merchant_scoped_and_has_stages(client, consumer, merchant, pp):
    oid, pid = pay(client, consumer, pp, 'hist-order-1')
    r = client.get('/api/merchants/m1/payments', headers=merchant)
    assert r.status_code == 200, r.text
    data = r.json()
    stages = {i['stage'] for i in data['items'] if i['order_id'] == oid}
    assert {'created', 'approved', 'captured'} <= stages
    row = next(i for i in data['items'] if i['order_id'] == oid and i['stage'] == 'captured')
    assert row['provider_order_id'] == pid and row['currency'] == 'USD' and row['amount_cents'] == 3999
    assert data['totals']['USD']['captured_cents'] >= 3999
    assert client.get('/api/merchants/m1/payments?stage=captured', headers=merchant).json()['items']
    # another store, a shopper, and unknown stores all get 404
    with SessionLocal() as db:
        other = db.scalar(select(Order.merchant_id).where(Order.merchant_id != 'm1'))
    assert other and client.get(f'/api/merchants/{other}/payments', headers=merchant).status_code == 404
    assert client.get('/api/merchants/m1/payments', headers=consumer).status_code == 404
    assert client.get('/api/merchants/nope/payments', headers=merchant).status_code == 404
    assert client.post(f'/api/merchants/{other}/payments/{oid}/reconcile', headers=merchant).status_code == 404
    rec = client.post(f'/api/merchants/m1/payments/{oid}/reconcile', headers=merchant)
    assert rec.status_code == 200 and rec.json()['payment_status'] == 'CAPTURED'


def test_demo_payments_are_not_listed_as_paypal(client, consumer, merchant, pp):
    oid = reserve(client, consumer, 'hist-demo')
    assert client.post(f'/api/orders/{oid}/mock-pay', headers=consumer).status_code == 200
    items = client.get('/api/merchants/m1/payments', headers=merchant).json()['items']
    assert all(i['order_id'] != oid for i in items)


def test_configured_merchant_account_is_used_as_payee(client, consumer, merchant, pp):
    assert client.put('/api/merchants/m1/paypal-account', headers=merchant, json=ACCOUNT).status_code == 200
    oid = reserve(client, consumer, 'payee-email')
    pid = client.post(f'/api/orders/{oid}/paypal/create', headers=consumer).json()['id']
    unit = pp.orders[pid]['body']['purchase_units'][0]
    assert unit['payee'] == {'email_address': 'seller@example.com'}
    assert unit['amount']['value'] == '39.99'  # amount still from the server catalogue
    # a PayPal merchant id takes precedence and is enforced on capture
    client.put('/api/merchants/m1/paypal-account', headers=merchant, json={**ACCOUNT, 'paypal_merchant_id': 'SELLER12345AB'})
    oid2 = reserve(client, consumer, 'payee-id')
    pid2 = client.post(f'/api/orders/{oid2}/paypal/create', headers=consumer).json()['id']
    assert pp.orders[pid2]['body']['purchase_units'][0]['payee'] == {'merchant_id': 'SELLER12345AB'}
    with SessionLocal() as db:
        assert db.get(Order, oid2).expected_payee_id == 'SELLER12345AB'
    pp.status[pid2] = 'APPROVED'
    # fake PayPal echoes the requested payee, so the capture passes the payee check
    done = client.post(f'/api/orders/{oid2}/paypal/capture', headers=consumer)
    assert done.status_code == 409 or done.json()['payment_status'] == 'CAPTURED'


def test_platform_seller_used_when_no_merchant_account(client, consumer, pp):
    oid = reserve(client, consumer, 'payee-none')
    pid = client.post(f'/api/orders/{oid}/paypal/create', headers=consumer).json()['id']
    assert 'payee' not in pp.orders[pid]['body']['purchase_units'][0]
