import json
import pytest

from app.database import SessionLocal, engine
from app.demo_catalogue import seed_expanded_demo
from app.models import Product
from app import routing


def test_product_detail_and_invalid_origins(client):
    result = client.get('/api/products/p1')
    assert result.status_code == 200
    product = result.json()
    assert product['name'] == 'USB-C 36W GaN Charger'
    assert product['image_url'] == '/images/products/p1.webp'
    assert product['merchant']['id'] == 'm1' and len(product['offers']) == 1
    assert client.get('/api/products/missing').status_code == 404
    assert client.get('/api/products/p1?latitude=37').status_code == 422
    with SessionLocal() as db:
        db.get(Product, 'p1').active = False; db.commit()
    assert client.get('/api/products/p1').status_code == 404


def test_expanded_catalogue_identity_comparison_and_pagination(client):
    if engine.dialect.name != 'sqlite':
        pytest.skip('Expanded fixture is deliberately local-only')
    with SessionLocal() as db:
        original = db.get(Product, 'p1')
        before = (original.quantity, original.hold_quantity, original.price_cents, original.stock_updated_at)
        seed_expanded_demo(db, force=True); db.commit()
        seed_expanded_demo(db, force=True); db.commit()
        db.refresh(original)
        assert before == (original.quantity, original.hold_quantity, original.price_cents, original.stock_updated_at)
    summary = client.get('/api/catalogue/summary').json()
    from app.demo_catalogue_grocery import grocery_data
    grocery = grocery_data()['products']  # the grocery / fresh-food stores are seeded by the same call
    assert summary['distinct_products'] == 200 + len({p['key'] for p in grocery})
    assert summary['offers'] == 244 + len(grocery) and summary['stores'] == 13 + len(grocery_data()['merchants'])
    detail = client.get('/api/products/p1?latitude=37.7786&longitude=-122.414').json()
    assert len(detail['offers']) == 2
    assert len({p['merchant_id'] for p in detail['offers']}) == 2
    assert detail['offers'][0]['price_cents'] < detail['price_cents']
    assert all(p['gtin'] is None for p in detail['offers'])
    first = client.get('/api/products?limit=24&offset=0').json()
    second = client.get('/api/products?limit=24&offset=24').json()
    assert len(first) == len(second) == 24 and not ({p['id'] for p in first} & {p['id'] for p in second})
    with SessionLocal() as db:
        db.add(Product(id='unrelated-lookalike', merchant_id='m2', location_id='loc-m2', name=detail['name'], sku='UNRELATED',
            price_cents=999, quantity=2, synthetic=True, image_url=detail['image_url']))
        db.commit()
    assert len(client.get('/api/products/p1').json()['offers']) == 2  # Identity, not fuzzy title/photo matching.


def test_google_route_traffic_wire_and_no_server_cache(client, monkeypatch):
    monkeypatch.setenv('GOOGLE_ROUTES_API_KEY', 'server-only-route-key')
    calls = []
    async def fake(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return {'routes': [{'distanceMeters': 1552, 'duration': '300s', 'staticDuration': '240s',
            'polyline': {'encodedPolyline': 'ipkcFfichVnP@j@BLoFVwM{E?'},
            'legs': [{'steps': [{'navigationInstruction': {'instructions': 'Turn right onto Market Street'}, 'distanceMeters': 500}]}]}]}
    monkeypatch.setattr(routing, 'fetch_json', fake)
    body = {'product_id': 'p1', 'origin_latitude': 37.7786, 'origin_longitude': -122.414}
    for _ in range(2):
        response = client.post('/api/routing/route', json=body)
        assert response.status_code == 200
        data = response.json()
        assert data['traffic_aware'] and data['provider'] == 'google' and data['traffic_delay_seconds'] == 60
        assert data['distance_m'] == 1552 and len(data['coordinates']) > 2
        assert data['destination']['latitude'] == 37.7744
        assert response.headers['cache-control'] == 'no-store'
        assert 'server-only-route-key' not in response.text
    assert len(calls) == 2
    method, url, options = calls[0]
    assert method == 'POST' and url == 'https://routes.googleapis.com/directions/v2:computeRoutes'
    assert options['headers']['X-Goog-Api-Key'] == 'server-only-route-key'
    assert options['json']['routingPreference'] == 'TRAFFIC_AWARE'
    assert options['json']['destination']['location']['latLng']['latitude'] == 37.7744
    assert client.post('/api/routing/route', json={**body, 'origin_latitude': 91}).status_code == 422
    assert client.post('/api/routing/route', json={**body, 'product_id': 'missing'}).status_code == 404


def test_nontraffic_route_never_claims_live_data(client, monkeypatch):
    for key in ('GOOGLE_ROUTES_API_KEY', 'GOOGLE_MAPS_API_KEY', 'GOOGLE_MAP_API_KEY'):
        monkeypatch.delenv(key, raising=False)
    async def fake(method, url, **kwargs):
        assert 'router.project-osrm.org/route/v1/driving/' in url
        return {'code': 'Ok', 'routes': [{'distance': 1500, 'duration': 400,
            'geometry': {'coordinates': [[-122.414, 37.7786], [-122.418, 37.776], [-122.4212, 37.7744]]}, 'legs': []}]}
    monkeypatch.setattr(routing, 'fetch_json', fake)
    response = client.post('/api/routing/route', json={'product_id':'p1','origin_latitude':37.7786,'origin_longitude':-122.414})
    assert response.status_code == 200 and response.json()['traffic_aware'] is False
    assert response.json()['traffic_delay_seconds'] is None
    assert 'without live traffic' in response.json()['estimate_label']


def test_no_route_and_key_exposure_boundaries(client, monkeypatch):
    monkeypatch.setenv('GOOGLE_ROUTES_API_KEY', 'private-server-key')
    for key in ('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAP_API_KEY', 'GOOGLE_MAPS_BROWSER_KEY'):
        monkeypatch.delenv(key, raising=False)
    config = client.get('/api/config').json()
    assert config['routing']['traffic_configured'] and not config['routing']['google_maps_browser_key']
    assert 'private-server-key' not in json.dumps(config)
    async def no_route(*args, **kwargs): return {'routes': []}
    monkeypatch.setattr(routing, 'fetch_json', no_route)
    assert client.post('/api/routing/route', json={'product_id':'p1','origin_latitude':0,'origin_longitude':0}).status_code == 404
