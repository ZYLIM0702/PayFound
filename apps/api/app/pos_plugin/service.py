"""Sync engine for the custom POS connector. Credentials use the connectors' Fernet helpers;"""
from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
import logging
import os
import re
import secrets
import time
from datetime import timedelta
from urllib.parse import urlsplit

import httpx
from sqlalchemy import or_, select, update
from sqlalchemy.exc import IntegrityError

from ..connectors.models import now
from ..connectors.security import (ConnectorError, SafeHTTP, decrypt, encrypt, normalize_store_url,
                                   resolve_public, response_json)
from ..models import MerchantLocation, Product
from .contract import ContractError, MAX_REPORTED_ERRORS, PosBranch, PosProduct, PosStockEvent, parse_rows
from .models import PosConnection, PosSyncRun, new_id

logger = logging.getLogger('payfound.pos_plugin')

SCHEDULES = {'15m': timedelta(minutes=15), '1h': timedelta(hours=1), 'manual': None}
MAX_PAGES = 10
PAGE_LIMIT = 500
REPLAY_WINDOW_SECONDS = 300
LEASE = timedelta(minutes=3)
LOOPBACK_HOSTS = {'127.0.0.1', 'localhost', '::1'}
PATH_RE = re.compile(r'^/[A-Za-z0-9._~\-/]{0,199}$')


def demo_mode() -> bool:
    return os.getenv('DEMO_MODE', 'false').lower() == 'true'


def is_loopback_url(url: str) -> bool:
    try:
        p = urlsplit(url)
        return (p.scheme == 'http' and p.hostname in LOOPBACK_HOSTS and not p.username and not p.password
                and not p.query and not p.fragment and (p.port is None or 1024 <= p.port <= 65535))
    except ValueError:
        return False


async def validate_base_url(url: str) -> tuple[str, bool]:
    """Return (normalized_url, loopback). HTTPS + public DNS only; http loopback only in DEMO_MODE."""
    url = (url or '').strip()
    if len(url) > 500:
        raise ConnectorError('Base URL is too long')
    if is_loopback_url(url):
        if not demo_mode():
            raise ConnectorError('Local addresses are only allowed in demo mode')
        return url.rstrip('/'), True
    normalized = normalize_store_url(url)  # https, port 443, no credentials/query/fragment
    host = urlsplit(normalized).hostname
    try:  # IP literals are checked directly so a "public" name cannot hide a private address
        ipaddress.ip_address(host)
    except ValueError:
        pass
    await resolve_public(host)
    return normalized, False


def clean_path(value: str | None, *, required=True) -> str | None:
    value = (value or '').strip()
    if not value:
        if required:
            raise ConnectorError('A path is required')
        return None
    if not PATH_RE.match(value) or '//' in value or any(s in ('.', '..') for s in value.split('/')):
        raise ConnectorError('Paths must start with / and contain only letters, digits and - . _ ~ /')
    return value


class LoopbackHTTP:
    """Demo-only client for http://127.0.0.1:<port>. Never constructed outside DEMO_MODE."""
    def __init__(self, transport=None):
        self.transport = transport
        if not demo_mode():
            raise ConnectorError('Local addresses are only allowed in demo mode')

    async def __aenter__(self):
        self.client = httpx.AsyncClient(transport=self.transport, trust_env=False, follow_redirects=False, timeout=httpx.Timeout(10, connect=3))
        return self

    async def __aexit__(self, *a):
        await self.client.aclose()

    async def request(self, method, url, **kw):
        if not is_loopback_url(str(httpx.URL(url).copy_with(query=None))):
            raise ConnectorError('Local addresses are only allowed in demo mode')
        try:
            r = await self.client.request(method, url, **kw)
            return httpx.Response(r.status_code, headers=r.headers, content=r.content[:4 * 1024 * 1024], request=r.request)
        except httpx.HTTPError as exc:
            raise ConnectorError('POS could not be reached') from exc


