# Product

**Find it nearby. Pay directly. Get it today.**

PayFound is a local-first product discovery, payment and pickup network. This document describes what each role can do, what the labels on screen mean, and where everything lives. The commercial reasoning is in [BUSINESS_STRATEGY.md](BUSINESS_STRATEGY.md).

## Principles

1. **Search products, not just stores.** A result is an exact item at a specific branch, with price, status and evidence.
2. **Honest availability.** Never show a listed quantity as a guarantee. Say how we know and how old it is.
3. **Merchants stay merchants.** They keep their POS, brand and payment account. PayFound does not hold seller funds.
4. **Local first, online as backup.** Online offers are always labelled ONLINE and never presented as local stock or pickup.
5. **The shopper pays; nothing pays on their behalf.** The AI never moves money. Reserving and paying are explicit clicks.
6. **Fictional data stays labelled.** Demo stores, stock and reviews are synthetic and say so.

## Availability labels

A shopper sees concepts that are kept separate in the data:

| Concept | Meaning | In the demo | With a real connector |
|---|---|---|---|
| Store location | Branch address and coordinates | Fictional stores, placed around the viewer | Merchant-verified geocoding and branch IDs |
| Opening hours | Scheduled hours in the branch's IANA time zone | Regular, holiday and overnight hours | Plus special hours and exceptions |
| Operational status | Open, temporarily closed, delayed | Schedule plus a merchant override | POS heartbeat and the merchant console |
| Quantity on hand | The source's reported shelf quantity | Synthetic value | Event or poll source with a version |
| Available to promise | Units not already held | `quantity - hold_quantity` | A confirmed source hold |
| Last update | When the source last asserted the quantity | Seed or edit time | Source-observed time, kept apart from ingest time |
| Pickup readiness | Real fulfilment state | Merchant workflow | Staff action or a POS event |

The label on the product card is derived from evidence and age:

| Label | Requires | Safe behaviour |
|---|---|---|
| **Reserved for you until [time]** | A merchant-authoritative hold or acknowledgement with expiry | Show hold ID, expiry, instructions |
| **Ready for pickup** | The merchant marked a specific paid order ready | Show branch, window, handover token |
| **In stock, updated N min ago** | A fresh reading | No hold implied |
| **Likely available** | A fresh feed with good source history | "Confirm before travelling" |
| **Availability uncertain** | Stale feed, unresponsive shop, unmapped variant | Ask to confirm, offer another branch or online |
| **Out of stock / not accepting pickup** | Authoritative zero, or the store cannot fulfil | Hide immediate purchase, offer alternatives |

Stock older than 15 minutes is treated as stale. A quantity of one is not a reservation.

## Shoppers

- **Home and Explore.** Search by product, category, "in stock" and "open now", with a radius and a Local / Online / Both switch. Results show price, store, straight-line and driving distance, hours and stock freshness. The Google map shows live traffic; **Show driving route** draws the road route with distance, ETA and arrival time. A shared location stays in the session and can be cleared.
- **Product page** (`/products/:id`). The item, its photos, and the same canonical item at other stores, cheapest first, with separate prices and stock. Comparison uses validated identity or an exact shared catalogue key, never fuzzy name or photo matching and never an invented GTIN.
- **Storefront** (`/stores/:slug`). Profile, hours, address, current status, products, verified-purchase reviews, directions and preparation time.
- **Basket and checkout.** The basket is saved to your account on the server, so it follows you across browsers and survives a cleared cache (the demo shopper starts with a few items). One merchant and branch per basket, server-locked totals, a ten-minute hold, pickup slot choice, and a PayPal sandbox payment with eligibility-aware Pay Later. A simulated payment is explicitly labelled and moves no funds.
- **Orders** (`/orders`). Status tracker from paid to collected, notifications, and a review once the order is collected.
- **Account** (`/account/...`). Wishlist, coupons, saved delivery details, payment-method link (sandbox), messages with stores, support tickets and profile.
- **Price watch.** Follow a product; a drop of 10% or more from the baseline is surfaced.
- **AI assistant** (`/agent`). See below.

