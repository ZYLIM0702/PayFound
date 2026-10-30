"""Exercise the actual local POS UI and synthetic platform bridge. No provider calls."""
from datetime import datetime, timezone
import json
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidence'
BASE = 'http://127.0.0.1:5173'
HEADERS = {'x-demo-role': 'merchant'}


def run():
    errors, layouts, checks, receipts = [], [], [], []
    with httpx.Client(base_url='http://127.0.0.1:8000/api', headers=HEADERS, timeout=30) as api:
        assert api.get('/config').json()['demo_mode']
        def state():
            response = api.get('/pos-simulator/state?merchant_id=m1')
            response.raise_for_status()
            return response.json()
        def stock(product_id):
            response = api.get('/products', params={'ids': product_id})
            response.raise_for_status()
            return response.json()[0]['quantity']
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1440, 'height': 1050})
            page.on('pageerror', lambda error: errors.append(str(error)))
            def screenshot(name):
                page.evaluate('window.scrollTo(0, 0)')
                page.screenshot(path=str(EVIDENCE / name), full_page=True)
            page.goto(BASE + '/pos/sell', wait_until='domcontentloaded')
            page.get_by_role('button', name='Enter merchant demo').click(timeout=30000)
            expect(page.locator('.pos-sidebar')).to_be_visible(timeout=30000)
            page.wait_for_timeout(600)
            connect = page.get_by_role('button', name='Connect demo register')
            if connect.is_visible():
                connect.click()
            expect(page.get_by_role('heading', name='Ready for your next sale.')).to_be_visible(timeout=30000)
            if not state()['online']:
                page.get_by_role('button', name='Resume platform sync').click()
            if stock('p1') < 3:
                api.post('/pos-simulator/stock-count?merchant_id=m1', json={'product_id': 'p1', 'quantity': 9}).raise_for_status()
                page.get_by_role('button', name='Sync now', exact=True).click()
            screenshot('pos-register-empty-1440.png')
            before = {pid: stock(pid) for pid in ('p1', 'pos-demo-headphones', 'pos-demo-speaker')}

            page.get_by_test_id('pos-product-pos-demo-headphones').click()
            page.get_by_test_id('pos-product-p1').click()
            page.get_by_role('button', name='Discount', exact=True).click()
            page.get_by_label('Discount percentage').fill('20')
            screenshot('pos-discount-1440.png')
            page.get_by_role('button', name='Apply discount').click()
            expect(page.get_by_test_id('pos-cart-total')).to_have_text('$95.91')
            page.get_by_role('button', name='Save cart', exact=True).click()
            expect(page.get_by_text('Good things start here.')).to_be_visible()
            page.get_by_role('button', name='Saved (1)', exact=True).click()
            page.get_by_role('button', name='Restore cart', exact=True).click()
            expect(page.get_by_test_id('pos-cart-total')).to_have_text('$95.91')
            screenshot('pos-register-1440.png')
            checks.append('cart, 20% discount, saved cart restore')

            def charge(outcome='approved'):
                page.locator('.pos-checkout-button').click()
                if outcome == 'declined':
                    page.get_by_label('Simulated card result').select_option('declined')
                with page.expect_response(lambda response: '/pos-simulator/sales?' in response.url and response.request.method == 'POST') as received:
                    page.get_by_role('button', name='Complete simulated sale', exact=True).click()
                response = received.value
                assert response.status == 200
                payload = response.json()
                assert payload['receipt']['simulated']
                receipts.append(payload['receipt']['id'])
                return payload

            sold = charge()
            expect(page.get_by_role('heading', name='Sale complete.')).to_be_visible()
            assert sold['receipt']['total_cents'] == 9591 and sold['receipt']['sync_status'] == 'ACKNOWLEDGED'
            assert stock('p1') == before['p1'] - 1
            assert stock('pos-demo-headphones') == before['pos-demo-headphones'] - 1
            screenshot('pos-sale-receipt-1440.png')
            with page.expect_download() as download:
                page.get_by_role('button', name='Download receipt').click()
            assert download.value.suggested_filename.endswith('-simulation.txt')
            page.get_by_role('button', name='Back to workspace').click()
            checks.append('approved simulation, receipt download, actual platform stock update')

            page.get_by_role('button', name='Pause platform sync', exact=True).click()
            expect(page.get_by_role('button', name='Resume platform sync', exact=True)).to_be_visible()
            page.get_by_test_id('pos-product-pos-demo-headphones').click()
            queued = charge()
            assert queued['receipt']['sync_status'] == 'QUEUED'
            assert stock('pos-demo-headphones') == before['pos-demo-headphones'] - 1
            page.get_by_role('button', name='Back to workspace').click()
            page.locator('.pos-sidebar a[href="/pos/sync"]').click()
            expect(page.get_by_text('1 queued · 0 conflicts')).to_be_visible()
            screenshot('pos-sync-paused-1440.png')
            page.get_by_role('button', name='Resume & sync', exact=True).click()
            expect(page.get_by_text('Up to date', exact=True)).to_be_visible()
            assert stock('pos-demo-headphones') == before['pos-demo-headphones'] - 2
            for _ in range(2):
                api.post('/pos-simulator/sync?merchant_id=m1').raise_for_status()
            assert stock('pos-demo-headphones') == before['pos-demo-headphones'] - 2
            screenshot('pos-sync-1440.png')
            checks.append('paused bridge, queued sale, resume, duplicate sync without extra deduction')

            page.locator('.pos-sidebar a[href="/pos/sell"]').click()
            page.get_by_test_id('pos-product-pos-demo-speaker').click()
            rejected = charge('declined')
            expect(page.get_by_role('heading', name='Payment declined', exact=True)).to_be_visible()
            assert rejected['receipt']['status'] == 'DECLINED' and stock('pos-demo-speaker') == before['pos-demo-speaker']
            screenshot('pos-declined-1440.png')
            page.get_by_role('button', name='Try again', exact=True).click()
            with page.expect_response(lambda response: '/pos-simulator/sales?' in response.url and response.request.method == 'POST') as retry:
                page.get_by_role('button', name='Complete simulated sale', exact=True).click()
            assert retry.value.status == 200 and retry.value.json()['receipt']['status'] == 'COMPLETED'
            receipts.append(retry.value.json()['receipt']['id'])
            expect(page.get_by_role('heading', name='Sale complete.')).to_be_visible()
            assert stock('pos-demo-speaker') == before['pos-demo-speaker'] - 1
            page.get_by_role('button', name='Back to workspace').click()
            checks.append('decline leaves stock untouched; explicit retry creates one successful sale')

            api.patch('/merchant/products/pos-demo-stand/stock', json={'quantity': 21}).raise_for_status()
            page.locator('.pos-sidebar a[href="/pos/products"]').click()
            page.get_by_role('button', name='Next Page', exact=True).click()
            row = page.locator('.ag-row').filter(has_text='SIM-STAND').first
            expect(row.get_by_role('button', name='Record count')).to_be_visible(timeout=30000)
            expect(row.locator('[col-id="quantity"]')).to_have_text('21', timeout=12000)
            row.get_by_role('button', name='Record count').click()
            page.get_by_label('On-hand quantity').fill('20')
            page.get_by_role('button', name='Save count', exact=True).click()
            expect(row.locator('[col-id="quantity"]')).to_have_text('20')
            assert stock('pos-demo-stand') == 20
            page.get_by_role('button', name='First Page', exact=True).click()
            screenshot('pos-products-1440.png')
            checks.append('platform-to-POS catalog refresh; POS-to-platform stock count')

            for view, title in (('overview', 'A good day, at a glance.'), ('receipts', 'Receipts, all together.'),
                                ('orders', 'Online meets in-store.'), ('settings', 'A simulator with a purpose.')):
                page.locator(f'.pos-sidebar a[href="/pos/{view}"]').click()
                expect(page.get_by_role('heading', name=title)).to_be_visible()
                page.wait_for_timeout(350)
                screenshot(f'pos-{view}-1440.png')
            page.locator('.pos-sidebar a[href="/pos/sell"]').click()
            page.get_by_role('button', name='Scan a product', exact=True).click()
            page.get_by_label('Product SKU', exact=True).fill('SIM-CABLE')
            page.get_by_role('button', name='Add to current sale', exact=True).click()
            expect(page.locator('.pos-cart-items')).to_contain_text('Braided Lightning cable')
            page.locator('.pos-checkout-button').click()
            page.get_by_role('button', name='Cash', exact=False).click()
            with page.expect_response(lambda response: '/pos-simulator/sales?' in response.url and response.request.method == 'POST') as cash_sale:
                page.get_by_role('button', name='Complete simulated sale', exact=True).click()
            assert cash_sale.value.status == 200 and cash_sale.value.json()['receipt']['payment_method'] == 'cash'
            receipts.append(cash_sale.value.json()['receipt']['id'])
            page.get_by_role('button', name='Back to workspace').click()
            page.set_viewport_size({'width': 390, 'height': 850})
            page.get_by_test_id('pos-product-pos-demo-cable').click()
            expect(page.get_by_role('button', name='View current sale', exact=True)).to_be_visible()
            page.get_by_role('button', name='View current sale', exact=True).click()
            expect(page.locator('.pos-checkout-button')).to_be_in_viewport(timeout=10000)
            page.screenshot(path=str(EVIDENCE / 'pos-mobile-cart-390.png'))
            page.get_by_role('button', name='Clear current sale', exact=True).click()
            checks.append('SKU scan, simulated cash sale, mobile cart access, overview, receipts, online orders, settings')

            for width in (1440, 1024, 768, 390):
                page.set_viewport_size({'width': width, 'height': 1000})
                for view in ('sell', 'sync', 'overview', 'products', 'receipts', 'orders'):
                    page.locator(f'.pos-sidebar a[href="/pos/{view}"]').click()
                    expect(page.locator('#pos-main h1')).to_be_visible()
                    page.wait_for_timeout(200)
                    overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')
                    layouts.append({'view': view, 'width': width, 'horizontal_overflow': overflow})
                    if width in (768, 390) and view in ('sell', 'sync', 'overview'):
                        screenshot(f'pos-{view}-{width}.png')
            browser.close()
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'status': 'passed' if not errors and not any(x['horizontal_overflow'] for x in layouts) else 'failed',
              'mode': 'local software simulation; no PayPal or Zettle calls', 'checks': checks,
              'receipt_ids': receipts, 'layouts': layouts, 'page_errors': errors}
    (EVIDENCE / 'pos-browser-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    assert report['status'] == 'passed'


if __name__ == '__main__':
    run()
