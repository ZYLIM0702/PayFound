import asyncio
import json

import pytest
from sqlalchemy import select
from agents.testing import ScriptedModel, assistant_message, function_call

from app import placement, routing
from app.assistant import stream as stream_module
from app.database import SessionLocal
from app.models import Merchant, MerchantLocation

KL = {'x-pf-anchor': '3.15,101.70', 'x-pf-timezone': 'Asia/Kuala_Lumpur'}


@pytest.fixture(autouse=True)
def fresh_cache(monkeypatch):
    placement.clear_cache()
    monkeypatch.setattr(placement, 'MAX_NEW_CELLS_PER_HOUR', 1000)
    yield
    placement.clear_cache()


def fake_geocoder(monkeypatch, is_sea=lambda lat, lng: False, calls=None):
    async def reverse(lat, lng):
        if calls is not None:
            calls.append((lat, lng))
        if is_sea(lat, lng):
            return [], 'mock'
        return [placement.Hit(lat, lng, f'{round(lat * 1e4)} Jalan {round(lng * 1e4)}, Testville', 4, True)], 'mock'
    monkeypatch.setattr(placement, 'reverse_geocode', reverse)


def stores(client, headers):
    return {m['id']: m for m in client.get('/api/merchants', headers=headers).json()}


def test_original_without_header(client, monkeypatch):
    fake_geocoder(monkeypatch)
    m = stores(client, {})['m1']
    assert (m['latitude'], m['longitude']) == (37.7744, -122.4212) and 'San Francisco' in m['address']
    state = client.get('/api/demo/placement').json()
    assert state['mode'] == 'original' and state['reason'] == 'no_anchor'


def test_relocated_stores_timezone_and_state(client, monkeypatch):
    fake_geocoder(monkeypatch)
    data = stores(client, KL)
    assert set(data) == {'m1', 'm2', 'm3', 'm4'}
    for m in data.values():
        assert placement.haversine_m((3.15, 101.70), (m['latitude'], m['longitude'])) < 6000
        assert 'Testville' in m['address'] and 'San Francisco' not in m['address']
        assert m['timezone'] == 'Asia/Kuala_Lumpur' and m['locations'][0]['timezone'] == 'Asia/Kuala_Lumpur'
    state = client.get('/api/demo/placement', headers=KL).json()
    assert state['mode'] == 'relocated' and state['cell'] == {'latitude': 3.16, 'longitude': 101.7}
    # No timezone header: stored timezone is kept.
    assert stores(client, {'x-pf-anchor': '3.15,101.70'})['m1']['timezone'] == 'America/Los_Angeles'


def test_deterministic(client, monkeypatch):
    fake_geocoder(monkeypatch)
    first = {k: (v['latitude'], v['longitude']) for k, v in stores(client, KL).items()}
    placement.clear_cache()
    second = {k: (v['latitude'], v['longitude']) for k, v in stores(client, KL).items()}
    assert first == second
    cell = placement.snap((3.15, 101.70))
    assert placement.candidate(placement.DEMO_BY_ID['m1'], cell, 0) == placement.candidate(placement.DEMO_BY_ID['m1'], cell, 0)


def test_sea_candidates_rejected_and_retried(client, monkeypatch):
    calls = []
    # Everything west of the cell centre is sea.
    fake_geocoder(monkeypatch, lambda lat, lng: lng < 101.70, calls)
    data = stores(client, KL)
    placed = [m for m in data.values() if m['longitude'] >= 101.70 and abs(m['latitude'] - 3.16) < 0.1]
    assert placed, 'at least some stores are placed on land'
    for m in data.values():
        if 'Testville' in m['address']:
            assert m['longitude'] >= 101.70
    assert len(calls) > 4


def test_duplicate_addresses_avoided(client, monkeypatch):
    async def reverse(lat, lng):
        return [placement.Hit(lat, lng, '1 Same Street, Dup', 4, True)], 'mock'
    monkeypatch.setattr(placement, 'reverse_geocode', reverse)
    layout = asyncio.run(placement.compute_layout(placement.snap((3.15, 101.70))))
    # Every candidate has the same address, so only one store can claim it and the rest fall back.
    assert layout.placed == 1
    assert layout.mode == 'original'


