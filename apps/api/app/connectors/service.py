"""Bounded, restartable snapshot jobs and conservative projections into Product."""
from __future__ import annotations

from datetime import timedelta
import hashlib
import json

from sqlalchemy import or_, select, update

from ..models import Product
from .models import ConnectorConnection, ConnectorEvent, ConnectorLocation, ConnectorOffer, ConnectorSyncRun, new_id, now
from .providers import capabilities, shop_info, shopify_page, verify_woo, woo_page
from .security import ConnectorError, SafeHTTP

SNAPSHOT_INTERVAL = timedelta(minutes=5)
FRESHNESS_TTL = timedelta(minutes=15)


def connection_view(connection):
    return {k: getattr(connection, k) for k in (
        'id', 'merchant_id', 'provider', 'status', 'capabilities', 'last_synced_at',
        'last_error', 'shop_domain', 'store_url', 'published')}


def run_view(run):
    return {k: getattr(run, k) for k in ('id', 'connection_id', 'status', 'started_at', 'finished_at', 'summary', 'error')}


def unpublish(db, connection):
    ids = select(ConnectorOffer.product_id).where(ConnectorOffer.connection_id == connection.id)
    db.execute(update(Product).where(Product.id.in_(ids)).values(active=False))
    connection.published = False
    connection.consent_at = None
    connection.consent_subject = None


def revoke(db, connection, message='Merchant disconnected the source'):
    unpublish(db, connection)
    connection.status = 'disconnected'
    connection.last_error = message
    connection.credentials_encrypted = None
    connection.state_hash = None
    connection.state_expires_at = None
    connection.lease_token = None
    connection.lease_until = None
    connection.sync_cursor = {}
    connection.next_sync_at = None
    connection.capabilities = capabilities(connection.provider)


def acquire_lease(db, connection):
    token = new_id()
    result = db.execute(update(ConnectorConnection).where(
        ConnectorConnection.id == connection.id,
        or_(ConnectorConnection.lease_until.is_(None), ConnectorConnection.lease_until <= now()),
        ConnectorConnection.status != 'disconnected',
    ).values(lease_token=token, lease_until=now() + timedelta(minutes=3)))
    db.commit()
    db.refresh(connection)
    if not result.rowcount:
        raise ConnectorError('Connector is busy or disconnected', retry_after=5)
    return token


def assert_lease(db, connection, token):
    # Read-after-network guard. Disconnect invalidates the lease immediately.
    db.refresh(connection, with_for_update=True)
    if connection.lease_token != token or not connection.lease_until or connection.lease_until <= now() or connection.status == 'disconnected':
        raise ConnectorError('Connector job lease expired or authorization changed')


def release_lease(db, connection, token):
    db.execute(update(ConnectorConnection).where(
        ConnectorConnection.id == connection.id, ConnectorConnection.lease_token == token,
    ).values(lease_token=None, lease_until=None))


def locations(db, connection):
    return list(db.scalars(select(ConnectorLocation).where(
        ConnectorLocation.connection_id == connection.id).order_by(ConnectorLocation.source_location_id)))


def replace_locations(db, connection, rows):
    existing = {loc.source_location_id: loc for loc in locations(db, connection)}
    seen = set()
    for row in rows:
        key = row['source_location_id']
        seen.add(key)
        loc = existing.get(key)
        if loc is None:
            loc = ConnectorLocation(connection_id=connection.id, **row)
            db.add(loc)
        else:
            loc.name, loc.kind, loc.active = row['name'], row['kind'], row['active']
        loc.seen_generation = connection.generation
    for key, loc in existing.items():
        if key not in seen:
            loc.active = False
    db.flush()
    inactive = [key for key, loc in existing.items() if not loc.active]
    if inactive:
        ids = select(ConnectorOffer.product_id).where(ConnectorOffer.connection_id == connection.id,
                                                     ConnectorOffer.source_location_id.in_(inactive))
        db.execute(update(Product).where(Product.id.in_(ids)).values(active=False))


