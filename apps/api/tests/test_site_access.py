"""SITE_ACCESS_KEY: an optional key in front of the whole API (abuse and cost protection for shared deployments)."""
import pytest

from app import site_access

KEY = 'judges-only-2026'


@pytest.fixture()
def locked(monkeypatch):
    monkeypatch.setenv('SITE_ACCESS_KEY', KEY)
    site_access._fails.clear()
    yield
    site_access._fails.clear()


def test_off_by_default(client, consumer, monkeypatch):
    monkeypatch.delenv('SITE_ACCESS_KEY', raising=False)
    assert client.get('/api/access').json() == {'required': False, 'ok': True}
    assert client.get('/api/config', headers=consumer).status_code == 200
    assert client.post('/api/access', json={'key': 'anything'}).json()['token'] is None


def test_locked_api_refuses_without_token(client, consumer, locked):
    res = client.get('/api/config', headers=consumer)
    assert res.status_code == 401
    assert res.json()['code'] == 'access_required'
    assert res.headers[site_access.HEADER] == 'required'
    assert client.get('/api/access').json() == {'required': True, 'ok': False}


def test_open_paths_stay_reachable(client, locked):
    assert client.get('/api/health').status_code == 200
    # PayPal and POS pushes carry their own signatures; the gate must not answer for them
    assert client.post('/api/paypal/webhook', content=b'{}').json().get('code') != 'access_required'
    assert client.post('/api/pos-plugin/nope/events', content=b'{}').json().get('code') != 'access_required'


def test_right_key_unlocks(client, consumer, locked):
    res = client.post('/api/access', json={'key': f'  {KEY} '})
    assert res.status_code == 200
    token = res.json()['token']
    assert KEY not in token  # the browser stores a derived token, never the key
    assert client.get('/api/access', headers={site_access.HEADER: token}).json() == {'required': True, 'ok': True}
    assert client.get('/api/config', headers={**consumer, site_access.HEADER: token}).status_code == 200


def test_wrong_key_refused_then_limited(client, locked):
    for _ in range(site_access.MAX_FAILS):
        assert client.post('/api/access', json={'key': 'guess'}).status_code == 401
    assert client.post('/api/access', json={'key': KEY}).status_code == 429


def test_tampered_and_rotated_tokens_fail(client, consumer, locked, monkeypatch):
    token = site_access.issue()
    assert site_access.valid(token)
    assert not site_access.valid(token[:-1] + ('0' if token[-1] != '0' else '1'))
    assert not site_access.valid('')
    monkeypatch.setenv('SITE_ACCESS_KEY', 'rotated-key')
    assert client.get('/api/config', headers={**consumer, site_access.HEADER: token}).status_code == 401
