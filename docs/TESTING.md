# Testing and acceptance

## Run the checks

```bash
# Backend: 349 tests, isolated database, no live provider calls
(cd apps/api && PYTHONPATH=. .venv/bin/python -m pytest -q)

# Frontend
npm run lint --prefix apps/web
npm test --prefix apps/web
npm run build --prefix apps/web          # runs the TypeScript check, then Vite

# Schema drift (fresh migration, then compare to the models)
(cd apps/api && .venv/bin/alembic upgrade head && .venv/bin/alembic check)

# Browser acceptance: the local --demo stack must be running; needs Playwright and Chromium
python3.12 scripts/browser_check.py               # shopper -> merchant -> admin journey, responsive widths
python3.12 scripts/pos_browser_check.py           # register, discounts, simulated payments, receipts, stock bridge
python3.12 scripts/discovery_browser_check.py     # location, Google map and traffic route, product pages, comparison
python3.12 scripts/online_ui_check.py             # Channel3 online section
python3.12 scripts/feature_check.py               # merchant features and sponsor workflows
python3.12 scripts/product_photo_check.py         # photo delivery and metadata-refresh safety

# Contracts and secrets
apps/api/.venv/bin/python scripts/export_api.py   # fresh OpenAPI export
python3.12 scripts/check_browser_secrets.py       # no server secret in compiled assets
apps/api/.venv/bin/python scripts/verify_integrations.py --channel3 --paypal-create   # one search, one sandbox order; no approval or capture
```

The backend suite can also target a disposable localhost PostgreSQL database named `payfound_test` with `PAYFOUND_TEST_DATABASE_URL`; it refuses any other host. CI runs it on SQLite and PostgreSQL, then the frontend and browser jobs.

### Opt-in PayPal sandbox checks

These talk to PayPal's sandbox and require credentials and an explicit flag. Exit code 0 is a pass, 2 is blocked or pending, 1 is a failure.

```bash
apps/api/.venv/bin/python scripts/paypal_card_check.py --live       # fixed public test card: capture + full refund
python3.12 scripts/paypal_browser_check.py --live                   # the genuine v6 wallet path
apps/api/.venv/bin/python scripts/paypal_webhook_check.py --live setup|exercise|verify|cleanup
```

Use a **distinct** sandbox buyer (`PAYPAL_SANDBOX_BUYER_EMAIL`, `PAYPAL_SANDBOX_BUYER_PASSWORD`) for the wallet run; a seller cannot approve its own purchase. Always run `cleanup` after a webhook run. Never push high load at the sandbox.

## What the backend suite covers

| Area | Examples |
|---|---|
| Inventory | Idempotent reservation; 100-buyer last-unit race; expiry and release; no oversized hold effects; capacity-limited pickup and rescheduling; overnight and holiday hours |
| Payments | Exact amount and currency checks; stable request IDs; timeout quarantine; readback instead of retry; pending refunds; refund-response variants; no terminal-state resurrection; atomic multi-item decrement |
| Webhooks | Missing headers, forged signatures and changed amounts rejected; valid replay acknowledged once; one outbox job per event |
| Authorisation | Role enforcement; real ES256 JWT handling; `user_metadata` cannot grant authority; fresh memberships; cross-tenant 404s on every merchant surface |
| Connectors | Encryption, publication scope, version ordering, mark-and-sweep, SSRF refusal, signed push with replay and stale timestamp rejection, held stock never erased |
| POS | Journal persistence, lost-acknowledgement recovery, concurrent counter and online buyers, conflict and retry |
| Assistant | Event order and shape; run recording without content; input policy and prompt-injection defence; result redaction; output guard; tool scoping per role; history ownership; photo validation; radius widening; wording rounds and category fallback; store placement inside the stream; Channel3 results surviving redaction |
| Placement | Determinism, sea and park rejection, address separation, caching, rate limits, header parsing |
| Merchant intelligence | Forecast drivers, stock-out handling, report cards, consent gating, currency separation |
| Catalogue | Idempotent seeding, identity-based comparison, no fabricated GTINs, stale stock never shown as confirmed |

The assistant tests use a scripted model, so they are deterministic and need no API key.

## Failure-injection matrix

| Fault | Invariant | Covered |
|---|---|---|
| Reuse an idempotency key for a different item | 409; original order unchanged | Yes |
| 100 concurrent buyers, 1 unit | Exactly one confirmed hold | Yes (SQLite); repeat on PostgreSQL |
| Double-click on the PayPal button | One provider operation, no second capture | Yes (mocks) and sandbox |
| Capture succeeds but the response is lost | Reconcile from the provider; no blind retry | Yes |
| Webhook replayed or out of order | Deduplicated; converges via provider readback | Yes |
| Merchant closes between search and reserve | Reservation rejected | Yes |
| Hold expires during approval | No capture until stock revalidated; reconcile | Yes |
| Merchant edits another merchant's product | 403 or 404 | Yes |
| Forged `x-demo-role` on a public host | Rejected | Yes |
| Refunded capture later marked collected | Rejected | Yes |
| Channel3 timeout or bad data | No fabricated stock; local results still shown | Yes |
| Source POS offline ten minutes | Confidence degrades; recovers on reconnect | Simulator only |
| API killed mid-checkout | Worker retry, outbox and idempotency recover | Partly; needs a staging drill |
| Sustained high-volume browsing | Rate limiting | Per-principal limits only; no load test yet |
| PostgreSQL backup restore | RPO and RTO recorded; ledger matches provider | Not run |

## Manual acceptance (shopper to administrator)

1. Open the home page at 390, 768 and 1440 px: demo banner, stores, thumbnails.
2. Search "charger", "wrench", "cat": correct categories, quantities and distances.
3. Explore: map markers, **Use my location** through the in-page card, driving route with traffic.
4. Open a store: labelled sample reviews, hours, address; reserve a valid product.
5. Checkout without PayPal credentials: an unmistakable **simulated, no payment** control. With sandbox credentials: the real v6 button; record the provider order and capture IDs, redacted.
6. As the merchant: the order in the AG Grid queue; move it to collected; confirm stock and totals.
7. As the shopper: review the collected order. As the administrator: hide it; the storefront no longer shows it.
8. Ask the assistant "where is a USB-C charger?", then upload a photo and ask "where can I buy this?": answers cite real records, show local and ONLINE results together, and say plainly when nothing is close.
9. With Channel3 configured, confirm the ONLINE section shows retailer links and no seller appears as a local branch.
10. In staging with `DEMO_MODE=false`: JWT verification, tenant isolation and account linking.

## Defect priority

**P0:** build failure; missing route; any false claim of real payment; sandbox capture failure; role bypass; duplicate-charge risk; a licence blocker.
**P1:** inaccurate stock or status; broken reviewer permissions; missing expiry handling; inaccessible layout; broken external links; the assistant presenting online results as local.
**P2:** incomplete filters, responsive polish, live POS gaps.

Keep logs, Postman runs and redacted receipts under `docs/evidence/` locally; never commit secrets.
