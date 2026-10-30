"""Assistant history is separated by surface; the server decides the surface from the principal, never the client."""
import httpx
import pytest
from agents.testing import ScriptedModel, assistant_message

from app import llm
from app.assistant import guard, stream as stream_module
from app.intelligence import channel3
from app.online import merge


@pytest.fixture(autouse=True)
def fresh_budget():
    llm.budget._windows.clear()
    yield
    llm.budget._windows.clear()


def mk(client, headers, tid, surface=None, title='t'):
    body = {'id': tid, 'title': title}
    if surface:
        body['surface'] = surface
    r = client.post('/api/assistant/threads', headers=headers, json=body)
    assert r.status_code == 201, r.text
    return r.json()


def titles(client, headers, surface=None):
    r = client.get('/api/assistant/threads' + (f'?surface={surface}' if surface else ''), headers=headers)
    assert r.status_code == 200, r.text
    return {t['id'] for t in r.json()['threads']}


def test_consumer_cannot_create_list_or_read_merchant_threads(client, consumer, merchant):
    mk(client, merchant, 'merch-thread-1', 'merchant')
    mk(client, consumer, 'shop-thread-0001', 'merchant')          # forged: server stores it as shopper
    assert client.get('/api/assistant/threads/shop-thread-0001', headers=consumer).json()['surface'] == 'shopper'
    assert client.get('/api/assistant/threads?surface=merchant', headers=consumer).status_code == 403
    assert titles(client, consumer) == {'shop-thread-0001'}
    assert client.get('/api/assistant/threads/merch-thread-1', headers=consumer).status_code == 404


def test_merchant_sees_only_merchant_threads_by_default(client, merchant):
    mk(client, merchant, 'merch-thread-1', 'merchant')
    mk(client, merchant, 'merch-shopper-1', 'shopper')
    assert titles(client, merchant) == {'merch-thread-1'}
    assert titles(client, merchant, 'merchant') == {'merch-thread-1'}
    assert titles(client, merchant, 'shopper') == {'merch-shopper-1'}
    assert client.get('/api/assistant/threads?surface=bogus', headers=merchant).status_code == 422


def test_surface_cannot_be_forged_through_the_stream(client, consumer, merchant, monkeypatch):
    monkeypatch.setattr(stream_module, 'get_model', lambda: ScriptedModel([[assistant_message('root = Card([h])\nh = CardHeader("ok")\n')]] * 3))
    def send(headers, tid, surface):
        r = client.post('/api/assistant/stream', headers=headers, json={'threadId': tid, 'runId': 'r', 'messages': [{'id': 'm1', 'role': 'user', 'content': 'cheapest charger'}],
                                                                        'forwardedProps': {'surface': surface}})
        assert r.status_code == 200
    send(consumer, 'forged-consumer-1', 'merchant')
    send(merchant, 'real-merchant-0001', 'merchant')
    send(merchant, 'merchant-as-shopper', 'shopper')
    assert titles(client, consumer) == {'forged-consumer-1'}
    assert client.get('/api/assistant/threads/forged-consumer-1', headers=consumer).json()['surface'] == 'shopper'
    assert titles(client, merchant, 'merchant') == {'real-merchant-0001'}
    assert titles(client, merchant, 'shopper') == {'merchant-as-shopper'}


def test_owner_isolation_still_holds(client, consumer, merchant):
    mk(client, consumer, 'shop-thread-0001', 'shopper')
    assert client.get('/api/assistant/threads/shop-thread-0001', headers=merchant).status_code == 404


def tool_names(client, headers, monkeypatch, props):
    model = ScriptedModel([[assistant_message('root = Card([h])\nh = CardHeader("ok")\n')]])
    monkeypatch.setattr(stream_module, 'get_model', lambda: model)
    client.post('/api/assistant/stream', headers=headers, json={'threadId': 'tools-check-01', 'runId': 'r', 'forwardedProps': props,
                                                                'messages': [{'id': 'm1', 'role': 'user', 'content': 'where can I buy a DJI Mavic 4?'}]})
    return {getattr(t, 'name', None) for t in model.calls[0].tools}


@pytest.mark.parametrize('who,props', [('consumer', {}), ('merchant', {'surface': 'merchant', 'merchant_id': 'm1'})])
def test_web_search_and_online_offers_on_both_surfaces(client, consumer, merchant, monkeypatch, who, props):
    headers = consumer if who == 'consumer' else merchant
    names = tool_names(client, headers, monkeypatch, props)
    assert {'web_search', 'online_offers'} <= names
    assert guard.check_tool('web_search', 'merchant', active_merchant_id=None, accessible=set(), is_admin=False) is None
    assert guard.check_tool('online_offers', 'consumer', active_merchant_id=None, accessible=set(), is_admin=False) is None


def test_online_results_are_channel3_only(monkeypatch):
    monkeypatch.setenv('CHANNEL3_API_KEY', 'k')
    raw = {'products': [{'id': 'p1', 'title': '65W GaN Charger', 'images': [{'url': 'https://img.example/a.jpg'}],
                         'offers': [{'url': 'https://shop.example/c', 'domain': 'shop.example', 'price': {'price': 29.9, 'currency': 'USD'}}]}]}

    async def fake(q, page_token=None, *, transport=None):
        return await real(q, page_token, transport=httpx.MockTransport(lambda r: httpx.Response(200, json=raw)))
    real = channel3.search
    import asyncio
    out = asyncio.run(merge.online_combined('65w charger', type('M', (), {'search': staticmethod(fake)})))
    assert set(out['sources']) == {'channel3'}
    assert out['verified_local_stock'] is False and out['online_only'] is True
    assert [o['source'] for o in out['offers']] == ['channel3'] and out['offers'][0]['label'] == 'ONLINE'
    assert 'ebay' not in str(out).lower()
