"""One opt-in live Channel3 browser query; no purchases or retailer navigation."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true', required=True, help='Use one configured Channel3 search credit')
    parser.parse_args()
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto('http://127.0.0.1:5173/explore?q=USB-C%2065W%20charger')
        button = page.get_by_role('button', name='Compare online offers', exact=True)
        expect(button).to_be_enabled(timeout=30000)
        with page.expect_response(lambda response: '/api/online/search?' in response.url, timeout=30000) as requested:
            button.click()
        response = requested.value
        assert response.status == 200
        data = response.json()
        assert data['online_only'] and not data['verified_local_stock'] and data['offers']
        section = page.locator('section').filter(has=page.get_by_role('heading', name='Looking further afield?'))
        expect(section.get_by_text('Online only', exact=True)).to_have_count(len(data['offers']))
        section.screenshot(path=str(ROOT / 'docs/evidence/channel3-live-ui.png'))
        browser.close()
    result = {'status': 'passed', 'offers_rendered': len(data['offers']), 'online_only': True, 'page_errors': errors}
    (ROOT / 'docs/evidence/online-ui-check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit('Online UI produced a browser error')


if __name__ == '__main__':
    run()
