import asyncio
import json
import time

import httpx
import pytest
from cryptography.fernet import Fernet
from sqlalchemy import select

from app.connectors.security import ConnectorError, SafeHTTP, decrypt, resolve_public as real_resolve_public
from app.database import SessionLocal
from app.models import MerchantLocation, Product
from app.pos_plugin import routes, service
from app.pos_plugin.contract import ContractError, PosBranch, PosProduct, parse_rows
from app.pos_plugin.models import PosConnection, PosSyncRun

TOKEN = 'tok_live_secret_1234'
BRANCH = {'external_id': 'b1', 'name': 'Dock Store', 'address': '1 Dock Rd', 'latitude': 51.5, 'longitude': -0.1, 'timezone': 'Europe/London'}


def prod(i=1, **kw):
    row = {'external_id': f'p{i}', 'sku': f'SKU{i}', 'name': f'Item {i}', 'price': 9.99, 'currency': 'USD', 'quantity': 5,
           'branch_external_id': 'b1', 'updated_at': '2026-01-01T10:00:00Z', 'active': True, 'vendor_junk': 'ignored'}
    row.update(kw)
    return row


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv('CONNECTOR_ENCRYPTION_KEY', Fernet.generate_key().decode())
    routes._hits.clear()

    async def public(host):
        return ['93.184.216.34']
    monkeypatch.setattr(service, 'resolve_public', public)


@pytest.fixture()
def pos(monkeypatch):
    """A scriptable fake POS behind httpx.MockTransport."""
    state = {'products': [prod(1), prod(2)], 'branches': [BRANCH], 'status': 200, 'seen': []}

    def handler(request: httpx.Request):
        state['seen'].append(request)
        if request.headers.get('authorization') != f'Bearer {TOKEN}':
            return httpx.Response(401)
        if state['status'] != 200:
            return httpx.Response(state['status'])
        path = request.url.path
        if path == '/health':
            return httpx.Response(200, json={'ok': True})
        if path == '/branches':
            return httpx.Response(200, json={'branches': state['branches']})
        if path == '/products':
            return httpx.Response(200, json={'products': state['products'], 'next_cursor': None})
        return httpx.Response(404)
    def factory(conn):
        transport = httpx.MockTransport(handler)
        if (conn.settings or {}).get('loopback'):
            return service.LoopbackHTTP(transport=transport)
        return SafeHTTP(transport=transport, test_allow_unresolved_hosts=True)
    monkeypatch.setattr(service, 'http_factory', factory)
    return state


def connect(client, merchant, **kw):
    body = {'merchant_id': 'm1', 'mode': 'api', 'name': 'Till', 'base_url': 'https://pos.example.com', 'token': TOKEN, 'schedule': '15m'}
    body.update(kw)
    return client.post('/api/merchant/pos-plugin/connections', json=body, headers=merchant)


def test_contract_reports_bad_rows_and_ignores_unknown_fields():
    rows, errors = parse_rows([prod(1), prod(2, price=-3), prod(3, quantity='lots'), 'nope', prod(5, name='x' * 500)], PosProduct, 'products')
    assert [r.external_id for r in rows] == ['p1']
    assert len(errors) == 4 and all(e['error'].startswith('products:') for e in errors)
    assert rows[0].price_cents == 999 and rows[0].updated_at.tzinfo is None
    assert not hasattr(rows[0], 'vendor_junk')


def test_contract_caps_and_envelope():
    with pytest.raises(ContractError):
        parse_rows([prod(i) for i in range(1001)], PosProduct, 'products')
    with pytest.raises(ContractError):
        parse_rows({'a': 1}, PosProduct, 'products')
    rows, errors = parse_rows([BRANCH, {**BRANCH, 'external_id': 'b2', 'timezone': 'Mars/Base'}], PosBranch, 'branches')
    assert len(rows) == 1 and 'timezone' in errors[0]['error']