def test_distinct_addresses_and_separation(client, monkeypatch):
    fake_geocoder(monkeypatch)
    layout = asyncio.run(placement.compute_layout(placement.snap((51.51, -0.13))))
    spots = list(layout.stores.values())
    assert layout.mode == 'relocated' and len({s.address for s in spots}) == len(spots)


def test_fallback_to_original_when_too_few(client, monkeypatch):
    fake_geocoder(monkeypatch, lambda lat, lng: True)
    data = stores(client, {'x-pf-anchor': '3.05,100.25'})
    assert data['m1']['latitude'] == 37.7744 and 'San Francisco' in data['m1']['address']
    state = client.get('/api/demo/placement', headers={'x-pf-anchor': '3.05,100.25'}).json()
    assert state['mode'] == 'original' and state['reason'] == 'not_enough_land_nearby'
    assert state['default_origin'] == [37.7786, -122.414]


def test_geocoder_down_falls_back(client, monkeypatch):
    async def boom(lat, lng):
        raise placement.ProviderError('down')
    monkeypatch.setattr(placement, 'reverse_geocode', boom)
    assert client.get('/api/demo/placement', headers=KL).json()['reason'] == 'geocoder_unavailable'


def test_slow_cell_serves_original_then_relocates(client, monkeypatch):
    async def slow(lat, lng):
        await asyncio.sleep(0.3)
        return [placement.Hit(lat, lng, f'{lat},{lng} Road', 4, True)], 'mock'
    monkeypatch.setattr(placement, 'reverse_geocode', slow)
    monkeypatch.setenv('PF_PLACEMENT_WAIT_S', '0.01')
    assert stores(client, KL)['m1']['latitude'] == 37.7744
    import time; time.sleep(0.3 * len(placement.DEMO_STORES) / 6 + 1.5)  # 6 concurrent lookups of 0.3 s each
    assert abs(stores(client, KL)['m1']['latitude'] - 3.16) < 0.1


def test_non_demo_merchants_never_move(client, monkeypatch, merchant):
    fake_geocoder(monkeypatch)
    body = {'name': 'Real Shop', 'slug': 'real-shop', 'category': 'Retail', 'address': '1 Real St', 'latitude': 37.7744,
            'longitude': -122.4212, 'timezone': 'America/Los_Angeles'}
    made = client.post('/api/merchant/onboard', headers={**KL, 'x-demo-role': 'merchant'}, json=body)
    assert made.status_code == 201, made.text
    real = stores(client, KL)[made.json()['id']]
    assert (real['latitude'], real['longitude'], real['address']) == (37.7744, -122.4212, '1 Real St')
    assert real['timezone'] == 'America/Los_Angeles'
    # A demo-looking id with a different slug is not treated as a demo store either.
    with SessionLocal() as db:
        db.add(Merchant(id='m1x', slug='northside-electronics-x', name='X', latitude=37.7744, longitude=-122.4212))
        db.commit()
    assert stores(client, KL)['m1x']['latitude'] == 37.7744


def test_overlay_never_persisted(client, monkeypatch, merchant, consumer):
    fake_geocoder(monkeypatch)
    shown = stores(client, KL)['m1']
    patched = client.patch('/api/merchant/profile', headers={**KL, **merchant},
        json={'phone': '+60 3 1234', 'latitude': shown['latitude'], 'longitude': shown['longitude'], 'address': shown['address']})
    assert patched.status_code == 200, patched.text
    assert patched.json()['phone'] == '+60 3 1234'
    loc = client.patch('/api/merchant/locations/loc-m1', headers={**KL, **merchant},
        json={'latitude': shown['latitude'], 'longitude': shown['longitude'], 'phone': '1'})
    assert loc.status_code == 200, loc.text
    res = client.post('/api/orders/reserve', headers={**KL, **consumer}, json={'product_id': 'p1', 'quantity': 1, 'idempotency_key': 'reserve-key-1'})
    assert res.status_code in (200, 201), res.text
    with SessionLocal() as db:
        m, l = db.get(Merchant, 'm1'), db.get(MerchantLocation, 'loc-m1')
        assert (m.latitude, m.longitude) == (37.7744, -122.4212) and 'San Francisco' in m.address and m.phone == '+60 3 1234'
        assert (l.latitude, l.longitude) == (37.7744, -122.4212) and l.timezone == 'America/Los_Angeles'
        raw = db.execute(__import__('sqlalchemy').text("select latitude, address from merchants where id='m1'")).one()
        assert raw[0] == 37.7744 and 'San Francisco' in raw[1]