### The assistant for shoppers

Ask in plain words or send a photo. It searches local stock first, widens the search itself if nothing is close, and shows ONLINE Channel3 offers beside the local results. It can plan a grocery basket for a dish (best single store, what is missing, a pickup slot), show a route, and check the weather. It asks for location in the page before the first search. It explains uncertainty instead of hiding it. Design and guardrails: [ASSISTANT.md](ASSISTANT.md).

## Merchants

A merchant workspace lives at `/merchant/*`, with onboarding at `/merchant/onboard`.

| Area | What it does |
|---|---|
| Overview | What needs attention today, ranked; KPIs; stock alerts; the order queue |
| Orders | AG Grid queue with master-detail; accept, prepare, mark ready, mark collected, refund |
| Pickup schedule | Bryntum Calendar of slots, capacity and bookings |
| Inventory and stock count | Inline edits with timestamps and audit; a printable count sheet; low and stale stock |
| Store profile | Branches, time zones, regular and exceptional hours, temporary closure |
| Forecast | Explainable demand forecast (trend x weather x events x weekday x payday x holidays), stock cover and what-if scenarios. Arithmetic, not a model; see [forecast-drivers](../apps/api/docs/forecast-drivers.md) |
| Analytics | AG Studio reports and a sales pivot; reports can be saved and printed |
| Online price check | Competitor prices from Channel3 (higher plans) |
| Connections | WooCommerce, Shopify and custom POS; publication controls; sync status |
| POS | A software register: tiles, cart, discounts, saved carts, SKU scan, simulated card and cash, receipts, a stock bridge. See [pos-plugin](../apps/api/docs/pos-plugin.md) |
| PayPal and payments | Receiving account, payment history, subscription and invoices |
| Plan | Free, Pro and Diamond (demo prices) |
| Messages, reviews, notifications | Pre-purchase enquiries, review replies, in-app alerts |
| Merchant assistant | Grounded, read-only operations partner that reads the store's own data |

The assistant on this surface only sees one store, only after the owner's AI consent for real data (synthetic demo data is exempt), and can only save a named report.

## Administrators

`/admin/*`: merchants, orders, review moderation (hide a review and the storefront updates), an audit table, the reconciliation queue for orders needing payment follow-up, failed-job retry, and integration status. Admin access is scoped and audited; there is no secret impersonation and no debug bypass in production.

## Page map

| Route | Who | Purpose |
|---|---|---|
| `/`, `/landing` | Everyone | Home and landing |
| `/explore`, `/map` | Everyone | Search and map |
| `/products/:id`, `/stores/:slug` | Everyone | Item, comparison, storefront |
| `/basket`, `/cart`, `/checkout/:orderId` | Shopper | Basket, reserve, pay |
| `/orders`, `/account/*` | Shopper | History, tracking, account area |
| `/agent` | Shopper | AI assistant |
| `/merchant/onboard`, `/merchant/*` | Merchant | Onboarding and workspace |
| `/pos`, `/pos/:view` | Merchant | Software POS |
| `/admin/*` | Admin | Operations |
| `/login`, `/signup`, `/forgot-password`, `/reset-password`, `/auth/callback` | Everyone | Supabase email auth |
| `/privacy`, `/terms` | Everyone | Policies |

## Definition of a working demo

A developer can: search and open the map; open a store and read labelled sample reviews; reserve an in-stock item with an expiring hold; complete a clearly simulated payment, or a real PayPal sandbox payment with sandbox credentials; switch to the merchant and move the order to collected; leave a verified review; switch to the administrator and moderate it; use AG Grid for operations and AG Studio for analytics; ask the assistant a question and see local and ONLINE results together.

This is not merchant-production readiness. Real POS synchronisation, certified connectors, PayPal platform approval and regulated operations are separate work ([STATUS.md](STATUS.md)).