@pytest.mark.parametrize('url', ['https://localhost', 'https://127.0.0.1', 'https://10.0.0.5', 'https://169.254.169.254',
                                 'https://192.168.1.2', 'http://pos.example.com', 'https://user:pw@pos.example.com',
                                 'https://pos.example.com:8443', 'https://pos.internal'])
def test_ssrf_guard_rejects_unsafe_urls(url, monkeypatch):
    monkeypatch.setattr(service, 'resolve_public', real_resolve_public)
    with pytest.raises(ConnectorError):
        asyncio.run(service.validate_base_url(url))


def test_ssrf_guard_rejects_hostname_resolving_to_private(monkeypatch):
    async def private(host):
        raise ConnectorError('Store host is not publicly routable')
    monkeypatch.setattr(service, 'resolve_public', private)
    with pytest.raises(ConnectorError):
        asyncio.run(service.validate_base_url('https://evil.example.com'))


def test_connect_endpoint_rejects_private_target(client, merchant):
    assert connect(client, merchant, base_url='https://10.0.0.5').status_code == 422
    assert connect(client, merchant, base_url='https://127.0.0.1').status_code == 422


def test_demo_loader_loopback_only(client, merchant, monkeypatch, pos):
    got = client.get('/api/merchant/pos-plugin', params={'merchant_id': 'm1'}, headers=merchant).json()
    assert got['demo']['base_url'] == 'http://127.0.0.1:9010'
    assert connect(client, merchant, base_url='http://example.com').status_code == 422
    assert connect(client, merchant, base_url='http://10.0.0.1:9010').status_code == 422
    ok = connect(client, merchant, base_url='http://127.0.0.1:9010')
    assert ok.status_code == 201 and ok.json()['connection']['demo'] is True
    monkeypatch.setenv('DEMO_MODE', 'false')
    assert service.demo_mode() is False  # the overview then returns demo: null


def test_loopback_refused_outside_demo(client, merchant, monkeypatch):
    monkeypatch.setenv('DEMO_MODE', 'false')
    with pytest.raises(ConnectorError):
        asyncio.run(service.validate_base_url('http://127.0.0.1:9010'))


def test_credentials_encrypted_and_masked(client, merchant, pos):
    r = connect(client, merchant)
    assert r.status_code == 201, r.text
    assert TOKEN not in r.text and r.json()['connection']['credential_hint'] == '••••1234'
    listing = client.get('/api/merchant/pos-plugin', params={'merchant_id': 'm1'}, headers=merchant)
    assert TOKEN not in listing.text and 'credentials_encrypted' not in listing.text
    with SessionLocal() as db:
        row = db.scalar(select(PosConnection))
        assert TOKEN not in row.credentials_encrypted and decrypt(row.credentials_encrypted)['token'] == TOKEN


def test_connect_rejects_bad_token_and_rate_limits(client, merchant, pos):
    assert connect(client, merchant, token='wrong-token-0000').status_code == 422
    codes = [connect(client, merchant, token='wrong-token-0000').status_code for _ in range(12)]
    assert 429 in codes


def sync(client, merchant, cid):
    r = client.post(f'/api/merchant/pos-plugin/{cid}/sync', headers=merchant)
    assert r.status_code == 200, r.text
    return r.json()