def test_products_default_origin_radius_and_sort(client, monkeypatch):
    fake_geocoder(monkeypatch)
    rows = client.get('/api/products?limit=50', headers=KL).json()
    assert rows and all(r['distance_km'] < 8 for r in rows)
    assert rows == sorted(rows, key=lambda r: (not r['in_stock'], r['distance_km'], r['price_cents'], r['id']))
    assert all('Testville' in r['merchant_address'] for r in rows)
    tight = client.get('/api/products?radius_km=0.5&latitude=3.16&longitude=101.70', headers=KL).json()
    assert len(tight) < len(rows) and all(r['distance_km'] <= 0.5 for r in tight)
    # explicit origin wins over the anchor
    far = client.get('/api/products?latitude=37.7786&longitude=-122.414&radius_km=50', headers=KL).json()
    assert far == []
    assert client.get('/api/products?radius_km=5').json()


def test_route_destination_relocated(client, monkeypatch):
    fake_geocoder(monkeypatch)
    seen = {}
    async def calc(origin, destination):
        seen['dest'] = destination
        return {'provider': 'osrm', 'attribution': '', 'distance_m': 1, 'duration_seconds': 1, 'static_duration_seconds': 1,
                'traffic_aware': False, 'traffic_delay_seconds': None, 'coordinates': [[0, 0], [1, 1]], 'steps': [],
                'fetched_at': 'x', 'arrival_at': 'x', 'estimate_label': 'x'}
    monkeypatch.setattr(routing, 'calculate', calc)
    data = client.post('/api/routing/route', headers=KL, json={'product_id': 'p1', 'origin_latitude': 3.15, 'origin_longitude': 101.7}).json()
    assert abs(data['destination']['latitude'] - 3.16) < 0.1 and seen['dest'] == (data['destination']['latitude'], data['destination']['longitude'])
    assert 'Testville' in data['destination']['address']


@pytest.mark.parametrize('value', ['', 'abc', '91,0', '0,181', 'nan,1', '1,2,3', '1' * 200, '3.15;101.7', '90,0', '-86,0'])
def test_bad_anchor_ignored(client, monkeypatch, value):
    fake_geocoder(monkeypatch)
    r = client.get('/api/merchants', headers={'x-pf-anchor': value, 'x-pf-timezone': 'Not/AZone'})
    assert r.status_code == 200 and r.json()[0]['latitude'] > 30


def test_parsers():
    assert placement.parse_anchor('3.14159,101.6953') == (3.14, 101.7)
    assert placement.parse_timezone('Europe/London') == 'Europe/London'
    assert placement.parse_timezone('Mars/Base') is None and placement.parse_timezone('x' * 100) is None
    assert placement.parse_timezone('../etc/passwd') is None


