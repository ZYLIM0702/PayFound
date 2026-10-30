# Merchant connectors and data rights

PayFound normalises products, branches, availability and fulfilment **without replacing** the merchant's authoritative POS or payment system. Connectors are graded by what they can actually promise, and that grade, not the vendor's name, decides what a shopper sees.

## Capability tiers

| Tier | Capability | PayFound may show |
|---|---|---|
| 1. Listable | Merchant-authorised catalogue and location | In search; stock may be unknown |
| 2. Observable | Stock snapshots or events | Freshness-labelled probable availability |
| 3. Reservable | Authoritative POS hold, draft order or merchant confirmation | A held state with expiry |
| 4. Transactable | Order, payment, fulfilment, refund and reconciliation | End-to-end reserve, pay and pickup |

Capabilities are independent flags recorded per merchant and branch (catalogue read, branch read, inventory read, inventory events, reservation, pickup-order write, external payment permitted, refund write, realtime status), along with grants, revocations and freshness. They are never inferred from a vendor name.

## What is built

| Source | Status | Notes |
|---|---|---|
| **WooCommerce** | Implemented and tested with provider stubs | Merchant REST keys entered in the wizard; encrypted at rest. Generic Woo stock is published only as ONLINE, never as an active local product; merchant-native checkout |
| **Shopify** | Implemented and tested with provider stubs | OAuth with an approved redirect; pinned stable GraphQL schema; inventory queried at one explicit location per page; cost-bucket-aware paging; signed event hints; conditional sync that never zeroes held inventory. Checkout stays on Shopify |
| **Custom POS (plugin)** | Implemented, with a loopback demo and a fake POS | Two modes: PayFound pulls (API key or bearer, on a schedule) or your POS pushes signed webhooks. Contract in [pos-plugin.md](../apps/api/docs/pos-plugin.md) |
| **Software POS simulator** | Implemented | A fictional register with a separate journal and stock bridge. Not a Zettle sandbox |
| **Channel3** | Implemented | Online catalogue only; never local stock |
| Square, Clover, Lightspeed, Loyverse | Not implemented | Candidates after the first certified connector |
| PayPal Zettle | Not implemented | API availability conflicts by region; see below |
| Google Merchant local inventory | Not implemented | Distribution channel, not a reservation service |

Nothing here has been run against a live merchant. Authorised WooCommerce and Shopify test stores are an open dependency ([STATUS.md](STATUS.md)).

## Source-specific constraints

| Source | Constraint |
|---|---|
| WooCommerce | Stock may be unmanaged; hold-stock plugins and variations differ |
| Shopify | Checkout, POS and marketplace rules apply; do not divert Shopify-generated orders into arbitrary PayPal checkout; API terms restrict indexing and AI use |
| Square | Webhooks are not ordered; the Orders API can add a 1% charge on externally processed payments, potentially billed to the developer; validate the contract |
| PayPal Zettle | The broad overview lists the U.S., while the detailed matrix and FAQ say Zettle APIs are not supported there and have no general sandbox. Malaysia is not on the supported list. Get written confirmation first |
| Google Merchant API | Updates can lag up to 30 minutes; not atomic |
| PayPal Store Sync | U.S. physical goods in USD with approval; not a universal local POS API |

## Consistency and freshness rules

- Record the source event ID, source version, `emitted_at`, `observed_at`, `processed_at` and a TTL or confidence.
- Reject events whose source version is older than the latest accepted one. Never let a delayed webhook overwrite a newer snapshot.
- Webhook retries must be idempotent; periodic full snapshots recover missed pushes.
- A missing version or stock figure is never read as a positive stock assertion. A negative provider quantity means unavailable, not negative local stock.
- Sync is mark-and-sweep: only records last seen *before* the current cycle can be removed, so a push arriving mid-cycle survives an older snapshot.
- PayFound-owned fields are never overwritten by a sync: hold quantity, hours and operational status, descriptions and canonical links. Quantity can never drop below outstanding holds.
- If the POS supports a hold, require its confirmation reference before promising pickup. If not, label stock "likely available", ask the merchant to confirm before taking payment, and offer another store or merchant-native checkout.
- When permissions are revoked, unpublish within the service level and account for propagation delays in other channels.

## Identity

Keep location-SKU identity composite and never assume the same SKU string means the same item across merchants. Authorised source variants can reuse a SKU without being merged. Use a GTIN only when its checksum validates and it is variant-specific; condition and dimensions matter as much as brand for compatibility.

## Data rights and consent

- A merchant grants product discovery separately from private analytics, assistant use and model training. Rights are explicit and revocable.
- A connected API alone does not permit an unrestricted cross-merchant index or model training. Respect each vendor's terms.
- Cross-merchant insights are opt-in, aggregated, and never competitor-sensitive benchmarking where unsupported.
- Credentials never enter queue events or model prompts. Every connector call is rate-limited and audited.
- Connector credentials are encrypted at rest and revoked on disconnect.

## Writing a connector

1. Implement catalogue and location listing, then inventory, then (only if the source truly supports it) reservation and order write.
2. Declare capabilities honestly; start at the lowest tier you can prove.
3. Handle OAuth scopes, expiry and revocation; map branches and products; respect provider rate limits; support both polling and webhooks.
4. Add contract tests with a provider stub, including bad rows (reported in the run log, never fatal), reordered events and a ten-minute outage.
5. Measure: median time to live catalogue, errors per 1,000 SKUs, usable branch-SKU offers, and support minutes per merchant. A connector that cannot be repeated cheaply is not worth shipping.
