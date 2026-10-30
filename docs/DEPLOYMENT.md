# Configuration and deployment

Operational detail (provider activation, recovery procedures, POS and connector setup) is in [PILOT_RUNBOOK.md](PILOT_RUNBOOK.md). This page is the map: which mode you are in, what to set, and how to stand it up.

## Modes

| | Local demo | Authenticated staging |
|---|---|---|
| Command | `scripts/dev.py --demo` | Render blueprint (`render.yaml`) |
| Database | SQLite, seeded with fictional stores | Supabase PostgreSQL, migrated by Alembic, **no seeding** |
| Identity | Role switcher via `x-demo-role`, loopback only | Supabase Auth JWTs, memberships checked per request |
| Payments | Simulated, or PayPal sandbox if credentials are set | PayPal **sandbox** |
| `DEMO_MODE` | `true` | **`false`** |

Never run demo mode on a public host. With `DEMO_MODE=false` the API rejects `x-demo-role`.

## Local demo

```bash
python3.12 -m venv apps/api/.venv
apps/api/.venv/bin/pip install -r apps/api/requirements.lock
npm ci --prefix apps/web
apps/api/.venv/bin/python scripts/setup.py          # creates .env files and a server-only connector encryption key
apps/api/.venv/bin/python scripts/dev.py --demo     # API, web and worker; Ctrl-C stops all
```

