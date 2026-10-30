from datetime import timedelta
import hashlib
import json
import os
import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, SecretStr
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..access import accessible_merchant_ids, require_merchant_access
from ..auth import Principal, current_principal
from ..database import db_session
from ..models import MerchantLocation
from . import providers, service
from .models import ConnectorConnection, ConnectorEvent, ConnectorLocation, ConnectorOffer, ConnectorSyncRun, now
from .security import (ConnectorError, SafeHTTP, decrypt, encrypt, normalize_store_url,
                       shop_domain, verify_body, verify_oauth)

router = APIRouter()


def guard(db, principal, connection_id, role='manager'):
    connection = db.get(ConnectorConnection, connection_id)
    if not connection:
        raise HTTPException(404, 'Connection not found')
    require_merchant_access(db, principal, connection.merchant_id, role)
    return connection


class ConnectInput(BaseModel):
    merchant_id: str
    provider: str = Field(pattern='^(woocommerce|shopify)$')
    store_url: str | None = None
    shop_domain: str | None = None
    consumer_key: SecretStr | None = None
    consumer_secret: SecretStr | None = None


@router.get('/merchant/connections')
def connections(merchant_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    require_merchant_access(db, p, merchant_id)
    return {'connections': [service.connection_view(c) for c in db.scalars(select(ConnectorConnection).where(
        ConnectorConnection.merchant_id == merchant_id).order_by(ConnectorConnection.created_at))],
        'providers': [{'id': 'woocommerce', 'name': 'WooCommerce', 'enabled': bool(os.getenv('CONNECTOR_ENCRYPTION_KEY'))},
                      {'id': 'shopify', 'name': 'Shopify', 'enabled': bool(os.getenv('SHOPIFY_CLIENT_ID') and os.getenv('SHOPIFY_CLIENT_SECRET') and os.getenv('PUBLIC_API_URL'))}]}


@router.post('/merchant/connections', status_code=201)
async def connect(body: ConnectInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    require_merchant_access(db, p, body.merchant_id, 'owner')
    try:
        domain = shop_domain(body.shop_domain or '') if body.provider == 'shopify' else None
        url = normalize_store_url(body.store_url or '') if body.provider == 'woocommerce' else f'https://{domain}'
        source_key = f'{body.provider}:{domain or url}'
        existing = db.scalar(select(ConnectorConnection).where(ConnectorConnection.source_key == source_key))
        if existing and (existing.merchant_id != body.merchant_id or existing.status != 'disconnected'):
            raise HTTPException(409, 'This source is already linked; disconnect or reauthorize the existing connection')
        connection = existing or ConnectorConnection(merchant_id=body.merchant_id, provider=body.provider,
                        source_key=source_key, store_url=url, shop_domain=domain, capabilities=providers.capabilities(body.provider))
        if not existing:
            db.add(connection)
        db.flush()
        authorization = None
        if body.provider == 'shopify':
            nonce = secrets.token_urlsafe(32)
            connection.state_hash = hashlib.sha256(nonce.encode()).hexdigest()
            connection.state_expires_at = now() + timedelta(minutes=10)
            connection.status = 'authorization_required'
            authorization = providers.authorization_url(connection, nonce)
        else:
            if not body.consumer_key or not body.consumer_secret:
                raise HTTPException(422, 'Authorized WooCommerce consumer key and secret required')
            connection.credentials_encrypted = encrypt({'consumer_key': body.consumer_key.get_secret_value(),
                'consumer_secret': body.consumer_secret.get_secret_value(), 'webhook_secret': secrets.token_urlsafe(32)})
            async with SafeHTTP() as http:
                await http.validate(url)
                await providers.verify_woo(http, connection)
            connection.status, connection.authorized_at = 'syncing', now()
            connection.capabilities = providers.capabilities('woocommerce', authorized=True)
            connection.next_sync_at = now()
        db.commit()
        return {'connection': service.connection_view(connection), 'authorization_url': authorization}
    except ConnectorError as exc:
        db.rollback()
        raise HTTPException(503, str(exc)) from None
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Connection already exists') from None


@router.get('/connectors/shopify/callback')
async def shopify_callback(request: Request, db: Session = Depends(db_session)):
    values = list(request.query_params.multi_items())
    params = dict(values)
    secret = os.getenv('SHOPIFY_CLIENT_SECRET', '')
    if not verify_oauth(values, secret):
        raise HTTPException(401, 'Invalid Shopify authorization signature')
    try:
        domain = shop_domain(params.get('shop', ''))
        digest = hashlib.sha256(params.get('state', '').encode()).hexdigest()
        connection = db.scalar(select(ConnectorConnection).where(ConnectorConnection.state_hash == digest,
            ConnectorConnection.state_expires_at > now(), ConnectorConnection.shop_domain == domain).with_for_update())
        if not connection or not params.get('code'):
            raise HTTPException(401, 'Authorization state expired or consumed')
        connection.state_hash, connection.state_expires_at = None, None
        db.commit()  # One-time nonce is consumed before exchanging a remote code.
        async with SafeHTTP() as http:
            await providers.exchange_code(http, connection, params['code'])
        connection.status, connection.authorized_at, connection.next_sync_at = 'syncing', now(), now()
        connection.capabilities = providers.capabilities('shopify', authorized=True)
        db.commit()
        return RedirectResponse(os.getenv('PUBLIC_WEB_URL', 'http://localhost:5173').rstrip('/') + '/merchant?connected=shopify', status_code=303)
    except ConnectorError as exc:
        db.rollback()
        raise HTTPException(503, str(exc)) from None


@router.post('/merchant/connections/{connection_id}/authorize')
def reauthorize(connection_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    c = guard(db, p, connection_id, 'owner')
    if c.provider != 'shopify':
        raise HTTPException(409, 'Reconnect WooCommerce with fresh merchant keys')
    nonce = secrets.token_urlsafe(32)
    try:
        url = providers.authorization_url(c, nonce)
        c.state_hash, c.state_expires_at = hashlib.sha256(nonce.encode()).hexdigest(), now() + timedelta(minutes=10)
        c.status = 'authorization_required'
        service.unpublish(db, c)
        db.commit()
        return {'authorization_url': url}
    except ConnectorError as exc:
        raise HTTPException(503, str(exc)) from None


@router.post('/merchant/connections/{connection_id}/sync')
async def sync(connection_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    c = guard(db, p, connection_id)
    try:
        async with SafeHTTP() as http:
            return await service.sync_connection(db, c, http)
    except ConnectorError as exc:
        raise HTTPException(409, str(exc)) from None


@router.delete('/merchant/connections/{connection_id}')
def disconnect(connection_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    c = guard(db, p, connection_id, 'owner')
    service.revoke(db, c)
    db.commit()
    return service.connection_view(c)


@router.get('/merchant/connections/{connection_id}/runs')
def runs(connection_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    guard(db, p, connection_id, 'staff')
    return {'runs': [service.run_view(r) for r in db.scalars(select(ConnectorSyncRun).where(
        ConnectorSyncRun.connection_id == connection_id).order_by(ConnectorSyncRun.started_at.desc()).limit(50))]}


@router.get('/merchant/connections/{connection_id}/locations')
def source_locations(connection_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    c = guard(db, p, connection_id, 'staff')
    return {'locations': [{'id': l.id, 'source_location_id': l.source_location_id, 'name': l.name, 'kind': l.kind,
                          'active': l.active, 'location_id': l.location_id, 'mapping_confirmed': l.mapping_confirmed}
                         for l in service.locations(db, c)]}


class Mapping(BaseModel):
    source_location_id: str
    location_id: str


class PublishInput(BaseModel):
    consent: bool = False
    mappings: list[Mapping] = Field(default_factory=list, max_length=100)


@router.post('/merchant/connections/{connection_id}/publish')
def publish(connection_id: str, body: PublishInput, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    c = guard(db, p, connection_id, 'owner')
    if not body.consent or c.status not in ('healthy', 'syncing', 'degraded'):
        raise HTTPException(409, 'Explicit display consent and an authorized source are required')
    for mapping in body.mappings:
        loc = db.scalar(select(ConnectorLocation).where(ConnectorLocation.connection_id == c.id,
                         ConnectorLocation.source_location_id == mapping.source_location_id))
        branch = db.get(MerchantLocation, mapping.location_id)
        if not loc or loc.kind != 'physical' or not branch or branch.merchant_id != c.merchant_id or not branch.active:
            raise HTTPException(409, 'Only verified source physical locations can map to an active merchant branch')
        loc.location_id, loc.mapping_confirmed = branch.id, True
    c.published, c.consent_at, c.consent_subject = True, now(), p.subject
    db.flush()
    for offer in db.scalars(select(ConnectorOffer).where(ConnectorOffer.connection_id == c.id)):
        service.project_offer(db, c, offer)
    db.commit()
    return service.connection_view(c)


@router.post('/merchant/connections/{connection_id}/webhooks')
async def register_hooks(connection_id: str, db: Session = Depends(db_session), p: Principal = Depends(current_principal)):
    c = guard(db, p, connection_id, 'owner')
    try:
        async with SafeHTTP() as http:
            await providers.register_webhooks(http, db, c)
        db.commit()
        return service.connection_view(c)
    except ConnectorError as exc:
        db.rollback()
        raise HTTPException(503, str(exc)) from None


@router.post('/connectors/{provider}/{connection_id}/webhook')
async def receive_hook(provider: str, connection_id: str, request: Request, db: Session = Depends(db_session)):
    c = db.get(ConnectorConnection, connection_id)
    if not c or c.provider != provider or c.status in ('disconnected', 'authorization_required'):
        raise HTTPException(404, 'Active connection not found')
    raw = await request.body()
    if len(raw) > 1024 * 1024:
        raise HTTPException(413, 'Webhook too large')
    try:
        creds = decrypt(c.credentials_encrypted)
        signature = request.headers.get('x-shopify-hmac-sha256' if provider == 'shopify' else 'x-wc-webhook-signature', '')
        secret = os.getenv('SHOPIFY_CLIENT_SECRET', '') if provider == 'shopify' else creds['webhook_secret']
        if not verify_body(raw, signature, secret):
            raise HTTPException(401, 'Invalid source signature')
        if provider == 'shopify' and request.headers.get('x-shopify-shop-domain') != c.shop_domain:
            raise HTTPException(401, 'Webhook shop mismatch')
        payload = json.loads(raw)
        topic = request.headers.get('x-shopify-topic' if provider == 'shopify' else 'x-wc-webhook-topic', '')
        delivery = request.headers.get('x-shopify-webhook-id' if provider == 'shopify' else 'x-wc-webhook-delivery-id', '')
        if not delivery or len(delivery) > 160 or not isinstance(payload, dict):
            raise HTTPException(400, 'Invalid source delivery')
        db.add(ConnectorEvent(connection_id=c.id, delivery_id=delivery, topic=topic[:100],
            body_hash=hashlib.sha256(raw).hexdigest(), payload_encrypted=encrypt(payload)))
        if topic == 'app/uninstalled':
            service.revoke(db, c, 'App uninstalled')
        db.commit()
        return {'ok': True, 'queued': True}
    except IntegrityError:
        db.rollback()
        return {'ok': True, 'duplicate': True}
    except (ValueError, KeyError, ConnectorError):
        raise HTTPException(400, 'Invalid source delivery') from None


@router.get('/connectors/{connection_id}/checkout')
def native_checkout(connection_id: str, product_id: str, db: Session = Depends(db_session)):
    c = db.get(ConnectorConnection, connection_id)
    offer = db.scalar(select(ConnectorOffer).where(ConnectorOffer.connection_id == connection_id,
                                                  ConnectorOffer.product_id == product_id, ConnectorOffer.deleted.is_(False)))
    if not c or not c.published or c.status not in ('healthy', 'syncing') or not offer or not offer.snapshot.get('native_checkout_supported'):
        raise HTTPException(409, 'Merchant checkout is not available')
    if not offer.observed_at or offer.observed_at < now() - service.FRESHNESS_TTL:
        raise HTTPException(409, 'Refresh source before checkout')
    if c.provider == 'shopify':
        variant = offer.source_variant_id.rsplit('/', 1)[-1]
        url = f'https://{shop_domain(c.shop_domain)}/cart/{variant}:1'
    else:
        # Native product page lets the merchant validate variations, taxes,
        # shipping and checkout stock; no external payment diversion.
        url = c.store_url + '/?' + urlencode({'p': offer.source_product_id, 'post_type': 'product'})
    return {'url': url, 'mode': 'merchant_native', 'verified_local_stock': False}
