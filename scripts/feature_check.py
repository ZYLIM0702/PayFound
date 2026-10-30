"""Exercise sponsor persistence, pickup publishing and merchant onboarding locally."""
from pathlib import Path
import json
import uuid
import sqlite3
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def cleanup_fixture(merchant_id, slug):
    """Remove only the empty, exact synthetic business created by this test."""
    path = ROOT / 'apps/api/payfound_demo.db'
    if not path.exists():
        raise RuntimeError('Expected local demo fixture database')
    with sqlite3.connect(path) as db:
        db.execute('PRAGMA foreign_keys=ON')
        row = db.execute('SELECT owner_subject,slug,address FROM merchants WHERE id=?', (merchant_id,)).fetchone()
        if row != ('demo-consumer', slug, '100 Synthetic Test Street, San Francisco') or not slug.startswith('browser-test-'):
            raise RuntimeError('Fixture identity mismatch; no data removed')
        for table in ('orders', 'products', 'connector_connections', 'merchant_reports', 'ai_consent_grants',
                      'agent_runs', 'pickup_slots', 'staff_invitations', 'notifications'):
            if db.execute(f'SELECT 1 FROM {table} WHERE merchant_id=? LIMIT 1', (merchant_id,)).fetchone():
                raise RuntimeError('Fixture has additional data; refusing cleanup')
        db.execute('DELETE FROM merchant_memberships WHERE merchant_id=?', (merchant_id,))
        db.execute('DELETE FROM merchant_locations WHERE merchant_id=?', (merchant_id,))
        db.execute('DELETE FROM merchants WHERE id=?', (merchant_id,))


def run():
    errors = []
    calendar_requests = []
    suffix = uuid.uuid4().hex[:8]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: calendar_requests.append(request.url) if request.method == 'GET' and urlparse(request.url).path == '/api/merchant/pickup-slots' else None)
        def screenshot(name):
            page.locator('main h1').click()
            page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
            page.wait_for_timeout(100)
            page.screenshot(path=str(ROOT / 'docs/evidence' / name), full_page=True)
        page.goto('http://127.0.0.1:5173')
        page.get_by_label('Switch demo role').select_option('merchant')
        expect(page.get_by_role('heading', name='Merchant workspace')).to_be_visible(timeout=30000)
        page.get_by_role('button', name='Analytics', exact=True).click()
        page.get_by_label('Report name', exact=True).fill('Browser report ' + suffix)
        page.get_by_role('button', name='Save report', exact=True).click()
        expect(page.get_by_text('Report saved.', exact=True)).to_be_visible()
        page.get_by_role('button', name='Settings', exact=True).click()
        page.get_by_role('button', name='Analytics', exact=True).click()
        page.get_by_label('Saved report').select_option(label='Browser report ' + suffix)
        expect(page.get_by_label('Report name', exact=True)).to_have_value('Browser report ' + suffix)
        screenshot('analytics-saved-report.png')
        page.get_by_role('button', name='Pickup', exact=True).click()
        times = page.evaluate('''() => {
          const start = new Date(); start.setDate(start.getDate()+1); start.setHours(10, Math.floor(Math.random()*55), 0, 0);
          const end = new Date(start.getTime()+3600000);
          const pad = n => String(n).padStart(2,'0');
          const local = d => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
          return { start: local(start), end: local(end), date: local(start).slice(0,10) };
        }''')
        page.get_by_label('Schedule date').fill(times['date'])
        page.get_by_label('Start (your local time)', exact=True).fill(times['start'])
        page.get_by_label('End (your local time)', exact=True).fill(times['end'])
        page.get_by_label('Capacity', exact=True).fill('2')
        with page.expect_response(lambda response: '/api/merchant/pickup-slots' in response.url and response.request.method == 'POST') as published:
            page.get_by_role('button', name='Publish pickup window', exact=True).click()
        assert published.value.status == 201, published.value.text()
        expect(page.get_by_role('button', name='Publish pickup window', exact=True)).to_be_enabled()
        expect(page.get_by_text('2/2 pickup spaces', exact=False).first).to_be_visible(timeout=15000)
        screenshot('pickup-populated.png')
        def calendar_range(response, minimum, maximum):
            if response.request.method != 'GET' or urlparse(response.url).path != '/api/merchant/pickup-slots':
                return False
            query = parse_qs(urlparse(response.url).query)
            if 'start_at' not in query or 'end_at' not in query:
                return False
            start = datetime.fromisoformat(query['start_at'][0].replace('Z', '+00:00'))
            end = datetime.fromisoformat(query['end_at'][0].replace('Z', '+00:00'))
            return minimum <= (end - start).total_seconds() / 86400 <= maximum
        with page.expect_response(lambda response: calendar_range(response, 6, 8), timeout=15000) as week:
            page.get_by_role('button', name='Week', exact=True).click()
        assert week.value.status == 200
        expect(page.get_by_text('Loading pickup windows…', exact=True)).to_have_count(0)
        before = page.get_by_label('Schedule date').input_value()
        with page.expect_response(lambda response: calendar_range(response, 6, 8), timeout=15000) as moved:
            page.get_by_role('button', name='Next calendar period', exact=True).click()
        assert moved.value.status == 200 and page.get_by_label('Schedule date').input_value() != before
        expect(page.get_by_text('Loading pickup windows…', exact=True)).to_have_count(0)
        try:
            with page.expect_response(lambda response: calendar_range(response, 27, 43), timeout=15000) as month:
                page.get_by_role('button', name='Month', exact=True).click()
        except Exception:
            print(json.dumps({'calendar_requests': calendar_requests[-8:], 'calendar_label': page.locator('.b-calendar').get_attribute('aria-label'), 'page_errors': errors}, indent=2))
            raise
        assert month.value.status == 200
        page.goto('http://127.0.0.1:5173/merchant/onboard')
        name = 'Browser Test Store ' + suffix
        page.get_by_label('Business name', exact=True).fill(name)
        page.get_by_label('Store URL slug', exact=True).fill('browser-test-' + suffix)
        page.get_by_label('Branch address', exact=True).fill('100 Synthetic Test Street, San Francisco')
        page.get_by_role('button', name='Create merchant account', exact=True).click()
        expect(page.get_by_role('heading', name='Merchant workspace')).to_be_visible(timeout=15000)
        expect(page.get_by_label('Business', exact=True).locator('option:checked')).to_have_text(name)
        expect(page.get_by_text('Not authorized for this merchant', exact=False)).to_have_count(0)
        screenshot('merchant-onboarded.png')
        merchant_id = page.get_by_label('Business', exact=True).input_value()
        browser.close()
    cleanup_fixture(merchant_id, 'browser-test-' + suffix)
    result = {'ag_studio_save_restore': 'passed', 'pickup_publishing_and_calendar_data': 'passed', 'calendar_range_navigation': 'passed',
              'merchant_onboarding_membership': 'passed', 'page_errors': errors}
    (ROOT / 'docs/evidence/feature-check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit('Feature check found browser errors')


if __name__ == '__main__':
    run()
