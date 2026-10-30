import asyncio
import base64
import hashlib
import hmac
from datetime import timedelta

import httpx
import pytest
from cryptography.fernet import Fernet
from sqlalchemy import select

from app.connectors import providers, service
from app.connectors.models import ConnectorConnection, ConnectorEvent, ConnectorLocation, ConnectorOffer
from app.connectors.security import ConnectorError, SafeHTTP, decrypt, encrypt, resolve_public
from app.database import SessionLocal
from app.models import Product, utcnow


def connector(db, *, published=True):
    row = ConnectorConnection(merchant_id='m1', provider='shopify', source_key='shopify:test.myshopify.com',
        shop_domain='test.myshopify.com', store_url='https://test.myshopify.com', status='healthy',
        capabilities=providers.capabilities('shopify', authorized=True), published=published)
    db.add(row)
    db.flush()
    return row


def test_credentials_are_ciphertext_and_private_hosts_are_not_egress_targets(monkeypatch):
    monkeypatch.setenv('CONNECTOR_ENCRYPTION_KEY', Fernet.generate_key().decode())
    encrypted = encrypt({'consumer_key': 'key', 'consumer_secret': 'secret'})
    assert 'secret' not in encrypted and decrypt(encrypted)['consumer_key'] == 'key'
    with pytest.raises(ConnectorError, match='not publicly routable'):
        asyncio.run(resolve_public('localhost'))
    with pytest.raises(ValueError, match='MockTransport'):
        SafeHTTP(test_allow_unresolved_hosts=True)


def test_safe_http_mock_transport_and_shopify_page_wire_contract(monkeypatch):
    monkeypatch.setenv('CONNECTOR_ENCRYPTION_KEY', Fernet.generate_key().decode())
    payload = {'data': {'productVariants': {'nodes': [{
        'id': 'gid://shopify/ProductVariant/2', 'title': 'Blue', 'sku': 'SKU-2', 'price': '12.34',
        'updatedAt': '2026-01-02T03:04:05Z', 'requiresComponents': False,
        'product': {'id': 'gid://shopify/Product/1', 'title': 'Hat', 'description': 'cotton', 'productType': 'Apparel',
                    'status': 'ACTIVE', 'updatedAt': '2026-01-02T03:04:05Z', 'onlineStoreUrl': 'https://shop/p/1', 'requiresSellingPlan': False},
        'inventoryItem': {'id': 'gid://shopify/InventoryItem/3', 'tracked': True,
                          'inventoryLevel': {'updatedAt': '2026-01-02T03:04:05Z', 'quantities': [{'name': 'available', 'quantity': 7}]}}
    }], 'pageInfo': {'hasNextPage': False, 'endCursor': None}}}}

    async def run():
        transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
        async with SafeHTTP(transport=transport, test_allow_unresolved_hosts=True) as http:
            row = ConnectorConnection(merchant_id='m1', provider='shopify', source_key='shopify:wire.myshopify.com',
                shop_domain='wire.myshopify.com', credentials_encrypted=encrypt({'access_token': 'token', 'refresh_token': 'refresh',
                'expires_at': (utcnow() + timedelta(hours=1)).isoformat(), 'refresh_expires_at': (utcnow() + timedelta(days=1)).isoformat()}),
                settings={'currency': 'USD'})
            rows, page = await providers.shopify_page(http, None, row, 'gid://shopify/Location/1')
            assert page == {'hasNextPage': False, 'endCursor': None}
            assert rows[0]['price_cents'] == 1234 and rows[0]['quantity'] == 7
            assert rows[0]['source_variant_id'].endswith('/2')
    asyncio.run(run())


