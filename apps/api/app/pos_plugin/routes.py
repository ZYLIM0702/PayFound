"""Merchant-scoped endpoints for the custom POS connector plus the signed push receiver."""
from __future__ import annotations

import json
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, SecretStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..access import ROLE_LEVEL, merchant_role, require_merchant_access
from ..auth import Principal, current_principal
from ..connectors.models import now
from ..connectors.security import ConnectorError, decrypt, encrypt
from ..database import db_session
from ..models import Merchant
from . import service
from .models import PosConnection, PosSyncRun

router = APIRouter(tags=['Custom POS connector'])

DEMO_POS = {'base_url': 'http://127.0.0.1:9010', 'token': 'demo-pos-token', 'name': 'Demo POS (local)'}
MAX_BODY = 1024 * 1024

# Sliding-window limiter per (merchant, action). Single process, like app.limits; not disabled in
# DEMO_MODE so the protection is visible; tests reset it.
_hits: dict[tuple, deque] = defaultdict(deque)
RATE_LIMITS = {'connect': (10, 60), 'test': (15, 60)}


def rate_limit(merchant_id: str, action: str):
    limit, window = RATE_LIMITS[action]
    q, t = _hits[(merchant_id, action)], time.monotonic()
    while q and q[0] < t - window:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(429, 'Too many attempts. Wait a minute and try again.', headers={'Retry-After': str(window)})
    q.append(t)


def guard(db: Session, p: Principal, connection_id: str, minimum='manager') -> PosConnection:
    """Another store's connection is indistinguishable from a missing one (404)."""
    conn = db.get(PosConnection, connection_id)
    merchant = db.get(Merchant, conn.merchant_id) if conn else None
    role = merchant_role(db, p, merchant) if merchant else None
    if not conn or not role:
        raise HTTPException(404, 'Connection not found')
    if ROLE_LEVEL[role] < ROLE_LEVEL[minimum]:
        raise HTTPException(403, 'Your role cannot do this')
    return conn


def view(c: PosConnection, request: Request | None = None):
    out = {k: getattr(c, k) for k in ('id', 'merchant_id', 'name', 'mode', 'status', 'base_url', 'products_path',
           'branches_path', 'health_path', 'auth_scheme', 'credential_hint', 'schedule', 'last_synced_at',
           'next_sync_at', 'last_error', 'failure_count', 'created_at')}
    out['demo'] = bool((c.settings or {}).get('loopback'))
    if c.mode == 'push' and request is not None:
        out['endpoint_url'] = endpoint_url(request, c)
    return out


def endpoint_url(request: Request, c: PosConnection) -> str:
    return str(request.base_url).rstrip('/') + f'/api/pos-plugin/{c.id}/events'


def run_view(r: PosSyncRun):
    return {k: getattr(r, k) for k in ('id', 'trigger', 'status', 'started_at', 'finished_at', 'created', 'updated',
            'skipped', 'failed', 'error', 'row_errors', 'next_run_at')}


class ConnectInput(BaseModel):
    merchant_id: str
    mode: str = Field(pattern='^(api|push)$')
    name: str = Field(min_length=1, max_length=80)
    base_url: str | None = Field(default=None, max_length=500)
    token: SecretStr | None = None
    auth_scheme: str = Field(default='bearer', pattern='^(bearer|api_key)$')
    products_path: str = Field(default='/products', max_length=200)
    branches_path: str | None = Field(default='/branches', max_length=200)
    health_path: str = Field(default='/health', max_length=200)
    schedule: str = Field(default='manual', pattern='^(15m|1h|manual)$')


class UpdateInput(BaseModel):
    schedule: str | None = Field(default=None, pattern='^(15m|1h|manual)$')
    paused: bool | None = None