def http_factory(conn: PosConnection):
    """Replaceable in tests (return a SafeHTTP over httpx.MockTransport)."""
    if (conn.settings or {}).get('loopback'):
        return LoopbackHTTP()
    return SafeHTTP()


def auth_headers(conn: PosConnection) -> dict:
    token = decrypt(conn.credentials_encrypted).get('token', '')
    if not token:
        raise ConnectorError('POS credentials are missing')
    return {'Authorization': f'Bearer {token}'} if conn.auth_scheme == 'bearer' else {'X-API-Key': token}


async def fetch(http, conn, path, params=None):
    url = conn.base_url.rstrip('/') + path
    return await http.request('GET', url, headers={**auth_headers(conn), 'Accept': 'application/json'}, params=params)


async def fetch_json(http, conn, path, params=None):
    data = response_json(await fetch(http, conn, path, params))
    if not isinstance(data, dict):
        raise ContractError('POS response must be a JSON object')
    return data


async def test_connection(conn: PosConnection) -> dict:
    started = time.monotonic()
    try:
        async with http_factory(conn) as http:
            response = await fetch(http, conn, conn.health_path)
    except ConnectorError as exc:
        return {'ok': False, 'message': str(exc)}
    ms = int((time.monotonic() - started) * 1000)
    if response.status_code in (401, 403):
        return {'ok': False, 'message': 'The POS rejected the credentials', 'status_code': response.status_code}
    if not 200 <= response.status_code < 300:
        return {'ok': False, 'message': f'The POS health path answered HTTP {response.status_code}', 'status_code': response.status_code}
    return {'ok': True, 'message': 'Connected', 'status_code': response.status_code, 'latency_ms': ms}


def mask(token: str) -> str:
    return '••••' + token[-4:] if len(token) >= 8 else '••••'


def store_token(conn: PosConnection, token: str):
    conn.credentials_encrypted = encrypt({'token': token})
    conn.credential_hint = mask(token)


def new_push_secret() -> str:
    return 'pfpos_' + secrets.token_urlsafe(32)


def sign(secret: str, timestamp: str, raw: bytes) -> str:
    return 'sha256=' + hmac.new(secret.encode(), timestamp.encode() + b'.' + raw, hashlib.sha256).hexdigest()


def verify_signature(secret: str, timestamp: str, raw: bytes, signature: str, *, at: float | None = None) -> str | None:
    """Return None if valid, otherwise a short controlled reason."""
    try:
        ts = int(timestamp)
    except (TypeError, ValueError):
        return 'Missing or invalid timestamp'
    if abs((at if at is not None else time.time()) - ts) > REPLAY_WINDOW_SECONDS:
        return 'Timestamp outside the 5 minute window'
    if not signature or not hmac.compare_digest(sign(secret, timestamp, raw), signature.strip()):
        return 'Invalid signature'
    return None


def branch_pk(conn, external_id):
    return 'posb_' + hashlib.sha256(f'{conn.id}\0{external_id}'.encode()).hexdigest()[:40]


def product_pk(conn, external_id):
    return 'pos_' + hashlib.sha256(f'{conn.id}\0{external_id}'.encode()).hexdigest()[:40]


class Counts:
    def __init__(self):
        self.created = self.updated = self.skipped = self.failed = 0
        self.errors: list[dict] = []
        self.max_updated = None

    def fail(self, errors):
        for e in errors:
            self.failed += 1
            if len(self.errors) < MAX_REPORTED_ERRORS:
                self.errors.append(e)

    def seen(self, ts):
        if ts and (self.max_updated is None or ts > self.max_updated):
            self.max_updated = ts


