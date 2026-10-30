"""Live Google-map UX + native test geolocation + product/compare acceptance."""
from datetime import datetime, timezone
import json
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidence'
BASE = 'http://127.0.0.1:5173'


def run():
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'status': 'running',
              'location': 'Explicit SF test coordinates; native browser geolocation grant', 'checks': [], 'layouts': [], 'page_errors': []}
    phase = 'catalogue'
    keys = []
    try:
        with httpx.Client(base_url='http://127.0.0.1:8000/api', timeout=30) as api:
            config = api.get('/config').json()
            assert config['demo_mode'] and config['routing']['provider'] == 'google'
            keys = [config['routing']['google_maps_browser_key']]
            summary = api.get('/catalogue/summary').json()
            assert summary['distinct_products'] >= 200 and summary['offers'] >= 244 and summary['stores'] >= 13
            report['catalogue'] = summary
            offers = api.get('/products?limit=1000').json()
            assert len(offers) >= 244
            for offer in offers:
                response = api.get('/products/' + offer['id'])
                assert response.status_code == 200 and response.json()['id'] == offer['id']
            report['checks'].append(f'Every public product offer has a detail endpoint ({len(offers)} checked)')
            p1 = api.get('/products/p1').json()
            assert len(p1['offers']) >= 2
        def redact(value):
            text = str(value)
            for key in keys:
                text = text.replace(key, '[redacted]')
            return text
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width':1440,'height':1050},
                geolocation={'latitude':37.7786,'longitude':-122.414,'accuracy':20}, permissions=['geolocation'])
            page = context.new_page()
            page.on('pageerror', lambda issue: report['page_errors'].append(redact(issue)))
            phase = 'Google Maps load'
            page.goto(BASE + '/explore', wait_until='domcontentloaded')
            expect(page.locator('.pf-google-map .gm-style')).to_be_visible(timeout=45000)
            page.wait_for_function('Number(document.querySelector(".pf-google-map")?.dataset.mapZoom) > 0', timeout=45000)
            assert not page.locator('.gm-err-container').count(), 'Google Maps authorization/billing error'
            report['checks'].append('Genuine Google Maps JavaScript map rendered with store markers')
            page.evaluate('window.scrollTo(0,0)')
            page.screenshot(path=str(EVIDENCE / 'discovery-google-map-1440.png'), full_page=False)
            phase = 'location permission'
            page.get_by_role('button', name='Use my location', exact=True).click()
            expect(page.get_by_text('Location shared for this app session', exact=False)).to_be_visible(timeout=20000)
            page.get_by_test_id('explore-search').fill('USB-C 36W')
            page.get_by_role('button', name='Search local', exact=True).click()
            card = page.get_by_test_id('product-p1')
            expect(card).to_be_visible(timeout=30000)
            expect(card.locator('.pf-card-distance')).to_contain_text('from you · straight-line')
            phase = 'store fly/zoom'
            card.locator('.pf-product-photo-link').click()
            expect(page.locator('[data-testid="store-map"]')).to_have_attribute('data-focus-id', 'p1')
            page.wait_for_function('Number(document.querySelector(".pf-google-map")?.dataset.mapZoom) >= 16', timeout=20000)
            page.wait_for_function('Math.abs(Number(document.querySelector(".pf-google-map")?.dataset.mapLatitude) - 37.7744) < .0005 && Math.abs(Number(document.querySelector(".pf-google-map")?.dataset.mapLongitude) + 122.4212) < .0005', timeout=20000)
            expect(page.locator('.pf-map-panel-head')).to_contain_text('Northside', timeout=10000)
            report['checks'].append('Photo/card focuses the correct store at zoom 16 and shows user-relative distance')
            phase = 'live traffic route'
            with page.expect_response(lambda r: '/api/routing/route' in r.url and r.request.method == 'POST', timeout=40000) as result:
                page.get_by_role('button', name='Show driving route', exact=True).click()
            response = result.value
            assert response.status == 200
            route = response.json()
            assert route['provider'] == 'google' and route['traffic_aware'] and route['duration_seconds'] > 0
            assert route['distance_m'] > 0 and len(route['coordinates']) > 2
            expect(page.get_by_test_id('driving-route-result')).to_contain_text('Traffic-aware ETA')
            expect(page.locator('[data-testid="store-map"]')).to_have_attribute('data-route-visible', 'true')
            expect(page.get_by_role('button', name='Traffic on', exact=True)).to_have_attribute('aria-pressed', 'true')
            page.evaluate('window.scrollTo(0,200)')
            page.screenshot(path=str(EVIDENCE / 'discovery-traffic-route-1440.png'))
            report['google_route_http_status'] = 200
            report['checks'].append('Genuine Google traffic-aware driving route, ETA, arrival, route line and traffic layer')
            # Stop auto-refresh before the remaining checks; do not keep making
            # provider requests after the bounded live acceptance step.
            page.locator('.pf-selected-store').get_by_role('button', name='Clear selected store').click()
            phase = 'product and comparison pages'
            card.get_by_role('link', name=p1['name'], exact=True).click()
            page.wait_for_url('**/products/p1')
            expect(page.get_by_role('heading', name=p1['name'], exact=True, level=1)).to_be_visible(timeout=30000)
            expect(page.locator('.pf-store-offers article')).to_have_count(2)
            assert len(set(page.locator('.pf-store-offers .pf-product-photo').evaluate_all('els => els.map(el => getComputedStyle(el).backgroundColor)'))) == 2
            page.locator('.pf-product-info-grid .pf-google-map').scroll_into_view_if_needed()
            page.wait_for_function('Number(document.querySelector(".pf-product-info-grid .pf-google-map")?.dataset.mapZoom) >= 16', timeout=30000)
            page.screenshot(path=str(EVIDENCE / 'product-detail-store-map-1440.png'))
            page.evaluate('window.scrollTo(0,0)')
            page.screenshot(path=str(EVIDENCE / 'product-detail-compare-1440.png'), full_page=True)
            page.locator('.pf-store-offers a').filter(has_text='View this offer').first.click()
            page.wait_for_url('**/products/offer-*')
            expect(page.locator('.pf-product-summary h1')).to_be_visible(timeout=30000)
            expect(page.locator('.pf-product-price > strong')).to_have_text(f"${min(p['price_cents'] for p in p1['offers']) / 100:.2f}")
            report['checks'].append('Product name navigates to detail page; cross-store prices, identity and merchant photo styles work')
            phase = 'responsive detail'
            for width in (1440,768,390):
                page.set_viewport_size({'width':width,'height':1000})
                page.evaluate('window.scrollTo(0,0)')
                report['layouts'].append({'route':'product detail','width':width,'horizontal_overflow':page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')})
                if width == 390:
                    page.screenshot(path=str(EVIDENCE / 'product-detail-390.png'), full_page=True)
            phase = 'pagination and responsive discovery'
            page.get_by_role('link', name='Explore products', exact=True).click()
            expect(page.locator('.pf-discovery-products article')).to_have_count(24, timeout=30000)
            first_ids = page.locator('.pf-discovery-products article').evaluate_all('els => els.map(el => el.dataset.testid)')
            page.get_by_role('button', name='Next', exact=True).click()
            expect(page.locator('.pf-pagination')).to_contain_text('Page 2')
            second_ids = page.locator('.pf-discovery-products article').evaluate_all('els => els.map(el => el.dataset.testid)')
            assert not set(first_ids) & set(second_ids)
            for width in (1440,768,390):
                page.set_viewport_size({'width':width,'height':1000})
                page.evaluate('window.scrollTo(0,0)')
                report['layouts'].append({'route':'explore','width':width,'horizontal_overflow':page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')})
                if width in (768,390):
                    page.screenshot(path=str(EVIDENCE / f'discovery-google-map-{width}.png'), full_page=True)
            report['checks'].append('24-offer pagination is disjoint; discovery and product layouts fit desktop/tablet/mobile')
            phase = 'location revocation'
            page.get_by_role('button', name='Stop using location', exact=False).click()
            expect(page.get_by_role('button', name='Use my location', exact=True)).to_be_visible()
            assert not page.evaluate('Object.keys(localStorage).some(k => /latitude|longitude|geolocation|user-location/i.test(k))')
            report['checks'].append('Location can be cleared and is not persisted in browser storage')
            context.close()
            phase = 'denied location'
            denied = browser.new_context(viewport={'width':390,'height':1000})
            denied.add_init_script('navigator.geolocation.getCurrentPosition = (ok, fail) => fail({code:1});')
            page = denied.new_page()
            page.goto(BASE + '/explore')
            page.get_by_role('button', name='Use my location', exact=True).click(timeout=30000)
            expect(page.get_by_role('alert').filter(has_text='Location blocked.')).to_be_visible()
            assert not page.locator('.pf-card-distance').filter(has_text='from you').count()
            denied.close()
            report['checks'].append('Denied geolocation shows browser-permission help without a fabricated user distance')
            phase = 'late location grant after store switch'
            delayed = browser.new_context(viewport={'width':1440,'height':1000})
            delayed.add_init_script('''navigator.geolocation.getCurrentPosition = (ok) => {
              window.__grantTestLocation = () => ok({coords:{latitude:37.7786,longitude:-122.414,accuracy:20},timestamp:Date.now()});
            };''')
            page = delayed.new_page()
            old_route_requests = []
            def intercept(route):
                old_route_requests.append(route.request.post_data_json.get('product_id'))
                route.fulfill(status=409, json={'detail':'Unexpected stale route request intercepted by test'})
            page.route('**/api/routing/route', intercept)
            page.goto(BASE + '/explore?q=USB-C%2036W')
            first = page.get_by_test_id('product-p1')
            expect(first).to_be_visible(timeout=30000)
            first.locator('.pf-product-photo-link').click()
            page.get_by_role('button', name='Show driving route', exact=True).click()
            page.wait_for_function('typeof window.__grantTestLocation === "function"')
            page.get_by_test_id('product-offer-p1-m5').locator('.pf-product-photo-link').click()
            page.evaluate('window.__grantTestLocation()')
            page.wait_for_timeout(600)
            assert not old_route_requests, 'Late permission grant must not request a route to the previously selected store'
            expect(page.locator('.pf-map-panel-head')).to_contain_text('Market Street Tech')
            delayed.close()
            report['checks'].append('Switching stores during a delayed location grant cancels the old destination before any route request')
            phase = 'outside demo region'
            distant = browser.new_context(viewport={'width':390,'height':1000},
                geolocation={'latitude':3.139,'longitude':101.6869,'accuracy':30}, permissions=['geolocation'])
            page = distant.new_page(); page.goto(BASE + '/explore')
            page.get_by_role('button', name='Use my location', exact=True).click(timeout=30000)
            expect(page.get_by_role('button', name='Browse the San Francisco demo area')).to_be_visible(timeout=20000)
            page.get_by_role('button', name='Browse the San Francisco demo area').click()
            expect(page.locator('.pf-discovery-products article')).to_have_count(24, timeout=30000)
            assert any(int(''.join(c for c in text.split(' km')[0] if c.isdigit())) > 1000 for text in page.locator('.pf-card-distance').all_text_contents())
            distant.close()
            report['checks'].append('Outside-region browsing preserves real user-relative distance instead of pretending the demo stores are nearby')
            browser.close()
        assert not report['page_errors'] and not any(x['horizontal_overflow'] for x in report['layouts'])
        report['status'] = 'passed'
    except Exception as issue:
        report.update(status='failed', phase=phase, error_type=type(issue).__name__)
        if isinstance(issue, AssertionError):
            text = str(issue)
            for key in keys: text = text.replace(key, '[redacted]')
            report['assertion'] = text[:1500]
        raise
    finally:
        (EVIDENCE / 'discovery-browser-check.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    run()
