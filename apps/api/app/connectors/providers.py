"""First-party wire protocols. No vendor SDK or external payment/hold writes."""
from __future__ import annotations

from datetime import timedelta
import os
import re
from urllib.parse import urlencode

import httpx

from .models import now
from .normalization import money_cents, quantity, timestamp
from .security import ConnectorError, decrypt, encrypt, response_json, shop_domain

SHOPIFY_VERSION = '2026-04'  # Supported stable schema, explicitly pinned.
REQUIRED_SCOPES = {'read_products', 'read_inventory', 'read_locations'}
SHOPIFY_TOPICS = ('APP_UNINSTALLED', 'APP_SCOPES_UPDATE', 'PRODUCTS_CREATE',
                  'PRODUCTS_UPDATE', 'PRODUCTS_DELETE', 'INVENTORY_LEVELS_UPDATE',
                  'LOCATIONS_UPDATE', 'LOCATIONS_DELETE')
WOO_TOPICS = ('product.created', 'product.updated', 'product.deleted')


def capabilities(provider, *, authorized=False, webhooks=False):
    return {
        'catalog_read': authorized, 'branch_read': authorized and provider == 'shopify',
        'inventory_read': authorized, 'inventory_events': authorized and webhooks,
        'inventory_reservation': False, 'source_reservation': False,
        'pickup_order_write': False, 'external_payment_permitted': False,
        'refund_write': False, 'merchant_profile_write': False, 'realtime_status': False,
        'merchant_checkout': authorized, 'hold_mode': 'merchant_native_checkout_or_confirmation',
        'stock_confidence': 'likely_available',
    }


def validate_scopes(scopes):
    granted = set(scopes)
    if any(s not in granted and 'write_' + s[5:] not in granted for s in REQUIRED_SCOPES):
        raise ConnectorError('Required Shopify scopes were not granted', revoked=True)


def app_credentials():
    client_id, secret = os.getenv('SHOPIFY_CLIENT_ID'), os.getenv('SHOPIFY_CLIENT_SECRET')
    if not client_id or not secret:
        raise ConnectorError('Shopify app credentials are not configured')
    return client_id, secret


def public_api_url():
    from .security import normalize_store_url
    value = os.getenv('PUBLIC_API_URL', '').rstrip('/')
    if not value:
        raise ConnectorError('PUBLIC_API_URL is not configured')
    return normalize_store_url(value)


def authorization_url(connection, nonce):
    client_id, _ = app_credentials()
    return f'https://{shop_domain(connection.shop_domain)}/admin/oauth/authorize?' + urlencode({
        'client_id': client_id, 'scope': ','.join(sorted(REQUIRED_SCOPES)),
        'redirect_uri': public_api_url() + '/api/connectors/shopify/callback', 'state': nonce,
    })


def store_tokens(connection, data, *, refresh=False):
    old = decrypt(connection.credentials_encrypted) if refresh else {}
    scopes = data.get('scope', ','.join(connection.scopes)).split(',')
    validate_scopes(scopes)
    try:
        expires = int(data['expires_in'])
        refresh_expires = int(data['refresh_token_expires_in'])
        if expires <= 0 or refresh_expires <= 0 or not data['access_token'] or not data['refresh_token']:
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise ConnectorError('Shopify did not issue an expiring offline token')
    old.update({
        'access_token': data['access_token'], 'refresh_token': data['refresh_token'],
        'expires_at': (now() + timedelta(seconds=expires)).isoformat(),
        'refresh_expires_at': (now() + timedelta(seconds=refresh_expires)).isoformat(),
    })
    connection.credentials_encrypted = encrypt(old)
    connection.scopes = scopes


async def exchange_code(http, connection, code):
    client_id, secret = app_credentials()
    response = await http.request('POST', f'https://{shop_domain(connection.shop_domain)}/admin/oauth/access_token',
                                  data={'client_id': client_id, 'client_secret': secret, 'code': code, 'expiring': '1'})
    store_tokens(connection, response_json(response))


async def refresh_token(http, db, connection):
    creds = decrypt(connection.credentials_encrypted)
    if not creds.get('refresh_token') or timestamp(creds.get('refresh_expires_at')) <= now():
        raise ConnectorError('Shopify refresh token expired; reauthorize the store', revoked=True)
    client_id, secret = app_credentials()
    response = await http.request('POST', f'https://{shop_domain(connection.shop_domain)}/admin/oauth/access_token',
                                  data={'client_id': client_id, 'client_secret': secret,
                                        'grant_type': 'refresh_token', 'refresh_token': creds['refresh_token']})
    store_tokens(connection, response_json(response), refresh=True)
    # Persist rotated refresh credentials before issuing another request. All
    # callers hold the connection lease, so refresh/acquire cannot race.
    db.commit()