CATALOG_KEYS = ('name', 'description', 'category', 'price_cents', 'currency', 'source_active',
                'native_checkout_supported', 'inventory_item_id')


def accept_snapshot(db, connection, row):
    """Catalog and inventory clocks are separate; arrival time is never a version."""
    offer = db.scalar(select(ConnectorOffer).where(
        ConnectorOffer.connection_id == connection.id,
        ConnectorOffer.source_location_id == row['source_location_id'],
        ConnectorOffer.source_variant_id == row['source_variant_id'],
    ).with_for_update())
    if offer is None:
        offer = ConnectorOffer(connection_id=connection.id, source_location_id=row['source_location_id'],
                               source_product_id=row['source_product_id'], source_variant_id=row['source_variant_id'],
                               sku=row['sku'], snapshot={})
        db.add(offer)
    state = dict(offer.snapshot or {})
    changed = False
    catalog_at, inventory_at = row.get('catalog_at'), row.get('inventory_at')
    if catalog_at and (not offer.source_catalog_at or catalog_at > offer.source_catalog_at):
        state.update({k: row[k] for k in CATALOG_KEYS if k in row})
        offer.source_catalog_at, offer.sku = catalog_at, row['sku']
        changed = True
    if inventory_at and (not offer.source_inventory_at or inventory_at > offer.source_inventory_at):
        state['quantity'] = row.get('quantity')
        offer.source_inventory_at = inventory_at
        changed = True
    # Missing version/stock is never interpreted as a positive stock assertion.
    if not offer.source_inventory_at:
        state['quantity'] = None
    offer.snapshot = state
    offer.observed_at, offer.seen_generation = now(), connection.generation
    offer.deleted = False
    db.flush()
    project_offer(db, connection, offer)
    return changed, offer


def project_offer(db, connection, offer):
    loc = db.scalar(select(ConnectorLocation).where(
        ConnectorLocation.connection_id == connection.id,
        ConnectorLocation.source_location_id == offer.source_location_id))
    state = offer.snapshot
    valid = (not offer.deleted and state.get('source_active', False)
             and state.get('quantity') is not None and 'price_cents' in state
             and offer.source_inventory_at is not None)
    mapped = bool(loc and loc.active and loc.mapping_confirmed and loc.location_id)
    # Generic Woo stock can be published only as ONLINE in connector_offers.
    # Never make it an active local Product, even when a merchant requests it.
    local = bool(mapped and loc.kind == 'physical')
    active = bool(connection.published and valid and local and connection.status != 'disconnected')
    offer.blocked_reason = None
    if not valid:
        offer.blocked_reason = 'unmanaged_stock_or_incomplete_snapshot'
    if not local:
        offer.blocked_reason = 'online_only' if loc and loc.kind == 'online' else 'location_mapping_required'
    if 'price_cents' not in state or 'name' not in state:
        return
    product = db.get(Product, offer.product_id) if offer.product_id else None
    if product is None:
        # Stable source-location-variant identity, independent of mutable SKU text.
        identity = '\0'.join((connection.id, offer.source_location_id, offer.source_variant_id))
        product = Product(id='cx_' + hashlib.sha256(identity.encode()).hexdigest()[:40],
                          merchant_id=connection.merchant_id, name=state['name'], sku=offer.sku,
                          price_cents=state['price_cents'], quantity=0, hold_quantity=0, active=False)
        if hasattr(Product, 'location_id'):
            product.location_id = loc.location_id if local else None
        db.add(product)
        db.flush()
        offer.product_id = product.id
    values = {k: state[k] for k in ('name', 'description', 'category', 'price_cents', 'currency') if k in state}
    values.update(sku=offer.sku, quantity=state.get('quantity') or 0,
                  stock_updated_at=offer.source_inventory_at or offer.observed_at, active=active)
    extra = {
        'location_id': loc.location_id if local else None,
        'inventory_source': connection.provider, 'synthetic': False,
        'availability_state': 'likely_available' if active else 'uncertain',
        'source_metadata': json.dumps({'connection_id': connection.id,
            'variant_id': offer.source_variant_id, 'source_location_id': offer.source_location_id,
            'checkout_mode': 'merchant_native'}),
        'source_connection_id': connection.id, 'source_product_id': offer.source_product_id,
        'source_variant_id': offer.source_variant_id, 'source_location_id': offer.source_location_id,
        'source_kind': 'local' if local else 'online',
        'source_version': (offer.source_inventory_at or offer.observed_at).isoformat(),
        'source_updated_at': offer.source_inventory_at, 'source_observed_at': offer.observed_at,
        'inventory_confidence': 'likely_available', 'source_reservation_supported': False,
        'checkout_mode': 'merchant_native',
    }
    values.update({k: v for k, v in extra.items() if hasattr(Product, k)})
    # Conditional SQL is the concurrency boundary with core reservations. Any
    # outstanding local hold blocks replacement; never zero/erase held inventory.
    result = db.execute(update(Product).where(Product.id == product.id, Product.hold_quantity == 0).values(**values))
    if not result.rowcount:
        db.execute(update(Product).where(Product.id == product.id).values(active=False))
        offer.blocked_reason = 'outstanding_local_hold_requires_reconciliation'
    db.flush()


