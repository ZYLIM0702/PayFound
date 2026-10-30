# Third-party notices

PayFound's own source code is MIT licensed ([LICENSE](LICENSE)). Everything below keeps its own terms. This file is a good-faith summary, not legal advice; check each licence before redistributing.

## Needs attention before public redistribution

| Component | Where | Terms | Action |
|---|---|---|---|
| **Metronic Tailwind React template** (KeenThemes) | Derived primitives in `apps/web/src/components/ui/` and `apps/web/src/styles/config.metronic.css` | Commercial licence; does not automatically permit public redistribution | Get written permission, or replace with permissively licensed equivalents. The template archives are not in this repository |
| **AG Studio** (`ag-studio`, `ag-studio-react`) | Merchant analytics | Commercial; a trial or evaluation key is not a redistribution right | Use your own licence; keep the key in `.env` (`AG_STUDIO_LICENSE_KEY`, `VITE_AG_STUDIO_LICENSE_KEY`) |
| **AG Grid Enterprise and AG Charts Enterprise** | Merchant and admin tables and charts | Commercial for enterprise features; Community is MIT | Licence for production, or restrict to Community features |
| **Bryntum Calendar** (`@bryntum/calendar-trial`) | Pickup calendar | Trial; shows a watermark; not for production | Purchase a licence and install the licensed package |

## Data and media

| Asset | Source | Licence |
|---|---|---|
| Catalogue photographs (196) | Amazon Berkeley Objects | CC BY 4.0 |
| Catalogue photographs (4) | Wikimedia Commons | CC0, public domain, CC BY-SA 3.0 and 4.0, reviewed individually |
| Grocery photographs | Open Food Facts front images | CC BY-SA; data under the ODbL |
| Authors, source URLs, transformations and checksums | `apps/web/public/images/products/manifest.json`, `/image-credits.html`, `/image-credits-grocery.json` | Attribution must be kept |
| Landing page imagery | `apps/web/public/landing/CREDITS.txt` | As stated there |
| Store names, prices, stock, reviews, sales | Invented for the demo | Fictional |

Product text and prices shown from Channel3 are fetched at request time and not redistributed.

## Services and trademarks

PayFound integrates PayPal, Supabase, Google Maps Platform, Channel3, OpenAI, Shopify and WooCommerce through their public APIs, under their own terms. All names and marks belong to their owners. PayFound is not affiliated with, endorsed by, or a partner of PayPal or any other provider named here.

## Open-source libraries

Principal runtime dependencies, with licences read from the installed packages (full lists in `apps/web/package-lock.json`, `apps/api/requirements.lock` and `sdk/`):

| Library | Licence |
|---|---|
| React, React DOM, React Router, Vite, Tailwind CSS, Radix UI, `clsx`, `tailwind-merge`, Zustand, Zod | MIT |
| `lucide-react` | ISC |
| `class-variance-authority`, `@paypal/react-paypal-js` | Apache-2.0 |
| `@supabase/supabase-js`, OpenUI (`@openuidev/*`) | MIT |
| `ag-grid-community`, `ag-charts-community` | MIT |
| Leaflet | BSD-2-Clause |
| `react-leaflet` | **Hippocratic-2.1** (an ethical-source licence that is not OSI-approved; review before shipping, or drop the Leaflet fallback map) |
| FastAPI, Pydantic, SQLAlchemy, Alembic, PyJWT, OpenAI Agents SDK | MIT |
| Starlette, httpx, Uvicorn | BSD-3-Clause |
| `cryptography` | Apache-2.0 or BSD-3-Clause |
| `psycopg` | LGPL-3.0 (an unmodified dependency) |

Commercial packages (AG Grid Enterprise, AG Charts Enterprise, AG Studio, Bryntum) are covered above.

Run a licence audit (`npx license-checker` for the web app, `pip-licenses` for the API) before a release.