def upsert_branch(db, conn, row: PosBranch, counts: Counts):
    pk = branch_pk(conn, row.external_id)
    loc = db.get(MerchantLocation, pk)
    if loc is None:
        db.add(MerchantLocation(id=pk, merchant_id=conn.merchant_id, name=row.name, address=row.address,
                                latitude=row.latitude, longitude=row.longitude, timezone=row.timezone, active=True))
        counts.created += 1
        return
    # Hours, phone and operational status are PayFound-owned and are not touched.
    new = (row.name, row.address, row.latitude, row.longitude, row.timezone)
    if new == (loc.name, loc.address, loc.latitude, loc.longitude, loc.timezone):
        counts.skipped += 1
        return
    loc.name, loc.address, loc.latitude, loc.longitude, loc.timezone = new
    counts.updated += 1


def resolve_location(db, conn, ext):
    if ext:
        loc = db.get(MerchantLocation, branch_pk(conn, ext))
        return loc.id if loc and loc.merchant_id == conn.merchant_id and loc.active else None
    return db.scalar(select(MerchantLocation.id).where(MerchantLocation.merchant_id == conn.merchant_id,
                     MerchantLocation.active.is_(True)).order_by(MerchantLocation.created_at, MerchantLocation.id).limit(1))


def err(row, reason):
    return {'index': None, 'external_id': row.external_id[:60], 'error': reason}


def upsert_product(db, conn, row: PosProduct, counts: Counts, at):
    loc_id = resolve_location(db, conn, row.branch_external_id)
    if not loc_id:
        counts.fail([err(row, 'unknown branch_external_id' if row.branch_external_id else 'no branch available; send branches first')])
        return
    pk = product_pk(conn, row.external_id)
    p = db.get(Product, pk)
    if p is not None and p.merchant_id != conn.merchant_id:
        counts.fail([err(row, 'product belongs to another store')])
        return
    online = conn.status != 'paused' and row.active
    meta = json.dumps({'plugin': 'custom_pos', 'connection_id': conn.id, 'branch_external_id': row.branch_external_id})
    if p is None:
        db.add(Product(id=pk, merchant_id=conn.merchant_id, location_id=loc_id, name=row.name, sku=row.sku,
                       price_cents=row.price_cents, currency=row.currency.upper(), quantity=row.quantity, hold_quantity=0,
                       stock_updated_at=at, active=online, inventory_source='custom_pos', source_product_id=row.external_id,
                       source_version=(row.updated_at or at).isoformat(), source_updated_at=row.updated_at,
                       source_observed_at=at, source_metadata=meta, availability_state='likely_available',
                       supports_reservation=False, synthetic=False))
        counts.created += 1
        counts.seen(row.updated_at)
        return
    # Idempotency / incremental: an older or identical POS version never rewrites the product.
    if row.updated_at and p.source_updated_at and row.updated_at <= p.source_updated_at:
        counts.skipped += 1
        counts.seen(row.updated_at)
        return
    # hold_quantity is PayFound-owned: quantity can never drop below outstanding holds
    # (ck_product_stock). description/category/image/canonical links are not overwritten.
    quantity = max(row.quantity, p.hold_quantity)
    changed = (p.name, p.sku, p.price_cents, p.currency, p.quantity, p.active, p.location_id) != (
        row.name, row.sku, row.price_cents, row.currency.upper(), quantity, online, loc_id)
    p.name, p.sku, p.price_cents, p.currency = row.name, row.sku, row.price_cents, row.currency.upper()
    p.quantity, p.active, p.location_id = quantity, online, loc_id
    p.stock_updated_at = at
    p.inventory_source, p.source_product_id = 'custom_pos', row.external_id
    p.source_version, p.source_updated_at, p.source_observed_at = (row.updated_at or at).isoformat(), row.updated_at, at
    p.source_metadata = meta
    counts.updated += changed
    counts.skipped += not changed
    counts.seen(row.updated_at)


