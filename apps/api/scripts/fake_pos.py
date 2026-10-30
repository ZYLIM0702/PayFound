"""Reference fake POS for the PayFound custom POS connector (stdlib only)."""
import argparse
import hashlib
import hmac
import json
import threading
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

LOCK = threading.Lock()
T0 = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)
BRANCHES = [
    {'external_id': 'br-1', 'name': 'Harbour Street Store', 'address': '12 Harbour Street', 'latitude': 51.5074, 'longitude': -0.1278, 'timezone': 'Europe/London'},
    {'external_id': 'br-2', 'name': 'Market Square Store', 'address': '3 Market Square', 'latitude': 51.5155, 'longitude': -0.0922, 'timezone': 'Europe/London'},
]
_ROWS = [('SKU-COF-250', 'Single Origin Coffee 250g', 8.5, 24, 'br-1'), ('SKU-OAT-1L', 'Oat Drink 1L', 2.2, 60, 'br-1'),
         ('SKU-BAG-TOTE', 'Canvas Tote Bag', 12.0, 15, 'br-2'), ('SKU-MUG-CER', 'Ceramic Mug', 9.75, 8, 'br-2'),
         ('SKU-NOTE-A5', 'A5 Notebook', 4.99, 40, 'br-1'), ('SKU-OLD', 'Discontinued Candle', 6.0, 0, 'br-2')]
PRODUCTS = [{'external_id': f'pos-{i + 1}', 'sku': sku, 'name': name, 'price': price, 'currency': 'USD', 'quantity': qty,
             'branch_external_id': br, 'updated_at': (T0 - timedelta(minutes=30 - i)).isoformat(), 'active': sku != 'SKU-OLD',
             'internal_note': 'unknown fields are ignored'} for i, (sku, name, price, qty, br) in enumerate(_ROWS)]
# A deliberately bad row so the run log shows "bad rows are reported, not fatal".
PRODUCTS.append({'external_id': 'pos-bad', 'sku': 'SKU-BAD', 'name': 'Broken row', 'price': -1, 'quantity': 3, 'branch_external_id': 'br-1'})


def make_handler(token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _json(self, status, body):
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _authorized(self):
            given = self.headers.get('Authorization', '')[7:] if self.headers.get('Authorization', '').startswith('Bearer ') else self.headers.get('X-API-Key', '')
            return hmac.compare_digest(given, token)

        def do_GET(self):
            url = urlsplit(self.path)
            if not self._authorized():
                return self._json(401, {'error': 'bad token'})
            q = parse_qs(url.query)
            if url.path == '/health':
                return self._json(200, {'status': 'ok', 'time': datetime.now(timezone.utc).isoformat()})
            if url.path == '/branches':
                return self._json(200, {'branches': BRANCHES})
            if url.path == '/products':
                since = q.get('updated_since', [''])[0]
                limit = max(1, min(int(q.get('limit', ['500'])[0] or 500), 500))
                offset = int(q.get('cursor', ['0'])[0] or 0)
                with LOCK:
                    rows = [p for p in PRODUCTS if not since or p.get('updated_at', '') >= since.rstrip('Z') or 'bad' in p['external_id']]
                    page = rows[offset:offset + limit]
                return self._json(200, {'products': page, 'next_cursor': str(offset + limit) if offset + limit < len(rows) else None})
            return self._json(404, {'error': 'not found'})

        def do_POST(self):
            url = urlsplit(self.path)
            if not self._authorized():
                return self._json(401, {'error': 'bad token'})
            if url.path.startswith('/sell/'):
                with LOCK:
                    for p in PRODUCTS:
                        if p['external_id'] == url.path[6:]:
                            p['quantity'] = max(0, p['quantity'] - 1)
                            p['updated_at'] = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None).isoformat()
                            return self._json(200, {'quantity': p['quantity']})
            return self._json(404, {'error': 'not found'})
    return Handler


def push(url, secret):
    """Send the whole catalogue as one signed push (HMAC-SHA256 over '<timestamp>.<raw body>')."""
    body = json.dumps({'branches': BRANCHES, 'products': PRODUCTS}).encode()
    ts = str(int(time.time()))
    sig = 'sha256=' + hmac.new(secret.encode(), ts.encode() + b'.' + body, hashlib.sha256).hexdigest()
    req = urllib.request.Request(url, data=body, method='POST', headers={
        'Content-Type': 'application/json', 'X-PayFound-Timestamp': ts, 'X-PayFound-Signature': sig})
    with urllib.request.urlopen(req, timeout=15) as r:
        print(r.status, r.read().decode())


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('command', nargs='?', default='serve', choices=['serve', 'push'])
    ap.add_argument('--port', type=int, default=9010)
    ap.add_argument('--token', default='demo-pos-token')
    ap.add_argument('--url')
    ap.add_argument('--secret')
    a = ap.parse_args()
    if a.command == 'push':
        push(a.url, a.secret)
    else:
        print(f'Fake POS on http://127.0.0.1:{a.port}  token={a.token}')
        ThreadingHTTPServer(('127.0.0.1', a.port), make_handler(a.token)).serve_forever()