def test_snapshot_version_never_regresses_and_revoke_unpublishes_mapped_offer(client, monkeypatch):
    monkeypatch.setenv('CONNECTOR_ENCRYPTION_KEY', Fernet.generate_key().decode())
    with SessionLocal() as db:
        row = connector(db)
        db.add(ConnectorLocation(connection_id=row.id, source_location_id='source-1', name='Source', kind='physical', location_id='loc-m1', mapping_confirmed=True))
        newest = {'source_location_id': 'source-1', 'source_product_id': 'product-1', 'source_variant_id': 'variant-1',
            'sku': 'V1', 'catalog_at': utcnow(), 'inventory_at': utcnow(), 'name': 'New name', 'description': '', 'category': 'Test',
            'price_cents': 999, 'currency': 'USD', 'quantity': 8, 'source_active': True, 'native_checkout_supported': True, 'inventory_item_id': 'i1'}
        service.accept_snapshot(db, row, newest)
        db.commit()
        offer = db.scalar(select(ConnectorOffer).where(ConnectorOffer.connection_id == row.id))
        product = db.get(Product, offer.product_id)
        assert product.active and product.quantity == 8
        older = dict(newest, quantity=1, inventory_at=utcnow() - timedelta(days=1), catalog_at=utcnow() - timedelta(days=1))
        service.accept_snapshot(db, row, older)
        db.commit()
        assert db.get(Product, offer.product_id).quantity == 8
        service.revoke(db, row)
        db.commit()
        assert not db.get(Product, offer.product_id).active
        assert row.credentials_encrypted is None and row.published is False and row.status == 'disconnected'


def test_webhook_hmac_duplicate_and_invalid_delivery_are_controlled(client, monkeypatch):
    secret = Fernet.generate_key().decode()
    monkeypatch.setenv('CONNECTOR_ENCRYPTION_KEY', secret)
    monkeypatch.setenv('SHOPIFY_CLIENT_SECRET', 'webhook-secret')
    with SessionLocal() as db:
        row = connector(db)
        row.credentials_encrypted = encrypt({'access_token': 'shopify-token'})
        db.commit()
        cid = row.id
    raw = b'{"id":"source-event"}'
    signature = base64.b64encode(hmac.digest(b'webhook-secret', raw, 'sha256')).decode()
    headers = {'x-shopify-hmac-sha256': signature, 'x-shopify-shop-domain': 'test.myshopify.com',
               'x-shopify-topic': 'products/update', 'x-shopify-webhook-id': 'delivery-1'}
    url = f'/api/connectors/shopify/{cid}/webhook'
    first = client.post(url, content=raw, headers=headers)
    assert first.status_code == 200, first.text
    assert first.json()['queued'] is True
    duplicate = client.post(url, content=raw, headers=headers)
    assert duplicate.status_code == 200 and duplicate.json()['duplicate'] is True
    assert client.post(url, content=raw, headers={**headers, 'x-shopify-hmac-sha256': 'bad'}).status_code == 401
    with SessionLocal() as db:
        events = list(db.scalars(select(ConnectorEvent).where(ConnectorEvent.connection_id == cid)))
        assert len(events) == 1 and decrypt(events[0].payload_encrypted) == {'id': 'source-event'}


def test_source_variant_identity_does_not_assume_unique_sku(client):
    with SessionLocal() as db:
        row = connector(db)
        db.add(ConnectorLocation(connection_id=row.id, source_location_id='source-1', name='Source',
            kind='physical', location_id='loc-m1', mapping_confirmed=True))
        snapshot = {'source_location_id': 'source-1', 'source_product_id': 'parent-1',
            'sku': 'REUSED-SKU', 'catalog_at': utcnow(), 'inventory_at': utcnow(),
            'description': '', 'category': 'Test', 'price_cents': 999, 'currency': 'USD',
            'quantity': 3, 'source_active': True, 'native_checkout_supported': True}
        for variant in ('blue', 'red'):
            service.accept_snapshot(db, row, {**snapshot, 'source_variant_id': variant, 'name': 'Variant ' + variant})
        db.commit()
        offers = list(db.scalars(select(ConnectorOffer).where(ConnectorOffer.connection_id == row.id)))
        assert len(offers) == 2 and len({o.product_id for o in offers}) == 2
        assert {db.get(Product, o.product_id).name for o in offers} == {'Variant blue', 'Variant red'}
        assert {db.get(Product, o.product_id).sku for o in offers} == {'REUSED-SKU'}
