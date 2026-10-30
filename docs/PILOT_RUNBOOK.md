# Operations runbook

Setup detail, connector and provider activation, and recovery procedures. Updated 23 October 2026. For the overview of modes and variables start with [DEPLOYMENT.md](DEPLOYMENT.md). Commands run from the repository root unless noted.

## Start the local stack

```bash
python3.12 -m venv apps/api/.venv
apps/api/.venv/bin/pip install -r apps/api/requirements.lock
npm ci --prefix apps/web
apps/api/.venv/bin/python scripts/setup.py
apps/api/.venv/bin/python scripts/dev.py --demo
```

Open http://127.0.0.1:5173. API: http://127.0.0.1:8000/docs. The launcher starts the API, Vite, and durable worker together. Ctrl-C stops all three.

For background operation, append `--background`. Stop it with `python3 scripts/dev.py --stop`. Logs and PID are under `docs/evidence/` and ignored by Git.

The explicit `--demo` launcher uses local SQLite, fictional stores, and loopback-only role switching. Merchant mode controls Northside Electronics. A simulated payment never moves funds. Real PayPal sandbox order creation is a separate path.

## Environment configuration

Process environment takes precedence over files. Files are loaded in this order: a workspace-level `.env` if one exists, application-root `.env`, then `apps/api/.env`. Existing shared credential names are supported:

| Existing name | Backend setting |
|---|---|
| `PAYPAL_PLATFORM_APP_CLIENT_ID` | `PAYPAL_CLIENT_ID` |
| `PAYPAL_PLATFORM_APP_SECRET_KEY` | `PAYPAL_CLIENT_SECRET` |
| `SUPABASE_URL` | `SUPABASE_PROJECT_URL` |

`/api/config` exposes only public client configuration, including the Supabase publishable key and PayPal client ID. Browser bundles never receive server keys. `scripts/setup.py` generates and preserves a server-only connector encryption key. Retain the same key for the API and worker when redeploying existing encrypted connections.


## Implemented workflows

- Local search, categories, location consent, radius filters, maps, storefronts, stock provenance and freshness.
- Single-merchant/branch baskets, locked server totals, idempotent reservations, merchant confirmation for non-synthetic stock, expiry and cancellation.
- Sandbox PayPal creation/capture/refund, eligibility-aware SDK v6 controls, durable provider-operation claims, uncertain-status reconciliation, verified webhook inbox and financial-review quarantine.
- Merchant onboarding, branches/time zones, regular and exceptional hours, catalog creation, checksum-validated canonical GTIN identity, staff invitations and fresh memberships.
- Capacity-limited pickup windows, rescheduling, fulfilment transitions and event/proof history.
- Durable in-app buyer/merchant notifications, backed by the transactional outbox.
- Consumer shopping tools, merchant copilot, validated cloud-model fact selection, consent and inference budgets, deterministic fallback, and live Channel3 online comparison.
- AG Grid operations, AG Studio report save/restore with version conflict checks, and Bryntum pickup scheduling. The installed Bryntum package is a trial and displays its watermark.
- Administrator review moderation, payment-review queue, failed-job retry and integration status.

## Database and migrations

`apps/api/migrations` is authoritative. Production startup does not create tables or seed fictional stores.

```bash
# From apps/api, with the actual server-only PostgreSQL URL configured:
.venv/bin/alembic upgrade head
.venv/bin/alembic check
```

The connected Supabase project was provisioned through staged MCP migrations. Browser roles have no direct table grants, and all application tables have RLS enabled. FastAPI provides authorized projections; backend database access still requires `DATABASE_URL`. A publishable or secret HTTP API key is not a PostgreSQL password.

`scripts/export_schema.py` exports the complete reviewed Alembic chain as a fresh-project bootstrap under `supabase/migrations/`. Do not replay that full bootstrap over an existing project; use Alembic forward migrations instead. Supabase MCP bootstrap history and the initialized `alembic_version` are both recorded in evidence.

For the long-running Render API/worker, use the Supabase session pooler on port 5432 when IPv4 connectivity is needed, with the provider's actual connection string and SSL settings. Pool sizes are bounded per process. The local regression suite can also target a disposable localhost PostgreSQL database named `payfound_test` using `PAYFOUND_TEST_DATABASE_URL`; it refuses remote databases because tests drop application tables.

## Connect merchant sources

### Local software POS simulator

Open `/pos/sell`, enter merchant demo mode and choose **Connect demo register** on first use. Northside has a 12-item register library; its eight POS-specific items are included by expanded seeding, or added on first connection in minimal mode. The merchant workspace links to the register and shows connection/sale/queue counts.