def test_assistant_tools_see_relocated_stores(client, consumer, monkeypatch):
    fake_geocoder(monkeypatch)
    async def calc(origin, destination):
        calc.dest = destination
        return {'provider': 'osrm', 'attribution': '', 'distance_m': 1500, 'duration_seconds': 300, 'static_duration_seconds': 300,
                'traffic_aware': False, 'traffic_delay_seconds': None, 'coordinates': [], 'steps': [], 'fetched_at': 'x',
                'arrival_at': 'x', 'estimate_label': 'x'}
    monkeypatch.setattr(routing, 'calculate', calc)
    model = ScriptedModel([[function_call('search_products', {'query': 'charger'}, call_id='c1')],
                           [function_call('get_route', {'product_id': 'p1'}, call_id='c2')],
                           [assistant_message('root = Card([h1])\nh1 = CardHeader("x")\n')]])
    monkeypatch.setattr(stream_module, 'get_model', lambda: model)
    body = {'threadId': 't', 'runId': 'r', 'messages': [{'id': 'm', 'role': 'user', 'content': 'charger'}],
            'forwardedProps': {'location': {'latitude': 3.15, 'longitude': 101.7}}}
    response = client.post('/api/assistant/stream', headers={**KL, **consumer}, json=body)
    evs = [json.loads(c[6:]) for c in response.text.split('\n\n') if c.strip()]
    out = {e['toolCallId']: json.loads(e['content']) for e in evs if e['type'] == 'TOOL_CALL_RESULT'}
    item = out['c1']['products'][0]
    assert 'Testville' in item['store']['address'] and abs(item['latitude'] - 3.16) < 0.1 and item['distance_km'] < 8
    assert abs(calc.dest[0] - 3.16) < 0.1 and out['c2']['store']


def _g(address, types, kind='ROOFTOP'):
    return placement._google_hit({'formatted_address': address, 'types': types,
                                  'geometry': {'location': {'lat': 3.1, 'lng': 101.7}, 'location_type': kind}})


def test_google_plus_codes_and_pois_rejected():
    assert _g('5PC3+PM Kelab Perubatan Hospital Besar, 50586 Kuala Lumpur', ['street_address']) is None
    assert _g('5PC3+PM, Kuala Lumpur', ['plus_code']) is None
    assert _g('Istana Negara, Jalan Duta, 50500 Kuala Lumpur', ['premise']) is None
    for t in ('transit_station', 'bus_station', 'train_station', 'hospital', 'place_of_worship', 'school', 'university', 'airport',
              'local_government_office', 'embassy'):
        assert _g('12 Jalan Test, KL', ['street_address', t]) is None, t
    assert _g('Klang Bus Station, Jalan Test, KL', ['premise']) is None
    assert _g('Sri Building, Jalan Bukit, KL', ['premise']) is None


def test_google_good_results_ranked_and_cleaned():
    street = _g('22, Medan Pasar, 50050 Kuala Lumpur', ['street_address'])
    assert street and street.precise and street.address.startswith('22,')
    premise = _g('Menara X, 8 Jalan Ampang, 50450 Kuala Lumpur', ['premise', 'establishment'])
    assert premise and premise.address == '8 Jalan Ampang, 50450 Kuala Lumpur'
    route = _g('Jalan Ampang, 50450 Kuala Lumpur', ['route'], 'GEOMETRIC_CENTER')
    assert route and not route.precise and route.rank < street.rank
    assert placement.choose((3.1, 101.7), [route, street]) is street


def test_park_and_water_points_rejected():
    park = [{'types': ['route'], 'formatted_address': 'Serpentine Rd, London W2 2UH, UK'},
            {'types': ['park', 'point_of_interest', 'establishment'], 'formatted_address': 'Hyde Park, London'}]
    assert placement.point_is_land_like(park) is False
    assert placement.point_is_land_like([{'types': ['natural_feature'], 'formatted_address': 'Tasik Titiwangsa'}]) is False
    assert placement.point_is_land_like([{'types': ['route'], 'formatted_address': 'Lake Road, Somewhere'}]) is False
    assert placement.point_is_land_like([{'types': ['street_address'], 'formatted_address': '12 Berners St, London'},
                                         {'types': ['neighborhood'], 'formatted_address': 'Fitzrovia, London'}]) is True


def test_route_inside_park_retried_with_shrunk_candidate(client, monkeypatch):
    fake_geocoder(monkeypatch)
    cell = placement.snap((51.51, -0.13))
    first = placement.candidate(placement.DEMO_BY_ID['m1'], cell, 0)
    async def verify(lat, lng):
        return placement.haversine_m((lat, lng), first) > 400  # everything near m1's first candidate is "inside a park"
    monkeypatch.setattr(placement, 'verify_point', verify)
    layout = asyncio.run(placement.compute_layout(cell))
    spot = layout.stores['m1']
    assert placement.haversine_m((spot.lat, spot.lng), first) > 400
    assert layout.mode == 'relocated'


