import pytest

from app import ipgeo


@pytest.fixture(autouse=True)
def fresh():
    ipgeo.clear_cache()
    yield
    ipgeo.clear_cache()


def provider(monkeypatch, responses):
    urls = []
    async def get(url):
        urls.append(url)
        value = responses.get(url.split('/')[2], None)
        if isinstance(value, Exception):
            raise value
        return value
    monkeypatch.setattr(ipgeo, '_get', get)
    return urls


GOOD = {'latitude': 5.41641, 'longitude': 100.33271, 'city': 'George Town', 'country_name': 'Malaysia'}


def test_private_ip_asks_provider_about_server_itself(client, monkeypatch):
    urls = provider(monkeypatch, {'ipapi.co': GOOD})
    r = client.get('/api/demo/ip-anchor')
    assert r.status_code == 200
    assert r.json() == {'latitude': 5.42, 'longitude': 100.33, 'city': 'George Town', 'country': 'Malaysia', 'source': 'ip'}
    assert urls == ['https://ipapi.co/json/']
    client.get('/api/demo/ip-anchor')
    assert len(urls) == 1


def test_forwarded_for_only_when_trusted(client, monkeypatch):
    urls = provider(monkeypatch, {'ipapi.co': GOOD})
    client.get('/api/demo/ip-anchor', headers={'x-forwarded-for': '8.8.4.4, 10.0.0.1'})
    assert urls == ['https://ipapi.co/json/']
    ipgeo.clear_cache()
    monkeypatch.setenv('TRUST_PROXY_HEADERS', 'true')
    client.get('/api/demo/ip-anchor', headers={'x-forwarded-for': '8.8.4.4, 10.0.0.1'})
    assert urls[-1] == 'https://ipapi.co/8.8.4.4/json/'
    ipgeo.clear_cache()
    client.get('/api/demo/ip-anchor', headers={'x-forwarded-for': 'garbage'})
    assert urls[-1] == 'https://ipapi.co/json/'


def test_fallback_provider_and_failure(client, monkeypatch):
    provider(monkeypatch, {'ipapi.co': ValueError('429'), 'ipwho.is': {'success': True, 'latitude': 51.5, 'longitude': -0.12, 'city': 'London', 'country': 'UK'}})
    assert client.get('/api/demo/ip-anchor').json()['city'] == 'London'
    ipgeo.clear_cache()
    provider(monkeypatch, {'ipapi.co': {'error': True}, 'ipwho.is': {'success': False}})
    assert client.get('/api/demo/ip-anchor').status_code == 204
    ipgeo.clear_cache()
    provider(monkeypatch, {'ipapi.co': {'latitude': 0, 'longitude': 0}, 'ipwho.is': ValueError('x')})
    assert client.get('/api/demo/ip-anchor').status_code == 204


def test_client_ip_classification():
    class R:
        def __init__(self, host): self.client = type('C', (), {'host': host})(); self.headers = {}
    assert ipgeo.client_ip(R('127.0.0.1')) == '' and ipgeo.client_ip(R('192.168.1.5')) == '' and ipgeo.client_ip(R('testclient')) == ''
    assert ipgeo.client_ip(R('8.8.8.8')) == '8.8.8.8'
