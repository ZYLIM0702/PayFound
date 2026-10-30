"""Browser acceptance against the local synthetic-data stack. No real payments."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidence'
BASE = 'http://127.0.0.1:5173'


def run():
    errors, results = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000})
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        # Deterministic UI acceptance uses mock checkout explicitly, while a
        # separate integration probe verifies real PayPal sandbox order creation.
        def config_route(route):
            response = route.fetch()
            data = response.json()
            assert data['demo_mode'], 'Browser acceptance must run on the synthetic local stack'
            data['paypal_sandbox_enabled'] = False
            route.fulfill(response=response, json=data)
        page.route('**/api/config', config_route)
        for width in (390, 768, 1440):
            page.set_viewport_size({'width': width, 'height': 1000})
            for path, name in (('/', 'home'), ('/explore?q=charger', 'explore'), ('/stores/northside-electronics', 'store'), ('/agent', 'agent')):
                page.goto(BASE + path, wait_until='domcontentloaded')
                expect(page.locator('main h1')).to_be_visible(timeout=30000)
                page.screenshot(path=str(EVIDENCE / f'{name}-{width}.png'), full_page=True)
                overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')
                results.append({'route': path, 'width': width, 'horizontal_overflow': overflow})
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.goto(BASE + '/explore?q=charger')
        page.get_by_test_id('add-to-cart-p1').click()
        page.get_by_test_id('cart-link').click()
        page.get_by_test_id('buyer-name').fill('Browser acceptance shopper')
        page.get_by_test_id('reserve-basket').click()
        page.wait_for_url('**/checkout/**')
        order_id = page.url.rsplit('/', 1)[-1]
        expect(page.get_by_role('heading', name='Checkout', exact=True)).to_be_visible(timeout=30000)
        expect(page.get_by_test_id('simulate-payment')).to_be_visible()
        page.screenshot(path=str(EVIDENCE / 'checkout-1440.png'), full_page=True)
        page.get_by_test_id('simulate-payment').click()
        expect(page.get_by_role('heading', name='Payment confirmed')).to_be_visible()
        page.get_by_label('Switch demo role').select_option('merchant')
        expect(page.get_by_role('heading', name='Merchant workspace')).to_be_visible()
        page.get_by_role('button', name='Orders', exact=True).click()
        for state in ('ACCEPTED', 'PREPARING', 'READY', 'COLLECTED'):
            row = page.locator('.ag-row').filter(has_text=order_id).first
            expect(row).to_be_visible()
            row.get_by_role('button', name=f'{state} →', exact=True).click()
            expect(row).to_contain_text(state)
        page.screenshot(path=str(EVIDENCE / 'merchant-orders-1440.png'), full_page=True)
        for tab in ('Pickup', 'Analytics', 'Connections', 'Settings', 'Agents'):
            page.get_by_role('button', name=tab, exact=True).click()
            page.wait_for_timeout(1200)
            page.screenshot(path=str(EVIDENCE / f'merchant-{tab.lower()}-1440.png'), full_page=True)
        for width in (390, 768):
            page.set_viewport_size({'width': width, 'height': 1000})
            page.get_by_role('button', name='Overview', exact=True).click()
            page.screenshot(path=str(EVIDENCE / f'merchant-{width}.png'), full_page=True)
            results.append({'route': '/merchant', 'width': width, 'horizontal_overflow': page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')})
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.get_by_label('Switch demo role').select_option('consumer')
        page.goto(BASE + '/orders')
        page.get_by_role('button', name='Leave review').last.click()
        page.get_by_label('Your pickup experience').fill('Verified browser acceptance review')
        page.get_by_role('button', name='Submit review').click()
        expect(page.get_by_text('Review submitted. Thank you.')).to_be_visible()
        page.get_by_label('Switch demo role').select_option('admin')
        expect(page.locator('main h1')).to_be_visible()
        page.screenshot(path=str(EVIDENCE / 'admin-1440.png'), full_page=True)
        for width in (390, 768):
            page.set_viewport_size({'width': width, 'height': 1000})
            page.screenshot(path=str(EVIDENCE / f'admin-{width}.png'), full_page=True)
            results.append({'route': '/admin', 'width': width, 'horizontal_overflow': page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')})
        context.close()
        browser.close()
    result = {'journey': 'synthetic basket → mock payment → fulfilment → review → admin', 'order_id': order_id,
              'screens': results, 'page_errors': errors}
    (EVIDENCE / 'browser-check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if errors or any(r['horizontal_overflow'] for r in results):
        raise SystemExit('Browser acceptance found layout or JavaScript errors; inspect evidence.')


if __name__ == '__main__':
    run()
