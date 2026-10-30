"""Channel3 v1 wire adapter. Never persist product facts or affiliate URLs."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
from urllib.parse import quote, urlsplit

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .. import llm
from ..auth import Principal, current_principal

router = APIRouter()


class WireModel(BaseModel):
    model_config = ConfigDict(extra='ignore', strict=True)


class Price(WireModel):
    price: float = Field(ge=0, allow_inf_nan=False)
    currency: str = Field(pattern=r'^[A-Z]{3}$')


class Offer(WireModel):
    url: str = Field(max_length=8192)
    domain: str = Field(min_length=1, max_length=250)
    price: Price


class Image(WireModel):
    url: str = Field(max_length=8192)


class OnlineProduct(WireModel):
    id: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=1000)
    images: list[Image] = Field(default_factory=list, max_length=64)
    offers: list[Offer] = Field(default_factory=list, max_length=100)


class SearchPage(WireModel):
    products: list[OnlineProduct] = Field(max_length=30)
    next_page_token: str | None = Field(default=None, max_length=4096)


def safe_url(value: str) -> str | None:
    try:
        parsed = urlsplit(value)
        if (parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password
                or any(ord(c) < 33 for c in value) or '\\' in value):
            return None
        return value
    except ValueError:
        return None


def configured() -> bool:
    return bool(os.getenv('CHANNEL3_API_KEY', '').strip())


def envelope(enabled: bool, offers=None, **extra) -> dict:
    return {'enabled': enabled, 'source': 'Channel3', 'online_only': True,
            'verified_local_stock': False, 'offers': offers or [], **extra}


def _base() -> str:
    # Support the earlier server-only search endpoint setting without guessing wire versions.
    legacy = os.getenv('CHANNEL3_SEARCH_URL', '').strip()
    base = os.getenv('CHANNEL3_BASE_URL', '').strip() or (
        legacy[:-len('/v1/search')] if legacy.endswith('/v1/search') else 'https://api.trychannel3.com')
    base = base.rstrip('/')
    try:
        parsed = urlsplit(base)
        if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
                or parsed.query or parsed.fragment or parsed.path not in {'', '/v1'}):
            raise ValueError()
        if legacy and not legacy.endswith('/v1/search'):
            raise ValueError()
    except ValueError:
        raise HTTPException(503, 'Channel3 endpoint configuration is invalid') from None
    return base if base.endswith('/v1') else base + '/v1'


async def _fetch(method: str, path: str, payload=None, *, transport=None):
    url = _base() + path
    timeout = llm._number('CHANNEL3_TIMEOUT_SECONDS', 12, 0.1, 30)
    try:
        async with asyncio.timeout(timeout):
            async with httpx.AsyncClient(timeout=timeout, transport=transport, follow_redirects=False) as client:
                async with client.stream(method, url, json=payload if method == 'POST' else None,
                                         headers={'x-api-key': os.environ['CHANNEL3_API_KEY'],
                                                  'Content-Type': 'application/json'}) as response:
                    response.raise_for_status()
                    data = bytearray()
                    async for chunk in response.aiter_bytes():
                        data.extend(chunk)
                        if len(data) > 2097152:
                            raise HTTPException(502, 'Channel3 returned an invalid response')
        return json.loads(data)
    except (TimeoutError, httpx.TimeoutException):
        raise HTTPException(504, 'Channel3 request timed out') from None
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status == 404 and method == 'GET':
            raise HTTPException(404, 'Online product is unavailable') from None
        if status in {401, 403}:
            raise HTTPException(503, 'Channel3 account access is unavailable') from None
        if status == 429:
            raise HTTPException(503, 'Channel3 is rate limited; retry later', headers={'Retry-After': '60'}) from None
        raise HTTPException(502, 'Channel3 request failed') from None
    except (httpx.HTTPError, ValueError, KeyError):
        raise HTTPException(502, 'Channel3 returned an invalid response') from None


def flatten(products: list[OnlineProduct]) -> list[dict]:
    results = []
    for product in products:
        image = next((safe_url(i.url) for i in product.images if safe_url(i.url)), None)
        for offer in product.offers:
            url = safe_url(offer.url)
            if not url:
                continue
            results.append({'product_id': product.id, 'title': product.title, 'price': offer.price.price,
                            'currency': offer.price.currency, 'merchant': offer.domain, 'image': image, 'url': url})
            if len(results) >= 30:
                return results
    return results


async def search(q: str, page_token: str | None = None, *, transport=None) -> dict:
    if not configured():
        return envelope(False, status='unconfigured', message='Online catalog is not configured; local stock is not verified.')
    payload = {'query': q, 'limit': 8}
    if page_token:
        payload['page_token'] = page_token
    raw = await _fetch('POST', '/search', payload, transport=transport)
    try:
        page = SearchPage.model_validate(raw)
    except ValidationError:
        raise HTTPException(502, 'Channel3 returned an invalid response') from None
    result = envelope(True, flatten(page.products))
    if page.next_page_token:
        result['next_page_token'] = page.next_page_token
    return result


async def details(product_id: str, *, transport=None) -> dict:
    if not configured():
        return envelope(False, status='unconfigured')
    raw = await _fetch('GET', '/products/' + quote(product_id, safe=''), transport=transport)
    try:
        product = OnlineProduct.model_validate(raw)
        if product.id != product_id:
            raise ValueError()
    except (ValidationError, ValueError):
        raise HTTPException(502, 'Channel3 returned an invalid response') from None
    return envelope(True, flatten([product]), product_id=product.id)


def rate_limit(principal: Principal, kind='online'):
    digest = hashlib.sha256(principal.subject.encode()).hexdigest()
    limit = int(llm._number('CHANNEL3_RATE_LIMIT_PER_MINUTE' if kind == 'online' else 'AGENT_RATE_LIMIT_PER_MINUTE',
                            20, 1, 1000))
    if not llm.budget.allow(kind + ':' + digest, limit):
        raise HTTPException(429, 'Request rate limit exceeded', headers={'Retry-After': '60'})


@router.get('/online/search')
async def online_search(response: Response, q: str = Query(min_length=2, max_length=200),
                        page_token: str | None = Query(default=None, max_length=4096),
                        p: Principal = Depends(current_principal)):
    rate_limit(p)
    response.headers['Cache-Control'] = 'no-store'
    from ..online import merge  # Channel3 only; response keys stay backwards compatible
    return await merge.online_combined(q, sys.modules[__name__], page_token)


@router.get('/online/products/{product_id}')
async def online_product(response: Response, product_id: str = Path(pattern=r'^[a-zA-Z0-9_.-]{1,200}$'),
                         p: Principal = Depends(current_principal)):
    rate_limit(p)
    response.headers['Cache-Control'] = 'no-store'
    return await details(product_id)