- **Sell:** product tiles, name/SKU search, keyboard barcode input, quantity controls, percent/fixed discounts, browser-local saved carts and simulated card/cash checkout. The decline scenario leaves stock untouched; an explicit retry uses a new simulated attempt.
- **Overview/receipts:** totals and charts derive from completed simulator receipts. Receipts can be reopened and downloaded as text, always labeled simulation.
- **Product library:** AG Grid compares POS on-hand, online holds and platform stock. Recording a fictional count pushes a stock event.
- **PayFound orders:** the merchant's existing local platform orders appear as a read-only information flow into the counter workspace.
- **Sync center:** inspect directions, event identifiers, queued/acknowledged/review states and errors. Pause the bridge, complete a sale, then resume and observe its single stock deduction. Resolve a conflicting online hold/count in PayFound before retrying.

The source journal is `apps/api/pos_simulator.db`, separate from `payfound_demo.db`, and ignored by Git. A server-only `POS_SIMULATOR_DATABASE` can override its location for isolated tests. Both stores must persist for durable demo history. The bridge writes a completed, unique platform acknowledgement in the same transaction as stock updates; a retry after lost source acknowledgement does not repeat the mutation.

The simulator is local-only, merchant-scoped, synthetic-inventory-only and USD-only. Its source journal is separate from the production ORM and needs no Supabase migration. Pausing the bridge simulates a link outage while the local API remains available; it does not provide offline card processing. No real PayPal/Zettle payment or hardware call is made.

```bash
python3.12 scripts/pos_browser_check.py
```

That check exercises the register and platform together, including discount arithmetic, saved carts, approved/declined/retried card and cash simulations, receipts, SKU input, bidirectional stock updates, pause/replay, and mobile cart access. It checks six views at four viewport widths and records `docs/evidence/pos-browser-check.json` plus screenshots. Eight POS backend tests remain covered in the full 57-test suite.

### Catalogue photographs

Mappings are in `apps/api/app/demo_photos.json` and the extension in `demo_catalogue.json`; local 600×600 WebP files and a provenance manifest are under `apps/web/public/images/products/`. `/image-credits.html` provides per-image credit/licensing. There are 196 ABO CC BY 4.0 images and four individually reviewed Wikimedia images. No image API key or remote product-image host is required.

Demo startup updates known default fixture names, descriptions and photo paths to match the photographed models. It preserves custom names/images/descriptions and does not reset prices, quantities, holds, freshness or payment records. Existing POS registers receive photo metadata through their normal catalogue refresh. Source stock and prices remain synthetic.

`python3.12 scripts/import_product_photos.py` rebuilds the selected assets, manifest and credit page from their public sources, using httpx, Pillow and Node. Existing generated assets are reused only when their source URL and checksum match. The importer respects bounded Wikimedia rate-limit backoff. Product image adaptations retain each source image's license.

For a metadata-refresh verification, run `python3.12 scripts/product_photo_check.py --snapshot` before restarting the demo, then `python3.12 scripts/product_photo_check.py` after the restart. This checks the prior inventory/price/freshness baseline, all catalogue asset hashes, POS/shopper/basket/order rendering and the credit page without creating a payment or changing stock.

### Expanded discovery, Google Maps and directions

The default local fixture has about 640 distinct items and about 1,000 offers across 40 fictional retailers (read `/api/catalogue/summary`). It seeds idempotently, shares exact catalogue identity for comparison groups and retains existing inventory, prices and financial history. Set `DEMO_EXPANDED_CATALOGUE=false` for the original small fixture. Unit-test fixtures stay minimal; expansion tests explicitly install and verify the full local set. No production migration or remote seed is performed.

Explore uses 24 offers per page with category/store/radius/sort filters. Names link to `/products/:id`; card/photo or **Show on map** focuses the store at zoom 16. Product pages provide photographs, pickup/stock facts, matching store offers and a directions map. Merchant-specific image surrounds/scales vary presentation while preserving identity.

The existing `GOOGLE_MAP_API_KEY` name is supported, along with `GOOGLE_MAPS_API_KEY`, `GOOGLE_ROUTES_API_KEY`, `GOOGLE_MAPS_BROWSER_KEY` and `GOOGLE_MAPS_MAP_ID`. In the loopback demo a general Maps key may load the browser SDK at runtime; it is not embedded in Vite assets. A Routes-only key is never exposed as a browser key. Authenticated staging requires a separate browser key with appropriate Google website/API restrictions. Enable Maps JavaScript API and Routes API for the configured project/key.

