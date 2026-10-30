import asyncio
from datetime import datetime, timezone, timedelta
import json
from sqlalchemy import select
from app import commerce, worker
from app.database import SessionLocal
from app.models import Merchant, MerchantLocation, Notification, OutboxJob, Order, ProviderWebhook, Product, utcnow


def test_outbox_notifications_are_idempotent_and_tenant_scoped(client, consumer, merchant):
    response = client.post('/api/orders/reserve', headers=consumer,
        json={'product_id': 'p1', 'idempotency_key': 'notification-purchase'})
    assert response.status_code == 201
    asyncio.run(worker.tick(connectors=False))
    buyer = client.get('/api/notifications', headers=consumer).json()['notifications']
    store = client.get('/api/notifications', headers=merchant).json()['notifications']
    assert len(buyer) == len(store) == 1
    assert buyer[0]['audience'] == 'buyer' and store[0]['audience'] == 'merchant'
    assert client.post('/api/notifications/' + buyer[0]['id'] + '/read', headers=merchant).status_code == 404
    with SessionLocal() as db:
        job = db.scalar(select(OutboxJob).where(OutboxJob.kind == 'domain_event'))
        job.state = 'PENDING'
        db.commit()
    asyncio.run(worker.tick(connectors=False))
    with SessionLocal() as db:
        assert len(list(db.scalars(select(Notification)))) == 2


def test_branch_overnight_uses_previous_day_and_holiday_override(client):
    with SessionLocal() as db:
        merchant = db.get(Merchant, 'm1')
        location = db.get(MerchantLocation, 'loc-m1')
        location.timezone = 'UTC'
        location.hours = json.dumps({'0': [{'start': '22:00', 'end': '02:00'}], '1': []})
        assert commerce.opening(merchant, location, datetime(2026, 10, 20, 1, tzinfo=timezone.utc))
        assert not commerce.opening(merchant, location, datetime(2026, 10, 21, 1, tzinfo=timezone.utc))
        location.special_hours = json.dumps({'2026-10-20': []})
        assert not commerce.opening(merchant, location, datetime(2026, 10, 20, 1, tzinfo=timezone.utc))


def test_manual_catalog_gtin_and_branch_identity(client, merchant):
    body = {'location_id': 'loc-m1', 'name': 'Branded test product', 'sku': 'BRANCH-TEST',
            'price_cents': 1999, 'quantity': 2, 'gtin': '012345678905', 'brand': 'Test brand'}
    made = client.post('/api/merchant/products?merchant_id=m1', headers=merchant, json=body)
    assert made.status_code == 201, made.text
    assert made.json()['gtin'] == body['gtin'] and made.json()['brand'] == 'Test brand'
    assert client.post('/api/merchant/products?merchant_id=m1', headers=merchant,
        json={**body, 'sku': 'BAD-GTIN', 'gtin': '012345678906'}).status_code == 422
    assert client.post('/api/merchant/products?merchant_id=m2', headers=merchant, json=body).status_code == 403


def test_verified_external_reversal_quarantines_handover(client, consumer, merchant):
    made = client.post('/api/orders/reserve', headers=consumer,
        json={'product_id': 'p1', 'idempotency_key': 'reversal-purchase'}).json()
    client.post('/api/orders/' + made['id'] + '/mock-pay', headers=consumer)
    with SessionLocal() as db:
        order = db.get(Order, made['id'])
        order.paypal_capture_id = 'verified-capture'
        db.add(ProviderWebhook(id='verified-reversal', verified=True, event_type='PAYMENT.CAPTURE.REVERSED',
            payload=json.dumps({'resource': {'id': 'verified-capture'}})))
        db.commit()
        asyncio.run(worker.process_webhook(db, 'verified-reversal'))
        assert db.get(Order, order.id).payment_status == 'PROVIDER_REVIEW_REQUIRED'
    assert client.post('/api/orders/' + made['id'] + '/fulfilment', headers=merchant,
        json={'status': 'ACCEPTED'}).status_code == 409


def test_pickup_display_day_is_explicit_across_timezones(client, merchant):
    start = (utcnow() + timedelta(days=2)).replace(hour=2, minute=0, second=0, microsecond=0)
    made = client.post('/api/merchant/pickup-slots', headers=merchant, json={
        'merchant_id': 'm1', 'location_id': 'loc-m1', 'start_at': start.isoformat() + 'Z',
        'end_at': (start + timedelta(hours=1)).isoformat() + 'Z', 'capacity': 2})
    assert made.status_code == 201
    path = '/api/merchants/m1/pickup-slots?date=' + start.date().isoformat()
    assert client.get(path).json() == []  # 02:00 UTC is the previous LA business day.
    assert client.get(path + '&view_timezone=Asia%2FSingapore').json()[0]['id'] == made.json()['id']
    assert client.get(path + '&view_timezone=invalid').status_code == 422