The launcher refuses to start if port 8000 or 5173 is taken, and holds a project lock. Add `--background` for logs under `docs/evidence/`; stop with `python3 scripts/dev.py --stop`. Demo stores are placed around your approximate location; see [ARCHITECTURE.md](ARCHITECTURE.md#per-viewer-store-placement).

## Environment variables

The root [`.env.sample`](../.env.sample) lists every variable the code reads, grouped by feature and marked required, optional or demo-only. Copy what you need into `apps/api/.env` (server) and `apps/web/.env` (browser `VITE_*` only). The tables below explain them.

Process environment wins over files. Files load in order: a workspace `.env` if present, the application-root `.env`, then `apps/api/.env`. Secrets never go in `VITE_*` variables. `/api/config` exposes only public values.

**Core**

| Variable | Purpose |
|---|---|
| `DEMO_MODE` | Local synthetic mode. `false` for anything public |
| `DATABASE_URL` | Server-only SQLAlchemy URL, for example `postgresql+psycopg://...` with SSL |
| `CORS_ORIGINS` | Exact web origin(s) |
| `PUBLIC_API_URL`, `PUBLIC_WEB_URL` | Public origins, used for OAuth redirects and links |
| `CONNECTOR_ENCRYPTION_KEY` | Encrypts connector credentials at rest. Same value for API and worker; keep it when redeploying |
| `TRUST_PROXY_HEADERS` | Honour verified proxy client addresses |
| `API_PUBLIC_RATE_LIMIT_PER_MINUTE`, `API_USER_RATE_LIMIT_PER_MINUTE` | Public-mode request limits (defaults 600 and 120) |
| `SITE_ACCESS_KEY` | Optional access key in front of the whole app. When set, the web app shows an *Enter the access key* page and every API call needs the signed token it returns, so a shared deployment cannot run up AI, maps or search bills. Health checks, PayPal webhooks and POS pushes stay reachable. A browser stays unlocked until the key changes. Unset by default |

**Identity (Supabase)**

| Variable | Purpose |
|---|---|
| `SUPABASE_PROJECT_URL`, `SUPABASE_JWKS_URL`, `SUPABASE_JWT_AUDIENCE` | Verify asymmetric JWTs |
| `SUPABASE_PUBLISHABLE_KEY` | Public key returned by `/api/config` |
| `SUPABASE_SECRET_KEY` | Server-only |
| `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_API_URL` | Web build; `VITE_API_URL` only if the API is on another origin |

**PayPal (sandbox)**

| Variable | Purpose |
|---|---|
| `PAYPAL_ENV` | `sandbox` |
| `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET` | REST app credentials (server) |
| `PAYPAL_WEBHOOK_ID` | From the registered HTTPS webhook |
| `PAYPAL_MERCHANT_ID`, `PAYPAL_PAYEE_MERCHANT_ID`, `PAYPAL_SANDBOX_POOL_CSV` | Receiving-account configuration for the demo |
| `PAYPAL_SANDBOX_BUYER_EMAIL`, `PAYPAL_SANDBOX_BUYER_PASSWORD` | Distinct sandbox buyer for the wallet check |

The names `PAYPAL_PLATFORM_APP_CLIENT_ID` and `PAYPAL_PLATFORM_APP_SECRET_KEY` (and `SUPABASE_URL`) from a shared workspace `.env` are accepted as aliases.

**Assistant and AI**

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY`, `OPENAI_MODEL` | Assistant model |
| `OPENAI_REALTIME_MODEL`, `OPENAI_REALTIME_VOICE`, `OPENAI_TRANSCRIBE_MODEL` | Voice and dictation |
| `ASSISTANT_RUN_TIMEOUT_SECONDS`, `ASSISTANT_PAYPAL_MCP`, `ASSISTANT_DB_RLS` | Run limit; administrator PayPal bridge; RLS context |
| `ENABLE_REMOTE_AI`, `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`, `LLM_BASE_URL` | Optional merchant-intelligence inference (needs owner consent) |
| `LLM_TIMEOUT_SECONDS`, `LLM_MAX_INPUT_TOKENS`, `LLM_MAX_OUTPUT_TOKENS`, `LLM_MAX_COST_USD_PER_RUN`, `LLM_DAILY_BUDGET_USD` | Budgets and cost rates |

**Integrations**

| Variable | Purpose |
|---|---|
| `CHANNEL3_API_KEY`, `CHANNEL3_BASE_URL`, `CHANNEL3_TIMEOUT_SECONDS`, `CHANNEL3_RATE_LIMIT_PER_MINUTE` | Online offers |
| `GOOGLE_MAPS_API_KEY` (or `GOOGLE_MAP_API_KEY`), `GOOGLE_ROUTES_API_KEY`, `GOOGLE_MAPS_BROWSER_KEY`, `GOOGLE_MAPS_MAP_ID` | Map, traffic and routes. A Routes-only key is never exposed to the browser; staging needs a separate referrer-restricted browser key |
| `SHOPIFY_CLIENT_ID`, `SHOPIFY_CLIENT_SECRET` | Shopify OAuth |
| `AG_STUDIO_LICENSE_KEY`, `VITE_AG_STUDIO_LICENSE_KEY` | AG Studio licence |

**Demo and tuning**

| Variable | Purpose |
|---|---|
| `DEMO_EXPANDED_CATALOGUE` | `false` for the small original fixture |
| `DEMO_PICKUP_TZ` | Time zone for seeded pickup slots |
| `POS_SIMULATOR_DATABASE` | Location of the POS simulator journal |
| `PF_PLACEMENT_BUDGET_S`, `PF_PLACEMENT_WAIT_S`, `PF_PLACEMENT_MAX_CELLS_PER_HOUR` | Store-placement time budget, per-request wait and cell cap |

## Database

`apps/api/migrations` is the schema authority. Production startup creates no tables and seeds no fictional data.

```bash
# from apps/api, with the server-only DATABASE_URL set
.venv/bin/alembic upgrade head
.venv/bin/alembic check          # no drift between models and migrations
```

`supabase/migrations/` is a reviewed bootstrap for a *fresh* project, exported by `scripts/export_schema.py`. Do not replay it over an existing project; use Alembic forward migrations. Browser roles get no table grants and every table has row-level security; FastAPI is the only access path. A Supabase publishable or secret HTTP key is not a PostgreSQL password. For long-running services needing IPv4, use the session pooler on port 5432 with the provider's SSL settings.

## Supabase project

1. Create a project in an allowed region.
2. Bootstrap with the SQL in `supabase/migrations/` (or run Alembic against the empty database).
3. Set `DATABASE_URL` (server-only), `SUPABASE_PROJECT_URL`, `SUPABASE_JWKS_URL` (`https://<id>.supabase.co/auth/v1/.well-known/jwks.json`) and `SUPABASE_JWT_AUDIENCE=authenticated`. Use asymmetric signing keys; never accept unsigned tokens.
4. Configure email auth, the Site URL (your web origin) and the callback and reset URLs.
5. Assign roles through `app_metadata` from a trusted server process. Never use `user_metadata`, and never trust a role chosen in the UI.
6. Keep `DEMO_MODE=false`. Onboard merchants through the real flow.

The security advisor will report "RLS enabled, no policy"; that is intentional for the backend-only access model. "Unused index" notes are expected on a new schema.

## Render staging

`render.yaml` defines three services: the API (pre-deploy `alembic upgrade head`, health check `/api/ready`), the durable worker, and the static web app. The worker shares the API's database and encryption credentials.

1. Connect the repository and choose compute plans in the authenticated Render workspace (review cost first).
2. Fill every `sync: false` variable in the blueprint; set `DEMO_MODE=false`.
3. Set `VITE_API_URL` to the API origin and `CORS_ORIGINS` to the web origin.
4. After the API has a public HTTPS URL, register the PayPal webhook at `/api/paypal/webhook` and set `PAYPAL_WEBHOOK_ID`.
5. For Shopify, register the exact redirect `https://<api-origin>/api/connectors/shopify/callback`.

The blueprint is a staging reference, not a live-money checkout. Add monitoring, backups, alerting and a recovery drill before accepting real orders.

## Containers

`apps/api/Dockerfile` and `apps/web/Dockerfile` (NGINX, needs a separate API host) are deployment references. They have not been built in CI or against a registry yet.