Google routing uses server-side `X-Goog-Api-Key`, explicit field masks and `DRIVE`/`TRAFFIC_AWARE`. A Google map renders the route and native TrafficLayer. Origin/route content is not stored or server-cached. Visible routes refresh every 60 seconds with per-client request quotas. The unconfigured fallback labels its road estimate as lacking live traffic. External Google Maps directions remain available.

Choose **Use my location**, then allow the native browser prompt. Location requires HTTPS/localhost, stays in app-session memory and can be cleared. Denial shows site-setting instructions. Straight-line distance is distinct from actual road distance/ETA. Outside-region users can browse the SF fixture while retaining distance from their actual shared position. Privacy/terms pages are linked in the footer.

`python3.12 scripts/discovery_browser_check.py` uses declared test geolocation, checks all 244 detail endpoints, actual Google camera movement and one live traffic route, comparison/pagination, six responsive cases, then denied/cleared/outside-region states and store switching during a delayed location grant. The cancellation guard runs before requesting permission so an old destination cannot be requested after the user selects another store. The check does not change the person's own browser permissions or capture their actual physical location. Sanitized JSON evidence does not retain Google route geometry.

### WooCommerce

Use Merchant → Connections. Enter an authorized HTTPS store URL and REST consumer key/secret. Credentials are encrypted server-side. Sync imports simple products and variants with source timestamps. Generic WooCommerce store inventory is online-only: it is not automatically a physical branch count. Explicit publication authorizes product display; native merchant checkout handles its own stock, tax and variation checks.

### Shopify

Configure `SHOPIFY_CLIENT_ID`, `SHOPIFY_CLIENT_SECRET` and `PUBLIC_API_URL`. Register the exact redirect URI:

```text
https://<api-origin>/api/connectors/shopify/callback
```

The connection wizard authorizes the exact `.myshopify.com` store, validates one-time state/HMAC, stores offline tokens encrypted, and imports location-specific inventory through the pinned GraphQL schema. Map source physical locations to authorized PayFound branches, then grant publication consent. Imported purchases use merchant-native checkout. A catalog authorization is not an external payment or reservation entitlement.

Snapshots are bounded and restartable. Signed delivery hints schedule authoritative reads. Disconnect/revocation unpublishes affected offers. Outbound requests reject private addresses and pin DNS destinations. Register source webhooks through the explicit connection action after public HTTPS is available.

## PayPal verification

The app supports sandbox only. A configured sandbox seller receives the test payment; this is not approved multi-seller settlement. The wallet path requires approval by a distinct sandbox buyer. The separate fixed-card API test confirms its public sandbox fixture directly with PayPal before application capture.

```bash
apps/api/.venv/bin/python scripts/verify_integrations.py --channel3 --paypal-create
```

That command performs one online catalog search and creates one sandbox order through the local application. It does not approve or capture it. Evidence is sanitized and saved under `docs/evidence/integrations.json`.

Configure `PAYPAL_WEBHOOK_ID` after registering the public HTTPS endpoint `/api/paypal/webhook`. Genuine sandbox-generated events are required to validate end-to-end signature verification. Simulator delivery alone does not prove it. The handler stores verified events and the worker reconciles them; duplicate business effects are prevented by database constraints and operation state.

External reversal/dispute/refund events quarantine affected purchases for provider review. They do not imply a full refund or physical return. Such orders must be resolved with the provider and an audited operator workflow before handover. No arbitrary database state edits should be used as payment proof.

### Recorded live checks

On 22 October, the fixed-card API flow captured and fully refunded USD 39.99, checked repeat capture/refund behavior, and finished `CANCELLED/REFUNDED`. It also exposed and fixed minimal refund-response handling: persist the known refund ID before authoritative detail lookup, then retry that lookup if its response is lost. These payment regressions remain covered in the 57-test backend suite.

Actual capture and refund webhooks were received at a temporary Supabase HTTPS function, retained as **unverified transport data**, and privately retrieved with their original bytes and five PayPal headers. The real FastAPI handler called PayPal's live sandbox verification API through ASGI transport. Both signatures verified; missing headers, forged signatures, changed amounts and forged replays returned HTTP 401. Each event created one reconciliation job; the worker processed both without extra restocking or resurrecting the refunded order. This verifies genuine provider delivery and the local application handler/worker, not a deployed public FastAPI service.

The temporary subscription and transport rows were removed. The test function remains deployed but its private run configuration is disabled (HTTP 410). A permanent webhook still needs the deployed non-demo API URL and a newly registered webhook ID.

### Repeat the opt-in checks

```bash
# Provider/API capture and refund using only the fixed public sandbox card:
apps/api/.venv/bin/python scripts/paypal_card_check.py --live

# Genuine wallet SDK path, using Python with Playwright installed:
python3.12 scripts/paypal_browser_check.py --live
```

