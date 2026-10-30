# Payments and security

The contract every payment, role and data-handling change must keep. Architecture context: [ARCHITECTURE.md](ARCHITECTURE.md).

## Hard rules

- PayPal is **sandbox only** in this repository. No production credentials, no live-money operation.
- Amounts come from the server's locked order, never from the browser.
- Every modifying PayPal request carries a stable `PayPal-Request-Id`. An uncertain write is **read back**, never retried with a new ID.
- A timeout after a capture is *unknown*, not failed. Quarantine the hold, query PayPal, then decide.
- Nothing autonomous moves money. The AI assistant has no payment, refund, payout or role tool.
- A simulated payment is labelled as simulated and never called a PayPal transaction.
- A PayFound-side stock hold is valid only for PayFound-owned inventory. For a merchant's real stock, a merchant acknowledgement or approved source hold is required.
- `DEMO_MODE=true` is loopback-only and must be `false` on every public host.

## The sandbox payment path

References: [React SDK v6](https://developer.paypal.com/sdk/react/reference), [Orders API v2](https://developer.paypal.com/api/rest/integration/orders-api/), [Payments v2 refunds](https://developer.paypal.com/docs/api/payments/v2/), [webhook verification](https://developer.paypal.com/api/rest/webhooks/rest/).

1. Create a **sandbox business** and **sandbox buyer**, and a REST app under the seller, at developer.paypal.com.
2. Put only the *sandbox* client ID and secret in `apps/api/.env`; set `PAYPAL_ENV=sandbox`. `/api/config` exposes the client ID and never the secret.
3. The shopper reserves an item and opens `/checkout/:orderId`. The page mounts the PayPal v6 SDK, which checks eligibility (including Pay Later).
4. `createOrder` calls `POST /api/orders/{id}/paypal/create`. The API obtains an OAuth token and creates the order with the server-locked amount and a stable request ID.
5. The buyer approves in the PayPal popup. `onApprove` calls `POST /api/orders/{id}/paypal/capture`. The API captures server-side and verifies the provider order ID, order status, **capture status, amount and currency** before it atomically updates the order and stock.
6. If the result is uncertain or mismatched, the order becomes `RECONCILIATION_REQUIRED`. The worker, or `POST /api/orders/{id}/paypal/reconcile`, reads provider state. It does not capture again.
7. The merchant moves fulfilment `PAID → ACCEPTED → PREPARING → READY → COLLECTED`. Refunds use `POST /api/orders/{id}/refund`, which calls the capture-refund API.

For in-store pickup, Orders v2 distinguishes `PICKUP_IN_STORE` from the deprecated generic pickup types. Seller and buyer protection depend on the full program terms.

### What was verified against PayPal's sandbox

OAuth and read; order creation; a fixed-test-card approval, server capture and full refund (USD 39.99, with repeat capture and refund checks); the v6 wallet button rendering and approval document; and live signed `PAYMENT.CAPTURE.COMPLETED` and `PAYMENT.CAPTURE.REFUNDED` webhooks passing PayPal's verification in the real FastAPI handler. Forged signatures, changed amounts and duplicate deliveries were rejected or acknowledged once with no extra stock effect. The sandbox seller and the configured login are the same account, so wallet approval by a distinct buyer remains an open item ([STATUS.md](STATUS.md)).

A live finding worth remembering: a successful Payments v2 refund response can contain only `id`, `status` and `links`. Rejecting it for lacking `amount` left a completed refund pending locally. The adapter now requests the full representation and persists the refund identity before fetching details, so a failed readback recovers through the known refund resource, not a second refund.

## Payment state machine

See the diagram in [ARCHITECTURE.md](ARCHITECTURE.md#reservation-and-payment). `Order.status` (fulfilment) is separate from `payment_status`. Provider operations, attempts, refunds and events are durable records with unique constraints, so replays are no-ops.

## Webhooks

- Register an HTTPS webhook for `/api/paypal/webhook`; set `PAYPAL_WEBHOOK_ID`.
- Verify `paypal-transmission-id`, `-time`, `-cert-url`, `-auth-algo` and `-transmission-sig` through PayPal's verification endpoint **before** trusting content. Keep the original bytes; never reconstruct the body.
- Deduplicate by provider event ID. Verification precedes duplicate detection.
- Process asynchronously from the inbox. A verified unmatched event stays visible to operators. A generic provider event never implies a refund, restitution or a physical return.
- The Webhooks Simulator is **not** equivalent to genuine signed events; validate signatures with a real sandbox transaction.
- Permanent activation needs a deployed, non-demo HTTPS API endpoint.

## Pay Later and fees

Pay Later appears only when PayPal reports eligibility for the buyer, merchant, amount and country. PayFound never promises approval, instalment terms or APR, and offers no financing of its own. The U.S. Pay Later merchant fee is higher than wallet checkout; see [BUSINESS_STRATEGY.md](BUSINESS_STRATEGY.md#83-published-us-payment-fees-october-2026).

## Settlement model

One merchant per order. The merchant is seller of record and receives proceeds in its own eligible PayPal account. PayFound bills merchant software separately and holds no pooled balance.

**Not implemented:** PayPal-approved multiparty payments, platform-seller onboarding and platform fees. These need PayPal approval and have their own rules (`intent=CAPTURE`, seller-specific transactions, partial-success cases); they must not be approximated by combining ordinary single-seller orders. Funds reaching a seller account do not imply instant bank withdrawal; holds, verification and fees can apply. Payment-processing revenue belongs to PayPal unless a partner contract says otherwise.

## Authentication and authorisation

| Control | Detail |
|---|---|
| Token verification | Supabase asymmetric JWTs via a bounded-TTL JWKS cache; audience and issuer checks; wrong or expired signatures rejected |
| Role source | Server-set `app_metadata` only. `user_metadata` never grants authority |
| Memberships | Checked fresh on every request, so a revocation takes effect with the same token |
| Staff invitations | Email-only invites stay pending until server-side auth resolves the subject; no editable email metadata grants access |
| Demo roles | `x-demo-role`, loopback only, rejected when `DEMO_MODE=false` |
| Tenancy | Other stores and missing IDs are indistinguishable (404) |
| Rate limits | Per principal for the assistant, Channel3 and POS actions; public-mode quotas |

## Data protection

- **Secrets are server-side.** The compiled web bundle is scanned for configured secrets (`scripts/check_browser_secrets.py`). `/api/config` returns only public values.
- **Connector credentials are encrypted at rest** with `CONNECTOR_ENCRYPTION_KEY` (generated by `scripts/setup.py`). The API and worker must share the key. Payment-method links store only a masked label.
- **Row-level security** is enabled on every table with no browser grants; the browser never reads tables directly.
- **Consent.** Merchants grant discovery, private analytics, assistant use and model training as separate, revocable purposes. Real private store data reaches an AI model only after the owner's consent; synthetic demo data is exempt. Raw user text, customer identities, addresses and credentials are never sent to the catalogue or model providers.
- **Logs and audit.** Agent runs record tool names, counts, latency and status, never message content. Errors do not persist HTTP exceptions whose URLs or headers could carry secrets.
- **Third-party use.** Shopify's API terms constrain product indexes and AI use of its data; treat them as architecture constraints. Channel3 affiliate URLs and product facts are not persisted beyond a short price cache.
- **Retention and deletion.** Keep financial records in a restricted, compliant form; honour deletion requests; revoke credentials on disconnect.

## Connector and SSRF safety

Custom POS URLs must be HTTPS on port 443 with no credentials, query or fragment; hostnames are resolved and private, loopback, link-local and multicast addresses are refused, and IP literals are checked directly. Webhook pushes require a signature and a fresh timestamp and reject replays. See [CONNECTORS.md](CONNECTORS.md).

## Checklist for changes

| If you touch... | You must... |
|---|---|
| Checkout, refunds, webhooks | Test the deterministic mock *and* the real sandbox separately; add duplicate, retry and timeout cases |
| Stock | Test conditional reservation with simultaneous buyers and expiry |
| Any merchant-sensitive route | Enforce authorisation server-side; add a cross-tenant 404 test |
| Assistant tools | Add the result shape to the allow-list; confirm redaction in a test |
| Environment or config | Keep secrets out of `VITE_*`; document the variable in `.env.example` |

## Production gaps (known)

Approved live merchant onboarding and KYB; production credentials; MFA and granular scopes for staff; tax, shipping and receipts; chargeback and dispute handling beyond quarantine; appeals and moderation policy for reviews; PostgreSQL load tests; permanent webhook activation; and a legal review of merchant-of-record disclosures.