def test_sync_is_idempotent_and_preserves_payfound_fields(client, merchant, pos):
    cid = connect(client, merchant).json()['connection']['id']
    first = sync(client, merchant, cid)
    assert (first['created'], first['updated'], first['failed'], first['status']) == (3, 0, 0, 'ok')
    second = sync(client, merchant, cid)
    assert (second['created'], second['updated'], second['skipped']) == (0, 0, 3)
    with SessionLocal() as db:
        assert db.scalar(select(MerchantLocation).where(MerchantLocation.name == 'Dock Store')) is not None
        products = list(db.scalars(select(Product).where(Product.inventory_source == 'custom_pos')))
        assert len(products) == 2
        p = next(x for x in products if x.source_product_id == 'p1')
        p.hold_quantity, p.description, p.category = 4, 'Merchant copy', 'Coffee'
        old_fresh = p.stock_updated_at
        db.commit()
    # POS lowers stock below the held units and changes price.
    pos['products'][0].update(quantity=1, price=11.5, updated_at='2026-01-02T10:00:00Z')
    third = sync(client, merchant, cid)
    assert third['updated'] == 1 and third['created'] == 0 and third['skipped'] == 2
    with SessionLocal() as db:
        p = db.scalar(select(Product).where(Product.source_product_id == 'p1', Product.inventory_source == 'custom_pos'))
        assert p.price_cents == 1150
        assert p.hold_quantity == 4 and p.quantity == 4
        assert (p.description, p.category) == ('Merchant copy', 'Coffee')
        assert p.stock_updated_at >= old_fresh
        conn = db.scalar(select(PosConnection))
        assert conn.cursor_updated_at.isoformat() == '2026-01-02T10:00:00'
    since = [r.url.params.get('updated_since') for r in pos['seen'] if r.url.path == '/products']
    assert since[0] is None and since[-1] == '2026-01-01T10:00:00Z'


def test_sync_reports_bad_rows_without_failing_run(client, merchant, pos):
    pos['products'] = [prod(1), prod(2, price=0), prod(3, branch_external_id='nope')]
    cid = connect(client, merchant).json()['connection']['id']
    run = sync(client, merchant, cid)
    assert (run['status'], run['created'], run['failed']) == ('partial', 2, 2)
    assert {e['external_id'] for e in run['row_errors']} == {'p2', 'p3'}
    runs = client.get(f'/api/merchant/pos-plugin/{cid}/runs', headers=merchant).json()['runs']
    assert runs[0]['failed'] == 2


def test_sync_failure_backs_off_and_shows_error(client, merchant, pos):
    cid = connect(client, merchant).json()['connection']['id']
    pos['status'] = 500
    run = sync(client, merchant, cid)
    assert run['status'] == 'failed' and run['error']
    sync(client, merchant, cid)
    with SessionLocal() as db:
        conn = db.get(PosConnection, cid)
        assert conn.status == 'error' and conn.failure_count == 2 and conn.last_error
        assert conn.next_sync_at is not None
    pos['status'] = 200
    sync(client, merchant, cid)
    with SessionLocal() as db:
        assert db.get(PosConnection, cid).status == 'connected' and db.get(PosConnection, cid).failure_count == 0


def test_worker_runs_due_schedule(client, merchant, pos):
    cid = connect(client, merchant).json()['connection']['id']
    with SessionLocal() as db:
        db.get(PosConnection, cid).next_sync_at = service.now() - service.timedelta(seconds=1)
        db.commit()
        result = asyncio.run(service.process_pos_jobs(db))
        assert len(result['pos_runs']) == 1
        run = db.get(PosSyncRun, result['pos_runs'][0])
        assert run.trigger == 'schedule' and run.created == 3
        assert db.get(PosConnection, cid).next_sync_at > service.now()


def test_disconnect_keeps_listings_but_unavailable(client, merchant, pos):
    cid = connect(client, merchant).json()['connection']['id']
    sync(client, merchant, cid)
    r = client.delete(f'/api/merchant/pos-plugin/{cid}', headers=merchant)
    assert r.json()['status'] == 'disconnected'
    with SessionLocal() as db:
        products = list(db.scalars(select(Product).where(Product.inventory_source == 'custom_pos')))
        assert len(products) == 2 and not any(p.active for p in products)
        assert db.get(PosConnection, cid).credentials_encrypted is None
    assert client.post(f'/api/merchant/pos-plugin/{cid}/sync', headers=merchant).status_code == 409


