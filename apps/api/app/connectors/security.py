"""Credential encryption, signature verification, and DNS-pinned HTTPS egress."""
from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import ipaddress
import json
import os
import re
import socket
from urllib.parse import unquote, urlsplit, urlunsplit

import httpx
from cryptography.fernet import Fernet, InvalidToken


class ConnectorError(Exception):
    """Only controlled messages from this exception may enter API responses/runs."""
    def __init__(self, message: str, *, revoked=False, retry_after=60):
        super().__init__(message)
        self.revoked = revoked
        self.retry_after = max(1, min(int(retry_after), 3600))


def cipher() -> Fernet:
    key = os.getenv('CONNECTOR_ENCRYPTION_KEY', '')
    try:
        return Fernet(key.encode('ascii'))
    except (ValueError, UnicodeError) as exc:
        raise ConnectorError('Connector encryption is not configured') from exc


def encrypt(value: dict) -> str:
    return cipher().encrypt(json.dumps(value, separators=(',', ':')).encode()).decode()


def decrypt(value: str | None) -> dict:
    if not value:
        raise ConnectorError('Merchant authorization required', revoked=True)
    try:
        return json.loads(cipher().decrypt(value.encode()))
    except (InvalidToken, ValueError) as exc:
        raise ConnectorError('Connector credentials cannot be decrypted') from exc


def shop_domain(value: str) -> str:
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9-]{0,62}\.myshopify\.com', value):
        raise ConnectorError('Use the exact store.myshopify.com domain')
    return value.lower()


def normalize_store_url(value: str) -> str:
    try:
        p = urlsplit(value)
        if (p.scheme != 'https' or not p.hostname or p.username or p.password
                or p.query or p.fragment or p.port not in (None, 443)):
            raise ValueError()
        host = p.hostname.encode('idna').decode().lower()
        if ':' in host or host.endswith('.') or not re.fullmatch(r'[a-z0-9.-]+', host):
            raise ValueError()
        path = unquote(p.path)
        if '\\' in path or any(x in ('.', '..') for x in path.split('/')) or '%' in path:
            raise ValueError()
        if any(ord(c) < 33 for c in value):
            raise ValueError()
        return urlunsplit(('https', host, p.path.rstrip('/'), '', ''))
    except (ValueError, UnicodeError) as exc:
        raise ConnectorError('Store URL must be a plain HTTPS URL on port 443') from exc


def _public_ip(value: str) -> bool:
    address = ipaddress.ip_address(value.split('%')[0])
    # is_global alone includes multicast on some supported Python versions.
    return (address.is_global and not address.is_multicast and not address.is_reserved
            and not address.is_loopback and not address.is_link_local
            and not address.is_unspecified and not address.is_private
            and not getattr(address, 'ipv4_mapped', None))


async def resolve_public(host: str) -> list[str]:
    if host == 'localhost' or host.endswith(('.localhost', '.local', '.internal')):
        raise ConnectorError('Store host is not publicly routable')
    try:
        answers = await asyncio.wait_for(asyncio.to_thread(
            socket.getaddrinfo, host, 443, type=socket.SOCK_STREAM), timeout=5)
        addresses = sorted({answer[4][0] for answer in answers})
        if not addresses or not all(_public_ip(ip) for ip in addresses):
            raise ConnectorError('Store host is not publicly routable')
        return addresses
    except (socket.gaierror, TimeoutError) as exc:
        raise ConnectorError('Store DNS could not be verified') from exc


def verify_body(raw: bytes, signature: str, secret: str) -> bool:
    expected = base64.b64encode(hmac.digest(secret.encode(), raw, 'sha256')).decode()
    return bool(signature and secret) and hmac.compare_digest(expected, signature)


def verify_oauth(params: list[tuple[str, str]], secret: str) -> bool:
    # Reject ambiguous repeated query parameters before canonicalizing.
    values = dict(params)
    if len(values) != len(params) or not secret:
        return False
    message = '&'.join(f'{key}={value}' for key, value in sorted(values.items()) if key != 'hmac')
    expected = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, values.get('hmac', ''))


class SafeHTTP:
    """Every request resolves and pins its destination; no proxy or redirect bypass."""
    def __init__(self, *, transport=None, test_allow_unresolved_hosts=False, budget=24):
        if test_allow_unresolved_hosts and not isinstance(transport, httpx.MockTransport):
            raise ValueError('DNS bypass requires httpx.MockTransport')
        self.mock_dns = test_allow_unresolved_hosts
        self.transport = transport
        self.budget = budget
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(transport=self.transport, trust_env=False,
                                       timeout=httpx.Timeout(15, connect=5), follow_redirects=False)
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()

    async def validate(self, base: str) -> str:
        base = normalize_store_url(base)
        if not self.mock_dns:
            await resolve_public(urlsplit(base).hostname)
        return base

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        if not self.client:
            raise RuntimeError('Use SafeHTTP as an async context manager')
        if self.budget <= 0:
            raise ConnectorError('Provider request budget reached', retry_after=5)
        self.budget -= 1
        target = httpx.URL(url)
        # Validate origin independently of query parameters generated by our code.
        normalize_store_url(str(target.copy_with(query=None)))
        headers = dict(kwargs.pop('headers', {}))
        extensions = {}
        if not self.mock_dns:
            addresses = await resolve_public(target.host)
            headers['Host'] = target.host
            extensions['sni_hostname'] = target.host
            target = target.copy_with(host=addresses[0])
        try:
            async with self.client.stream(method, target, headers=headers, extensions=extensions, **kwargs) as response:
                chunks, size = [], 0
                async for chunk in response.aiter_bytes():
                    size += len(chunk)
                    if size > 4 * 1024 * 1024:
                        raise ConnectorError('Provider response exceeded the pilot size limit')
                    chunks.append(chunk)
                return httpx.Response(response.status_code, headers=response.headers,
                                      content=b''.join(chunks), request=response.request)
        except httpx.HTTPError as exc:
            # Do not persist HTTP exceptions: their URLs/headers may contain secrets.
            raise ConnectorError('Provider transport failed') from exc


def response_json(response: httpx.Response, *, oauth=False):
    if response.status_code in (401, 403):
        raise ConnectorError('Provider authorization revoked or insufficient', revoked=True)
    if response.status_code == 429:
        try:
            delay = int(response.headers.get('Retry-After', '60'))
        except ValueError:
            delay = 60
        raise ConnectorError('Provider rate limit reached', retry_after=delay)
    if not 200 <= response.status_code < 300:
        raise ConnectorError('Provider rejected the request' if response.status_code < 500 else 'Provider unavailable')
    try:
        return response.json()
    except ValueError as exc:
        raise ConnectorError('Provider returned invalid JSON') from exc
