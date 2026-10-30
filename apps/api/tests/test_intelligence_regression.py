import asyncio
import json

import httpx

from app import llm
from app.auth import Principal, current_principal
from app.intelligence import channel3
from app.main import app


def test_report_persistence_version_conflict_and_tenant_scoped_read(client, consumer):
    created = client.post('/api/merchant/reports', headers={'x-demo-role': 'merchant'},
        json={'merchant_id': 'm1', 'name': 'Inventory board', 'state': {'columns': ['low_stock']}})
    assert created.status_code == 201, created.text
    report = created.json()
    updated = client.put('/api/merchant/reports/' + report['id'], headers={'x-demo-role': 'merchant'},
        json={'version': report['version'], 'state': {'columns': ['stale_stock']}})
    assert updated.status_code == 200 and updated.json()['version'] == report['version'] + 1
    assert client.put('/api/merchant/reports/' + report['id'], headers={'x-demo-role': 'merchant'},
        json={'version': report['version'], 'name': 'stale writer'}).status_code == 409
    app.dependency_overrides[current_principal] = lambda: Principal('tenant-two', 'consumer')
    try:
        denied = client.put('/api/merchant/reports/' + report['id'], json={'name': 'foreign write'})
        assert denied.status_code == 404
    finally:
        app.dependency_overrides.pop(current_principal, None)


def test_fresh_merchant_membership_cannot_cross_tenant_boundaries(client, consumer):
    onboarded = client.post('/api/merchant/onboard', headers=consumer, json={
        'name': 'Fresh Tenant', 'slug': 'fresh-tenant', 'address': '1 Isolated Way',
        'latitude': 1, 'longitude': 1, 'timezone': 'UTC'})
    assert onboarded.status_code == 201, onboarded.text
    new_id = onboarded.json()['id']
    assert client.get('/api/merchant/dashboard?merchant_id=m1', headers=consumer).status_code == 403
    own = client.get('/api/merchant/dashboard?merchant_id=' + new_id, headers=consumer)
    assert own.status_code == 200 and own.json()['merchant_ids'] == [new_id]


def test_remote_inference_requires_consent_and_malformed_or_unknown_claims_are_rejected(monkeypatch):
    monkeypatch.setenv('ENABLE_REMOTE_AI', 'true')
    monkeypatch.setenv('LLM_API_KEY', 'test-key')
    monkeypatch.setenv('LLM_MODEL', 'test-model')
    monkeypatch.setenv('LLM_BASE_URL', 'http://localhost:9999/v1')
    facts = {'products': [{'id': 'p1', 'name': 'Known', 'price_cents': 3999, 'currency': 'USD', 'freshness': 'fresh', 'stock_updated_at': None}],
             'numeric_facts': {'order_count': 1}}
    assert asyncio.run(llm.infer(facts, 'merchant')).status == 'consent_required'

    def response_for(answer):
        return httpx.MockTransport(lambda request: httpx.Response(200, json={'choices': [{'message': {'content': answer}}],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 10}}))

    malformed = asyncio.run(llm.infer(facts, 'consumer', transport=response_for('not json')))
    assert malformed.status == 'invalid_output'
    invented = json.dumps({'intent': 'recommend_products', 'products': [{'product_id': 'unknown', 'price_cents': 1, 'currency': 'USD'}],
        'facts': [], 'actions': ['confirm_stock']})
    rejected = asyncio.run(llm.infer(facts, 'consumer', transport=response_for(invented)))
    assert rejected.status == 'invalid_output'


def test_channel3_current_wire_shape_is_flattened_without_external_network(monkeypatch):
    monkeypatch.setenv('CHANNEL3_API_KEY', 'test-key')
    monkeypatch.setenv('CHANNEL3_BASE_URL', 'https://catalog.example/v1')
    seen = {}

    def handler(request):
        seen['url'], seen['body'] = str(request.url), json.loads(request.content)
        return httpx.Response(200, json={'products': [{'id': 'sku-1', 'title': 'USB Cable',
            'images': [{'url': 'https://images.example/cable.png'}],
            'offers': [{'url': 'https://shop.example/item', 'domain': 'shop.example', 'price': {'price': 12.5, 'currency': 'USD'}},
                       {'url': 'file:///bad', 'domain': 'bad', 'price': {'price': 1.0, 'currency': 'USD'}}]}], 'next_page_token': 'page-2'})

    result = asyncio.run(channel3.search('usb cable', transport=httpx.MockTransport(handler)))
    assert seen == {'url': 'https://catalog.example/v1/search', 'body': {'query': 'usb cable', 'limit': 8}}
    assert result['next_page_token'] == 'page-2'
    assert result['offers'] == [{'product_id': 'sku-1', 'title': 'USB Cable', 'price': 12.5, 'currency': 'USD',
                                 'merchant': 'shop.example', 'image': 'https://images.example/cable.png', 'url': 'https://shop.example/item'}]


def test_merchant_agent_falls_back_to_deterministic_output_without_remote_consent(client, merchant):
    response = client.post('/api/agents/merchant', headers=merchant, json={'message': 'revenue summary', 'merchant_id': 'm1'})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body['ai_status'] in {'disabled', 'consent_required'}
    assert body['mode'] == 'deterministic-tool-baseline'
    assert 'No stock, payment, refund or staff-role changes were made.' in body['reply']