async def graphql(http, db, connection, query, variables=None):
    creds = decrypt(connection.credentials_encrypted)
    expiry = timestamp(creds.get('expires_at'))
    if not expiry or expiry <= now() + timedelta(seconds=60):
        await refresh_token(http, db, connection)
    url = f'https://{shop_domain(connection.shop_domain)}/admin/api/{SHOPIFY_VERSION}/graphql.json'
    for attempt in range(2):
        response = await http.request('POST', url,
            headers={'X-Shopify-Access-Token': decrypt(connection.credentials_encrypted)['access_token']},
            json={'query': query, 'variables': variables or {}})
        if response.status_code != 401 or attempt:
            break
        await refresh_token(http, db, connection)
    data = response_json(response)
    errors = data.get('errors') or []
    if errors:
        codes = {error.get('extensions', {}).get('code') for error in errors}
        if 'THROTTLED' in codes:
            raise ConnectorError('Shopify GraphQL rate limit reached', retry_after=10)
        raise ConnectorError('Shopify GraphQL request rejected', revoked='ACCESS_DENIED' in codes)
    # Respect the cost bucket before the next page, without sleeping in a request.
    cost = data.get('extensions', {}).get('cost', {})
    throttle = cost.get('throttleStatus', {})
    if throttle and throttle.get('currentlyAvailable', 1000) < max(50, cost.get('requestedQueryCost', 50)):
        connection.next_sync_at = now() + timedelta(seconds=10)
    if not isinstance(data.get('data'), dict):
        raise ConnectorError('Shopify response is missing data')
    return data['data']


SHOP_INFO = '''query ConnectorShop {
  shop { currencyCode }
  currentAppInstallation { accessScopes { handle } }
  locations(first: 100, includeInactive: true) {
    nodes { id name isActive fulfillsOnlineOrders }
    pageInfo { hasNextPage endCursor }
  }
}'''

# Inventory is queried at ONE explicit location per page. No truncated nested
# variant/level connections and no aggregate inventoryQuantity branch inference.
VARIANTS = '''query ConnectorVariants($after: String, $location: ID!) {
  productVariants(first: 50, after: $after, sortKey: ID) {
    nodes {
      id title sku price updatedAt requiresComponents
      product { id title description productType status updatedAt onlineStoreUrl requiresSellingPlan }
      inventoryItem { id tracked inventoryLevel(locationId: $location) {
        updatedAt quantities(names: ["available"]) { name quantity }
      } }
    }
    pageInfo { hasNextPage endCursor }
  }
}'''


async def shop_info(http, db, connection):
    data = await graphql(http, db, connection, SHOP_INFO)
    scopes = [s['handle'] for s in data['currentAppInstallation']['accessScopes']]
    validate_scopes(scopes)
    connection.scopes = scopes
    if data['locations']['pageInfo']['hasNextPage']:
        raise ConnectorError('Store exceeds the pilot limit of 100 source locations')
    connection.settings = {**connection.settings, 'currency': data['shop']['currencyCode']}
    return [dict(source_location_id=n['id'], name=n['name'], active=n['isActive'], kind='physical')
            for n in data['locations']['nodes']]


async def shopify_page(http, db, connection, location, after=None):
    data = await graphql(http, db, connection, VARIANTS, {'after': after, 'location': location})
    rows = []
    currency = connection.settings['currency']
    for variant in data['productVariants']['nodes']:
        product, item = variant['product'], variant['inventoryItem']
        level = item.get('inventoryLevel')
        available = next((q['quantity'] for q in (level or {}).get('quantities', []) if q['name'] == 'available'), None)
        rows.append({
            'source_location_id': location, 'source_product_id': product['id'],
            'source_variant_id': variant['id'], 'sku': (variant.get('sku') or variant['id'])[:90],
            'catalog_at': max(filter(None, [timestamp(variant['updatedAt']), timestamp(product['updatedAt'])])),
            'inventory_at': timestamp(level.get('updatedAt')) if level else None,
            'name': (product['title'] + ('' if variant['title'] == 'Default Title' else ' — ' + variant['title']))[:180],
            'description': product.get('description', '')[:10000],
            'category': (product.get('productType') or 'Miscellaneous')[:90],
            'price_cents': money_cents(variant['price'], currency), 'currency': currency,
            'quantity': quantity(available) if item['tracked'] else None,
            'source_active': product['status'] == 'ACTIVE' and bool(product.get('onlineStoreUrl')),
            'native_checkout_supported': not product.get('requiresSellingPlan') and not variant.get('requiresComponents'),
            'inventory_item_id': item['id'],
        })
    return rows, data['productVariants']['pageInfo']


async def woo_request(http, connection, method, path, **kwargs):
    creds = decrypt(connection.credentials_encrypted)
    response = await http.request(method, connection.store_url + '/wp-json/wc/v3/' + path,
                                  auth=httpx.BasicAuth(creds['consumer_key'], creds['consumer_secret']), **kwargs)
    return response_json(response), response.headers


async def verify_woo(http, connection):
    # edit context requires authorized read access, unlike the public API index.
    data, _ = await woo_request(http, connection, 'GET', 'products', params={'context': 'edit', 'per_page': 1})
    if not isinstance(data, list):
        raise ConnectorError('Store did not return a WooCommerce product list')
    currency, _ = await woo_request(http, connection, 'GET', 'data/currencies/current')
    code = currency.get('code', '')
    money_cents('0', code)
    connection.settings = {**connection.settings, 'currency': code}