def test_route_only_hits_used_only_as_last_resort(monkeypatch):
    # Roads (e.g. paths inside parks) are rejected while real street addresses exist nearby...
    async def mixed(lat, lng):
        return [placement.Hit(lat, lng, f'Park Path {lat}', 5, False)] + (
            [placement.Hit(lat, lng, f'{lat} Real St', 4, True)] if lat > 0 else []), 'mock'
    monkeypatch.setattr(placement, 'reverse_geocode', mixed)
    layout = asyncio.run(placement.compute_layout(placement.snap((51.51, -0.13))))
    assert layout.mode == 'relocated' and all('Real St' in p.address for p in layout.stores.values())
    # ...and accepted only when too few addresses exist at all.
    async def roads_only(lat, lng):
        return [placement.Hit(lat, lng, f'Road {round(lat, 4)} {round(lng, 4)}', 3, False)], 'mock'
    monkeypatch.setattr(placement, 'reverse_geocode', roads_only)
    layout = asyncio.run(placement.compute_layout(placement.snap((51.51, -0.13))))
    assert layout.mode == 'relocated' and layout.placed == len(placement.DEMO_STORES)


def test_coastal_anchor_widens_search_to_find_land(monkeypatch):
    calls = []
    fake_geocoder(monkeypatch, lambda lat, lng: lng < 101.82, calls)  # land starts ~13 km east of the anchor
    layout = asyncio.run(placement.compute_layout(placement.snap((3.15, 101.70))))
    assert layout.mode == 'relocated' and layout.placed >= placement.MIN_PRECISE
    assert all(p.lng >= 101.82 - 0.01 for p in layout.stores.values())
    assert max(placement.haversine_m((3.16, 101.70), (p.lat, p.lng)) for p in layout.stores.values()) < 26000


def test_open_sea_skips_retries_and_falls_back(monkeypatch):
    calls = []
    fake_geocoder(monkeypatch, lambda lat, lng: True, calls)
    layout = asyncio.run(placement.compute_layout(placement.snap((3.05, 100.25))))
    assert layout.mode == 'original' and layout.reason == 'not_enough_land_nearby'
    assert len(calls) <= len(placement.DEMO_STORES) + 40  # one round plus the wide probes; no retry rounds in open water


def test_placement_header_pending_then_relocated(client, monkeypatch):
    async def slow(lat, lng):
        await asyncio.sleep(0.2)
        return [placement.Hit(lat, lng, f'{lat},{lng} Road', 4, True)], 'mock'
    monkeypatch.setattr(placement, 'reverse_geocode', slow)
    monkeypatch.setenv('PF_PLACEMENT_WAIT_S', '0.01')
    first = client.get('/api/merchants', headers=KL)
    assert first.headers['x-pf-placement'] == 'pending' and first.headers['x-pf-cell'] == '3.16,101.70'
    # The placement endpoint waits for the whole compute budget and reports the final state.
    state = client.get('/api/demo/placement', headers=KL)
    assert state.json()['mode'] == 'relocated' and state.headers['x-pf-placement'] == 'relocated'
    assert client.get('/api/merchants', headers=KL).headers['x-pf-placement'] == 'relocated'
    assert 'x-pf-placement' not in client.get('/api/merchants').headers


def test_ip_anchor_warms_cell_and_reset_endpoint(client, monkeypatch):
    from app import ipgeo
    ipgeo.clear_cache()
    fake_geocoder(monkeypatch)
    async def get(url):
        return {'latitude': 4.5975, 'longitude': 101.0901, 'city': 'Ipoh', 'country_name': 'Malaysia'}
    monkeypatch.setattr(ipgeo, '_get', get)
    assert client.get('/api/demo/ip-anchor').json()['city'] == 'Ipoh'
    import time; time.sleep(0.5)
    assert placement._cached(placement.snap((4.6, 101.09))) is not None
    assert client.post('/api/demo/placement/reset').json() == {'ok': True}
    assert placement._cached(placement.snap((4.6, 101.09))) is None
    ipgeo.clear_cache()
