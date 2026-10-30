# PayFound custom POS plugin contract (v1)

Any POS can feed PayFound in one of two ways. Both use the same JSON rows.

| | API connection (PayFound pulls) | Webhook (your POS pushes) |
|---|---|---|
| You provide | HTTPS base URL, API key or bearer token, paths | nothing: PayFound gives you an endpoint URL and a secret (shown once) |
| Sync | "Sync now", every 15 min, hourly, or manual | each signed POST is applied immediately |
| Incremental | `updated_since` query parameter | you send only what changed |

Rules for both: unknown fields are ignored; a bad row is reported in the sync run log and skipped (never fatal);
lists are capped at **1000 rows** per request (larger lists are rejected whole); strings have the length limits below.

## Rows

**Product** (`products`)

| field | type | notes |
|---|---|---|
| `external_id` | string 1-120 | your stable id. PayFound upserts on (connection, `external_id`) |
| `sku` | string 1-90 | |
| `name` | string 1-180 | |
| `price` | number > 0, max 2 decimals | major units (12.99), not cents |
| `currency` | 3 letters | default `USD` |
| `quantity` | integer 0..1,000,000 | on-hand quantity at the branch |
| `branch_external_id` | string, optional | must match a branch you sent; omitted = merchant's first active branch |
| `updated_at` | ISO-8601 datetime, optional | UTC if no offset. A row not newer than the stored version is skipped |
| `active` | boolean, default true | false lists the product as unavailable online |

**Branch** (`branches`): `external_id`, `name` (1-130), `address` (max 250), `latitude` (-90..90), `longitude` (-180..180),
`timezone` (IANA, e.g. `Europe/London`). Opening hours, phone and status stay editable in PayFound and are never overwritten.

**Stock event** (`stock_events`, push only): `external_id` (an already-synced product), `quantity` (absolute level, not a delta, so
redelivery is harmless), `updated_at` optional.

## API connection (pull)

PayFound sends `Authorization: Bearer <token>` (or `X-API-Key: <token>` if you choose "API key") and `Accept: application/json`.

* `GET {base}{health_path}` (default `/health`): any 2xx means healthy. Used by "Test connection".
* `GET {base}{branches_path}` (default `/branches`, optional) returns `{"branches": [Branch, ...]}`.
* `GET {base}{products_path}?limit=500&updated_since=<ISO>&cursor=<opaque>` (default `/products`) returns
  `{"products": [Product, ...], "next_cursor": "<opaque>" | null}`. `updated_since` is inclusive and is omitted on the first sync.
  Keep following `next_cursor` (PayFound reads at most 10 pages per run). Responses larger than 4 MB are rejected.
* Use `401/403` for bad credentials, `429` + `Retry-After` to slow us down. Redirects are not followed.

Security: HTTPS on port 443 only. The host is resolved on every request and must be public (private, loopback, link-local and
multicast addresses are refused). In `DEMO_MODE` only, `http://127.0.0.1:<port>` is accepted for the local fake POS.

## Webhook (push)

`POST https://<payfound>/api/pos-plugin/<connection_id>/events`, `Content-Type: application/json`, body up to 1 MB:

```json
{"branches": [...], "products": [...], "stock_events": [{"external_id": "pos-1", "quantity": 7, "updated_at": "2026-01-02T10:00:00Z"}]}
```

Headers:

* `X-PayFound-Timestamp`: current unix time in seconds
* `X-PayFound-Signature`: `sha256=` + hex `HMAC_SHA256(secret, timestamp + "." + raw_body_bytes)`

```python
ts = str(int(time.time()))
sig = "sha256=" + hmac.new(secret.encode(), ts.encode() + b"." + body, hashlib.sha256).hexdigest()
```

Responses: `200` accepted (`{"ok": true, "created", "updated", "skipped", "failed", "errors": [...]}`); `401` bad signature, timestamp
older/newer than 5 minutes, or the same signed delivery sent twice (replay); `404` unknown/disconnected connection; `413` body too large.
Sign the exact bytes you send. Change the body or timestamp for each new delivery. Retrying the *same* delivery after a timeout returns `401 Replayed delivery`
only if the first attempt was accepted; it is safe to treat that as success.

## What sync does and never does

* Creates/updates products (name, sku, price, currency, quantity, branch, active) and branches (name, address, coordinates, timezone).
* Sets `stock_updated_at` to the sync time, so PayFound's stock-freshness rules treat the quantity as freshly asserted by your POS.
* Never overwrites PayFound-only data: reservation holds, descriptions, categories, photos. The quantity is never set below the units
  currently held for pickup reservations; the difference clears when the reservation completes or expires.
* Stock from your POS is *merchant-asserted local stock*. A pickup reservation still needs the merchant's confirmation.
* Failures back off (1, 2, 4... up to 60 minutes) and show on the Connections page. Disconnecting stops sync, keeps the listings and marks them unavailable online.

## Local demo

`python scripts/fake_pos.py` serves this contract on `http://127.0.0.1:9010` (token `demo-pos-token`, includes one bad row).
`python scripts/fake_pos.py push --url <endpoint> --secret <secret>` sends a signed push.