def woo_row(connection, item, parent=None):
    parent = parent or item
    variant_id = str(item['id'])
    if not re.fullmatch(r'[1-9]\d*', variant_id):
        raise ConnectorError('Invalid WooCommerce variant ID')
    managed = item.get('manage_stock') is True
    active = parent.get('status') == 'publish' and item.get('status', 'publish') == 'publish'
    attributes = [str(a.get('option', '')) for a in item.get('attributes', [])]
    return {
        'source_location_id': 'online', 'source_product_id': str(parent['id']),
        'source_variant_id': variant_id, 'sku': (item.get('sku') or 'woo-' + variant_id)[:90],
        'catalog_at': timestamp(item.get('date_modified_gmt') or item.get('date_created_gmt')),
        'inventory_at': timestamp(item.get('date_modified_gmt') or item.get('date_created_gmt')),
        'name': (parent.get('name', 'Product') + (' — ' + ' / '.join(attributes) if parent is not item and attributes else ''))[:180],
        'description': re.sub('<[^>]*>', '', item.get('description') or parent.get('description', ''))[:10000],
        'category': ((parent.get('categories') or [{'name': 'Miscellaneous'}])[0]['name'])[:90],
        'price_cents': money_cents(item.get('price', ''), connection.settings['currency']),
        'currency': connection.settings['currency'],
        'quantity': quantity(item.get('stock_quantity')) if managed else None,
        'source_active': active and item.get('stock_status') == 'instock',
        'native_checkout_supported': item.get('type', 'variation') in {'simple', 'variation'},
    }


async def woo_page(http, connection, cursor):
    """One provider page; variable parents kept in a bounded durable cursor."""
    cursor = dict(cursor)
    parents = list(cursor.get('parents', []))
    if parents:
        parent = parents[0]
        page = cursor.get('variation_page', 1)
        data, headers = await woo_request(http, connection, 'GET', f"products/{parent['id']}/variations",
                                          params={'per_page': 50, 'page': page, 'context': 'edit'})
        rows = [woo_row(connection, item, parent) for item in data]
        more = page < int(headers.get('X-WP-TotalPages', page + int(len(data) == 50)))
        if more:
            cursor['variation_page'] = page + 1
        else:
            cursor['parents'], cursor['variation_page'] = parents[1:], 1
        return rows, cursor, not more and not cursor.get('parents') and cursor.get('products_done', False)
    page = cursor.get('page', 1)
    data, headers = await woo_request(http, connection, 'GET', 'products',
        params={'per_page': 50, 'page': page, 'context': 'edit', 'orderby': 'id', 'order': 'asc'})
    rows = []
    for item in data:
        if item.get('type') == 'variable':
            # Only the fields needed to describe child variants enter this cursor.
            parents.append({k: item.get(k) for k in ('id', 'name', 'description', 'categories', 'status')})
        elif item.get('type') == 'simple':
            rows.append(woo_row(connection, item))
    more = page < int(headers.get('X-WP-TotalPages', page + int(len(data) == 50)))
    cursor.update(page=page + 1, parents=parents, products_done=not more, variation_page=1)
    return rows, cursor, not more and not parents


async def register_webhooks(http, db, connection):
    """Explicit merchant action; read-only Woo keys can still use snapshot sync."""
    url = public_api_url() + f'/api/connectors/{connection.provider}/{connection.id}/webhook'
    registered = dict(connection.settings.get('webhook_ids', {}))
    topics = SHOPIFY_TOPICS if connection.provider == 'shopify' else WOO_TOPICS
    for topic in topics:
        if topic in registered:
            continue
        if connection.provider == 'shopify':
            data = await graphql(http, db, connection, '''mutation ConnectorWebhook($topic: WebhookSubscriptionTopic!, $sub: WebhookSubscriptionInput!) {
              webhookSubscriptionCreate(topic: $topic, webhookSubscription: $sub) {
                webhookSubscription { id } userErrors { field message }
              }
            }''', {'topic': topic, 'sub': {'uri': url, 'format': 'JSON'}})
            result = data['webhookSubscriptionCreate']
            if result['userErrors'] or not result.get('webhookSubscription'):
                raise ConnectorError('Shopify webhook subscription was rejected')
            registered[topic] = result['webhookSubscription']['id']
        else:
            # Unsigned setup ping has no authority and never enters the queue.
            result, _ = await woo_request(http, connection, 'POST', 'webhooks', json={
                'name': 'PayFound ' + topic, 'topic': topic, 'delivery_url': url,
                'secret': decrypt(connection.credentials_encrypted)['webhook_secret'], 'status': 'active'})
            registered[topic] = str(result['id'])
        connection.settings = {**connection.settings, 'webhook_ids': dict(registered)}
        db.commit()
    connection.capabilities = capabilities(connection.provider, authorized=True, webhooks=True)