def expire_stale_offers(db):
    stale = select(ConnectorOffer.product_id).where(ConnectorOffer.observed_at < now() - FRESHNESS_TTL)
    db.execute(update(Product).where(Product.id.in_(stale)).values(active=False))


async def sync_connection(db, connection, http: SafeHTTP, *, max_pages=4):
    """At most four 50-item pages; continuation persisted after EACH page."""
    if connection.status in {'authorization_required', 'disconnected'}:
        raise ConnectorError('Merchant authorization required', revoked=True)
    if connection.next_sync_at and connection.next_sync_at > now():
        raise ConnectorError('Connector rate limited; retry after next_sync_at', retry_after=5)
    token = acquire_lease(db, connection)
    run = ConnectorSyncRun(connection_id=connection.id)
    db.add(run)
    db.commit()
    summary = {'imported': 0, 'unchanged': 0, 'blocked': 0, 'pages': 0, 'complete': False}
    try:
        if not connection.sync_cursor:
            connection.generation, connection.cycle_started_at = new_id(), now()
            connection.status = 'syncing'
            db.commit()
            if connection.provider == 'shopify':
                rows = await shop_info(http, db, connection)
            else:
                await verify_woo(http, connection)
                rows = [dict(source_location_id='online', name='Online store (not branch inventory)', kind='online', active=True)]
            # shop_info changes settings/scopes; preserve them across refresh guard.
            settings, scopes = dict(connection.settings), list(connection.scopes)
            assert_lease(db, connection, token)
            connection.settings, connection.scopes = settings, scopes
            replace_locations(db, connection, rows)
            connection.sync_cursor = {'location_index': 0} if connection.provider == 'shopify' else {'page': 1}
            db.commit()
        source_locations = [loc for loc in locations(db, connection) if loc.active]
        for _ in range(min(max(1, max_pages), 4)):
            cursor = dict(connection.sync_cursor)
            if connection.provider == 'shopify':
                index = cursor.get('location_index', 0)
                if index >= len(source_locations):
                    rows, complete = [], True
                else:
                    rows, page = await shopify_page(http, db, connection, source_locations[index].source_location_id, cursor.get('after'))
                    if page['hasNextPage']:
                        if not page.get('endCursor') or page['endCursor'] == cursor.get('after'):
                            raise ConnectorError('Shopify returned a non-advancing cursor')
                        cursor['after'] = page['endCursor']
                    else:
                        cursor = {'location_index': index + 1}
                    complete = cursor.get('location_index', 0) >= len(source_locations)
            else:
                rows, cursor, complete = await woo_page(http, connection, cursor)
            throttle_at = connection.next_sync_at
            assert_lease(db, connection, token)
            for row in rows:
                changed, offer = accept_snapshot(db, connection, row)
                summary['imported' if changed else 'unchanged'] += 1
                if offer.blocked_reason not in (None, 'location_mapping_required', 'online_only'):
                    summary['blocked'] += 1
            summary['pages'] += 1
            connection.sync_cursor = cursor
            connection.next_sync_at = throttle_at
            if complete:
                # Mark-and-sweep only records last seen BEFORE this cycle. A push
                # arriving mid-cycle cannot be removed by an older snapshot.
                missing = list(db.scalars(select(ConnectorOffer).where(
                    ConnectorOffer.connection_id == connection.id,
                    ConnectorOffer.seen_generation != connection.generation,
                    ConnectorOffer.observed_at < connection.cycle_started_at)))
                for offer in missing:
                    offer.deleted = True
                    project_offer(db, connection, offer)
                connection.sync_cursor = {}
                connection.last_synced_at = now()
                connection.next_sync_at = now() + SNAPSHOT_INTERVAL
                summary['complete'] = True
            db.commit()
            if complete or (connection.next_sync_at and connection.next_sync_at > now()):
                break
        connection.status = 'degraded' if summary['blocked'] else ('healthy' if summary['complete'] else 'syncing')
        connection.last_error = 'Some offers require inventory reconciliation' if summary['blocked'] else None
        run.status = 'completed' if summary['complete'] else 'continued'
    except ConnectorError as exc:
        db.rollback()
        db.refresh(connection)
        if exc.revoked:
            revoke(db, connection, str(exc))
        elif connection.status != 'disconnected':
            connection.status, connection.last_error = 'degraded', str(exc)
            connection.next_sync_at = now() + timedelta(seconds=exc.retry_after)
        run.status, run.error = 'failed', str(exc)
    except Exception:
        db.rollback()
        db.refresh(connection)
        if connection.status != 'disconnected':
            connection.status, connection.last_error = 'degraded', 'Connector snapshot could not be normalized'
            connection.next_sync_at = now() + timedelta(minutes=1)
        run.status, run.error = 'failed', 'Connector snapshot could not be normalized'
    run.summary, run.finished_at = summary, now()
    release_lease(db, connection, token)
    db.commit()
    return run_view(run)


