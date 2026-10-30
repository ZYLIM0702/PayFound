# Status

What is built, what has been verified, and what still depends on access PayFound does not have. Last updated 23 October 2026.

PayFound is a **pre-commercial prototype**. It has no live merchants, no approved PayPal partner status, no certified POS connector and no consumer traction. Everything below is described at the level it was actually tested.

## Built

| Area | State |
|---|---|
| Shopper journeys | Search, map, storefronts, product pages and cross-store comparison, basket (one merchant and branch), reserve with expiring hold, PayPal sandbox or clearly simulated checkout, order tracking, verified reviews, account area, price watch |
| AI assistant | Streaming agent with OpenUI generative UI, photo input, live voice and dictation, grocery recipe planning, multi-round search with radius widening, Channel3 ONLINE offers beside local results, in-page location request, server-side chat history ([ASSISTANT.md](ASSISTANT.md)) |
| Merchant workspace | Onboarding, branches and hours, inventory and stock-count sheet, orders (AG Grid), pickup calendar (Bryntum), explainable forecast, analytics (AG Studio) with saved reports, online price check, plans, invoices, messages, notifications |
| POS | Software POS simulator with a stock bridge; custom POS plugin (pull or signed push) with a loopback demo and a fake POS |
| Connectors | WooCommerce and Shopify adapters with encrypted credentials, scoped publication, location mapping and version-aware sync ([CONNECTORS.md](CONNECTORS.md)) |
| Payments | PayPal Orders v2 create, capture and refund; SDK v6 with Pay Later eligibility; durable provider operations; verified webhook inbox; reconciliation and financial-review quarantine |
| Platform | Supabase-ready auth with fresh memberships, Alembic migrations, transactional outbox and leased worker, per-viewer store placement, row-level security, OpenAPI and Postman artefacts, generated Python and TypeScript SDKs, CI, Render blueprint |
| Demo data | About 640 distinct products, about 1,000 offers and 40 fictional stores (`/api/catalogue/summary`), with 460+ licensed photographs and per-image credits |

## Verified

| Check | Result |
|---|---|
| Backend regression suite | **349 passed** (isolated database, no live provider calls) |
| Last-unit concurrency | 100 competing clients, exactly one reservation |
| JWT trust boundaries | Real ES256 signatures; user metadata cannot grant admin; wrong or expired signatures rejected; membership revocation honoured with the same token |
| Payment faults | Exact amounts, timeout quarantine, pending-refund restrictions, minimal refund-response recovery, no terminal-state resurrection |
| Frontend | ESLint clean; 6 unit tests pass; TypeScript and production Vite build pass |
| Browser journeys (Playwright) | Basket, simulated payment, merchant fulfilment, collected review, administrator view; responsive layouts at 390 / 768 / 1440 px; POS flows across 24 view-and-width checks |
| PayPal sandbox | OAuth and read; fixed-card approval, server capture and full refund (USD 39.99); repeat-capture checks; SDK v6 button rendering; **live signed capture and refund webhooks** verified through PayPal in the real handler, with forgery and replay rejected |
| Channel3 | Live server-side query; offers rendered in the browser; assistant integration regression-tested |
| Google Maps | Genuine Maps JavaScript and Routes responses, traffic-aware ETA, route polyline, traffic layer |
| Supabase | Schema provisioned through staged migrations; row-level security on every table; zero browser table grants; column fingerprint matches the ORM; signing-key endpoint reachable |
| Postman / Newman | 21 requests, 20 assertions, 0 failures (payment folder excluded) |
| Secrets | No configured server secret found in compiled browser assets |
| Assistant search | Regressions for radius widening, wording rounds, category fallback, per-viewer store placement and Channel3 result redaction |

The suite retains one upstream Starlette/httpx deprecation warning. Vite reports large merchant-library chunks; they are lazy-loaded away from shopper start-up. No production performance SLO is claimed.

## Not verified, or not possible yet

| Dependency | What is needed |
|---|---|
| PostgreSQL runtime | A server-only `DATABASE_URL` with real credentials. The schema is provisioned but FastAPI has not been exercised against it |
| Wallet approval | A **distinct** sandbox buyer. The configured sandbox login is the receiving seller and cannot approve its own purchase |
| Permanent PayPal webhook | A deployed non-demo HTTPS API URL and its own `PAYPAL_WEBHOOK_ID`. The temporary test subscription was removed |
| WooCommerce and Shopify | An authorised test store each (REST keys; development store, client ID and secret, approved redirect) |
| Real POS synchronisation | Written API rights and a live merchant. Provider stubs and the simulator are not proof of POS sync |
| Cloud inference at scale | Provider budget and merchant consent for real data |
| Render | Workspace and repository access; Docker image builds were not run (no daemon) and no remote CI run is claimed |
| Licensed release | Production licences for AG Studio and Bryntum (a trial is installed); redistribution rights for any template-derived code ([THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)) |
| PayPal partnership | Written answers to the questions in [BUSINESS_STRATEGY.md](BUSINESS_STRATEGY.md#104-written-answers-needed-from-paypal) |

## Boundaries to keep in mind

- All stores, prices, stock, reviews and sales in the demo are fictional. Demo photographs are real and individually licensed.
- A simulated payment moves no funds and is never called a PayPal transaction.
- The POS is a simulator, not an authorised Zettle sandbox.
- PayFound is not a PayPal partner. A sandbox seller is not a platform entitlement, multiparty payments are not implemented, and nothing implies instant bank payout.
- Online offers (Channel3) are not local stock.
- Demo mode is loopback-only; the demo role switcher must never run publicly.

## Evidence

Verification scripts write sanitised results and screenshots under `docs/evidence/` when you run them (logs and raw provider data are git-ignored). The scripts are listed in [TESTING.md](TESTING.md). Provider checks that touch PayPal require an explicit `--live` flag.