def test_other_merchant_connection_is_404(client, merchant, pos):
    with SessionLocal() as db:
        row = PosConnection(merchant_id='m2', name='Theirs', mode='api', base_url='https://x.example.com', settings={})
        db.add(row)
        db.commit()
        cid = row.id
    for method, path in [('post', f'/api/merchant/pos-plugin/{cid}/sync'), ('post', f'/api/merchant/pos-plugin/{cid}/test'),
                         ('get', f'/api/merchant/pos-plugin/{cid}/runs'), ('delete', f'/api/merchant/pos-plugin/{cid}')]:
        assert getattr(client, method)(path, headers=merchant).status_code == 404, path
    assert client.post('/api/merchant/pos-plugin/connections', headers=merchant,
                       json={'merchant_id': 'm2', 'mode': 'push', 'name': 'x'}).status_code == 403


def make_push(client, merchant):
    r = client.post('/api/merchant/pos-plugin/connections', headers=merchant, json={'merchant_id': 'm1', 'mode': 'push', 'name': 'Push till'})
    assert r.status_code == 201
    body = r.json()
    assert body['secret'].startswith('pfpos_') and body['endpoint_url'].endswith(f"/api/pos-plugin/{body['connection']['id']}/events")
    assert body['secret'] not in json.dumps(body['connection'])
    return body['connection']['id'], body['secret']


def signed(secret, payload, ts=None):
    raw = json.dumps(payload).encode()
    ts = str(ts if ts is not None else int(time.time()))
    return raw, {'x-payfound-timestamp': ts, 'x-payfound-signature': service.sign(secret, ts, raw), 'content-type': 'application/json'}


def test_webhook_signature_and_replay(client, merchant):
    cid, secret = make_push(client, merchant)
    url = f'/api/pos-plugin/{cid}/events'
    payload = {'branches': [BRANCH], 'products': [prod(1), prod(2, price=-1)]}
    raw, headers = signed(secret, payload)
    ok = client.post(url, content=raw, headers=headers)
    assert ok.status_code == 200 and ok.json()['created'] == 2 and ok.json()['failed'] == 1
    assert client.post(url, content=raw, headers=headers).status_code == 401
    bad = dict(headers, **{'x-payfound-signature': 'sha256=' + '0' * 64})
    assert client.post(url, content=raw, headers=bad).status_code == 401
    assert client.post(url, content=raw + b' ', headers=headers).status_code == 401
    # old timestamp, even though correctly signed
    raw2, old = signed(secret, payload, ts=int(time.time()) - 400)
    assert client.post(url, content=raw2, headers=old).status_code == 401
    raw3, wrong = signed('pfpos_other', payload)
    assert client.post(url, content=raw3, headers=wrong).status_code == 401
    # stock event then no regression of an older one
    raw4, h4 = signed(secret, {'stock_events': [{'external_id': 'p1', 'quantity': 2, 'updated_at': '2026-02-01T00:00:00Z'}]})
    assert client.post(url, content=raw4, headers=h4).json()['updated'] == 1
    raw5, h5 = signed(secret, {'stock_events': [{'external_id': 'p1', 'quantity': 9, 'updated_at': '2026-01-15T00:00:00Z'}, {'external_id': 'ghost', 'quantity': 1}]})
    out = client.post(url, content=raw5, headers=h5).json()
    assert (out['skipped'], out['failed']) == (1, 1)
    with SessionLocal() as db:
        p = db.scalar(select(Product).where(Product.source_product_id == 'p1', Product.inventory_source == 'custom_pos'))
        assert p.quantity == 2


def test_webhook_unknown_or_disconnected_is_404(client, merchant):
    assert client.post('/api/pos-plugin/nope/events', content=b'{}').status_code == 404
    cid, secret = make_push(client, merchant)
    client.delete(f'/api/merchant/pos-plugin/{cid}', headers=merchant)
    raw, h = signed(secret, {})
    assert client.post(f'/api/pos-plugin/{cid}/events', content=raw, headers=h).status_code == 404
