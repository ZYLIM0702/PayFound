"""Optional access key in front of the whole API, so a shared deployment cannot run up AI, maps or search bills.

Set SITE_ACCESS_KEY (apps/api/.env) to turn it on. POST /api/access exchanges the key for a signed token that the web
app sends as x-pf-access on every call. The token never expires; changing the key signs every browser out. Unset,
nothing changes.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import threading
import time

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

HEADER = 'x-pf-access'
# Reachable without the key: health checks, the key exchange itself, and calls from PayPal and POS systems,
# which carry their own signatures.
OPEN_PATHS = ('/api/health', '/api/ready', '/api/access', '/api/paypal/webhook')
_POS_PUSH = re.compile(r'^/api/pos-plugin/[^/]+/events$')
MAX_FAILS, FAIL_WINDOW_S = 8, 15 * 60

router = APIRouter()
_fails: dict[str, list[float]] = {}
_lock = threading.Lock()


def _key() -> str:
    return os.getenv('SITE_ACCESS_KEY', '').strip()


def required() -> bool:
    return bool(_key())


def _token_for(key: str) -> str:
    # derived from the key, never the key itself, so the browser never stores the key
    secret = hashlib.sha256(b'payfound-site-access:' + key.encode()).digest()
    return 'v1.' + hmac.new(secret, b'v1', hashlib.sha256).hexdigest()


def issue() -> str:
    return _token_for(_key())


def valid(token: str | None) -> bool:
    key = _key()
    return bool(key and token) and hmac.compare_digest(_token_for(key), token)


def is_open(path: str) -> bool:
    return not path.startswith('/api/') or path in OPEN_PATHS or bool(_POS_PUSH.match(path))


def _caller(request: Request) -> str:
    # hashed, never stored raw (same rule as limits.py)
    return hashlib.sha256((request.client.host if request.client else 'unknown').encode()).hexdigest()


def _recent_fails(caller: str, now: float) -> list[float]:
    kept = [t for t in _fails.get(caller, []) if now - t < FAIL_WINDOW_S]
    if kept:
        _fails[caller] = kept
    else:
        _fails.pop(caller, None)
    return kept


class KeyIn(BaseModel):
    key: str = Field(min_length=1, max_length=256)


@router.get('/access')
def access_state(request: Request):
    """Whether this deployment needs the access key, and whether the caller's token is good."""
    return {'required': required(), 'ok': not required() or valid(request.headers.get(HEADER))}


@router.post('/access')
def unlock(body: KeyIn, request: Request):
    """Exchange the access key for the signed token. Wrong keys are limited per caller."""
    key = _key()
    if not key:
        return {'required': False, 'token': None}
    caller, now = _caller(request), time.time()
    with _lock:
        if len(_recent_fails(caller, now)) >= MAX_FAILS:
            raise HTTPException(429, 'Too many attempts. Try again in a few minutes.', headers={'Retry-After': str(FAIL_WINDOW_S)})
    if not hmac.compare_digest(hashlib.sha256(body.key.strip().encode()).digest(), hashlib.sha256(key.encode()).digest()):
        with _lock:
            if len(_fails) > 10000:
                _fails.clear()
            _fails.setdefault(caller, []).append(now)
        raise HTTPException(401, 'That access key is not right.')
    with _lock:
        _fails.pop(caller, None)
    return {'required': True, 'token': issue()}