def test_cart_product_lookup_filters_before_pagination(client):
    result = client.get('/api/products?ids=p14&limit=1&radius_km=20040')
    assert result.status_code == 200 and [p['id'] for p in result.json()] == ['p14']
    assert client.get('/api/products?ids=private%2Fpath').status_code == 422


def test_oversized_basket_cannot_overflow_postgres_money_or_acquire_holds(client, consumer):
    with SessionLocal() as db:
        for index in range(3):
            db.add(Product(id=f'expensive-{index}', merchant_id='m1', location_id='loc-m1',
                name='Large-value fixture', sku=f'EXP-{index}', price_cents=100000000,
                quantity=100, synthetic=True))
        db.commit()
    result = client.post('/api/orders/reserve', headers=consumer, json={
        'items': [{'product_id': f'expensive-{index}', 'quantity': 10} for index in range(3)],
        'idempotency_key': 'overflow-purchase'})
    assert result.status_code == 422
    with SessionLocal() as db:
        assert all(db.get(Product, f'expensive-{index}').hold_quantity == 0 for index in range(3))
        assert db.scalar(select(Order).where(Order.idempotency_key == 'overflow-purchase')) is None


def test_keyword_search_matches_specs_across_title_tokens_without_inventing_matches(client):
    found = client.get('/api/products', params={'q': 'USB-C 36W charger'}).json()
    assert [p['id'] for p in found] == ['p1']
    assert client.get('/api/products', params={'q': 'wrench charger'}).json() == []


def test_public_mode_throttles_before_unauthorized_business_writes(client, monkeypatch):
    monkeypatch.setenv('DEMO_MODE', 'false')
    monkeypatch.setenv('PAYFOUND_TESTING', '0')
    monkeypatch.setenv('API_PUBLIC_RATE_LIMIT_PER_MINUTE', '2')
    assert client.get('/api/health').status_code == 200
    body = {'product_id': 'p1', 'idempotency_key': 'unauthorized-rate-limit'}
    assert client.post('/api/orders/reserve', json=body).status_code == 401
    assert client.post('/api/orders/reserve', json=body).status_code == 401
    blocked = client.post('/api/orders/reserve', json=body)
    assert blocked.status_code == 429 and blocked.headers['retry-after'] == '60'
    with SessionLocal() as db:
        assert db.scalar(select(Order).where(Order.idempotency_key == body['idempotency_key'])) is None


def test_calendar_visible_ranges_include_overnight_slots_and_enforce_tenant_scope(client, merchant, consumer):
    start = (utcnow() + timedelta(days=2)).replace(hour=23, minute=0, second=0, microsecond=0)
    slot = client.post('/api/merchant/pickup-slots', headers=merchant, json={
        'merchant_id': 'm1', 'location_id': 'loc-m1', 'start_at': start.isoformat() + 'Z',
        'end_at': (start + timedelta(hours=2)).isoformat() + 'Z', 'capacity': 2}).json()
    params = {'merchant_id': 'm1', 'start_at': (start + timedelta(hours=1)).isoformat() + 'Z',
              'end_at': (start + timedelta(days=7)).isoformat() + 'Z'}
    path = '/api/merchant/pickup-slots'
    result = client.get(path, headers=merchant, params=params)
    assert result.status_code == 200 and result.json()['slots'][0]['id'] == slot['id']
    assert client.get(path, headers=consumer, params=params).status_code == 403
    assert client.get(path, headers=merchant, params={**params, 'merchant_id': 'm2'}).status_code == 403


def test_environment_layout_supports_shallow_container_service_root():
    from pathlib import Path
    from app.config import environment_roots
    api, app, workspace = environment_roots('/app/app/config.py')
    assert api == app == Path('/app') and workspace == Path('/')
    api, app, workspace = environment_roots('/workspace/PayFound/apps/api/app/config.py')
    assert api == Path('/workspace/PayFound/apps/api')
    assert app == Path('/workspace/PayFound') and workspace == Path('/workspace')


def test_demo_role_impersonation_rejects_nonloopback_host_headers(client):
    response = client.get('/api/admin/overview', headers={'host': 'untrusted.example', 'x-demo-role': 'admin'})
    assert response.status_code == 403
