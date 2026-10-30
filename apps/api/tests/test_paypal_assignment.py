"""Sandbox account pool assignment, 'Sandbox demo' payment rows and payee routing. Mocked PayPal HTTP only."""
import json
import os
import httpx
import pytest
from sqlalchemy import select
from app import paypal
from app.database import SessionLocal, engine
from app.models import Merchant, Order
from app.paypal_accounts import PaypalSandboxAccount, PaypalDemoPayment
from app.paypal_pool import seed_demo_payments, seed_paypal_pool

# Obviously fake secrets. They must never reach the database or any API response.
PASSWORDS = [f'Pw!Fake{i:02d}-zQ9x' for i in range(20)]
CARDS = [f'4111000011{i:06d}' for i in range(20)]


@pytest.fixture()
def pool(client, tmp_path, monkeypatch):
    path = tmp_path / 'pool.csv'
    lines = ['country_code,account_type,primary_email_alias,password,first_name,last_name,ppBalance,addBank,ccType,payment_card']
    for i in range(20):
        lines.append(f'US,BUSINESS,sb-test{i:02d}@business.example.com,{PASSWORDS[i]},First{i},Last{i},1000,,VISA,{CARDS[i]}')
    path.write_text('\n'.join(lines))
    monkeypatch.setenv('PAYPAL_SANDBOX_POOL_CSV', str(path))
    with SessionLocal() as db:
        seed_paypal_pool(db, force=True)
        seed_demo_payments(db, force=True)
    return path


def mapping():
    with SessionLocal() as db:
        return {a.assigned_to_merchant_id: a.email for a in db.scalars(select(PaypalSandboxAccount)) if a.assigned_to_merchant_id}


def test_one_account_per_merchant_stable_across_reseeds(client, pool):
    first = mapping()
    with SessionLocal() as db:
        stores = db.query(Merchant).count()
    assert len(first) == min(stores, 20) and len(set(first.values())) == len(first) and first['m1'] == 'sb-test00@business.example.com'
    with SessionLocal() as db:
        seed_paypal_pool(db, force=True)
        seed_paypal_pool(db, force=True)
        assert db.query(PaypalSandboxAccount).count() == 20
    assert mapping() == first


def test_no_passwords_or_cards_in_database_or_responses(client, pool, merchant, consumer):
    bodies = [client.get('/api/merchants/m1/paypal-account', headers=merchant).text,
              client.get('/api/merchants/m1/payments?limit=200', headers=merchant).text,
              client.get('/api/me/payment-methods', headers=consumer).text]
    secrets = PASSWORDS + CARDS
    for body in bodies:
        assert not any(x in body for x in secrets)
    engine.dispose()
    path = engine.url.database
    raw = open(path, 'rb').read()
    assert not any(x.encode() in raw for x in secrets)


def test_account_endpoint_prefills_assigned_email_without_secrets(client, pool, merchant):
    body = client.get('/api/merchants/m1/paypal-account', headers=merchant).json()
    assert body['connected'] is False and body['assigned'] is True and body['status'] == 'assigned'
    assert body['receiving_email'] == 'sb-test00@business.example.com'
    assert not any(k in body for k in ('client_secret', 'secret_hint', 'password'))


def test_payee_routing_uses_assigned_email(client, consumer, pool, monkeypatch):
    seen = {}

    def handler(request: httpx.Request):
        if request.url.path == '/v1/oauth2/token':
            return httpx.Response(200, json={'access_token': 't', 'expires_in': 3600})
        if request.method == 'POST' and request.url.path == '/v2/checkout/orders':
            seen['body'] = json.loads(request.content)
            seen['rid'] = request.headers.get('paypal-request-id')
            return httpx.Response(201, json={'id': 'PPORDERX', 'status': 'CREATED'})
        return httpx.Response(404, json={})
    monkeypatch.setenv('PAYPAL_CLIENT_ID', 'platform-id')
    monkeypatch.setenv('PAYPAL_CLIENT_SECRET', 'platform-secret')
    monkeypatch.setattr(paypal, '_transport', httpx.MockTransport(handler))
    paypal._tokens.clear()
    r = client.post('/api/orders/reserve', headers=consumer, json={'product_id': 'p1', 'idempotency_key': 'assign-payee'})
    assert r.status_code in (200, 201), r.text
    oid = r.json()['id']
    assert client.post(f'/api/orders/{oid}/paypal/create', headers=consumer).status_code == 200
    assert seen['body']['purchase_units'][0]['payee'] == {'email_address': 'sb-test00@business.example.com'}
    assert seen['rid'] == 'create-' + oid


def test_demo_payment_rows_are_labelled_and_not_live(client, pool, merchant):
    body = client.get('/api/merchants/m1/payments?limit=200', headers=merchant).json()
    assert body['totals'] == {} and body['demo_totals']['USD']['captured_cents'] > 0
    demo = [i for i in body['items'] if i['demo']]
    assert demo and all(i['label'] == 'Sandbox demo' and i['reference'].startswith('SBX-DEMO-') for i in demo)
    assert all(i['provider_order_id'] is None and i['capture_id'] is None for i in demo)
    assert body['daily']
    with SessionLocal() as db:
        assert db.query(PaypalDemoPayment).count() == db.query(PaypalDemoPayment).filter_by(provider='paypal_sandbox', demo_seeded=True).count() > 0
        before = db.query(Order).count()
        assert seed_demo_payments(db, force=True) == 0 and db.query(Order).count() == before


def test_shopper_assignment_is_private(client, consumer, pool):
    mine = client.get('/api/me/payment-methods', headers=consumer).json()['methods']
    assert mine and mine[0]['assigned'] is True and 'sb-test' not in json.dumps(mine)
    other = {'x-demo-role': 'merchant'}
    theirs = client.get('/api/me/payment-methods', headers=other).json()['methods']
    assert all(m['label'] != mine[0]['label'] for m in theirs)
    assert client.get('/api/merchants/m1/paypal-account', headers=consumer).status_code == 404

