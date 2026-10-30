from urllib.parse import parse_qs
import httpx
from app import main
from app.auth import Principal, current_principal


def test_server_invitation_uses_provider_redirect_query_and_requires_recipient_acceptance(client, monkeypatch):
    monkeypatch.setenv('DEMO_MODE', 'false')
    monkeypatch.setenv('SUPABASE_PROJECT_URL', 'https://auth-test.example')
    monkeypatch.setenv('SUPABASE_SECRET_KEY', 'server-test-key')
    monkeypatch.setenv('PUBLIC_WEB_URL', 'https://payfound.example')
    monkeypatch.setitem(main.app.dependency_overrides, current_principal,
        lambda: Principal('demo-merchant', 'merchant', 'm1'))
    original = httpx.AsyncClient
    calls = []

    def provider(request):
        calls.append(request)
        assert request.url.path == '/auth/v1/invite'
        assert parse_qs(request.url.query.decode())['redirect_to'] == ['https://payfound.example/auth/callback?next=%2Forders']
        assert request.headers['apikey'] == 'server-test-key'
        return httpx.Response(200, json={'id': 'invited-subject'})

    monkeypatch.setattr(main.httpx, 'AsyncClient', lambda **kwargs: original(**kwargs, transport=httpx.MockTransport(provider)))
    made = client.post('/api/merchant/staff?merchant_id=m1', json={'email': 'staff@example.test', 'role': 'staff'})
    assert made.status_code == 201 and made.json()['delivery'] == 'supabase_email'
    assert made.json()['status'] == 'PENDING' and len(calls) == 1
    invitation = made.json()['id']
    monkeypatch.setitem(main.app.dependency_overrides, current_principal,
        lambda: Principal('invited-subject', 'consumer'))
    assert client.get('/api/me').json()['merchant_ids'] == []
    accepted = client.post(f'/api/merchant/staff/invitations/{invitation}/accept')
    assert accepted.status_code == 200 and accepted.json()['role'] == 'staff'
    assert client.get('/api/me').json()['merchant_ids'] == ['m1']