def apply_stock_event(db, conn, ev: PosStockEvent, counts: Counts, at):
    p = db.get(Product, product_pk(conn, ev.external_id))
    if p is None or p.merchant_id != conn.merchant_id:
        counts.fail([{'index': None, 'external_id': ev.external_id[:60], 'error': 'stock_events: unknown product'}])
        return
    if ev.updated_at and p.source_updated_at and ev.updated_at <= p.source_updated_at:
        counts.skipped += 1
        return
    quantity = max(ev.quantity, p.hold_quantity)
    changed = quantity != p.quantity
    p.quantity, p.stock_updated_at, p.source_observed_at = quantity, at, at
    if ev.updated_at:
        p.source_updated_at, p.source_version = ev.updated_at, ev.updated_at.isoformat()
    counts.updated += changed
    counts.skipped += not changed


def apply_payload(db, conn, counts: Counts, *, branches=(), products=(), stock_events=()):
    at = now()
    for b in branches:
        upsert_branch(db, conn, b, counts)
    db.flush()
    for pr in products:
        upsert_product(db, conn, pr, counts, at)
    for ev in stock_events:
        apply_stock_event(db, conn, ev, counts, at)
    db.flush()


def next_run(conn, *, failed=False):
    interval = SCHEDULES.get(conn.schedule)
    if failed:
        backoff = timedelta(seconds=min(3600, 60 * 2 ** max(0, conn.failure_count - 1)))
        return now() + max(backoff, interval or timedelta(0)) if conn.schedule != 'manual' else None
    return now() + interval if interval else None


def set_products_offline(db, conn):
    """Pause/disconnect keeps listings but marks them unavailable online."""
    ids = [p.id for p in db.scalars(select(Product).where(Product.merchant_id == conn.merchant_id,
           Product.inventory_source == 'custom_pos', Product.source_metadata.like(f'%"{conn.id}"%')))]
    if ids:
        db.execute(update(Product).where(Product.id.in_(ids)).values(active=False))


def disconnect(db, conn):
    set_products_offline(db, conn)
    conn.status, conn.credentials_encrypted, conn.credential_hint = 'disconnected', None, None
    conn.next_sync_at, conn.lease_until, conn.disconnected_at = None, None, now()


def acquire_lease(db, conn) -> bool:
    result = db.execute(update(PosConnection).where(
        PosConnection.id == conn.id, PosConnection.status.notin_(['disconnected', 'paused']),
        or_(PosConnection.lease_until.is_(None), PosConnection.lease_until <= now()),
    ).values(lease_until=now() + LEASE))
    db.commit()
    db.refresh(conn)
    return bool(result.rowcount)


async def sync_connection(db, conn: PosConnection, trigger: str = 'manual') -> PosSyncRun:
    if conn.mode != 'api':
        raise ConnectorError('Webhook connections receive pushes; there is nothing to pull')
    if conn.status in ('disconnected', 'paused'):
        raise ConnectorError('Connection is ' + conn.status)
    if not acquire_lease(db, conn):
        raise ConnectorError('A sync is already running')
    run = PosSyncRun(connection_id=conn.id, trigger=trigger)
    db.add(run)
    conn.status = 'syncing'
    db.commit()
    counts, cursor_before = Counts(), conn.cursor_updated_at
    error = None
    try:
        async with http_factory(conn) as http:
            if conn.branches_path:
                data = await fetch_json(http, conn, conn.branches_path)
                rows, bad = parse_rows(data.get('branches'), PosBranch, 'branches')
                counts.fail(bad)
                apply_payload(db, conn, counts, branches=rows)
                db.commit()
            page_cursor = None
            for _ in range(MAX_PAGES):
                params = {'limit': PAGE_LIMIT}
                if cursor_before:
                    params['updated_since'] = cursor_before.isoformat() + 'Z'
                if page_cursor:
                    params['cursor'] = page_cursor
                data = await fetch_json(http, conn, conn.products_path, params)
                rows, bad = parse_rows(data.get('products'), PosProduct, 'products')
                counts.fail(bad)
                apply_payload(db, conn, counts, products=rows)
                db.commit()
                page_cursor = data.get('next_cursor')
                if not page_cursor or not isinstance(page_cursor, str) or len(page_cursor) > 500:
                    break
    except (ConnectorError, ContractError) as exc:
        db.rollback()
        error = str(exc)[:300]
    except IntegrityError:
        db.rollback()
        error = 'A product could not be saved (conflicting data)'
    except Exception as exc:  # noqa: BLE001 - never log payloads, only the type
        db.rollback()
        logger.warning('pos_sync_failed connection=%s error=%s', conn.id, type(exc).__name__)
        error = 'Unexpected error while syncing'
    return finish_run(db, conn.id, run.id, counts, error)