@router.get('/merchant/pos-plugin')
def overview(merchant_id: str, request: Request, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    require_merchant_access(db, p, merchant_id)
    rows = db.scalars(select(PosConnection).where(PosConnection.merchant_id == merchant_id,
                      PosConnection.status != 'disconnected').order_by(PosConnection.created_at))
    return {'connections': [view(c, request) for c in rows],
            'demo': dict(DEMO_POS) if service.demo_mode() else None}


@router.post('/merchant/pos-plugin/connections', status_code=201)
async def connect(body: ConnectInput, request: Request, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    require_merchant_access(db, p, body.merchant_id, 'owner')
    rate_limit(body.merchant_id, 'connect')
    try:
        conn = PosConnection(merchant_id=body.merchant_id, name=body.name.strip(), mode=body.mode, schedule=body.schedule, settings={})
        reveal = None
        if body.mode == 'api':
            token = body.token.get_secret_value().strip() if body.token else ''
            if not body.base_url or not token or len(token) > 2000:
                raise HTTPException(422, 'Base URL and an API key or token are required')
            conn.base_url, loopback = await service.validate_base_url(body.base_url)
            conn.settings = {'loopback': loopback} if loopback else {}
            conn.products_path = service.clean_path(body.products_path)
            conn.branches_path = service.clean_path(body.branches_path, required=False)
            conn.health_path = service.clean_path(body.health_path)
            conn.auth_scheme = body.auth_scheme
            service.store_token(conn, token)
            health = await service.test_connection(conn)
            if not health['ok']:
                raise HTTPException(422, f"Could not connect: {health['message']}")
            conn.next_sync_at = service.next_run(conn)
        else:
            secret = service.new_push_secret()
            conn.credentials_encrypted, conn.credential_hint = encrypt({'secret': secret}), service.mask(secret)
            conn.schedule = 'manual'
            reveal = secret
        db.add(conn)
        db.commit()
    except ConnectorError as exc:
        db.rollback()
        raise HTTPException(422, str(exc)) from None
    out = {'connection': view(conn, request)}
    if reveal:
        out['secret'] = reveal
        out['endpoint_url'] = endpoint_url(request, conn)
    return out


@router.post('/merchant/pos-plugin/{connection_id}/test')
async def test(connection_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    conn = guard(db, p, connection_id)
    rate_limit(conn.merchant_id, 'test')
    if conn.mode != 'api' or conn.status == 'disconnected':
        raise HTTPException(409, 'Only active API connections can be tested')
    return await service.test_connection(conn)


@router.post('/merchant/pos-plugin/{connection_id}/sync')
async def sync_now(connection_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    conn = guard(db, p, connection_id)
    try:
        return run_view(await service.sync_connection(db, conn, 'manual'))
    except ConnectorError as exc:
        raise HTTPException(409, str(exc)) from None


@router.patch('/merchant/pos-plugin/{connection_id}')
def update(connection_id: str, body: UpdateInput, request: Request, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    conn = guard(db, p, connection_id, 'owner')
    if conn.status == 'disconnected':
        raise HTTPException(409, 'Connection is disconnected')
    if body.schedule and conn.mode == 'api':
        conn.schedule = body.schedule
    if body.paused is True and conn.status != 'paused':
        service.set_products_offline(db, conn)
        conn.status, conn.next_sync_at = 'paused', None
    elif body.paused is False and conn.status == 'paused':
        conn.status, conn.failure_count = 'connected', 0
        # Listings come back online with the next sync (the POS stays the source of truth).
    if conn.status != 'paused' and conn.mode == 'api':
        conn.next_sync_at = service.next_run(conn) if conn.schedule != 'manual' else None
        if body.paused is False and conn.schedule != 'manual':
            conn.next_sync_at = now()
    db.commit()
    return view(conn, request)


@router.delete('/merchant/pos-plugin/{connection_id}')
def disconnect(connection_id: str, request: Request, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    conn = guard(db, p, connection_id, 'owner')
    service.disconnect(db, conn)
    db.commit()
    return view(conn, request)


@router.get('/merchant/pos-plugin/{connection_id}/runs')
def runs(connection_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    guard(db, p, connection_id, 'staff')
    rows = db.scalars(select(PosSyncRun).where(PosSyncRun.connection_id == connection_id)
                      .order_by(PosSyncRun.started_at.desc()).limit(30))
    return {'runs': [run_view(r) for r in rows]}


@router.post('/pos-plugin/{connection_id}/events')
async def receive(connection_id: str, request: Request, db: Session = Depends(db_session)):
    """Signed push. Headers: X-PayFound-Timestamp (unix seconds), X-PayFound-Signature (sha256=hex of
    HMAC-SHA256(secret, timestamp + '.' + raw body))."""
    conn = db.get(PosConnection, connection_id)
    if not conn or conn.mode != 'push' or conn.status == 'disconnected':
        raise HTTPException(404, 'Connection not found')
    raw = await request.body()
    if len(raw) > MAX_BODY:
        raise HTTPException(413, 'Body too large')
    try:
        secret = decrypt(conn.credentials_encrypted)['secret']
    except (ConnectorError, KeyError):
        raise HTTPException(401, 'Invalid signature') from None
    signature = request.headers.get('x-payfound-signature', '')
    reason = service.verify_signature(secret, request.headers.get('x-payfound-timestamp', ''), raw, signature)
    if reason:
        raise HTTPException(401, reason)
    try:
        body = json.loads(raw)
        if not isinstance(body, dict):
            raise ValueError()
    except ValueError:
        raise HTTPException(400, 'Body must be a JSON object') from None
    try:
        run = service.handle_push(db, conn, body, signature)
    except ConnectorError:
        raise HTTPException(401, 'Replayed delivery') from None
    return {'ok': run.status != 'failed', 'status': run.status, 'created': run.created, 'updated': run.updated,
            'skipped': run.skipped, 'failed': run.failed, 'errors': run.row_errors, 'error': run.error}