Wallet credentials can use server-only `PAYPAL_SANDBOX_BUYER_EMAIL` and `PAYPAL_SANDBOX_BUYER_PASSWORD`. The existing generic sandbox login is the receiving seller, so the recorded wallet run stops before login/capture. Do not use a seller account to approve its own purchase. Check scripts exit 0 on a passed check (or explicit wallet inspection), 2 on a blocked/pending check, and 1 on failure.

For another temporary signed-event run, deploy `supabase/functions/payfound-sandbox-test-relay/index.ts` with its `deno.json` and `verify_jwt=false`: the provider does not send a Supabase JWT, and the function instead checks an expiring run nonce against a private hash. A server-only Supabase secret key must be available to the runner. This harness is for the loopback demo stack only and does not expose it publicly.

```bash
apps/api/.venv/bin/python scripts/paypal_webhook_check.py --live setup
apps/api/.venv/bin/python scripts/paypal_webhook_check.py --live exercise
apps/api/.venv/bin/python scripts/paypal_webhook_check.py --live verify --wait-seconds 100
# Always retire this run after verification or a blocked/failed attempt:
apps/api/.venv/bin/python scripts/paypal_webhook_check.py --live cleanup
```

Exercise is one-shot per run. Verify exits 2 if the bounded delivery wait expires; it can be retried while still waiting. Cleanup is safe to repeat after success. The temporary ingress expires after 45 minutes even if cleanup is interrupted. Raw transport envelopes are private and untrusted until the actual application's signature check succeeds. Run state lives in ignored `docs/evidence/paypal-webhook-raw/` (directory mode 0700, state-file mode 0600); sanitized evidence contains IDs, checks and body hashes, without the run nonce, credentials, signatures or raw bodies.

## Cloud AI activation

Set `LLM_PROVIDER` (`openai-compatible`, `openai`, `anthropic`, or `gemini`), `LLM_MODEL`, `LLM_API_KEY`, and an optional provider `LLM_BASE_URL`. Enable `ENABLE_REMOTE_AI=true` only for permitted data. Merchant inference additionally requires the owner consent control in the copilot screen. Missing configuration, invalid model claims, timeouts and budget failures retain the deterministic tool result. Inference does not receive customer identities or raw merchant conversations and cannot call financial mutation tools.

The process-local rate/cost budget is suitable for this single-process pilot. Public mode also bounds API traffic per client address and per verified subject, configured by `API_PUBLIC_RATE_LIMIT_PER_MINUTE` (default 600) and `API_USER_RATE_LIMIT_PER_MINUTE` (default 120). Health/readiness probes are exempt. A shared limiter, verified proxy-client addressing and measured retrieval/availability calibration are needed before multi-instance production scaling.

## Render staging

`render.yaml` defines API, worker and static React services. API pre-deploy runs Alembic; `/api/ready` checks database readiness. Worker credentials reference the API service, including its encryption key. Set `DEMO_MODE=false` publicly. Select current Render compute plans and review their cost in the authenticated workspace before deployment.

Required external inputs: deployment repository/workspace access, PostgreSQL `DATABASE_URL`, exact web/API origins, and provider credentials for the integrations being enabled. Set `VITE_API_URL` to the API origin and `CORS_ORIGINS` to the web origin. Set Supabase Auth's Site URL to the web origin and allow its callback/reset URLs, including callback query parameters. Configure permitted email delivery/SMTP for the intended pilot users. Admin invitation fragments are installed explicitly through the SDK while signup/recovery retain PKCE. No cloud deployment was performed without this account access.

## Recovery and evidence

- `RECONCILIATION_REQUIRED`: inspect original provider order/capture IDs; run the scoped reconcile action. Reconciliation may replay an existing uncertain operation using its original idempotency key.
- `REFUND_PENDING`: worker reads provider refund state. Do not mark collected or issue an unrelated second refund.
- `PROVIDER_REVIEW_REQUIRED`: external financial exception; stop handover and inspect the provider case. Automatic capture readback cannot clear this quarantine.
- Failed outbox jobs: inspect kind/attempt count and use the admin retry action after correcting the cause. Unmatched verified webhooks remain reviewable rather than being assumed successful.
- Stale/disconnected sources: sync, reauthorize, or keep offers unpublished. A browser refresh is not a stock verification.

Useful advisory references: [RLS without a browser policy](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy) is intentional for this backend-only access model; [unused indexes](https://supabase.com/docs/guides/database/database-linter?lint=0005_unused_index) are expected on an empty new schema. The two missing foreign-key indexes identified during provisioning were added. [Auth connection allocation](https://supabase.com/docs/guides/deployment/going-into-prod) remains a provider configuration choice.
