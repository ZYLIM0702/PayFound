import json

import pytest

from app.assistant import realtime
from app.database import SessionLocal  # noqa: F401


@pytest.fixture(autouse=True)
def _limits(monkeypatch):
    from app import llm
    saved = dict(llm.budget._windows)
    monkeypatch.setenv('AGENT_RATE_LIMIT_PER_MINUTE', '1000')
    yield
    llm.budget._windows.clear()
    llm.budget._windows.update(saved)


@pytest.fixture
def minted(monkeypatch):
    seen = {}

    async def fake(api_key, body, safety_id):
        seen.update(key=api_key, body=body, safety=safety_id)
        return {'value': 'ek_test_123', 'expires_at': 1900000000}

    monkeypatch.setenv('OPENAI_API_KEY', 'sk-real-secret')
    monkeypatch.delenv('OPENAI_REALTIME_MODEL', raising=False)
    monkeypatch.setattr(realtime, 'post_secret', fake)
    return seen


def test_session_mint_shape_and_no_key_leak(client, consumer, minted):
    r = client.post('/api/assistant/realtime/session', headers=consumer, json={})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d['client_secret'] == 'ek_test_123' and d['model'] == 'gpt-realtime-2.1'
    assert 'sk-real-secret' not in r.text
    s = minted['body']['session']
    assert s['type'] == 'realtime' and s['model'] == 'gpt-realtime-2.1'
    assert s['audio']['input']['transcription']['model'] == 'gpt-4o-transcribe'
    assert s['audio']['input']['turn_detection'] == {'type': 'server_vad', 'threshold': 0.5, 'prefix_padding_ms': 300, 'silence_duration_ms': 500}
    assert minted['key'] == 'sk-real-secret'


def test_semantic_vad_and_model_env(client, consumer, minted, monkeypatch):
    monkeypatch.setenv('OPENAI_REALTIME_MODEL', 'gpt-realtime-custom')
    r = client.post('/api/assistant/realtime/session', headers=consumer, json={'vad': 'semantic'})
    assert r.json()['model'] == 'gpt-realtime-custom'
    assert minted['body']['session']['audio']['input']['turn_detection']['type'] == 'semantic_vad'


def test_instructions_forbid_payment_and_tools_are_read_only(client, consumer, minted):
    d = client.post('/api/assistant/realtime/session', headers=consumer, json={}).json()
    s = minted['body']['session']
    assert 'Voice can never pay, refund or change anything' in s['instructions'] and 'OpenUI' in s['instructions']
    names = set(d['tools'])
    assert 'search_products' in names and 'get_route' in names
    assert not any(n.startswith(realtime.FORBIDDEN_PREFIXES) for n in names)
    assert not names & {'merchant_dashboard', 'reconciliation_queue', 'integration_status'}


def test_merchant_session_has_merchant_tools(client, merchant, minted):
    names = set(client.post('/api/assistant/realtime/session', headers=merchant, json={}).json()['tools'])
    assert 'merchant_dashboard' in names and 'reconciliation_queue' not in names


def test_provider_failure_is_sanitised(client, consumer, monkeypatch):
    async def boom(*a, **k):
        raise RuntimeError('upstream said sk-real-secret is invalid')
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-real-secret')
    monkeypatch.setattr(realtime, 'post_secret', boom)
    r = client.post('/api/assistant/realtime/session', headers=consumer, json={})
    assert r.status_code == 502 and 'sk-' not in r.text and 'upstream' not in r.text


def test_missing_key_and_auth(client, consumer, monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    assert client.post('/api/assistant/realtime/session', headers=consumer, json={}).status_code == 503
    assert client.post('/api/assistant/realtime/session', headers={'x-demo-role': 'bogus'}, json={}).status_code in (400, 401, 403, 422)
    assert client.post('/api/assistant/realtime/tool', headers={'x-demo-role': 'bogus'}, json={'name': 'search_products'}).status_code in (400, 401, 403, 422)


def call_tool(client, headers, name, args=None, props=None):
    return client.post('/api/assistant/realtime/tool', headers=headers, json={'name': name, 'arguments': json.dumps(args or {}), 'forwardedProps': props})


def test_tool_runs_for_consumer(client, consumer):
    r = call_tool(client, consumer, 'search_products', {'query': 'charger'})
    assert r.status_code == 200, r.text
    assert json.loads(r.json()['output'])


def test_consumer_cannot_call_merchant_admin_or_write_tools(client, consumer):
    for name in ('merchant_dashboard', 'order_queue', 'low_stock', 'reconciliation_queue', 'integration_status', 'pay_order', 'create_refund', 'reserve_order'):
        assert call_tool(client, consumer, name, props={'surface': 'merchant', 'merchant_id': 'm1'}).status_code == 403, name


def test_merchant_cannot_call_admin_tools(client, merchant):
    assert call_tool(client, merchant, 'reconciliation_queue').status_code == 403
    assert call_tool(client, merchant, 'merchant_dashboard').status_code == 200


def test_consumer_cannot_read_others_order(client, consumer, merchant):
    orders = client.get('/api/orders', headers=consumer).json()
    other = client.get('/api/merchant/orders', headers=merchant)
    oid = (other.json()[0]['id'] if other.status_code == 200 and other.json() else 'ord_missing')
    out = json.loads(call_tool(client, consumer, 'get_order', {'order_id': oid}).json()['output'])
    assert out.get('error') in ('request_denied', 'request_failed') or 'items' not in out
    assert isinstance(orders, list)
