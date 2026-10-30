"""City-level default location from the caller's IP address."""
from __future__ import annotations

import ipaddress
import logging
import os
import time
from collections import OrderedDict

import httpx

log = logging.getLogger('payfound.ipgeo')
TTL, SIZE = 24 * 3600, 500
_cache: 'OrderedDict[str, tuple[float, dict | None]]' = OrderedDict()


def clear_cache():
    _cache.clear()


def client_ip(request):
    """Public IP string, or '' when the caller is loopback/private/unknown (meaning: use the server's own public IP)."""
    raw = request.client.host if request.client else ''
    if os.getenv('TRUST_PROXY_HEADERS', 'false').lower() == 'true':
        forwarded = request.headers.get('x-forwarded-for', '').split(',')[0].strip()
        if forwarded:
            raw = forwarded
    try:
        ip = ipaddress.ip_address(raw)
    except ValueError:
        return ''
    return '' if (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_unspecified) else str(ip)


async def _get(url):
    async with httpx.AsyncClient(timeout=httpx.Timeout(2.5, connect=2.0), follow_redirects=False,
                                 headers={'User-Agent': 'PayFound-local-demo/1.0'}) as client:
        response = await client.get(url)
    if response.status_code != 200:
        raise ValueError(f'http {response.status_code}')
    return response.json()


def _clean(lat, lng, city, country):
    try:
        lat, lng = float(lat), float(lng)
    except (TypeError, ValueError):
        return None
    if not (-85 <= lat <= 85 and -180 <= lng <= 180) or (lat == 0 and lng == 0):
        return None
    return {'latitude': round(lat, 2), 'longitude': round(lng, 2), 'city': str(city or '')[:80], 'country': str(country or '')[:80],
            'source': 'ip'}


async def lookup(ip):
    key = ip or 'self'
    entry = _cache.get(key)
    if entry and entry[0] > time.monotonic():
        _cache.move_to_end(key)
        return entry[1]
    result = None
    suffix = ip + '/' if ip else ''
    for url, parse in ((f'https://ipapi.co/{suffix}json/', lambda d: None if d.get('error') else _clean(
                            d.get('latitude'), d.get('longitude'), d.get('city'), d.get('country_name'))),
                       (f'https://ipwho.is/{ip}', lambda d: _clean(d.get('latitude'), d.get('longitude'), d.get('city'),
                            d.get('country')) if d.get('success', True) else None)):
        try:
            result = parse(await _get(url))
        except (httpx.HTTPError, ValueError, AttributeError):
            result = None
        if result:
            break
    _cache[key] = (time.monotonic() + (TTL if result else 300), result)
    _cache.move_to_end(key)
    while len(_cache) > SIZE:
        _cache.popitem(last=False)
    return result
