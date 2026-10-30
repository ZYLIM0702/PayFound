from app import placement
from test_assistant import call, events, results, script, talk
from test_placement import KL, fake_geocoder, fresh_cache  # noqa: F401 - autouse fixture


def test_assistant_search_sees_relocated_stores(client, consumer, monkeypatch):
    """The streamed assistant run must see the same per-viewer store layout as the REST API (Explore)."""
    fake_geocoder(monkeypatch)
    me = {'latitude': 3.15, 'longitude': 101.70}
    rest = client.get('/api/products?q=screwdriver&latitude=3.15&longitude=101.70&radius_km=10', headers={**consumer, **KL}).json()
    assert rest and rest[0]['distance_km'] < 10
    script(monkeypatch, call('search_products', {'query': 'screwdriver'}), talk())
    body = {'threadId': 't1', 'runId': 'r1', 'messages': [{'id': 'm1', 'role': 'user', 'content': 'screwdriver'}], 'forwardedProps': {'location': me}}
    data = list(results(events(client.post('/api/assistant/stream', headers={**consumer, **KL}, json=body))).values())[0]
    assert data['count'] >= 1 and data['nearest_km'] < 10 and data['widened'] == []