def finish_run(db, conn_id, run_id, counts, error):
    conn, run = db.get(PosConnection, conn_id), db.get(PosSyncRun, run_id)
    run.created, run.updated, run.skipped, run.failed = counts.created, counts.updated, counts.skipped, counts.failed
    run.row_errors, run.finished_at = counts.errors, now()
    if conn.status != 'disconnected':
        if error:
            conn.failure_count += 1
            conn.status, conn.last_error = 'error', error
            conn.next_sync_at = next_run(conn, failed=True)
            run.status, run.error = 'failed', error
        else:
            conn.failure_count, conn.status = 0, 'connected'
            conn.last_error = None
            conn.last_synced_at = run.finished_at
            if counts.max_updated and (not conn.cursor_updated_at or counts.max_updated > conn.cursor_updated_at):
                conn.cursor_updated_at = counts.max_updated
            conn.next_sync_at = next_run(conn)
            run.status = 'partial' if counts.failed else 'ok'
        run.next_run_at = conn.next_sync_at
    else:
        run.status, run.error = 'failed', 'Disconnected during sync'
    conn.lease_until = None
    db.commit()
    return run


async def process_pos_jobs(db, *, max_connections=3):
    """Worker entry: run due scheduled pulls."""
    due = list(db.scalars(select(PosConnection).where(
        PosConnection.mode == 'api', PosConnection.status.in_(['connected', 'error']),
        PosConnection.schedule != 'manual', PosConnection.next_sync_at.is_not(None), PosConnection.next_sync_at <= now(),
        or_(PosConnection.lease_until.is_(None), PosConnection.lease_until <= now()),
    ).order_by(PosConnection.next_sync_at).limit(max_connections)))
    runs = []
    for conn in due:
        try:
            runs.append((await sync_connection(db, conn, 'schedule')).id)
        except ConnectorError:
            db.rollback()
    return {'pos_runs': runs}


def handle_push(db, conn: PosConnection, body: dict, signature: str) -> PosSyncRun:
    counts, error = Counts(), None
    run = PosSyncRun(connection_id=conn.id, trigger='push', delivery_id=hashlib.sha256(signature.encode()).hexdigest()[:64])
    db.add(run)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ConnectorError('Replayed delivery') from None
    try:
        branches, bad1 = parse_rows(body.get('branches'), PosBranch, 'branches')
        products, bad2 = parse_rows(body.get('products'), PosProduct, 'products')
        events, bad3 = parse_rows(body.get('stock_events'), PosStockEvent, 'stock_events')
        counts.fail(bad1 + bad2 + bad3)
        apply_payload(db, conn, counts, branches=branches, products=products, stock_events=events)
    except ContractError as exc:
        db.rollback()
        db.add(run)
        error = str(exc)
    run.created, run.updated, run.skipped, run.failed = counts.created, counts.updated, counts.skipped, counts.failed
    run.row_errors, run.finished_at = counts.errors, now()
    run.status = 'failed' if error else ('partial' if counts.failed else 'ok')
    run.error = error
    if not error:
        conn.last_synced_at, conn.last_error, conn.status, conn.failure_count = run.finished_at, None, 'connected', 0
    else:
        conn.last_error = error[:300]
    db.commit()
    return run
