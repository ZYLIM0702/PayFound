"""Verify local photo delivery and UI without making purchases or changing stock."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import httpx
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidence'
CATALOGUE = json.loads((ROOT / 'apps/api/app/demo_photos.json').read_text())['products']
EXPANDED = ROOT / 'apps/api/app/demo_catalogue.json'
if EXPANDED.exists():
    CATALOGUE += json.loads(EXPANDED.read_text())['products']


def products(api):
    response = api.get('/products', params={'limit': 1000, 'radius_km': 20040})
    response.raise_for_status()
    wanted = {p['id'] for p in CATALOGUE}
    return [p for p in response.json() if p['id'] in wanted]


def invariants(rows):
    return {p['id']: {key: p.get(key) for key in ('merchant_id', 'sku', 'price_cents', 'currency', 'quantity',
        'available_quantity', 'stock_updated_at')} for p in rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot', action='store_true')
    args = parser.parse_args()
    with httpx.Client(base_url='http://127.0.0.1:8000/api', timeout=20) as api:
        assert api.get('/config').json()['demo_mode']
        current = products(api)
        snapshot_path = EVIDENCE / 'product-photo-inventory-before.json'
        if args.snapshot:
            snapshot_path.write_text(json.dumps(invariants(current), indent=2) + '\n')
            print(f'Saved metadata-refresh inventory baseline for {len(current)} demo products')
            return
        before = json.loads(snapshot_path.read_text())
        after = invariants(current)
        assert all(after.get(pid) == value for pid, value in before.items()), 'Photo refresh must not reset prices, stock, holds or freshness'
        expected = {p['id']: p for p in CATALOGUE}
        assert len(current) == len(expected)
        for product in current:
            assert product['image_url'] == '/images/products/' + product['id'] + '.webp'
            assert product['name'] == expected[product['id']]['name']
        manifest = httpx.get('http://127.0.0.1:5173/images/products/manifest.json', timeout=20).json()
        total_bytes = 0
        for photo in manifest['products']:
            response = httpx.get('http://127.0.0.1:5173' + photo['image_url'], timeout=20)
            assert response.status_code == 200 and 'image/webp' in response.headers['content-type']
            assert hashlib.sha256(response.content).hexdigest() == photo['asset_sha256']
            assert photo['author'] and photo['license'] and photo['source_url']
            total_bytes += len(response.content)
        existing_orders = api.get('/orders', headers={'x-demo-role': 'consumer'}).json()
        existing_order = next((o for o in existing_orders if not o['id'].startswith('seed-') and o.get('items') and o['payment_status'] == 'CAPTURED'), None)

    errors, layouts, checks = [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1050})
        page.on('pageerror', lambda issue: errors.append(str(issue)))
        page.goto('http://127.0.0.1:5173/pos/sell')
        page.get_by_role('button', name='Enter merchant demo').click(timeout=30000)
        expect(page.locator('.pos-tile')).to_have_count(12, timeout=30000)
        for image in page.locator('.pos-tile .pf-product-photo img').all():
            image.scroll_into_view_if_needed()
            expect(image).to_be_visible()
        assert page.locator('.pos-tile .pf-product-photo img').count() == 12
        page.wait_for_function('Array.from(document.querySelectorAll(".pos-tile .pf-product-photo img")).every(i => i.complete && i.naturalWidth === 600)')
        page.get_by_test_id('pos-product-pos-demo-headphones').click()
        expect(page.locator('.pos-cart-mini img')).to_be_visible()
        page.evaluate('window.scrollTo(0, 0)')
        page.screenshot(path=str(EVIDENCE / 'pos-real-photos-1440.png'), full_page=True)
        page.set_viewport_size({'width': 390, 'height': 900})
        page.evaluate('window.scrollTo(0, 0)')
        page.screenshot(path=str(EVIDENCE / 'pos-real-photos-390.png'), full_page=True)
        layouts.append({'route': '/pos/sell', 'width': 390,
                        'horizontal_overflow': page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')})
        page.set_viewport_size({'width': 1440, 'height': 1050})
        page.get_by_role('button', name='Clear current sale', exact=True).click()
        checks.append('12 POS product photos and matching cart thumbnail loaded locally')

        for route, filename, count in [('/stores/northside-electronics', 'store-real-photos', 12), ('/explore', 'catalogue-real-photos', 24)]:
            page.goto('http://127.0.0.1:5173' + route)
            expect(page.locator('.pf-product-photo img')).to_have_count(count, timeout=30000)
            for image in page.locator('.pf-product-photo img').all():
                image.scroll_into_view_if_needed()
            page.wait_for_function('Array.from(document.querySelectorAll(".pf-product-photo img")).every(i => i.complete && i.naturalWidth === 600)')
            for width in (1440, 390):
                page.set_viewport_size({'width': width, 'height': 1000})
                page.evaluate('window.scrollTo(0, 0)')
                page.screenshot(path=str(EVIDENCE / f'{filename}-{width}.png'), full_page=True)
                layouts.append({'route': route, 'width': width, 'horizontal_overflow': page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')})
            checks.append(f'{count} local photos loaded on {route}')
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.goto('http://127.0.0.1:5173/stores/northside-electronics')
        page.get_by_test_id('add-to-cart-p1').click()
        page.get_by_test_id('cart-link').click()
        expect(page.locator('[data-testid="cart-item-p1"] img')).to_be_visible()
        page.screenshot(path=str(EVIDENCE / 'basket-real-photos-1440.png'), full_page=True)
        checks.append('Consumer basket displays the same product photograph')
        if existing_order:
            page.goto('http://127.0.0.1:5173/checkout/' + existing_order['id'])
            expect(page.locator('.pf-line-photo img').first).to_be_visible(timeout=30000)
            page.screenshot(path=str(EVIDENCE / 'checkout-real-photos-1440.png'), full_page=True)
            page.goto('http://127.0.0.1:5173/orders')
            expect(page.locator('.pf-line-photo img').first).to_be_visible(timeout=30000)
            checks.append('Existing checkout and order-list thumbnails load without any payment action')
        page.goto('http://127.0.0.1:5173/image-credits.html')
        expect(page.get_by_role('heading', name='Real photographs. Clear credits.')).to_be_visible()
        assert page.locator('article').count() == len(CATALOGUE)
        page.screenshot(path=str(EVIDENCE / 'product-image-credits-1440.png'), full_page=True)
        browser.close()
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'status': 'passed', 'photos': len(current),
        'total_webp_bytes': total_bytes, 'inventory_and_prices_preserved': True, 'checks': checks,
        'layouts': layouts, 'page_errors': errors, 'credits_url': '/image-credits.html'}
    if errors or any(row['horizontal_overflow'] for row in layouts):
        report['status'] = 'failed'
    (EVIDENCE / 'product-photo-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    assert report['status'] == 'passed'


if __name__ == '__main__':
    main()