async def process_connector_events(db, *, limit=20):
    """Signed deliveries are hints; queue authoritative recovery instead of trusting"""
    events = list(db.scalars(select(ConnectorEvent).where(
        ConnectorEvent.status == 'pending',
        or_(ConnectorEvent.next_attempt_at.is_(None), ConnectorEvent.next_attempt_at <= now()),
    ).order_by(ConnectorEvent.observed_at).limit(min(limit, 50)).with_for_update(skip_locked=True)))
    for event in events:
        connection = db.get(ConnectorConnection, event.connection_id)
        if connection and connection.status not in {'disconnected', 'authorization_required'}:
            # Do not clear an unfinished page cursor: event storms must not starve
            # snapshot completion. A subsequent cycle repairs any earlier pages.
            connection.next_sync_at = now()
        event.status, event.processed_at = 'processed', now()
        event.attempts += 1
    db.commit()
    return {'processed': len(events)}


async def process_connector_jobs(db, *, max_connections=2, http_factory=SafeHTTP):
    """Core worker entry. Caller supplies one Session; no detached background tasks."""
    processed = await process_connector_events(db)
    expire_stale_offers(db)
    due = list(db.scalars(select(ConnectorConnection).where(
        ConnectorConnection.status.in_(['healthy', 'degraded', 'syncing']),
        or_(ConnectorConnection.next_sync_at.is_(None), ConnectorConnection.next_sync_at <= now()),
        or_(ConnectorConnection.lease_until.is_(None), ConnectorConnection.lease_until <= now()),
    ).order_by(ConnectorConnection.next_sync_at).limit(min(max_connections, 4))))
    runs = []
    for connection in due:
        try:
            async with http_factory() as http:
                runs.append(await sync_connection(db, connection, http))
        except ConnectorError:
            # Another worker may have won the conditional lease acquisition.
            db.rollback()
    db.commit()
    return {**processed, 'runs': runs}
