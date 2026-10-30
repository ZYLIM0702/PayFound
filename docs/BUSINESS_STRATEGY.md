# PayFound business strategy

> **Find it nearby. Pay directly. Get it today.**
> The world has connected payments, but local products remain disconnected.

This document is the commercial thesis behind PayFound: who it serves, why it can win, how it makes money, how it gets its first customers, and what has to be proven before it scales. It is written for partners, judges, investors and anyone deciding what to build next.

**How to read the numbers.** Every figure below falls into one of four classes, and the text says which:

| Class | Meaning |
|---|---|
| **Fact** | Published by a primary source (Census, SEC filings, vendor pricing pages). Sources are listed in [Sources](#sources). |
| **Design** | A decision PayFound has made and, where noted, built. |
| **Hypothesis** | A belief to be tested in the pilot. It is not evidence. |
| **Scenario** | An explicit-assumption model, not a forecast. |

PayFound is a pre-commercial prototype. It has no live merchant partnerships, no approved PayPal platform status, no certified POS connectors and no consumer traction. Nothing here should be read as claiming otherwise.

---

## 1. The thesis in one page

A shopper who needs a specific product today can usually find *shops* nearby. They cannot reliably find the *exact product inside those shops*, learn which branch has it, confirm the branch is open and taking pickup orders, reserve it, and pay, without a wasted trip. Independent retailers already hold the stock, the addresses, the hours and a payment account. What is missing is a trustworthy, permissioned, fresh view of local supply that a person or an AI agent can act on.

PayFound is that layer: a **local-first commerce discovery and transaction-execution network**. It connects merchant-authorised POS and catalogue data, shows honest branch-level availability with evidence and freshness, lets the shopper reserve, pays the merchant directly through eligible PayPal checkout, and tracks the order through pickup.

Three parties each lack one thing, and PayFound supplies all three:

| Party | Cares about | What is missing today | What PayFound provides |
|---|---|---|---|
| **Merchant** | Visibility | Product-level local discovery; a way to accept an order without a new system | Publish the inventory they already own, then receive pickup orders |
| **Shopper** | Convenience | Trustworthy stock; reserve and pay in one step | Search products on a map or by asking an AI agent, then reserve, pay and collect |
| **AI agent** | Context | Live, structured, permissioned facts about the physical world | A governed local commerce graph with timestamps, evidence and safe tools |

**Core bet:** for physical commerce, the binding constraint on AI shopping is not model size, it is missing real-world context. A larger model cannot know that a shop's last unit sold two minutes ago. PayFound's job is to connect and govern the source systems that can know, and to let AI interpret intent and act safely on that data.

## 2. What PayFound is, and is not

| PayFound is | PayFound is not |
|---|---|
| A connector above existing POS and inventory systems | A forced POS replacement |
| A product-and-location-aware discovery layer | Another map of store addresses |
| A merchant-authorised reserve, pay and pickup coordinator | A promise that every merchant can hold stock |
| A tool and data layer for grounded AI shopping | A model that invents missing stock facts |
| A preferred PayPal integration where permitted | A new payment gateway, or an existing PayPal partner |
| A network online stores can join as complementary supply | A general online storefront builder |
| Merchant-direct in its payment design | A pooled-funds marketplace that holds seller money |

**Local first, not local only.** Physical branches are the launch supply base. Online stores connect as complementary supply and as the fallback when the best answer is online. PayFound does not try to displace e-commerce; it connects physical commerce to AI-assisted buying.

## 3. The problem, in four failure modes

1. **Discovery.** A search returns stores, categories or shippable items, not the exact nearby SKU and compatible variant. Local merchants are invisible at the moment demand exists.
2. **Context.** The shopper's needs (compatibility, budget, urgency, distance) meet store feeds with mismatched identifiers and missing attributes. A text-only agent confidently recommends the wrong variant.
3. **Availability.** A feed says "2 left", but the branch is closed, the count is stale, or a walk-in bought the last unit. "In the POS" is not "physically verified", "reserved" or "ready for pickup".
4. **Execution.** Even after discovery there may be no merchant-authorised way to reserve, take payment, alert staff, confirm readiness or reconcile a cancellation. A results page without an order path produces a lead, not a purchase.

A concrete case: *"My laptop charger broke. I need a compatible 65 W USB-C charger in the next two hours, under $60. Where can I collect it?"* A normal search surfaces stores, websites and delivery offers. PayFound extracts the requirements, queries branch-level offers, checks hours and pickup capacity, separates trustworthy stock from unconfirmed counts, reserves with the merchant where supported, and presents approved payment. If no local option is feasible, the same agent shows online offers, clearly labelled, so the shopper gets the best fit under their constraints rather than a falsely local answer.

## 4. Market and wedge

### 4.1 Why physical retail

**Fact.** The U.S. Census Bureau reported Q2 2026 seasonally adjusted retail sales of $1,986.5 billion, of which $340.2 billion (17.1%) was classified as e-commerce. The other 82.9% was not classified as e-commerce.

**Careful reading.** This shows retail is far broader than the web-ordering channel. It does **not** mean 82.9% of purchases are available to PayFound, that 82.9% of shoppers buy in stores, or that this is PayFound's addressable market. Census classifies by ordering method, so a pickup order placed online is still e-commerce. The figure is context, not a TAM.

### 4.2 Bottom-up reachable market

Do not multiply retail volume by a fee. The market that matters is:

```
reachable merchant locations
  x share with legally integrable inventory
  x usable SKU fraction
  x merchant willingness to join
  x economically addressable local demand
  x ability to complete orders
```

Keep locations, merchant organisations, PayPal accounts, products, inventory records and consumer accounts distinct; they are not interchangeable. The starting market is one testable district or city cluster. National and global expansion follow measured coverage and activation economics.

### 4.3 The wedge

Launch with **one geography, one or two categories, and a dense group of real stores**, in situations where the product is identifiable, the buyer wants it soon, the branch is close and the merchant can fulfil without delivery operations.

| Category | Role |
|---|---|
| Electronics accessories | Clear demonstration: chargers, cables, adapters |
| Hardware and home repair | Strongest commercial test, if SKU and fitment quality can be controlled |
| Pet essentials, selected auto consumables | Later comparison cohorts |
| Fashion, full automotive fitment, grocery delivery | Deliberately avoided in the first release; too much complexity |

### 4.4 Who to sell to first

| Segment | Need | Starting attractiveness |
|---|---|---|
| Physical stores with usable POS stock but little online product exposure | Product-level local visibility and pickup | **High**, given merchant consent and usable SKUs |
| Specialty stores with urgent exact-match products | Fitment, stock confidence, immediate collection | **High** with a bounded taxonomy |
| Multi-branch independents | Per-branch allocation and status accuracy | High, but integration is harder |
| Multi-channel retailers with disconnected stock | Reconcile physical and digital availability | High if PayFound adds value beyond their own connectors |
| Single Shopify store already using native pickup and Google | Incremental discovery only | Lower, unless a clear new buyer channel appears |
| Large omnichannel enterprise | Contracted integrations | Later; sales and implementation burden |

## 5. Competition and the white space

Local inventory search already exists. Saying nobody does this would be a factual error.

| Provider | What it already does | PayFound's opening to validate |
|---|---|---|
| Google Search, Maps, Merchant Center | Local inventory and free local listings at huge reach | Faster, more reliable holds; Google's own docs say local inventory changes can take up to 30 minutes to appear, so it suits distribution, not transactional locking |
| Locally | Retailer inventory feeds, BOPIS/ROPIS, attribution; paid order services from 3.5% | Easier entry for an underserved merchant cohort; a merchant-neutral shopper and agent experience |
| NearSt | POS inventory published to Google and others; from about £49 per location per month on selected POS | Deeper reservation and transaction execution, beyond feed publishing |
| Shopify, Square, Clover, Lightspeed | Merchant checkout, native pickup, POS and order management | Cross-vendor discovery with no merchant migration (integration rights differ by vendor) |
| Amazon, eBay, Etsy | Online search, traffic and transactions | On-demand nearby independent shelves; not a replacement for online marketplaces |
| Alipay, Ant, Taobao | Payments, local services, mini-programs, agentic services | A different market-entry wedge; not a claim that Alipay lacks local services |

**The precise gap to validate:** incomplete independent-retailer coverage, unreliable cross-system stock, inconsistent pickup readiness, and the inability to execute one trustworthy local order across heterogeneous merchant systems.

### Moat hypotheses

Defensibility is not established yet. It could accumulate from:

- authorised merchant density in a place;
- quality of normalised product identity;
- per-location freshness and accuracy history;
- verified successful pickups;
- repeatable, cheap connector activation;
- consented merchant and shopper preference signals.

Each is only a moat if it is made operationally reliable and cheap to maintain. An API wrapper, a generic assistant or an attractive storefront is not one.

## 6. Why PayPal, and what that does and does not give us

PayPal already offers checkout, Pay Later, risk and fraud tooling, merchant servicing, POS, and emerging agentic commerce products. PayFound does not claim PayPal lacks discovery or merchant data. The narrower thesis:

> PayPal's payment and shopping products do not automatically create an open, branch-specific, live reservation network across independent third-party POS systems. PayFound can supply that source-system orchestration and local fulfilment context, producing more eligible PayPal transactions and merchant touchpoints.

Whether that is attractive to PayPal is a partner conversation, not an assumption.

**Fact (PayPal Q2 2026 Form 10-Q).** 439 million active accounts, about $486.4 billion quarterly total payment volume, about $8.68 billion quarterly net revenue. Consolidated lines cannot be used to value any single product.

**What integrating PayPal gives:** familiar checkout, risk controls, a developer platform, and less payment infrastructure to build.

**What it does not give:** distribution to PayPal's user base, rights to its Transaction Graph, access to merchants' POS inventory, approved platform-seller status, or partner economics. Network growth still means PayFound recruiting merchants and shoppers itself.

### Integration priorities

| PayPal capability | Role | Priority | Constraint |
|---|---|---|---|
| Orders API v2 and Checkout | Single-merchant shopper checkout | **P0, built (sandbox)** | Merchant configuration and eligibility |
| Webhooks and refunds | Confirmation, cancellation, reconciliation | **P0, built (sandbox)** | Signature validation, idempotency, provider-state recovery |
| Pay Later | Financing on eligible higher-ticket buys | P1 | Eligibility varies; higher merchant fee in the U.S. |
| Subscriptions | PayFound's own merchant SaaS billing | P1, partly built | Separate platform-billing rules |
| Invoicing, Payment Links | Special and reservation payments | Conditional | Not a stock-hold system |
| POS / Zettle | Stock and purchase records | Conditional | Regional API conflicts; no universal stock access |
| Approved platform seller onboarding, multiparty payments | Seller-direct settlement and platform fees | Later; partner track | Explicit PayPal approval |
| Store Sync, Agent Ready | Catalogue and cart publication to agents | Later | U.S. physical goods in USD; approval needed |
| AI Toolkit / MCP | Build-time help for integrating PayPal | Build-time tool | Not a store-stock API |

PayFound's assistant exposes PayPal sandbox status through a read-only MCP bridge for administrators. It never moves money on its own.

## 7. The product promise: honest availability

The defensible technology is **product identity + precise location + opening and pickup status + source-observed availability + the ability to reserve + verified transaction execution.** Trust is the product, so the labels are strict:

| Label shown to shoppers | Evidence required | Experience |
|---|---|---|
| **Reserved for you until [time]** | Merchant-authoritative hold or explicit merchant acknowledgement with expiry | Hold ID, expiry, pickup instructions |
| **Ready for pickup** | Merchant marks a specific paid order ready | Branch, collection window, handover token |
| **In stock, recently updated** | Fresh source reading | "Updated X minutes ago"; no hold implied |
| **Likely available** | Fresh feed plus good source history, no hold | "Confirm before travelling" |
| **Availability uncertain** | Stale feed, unresponsive shop or unmapped variant | Request confirmation, another branch, or online |
| **Out of stock / not accepting pickup** | Authoritative zero, or store cannot fulfil | Hide immediate purchase; offer alternatives |

A quantity of one in a POS feed is **not** a reservation: staff may sell it to a walk-in before the online payment completes. A PayFound-side hold is valid only where PayFound is authoritative for that inventory; otherwise a merchant acknowledgement or an approved source-system hold is required. This is why connectors are graded by capability.

### Connector capability tiers

| Tier | Capability | What PayFound may offer |
|---|---|---|
| 1. Listable | Merchant-authorised catalogue and location | Appears in search; stock may be unknown |
| 2. Observable | Stock snapshots or events | Freshness-labelled probable availability |
| 3. Reservable | Authoritative POS hold, draft order or merchant confirmation | Explicit held state with expiry |
| 4. Transactable | Order, payment, fulfilment, refund and reconciliation | End-to-end buy, reserve and pickup |

## 8. Business model

### 8.1 Revenue ladder: value before fee extraction

1. **Merchant subscription (first).** For connectivity, validated stock quality, order acceptance and operations reporting. *Hypothesis:* $49 to $99 per month per merchant or eligible branch package, segmented by connector effort, locations and usage. This is a price **test**, not demonstrated willingness to pay. Adjacent benchmarks are Locally (free base publishing, paid transactions) and NearSt (from about £49 per location per month).
2. **Order execution services (second).** Optional service fees or approved referral and partner fees, only where orders deliver enough incremental merchant profit.
3. **Later.** Premium branch analytics, labelled promotion and performance services, once real network traffic exists.

**Never counted as PayFound revenue:** PayPal processing fees, merchant GMV, unapproved partner fees, or any assumed share of PayPal Ads revenue.

The prototype implements this ladder with three demo price points (`apps/api/app/plans.py`), billed through PayPal subscriptions (`paypal_billing.py`):

| Plan | Monthly | Active listings | Captured sales per month | PayFound fee on captured sales |
|---|---:|---:|---:|---:|
| Free | $0 | 15 | $5,000 | 2.5% |
| Pro | $49 | 300 | $50,000 | 1.5% |
| Diamond | $199 | Unlimited | Unlimited | 0.75% |

These are placeholders to exercise the plumbing, not validated prices. The fee is charged **on top of** PayPal processing, so a Free-plan order carries about 6% combined cost at U.S. wallet rates; section 8.4 explains why that level needs real incremental-order evidence before it is used with live merchants.

### 8.2 Merchant unit economics (illustrative)

A genuinely incremental $60 pickup order, 35% product gross margin, PayPal wallet fee of 3.49% + $0.49 (U.S. published rate), a hypothetical 1.5% PayFound service fee and $2 of picking labour:

| Item | Amount |
|---|---:|
| Gross profit on goods ($60 x 35%) | +$21.00 |
| PayPal wallet processing | -$2.58 |
| Hypothetical PayFound service fee | -$0.90 |
| Picking and preparation | -$2.00 |
| **Merchant incremental contribution** | **+$15.52** |

A $59 per month subscription needs about four such orders to pay for itself. The simplification ignores tax, refunds, fraud, returns, fixed costs and discounts. **If the shopper would have bought from that merchant anyway, PayFound only adds cost.** A merchant wins on incremental contribution profit, not on impressions or attributed GMV.

### 8.3 Published U.S. payment fees (October 2026)

| Category | Published standard fee | On a $100 purchase |
|---|---:|---:|
| PayPal Checkout wallet | 3.49% + $0.49 | $3.98 |
| PayPal Pay Later | 4.99% + $0.49 | $5.48 |
| Standard card | 2.99% + $0.49 | $3.48 |
| Eligible Expanded Checkout cards | from 2.89% + $0.29 | $3.18 |
| POS card-present | 2.29% + $0.09 | $2.38 |

These are published U.S. rates. Contracts, currencies and surcharges change the real cost. None of it is automatically PayFound revenue. Pay Later is a conversion option with a higher merchant fee, not free merchant revenue; eligibility must be queried live and PayPal-approved messaging used.

### 8.4 Why a 1% commission is dangerous

On a $50 basket, 1% is $0.50. For some Square Orders API operations that record externally processed payments, published terms identify an extra 1% API charge that can fall on the developer, which could erase the whole 1% before any support, infrastructure or acquisition cost. PayFound therefore stays **payment-flexible and provider-aware**, and gets written, current terms before quoting a margin.

### 8.5 Four money-flow models

| Model | Buyer checkout | Seller proceeds | PayFound earns | Verdict |
|---|---|---|---|---|
| **A. Merchant checkout** | Merchant's own permitted checkout | Merchant | SaaS and contracted services | **Start here (built)** |
| **B. Approved PayPal multiparty** | Platform-enabled order | Eligible sellers directly | Approved platform fees plus SaaS | Strategic later path; needs PayPal approval |
| **C. Marketplace funds custody** | PayFound collects, then remits | PayFound first | Marketplace spread | **Avoid by default:** payouts, licensing, treasury, disputes |
| **D. Referral / pay in store** | At the store or an external checkout | Merchant | SaaS or explicit referral fee | Good fallback where the POS has no digital hold |

Merchant-direct settlement is **not** "no accounting". PayFound still needs order-level payment references, fee accounting, refund and chargeback handling, merchant-of-record disclosure and reconciliation. Funds reaching a seller's PayPal balance do not imply instant bank withdrawal.

### 8.6 Five-year scenario (assumptions, not a forecast)

Assumptions: $89 per month subscription; 94% retained after a blended billing deduction; 14% annual merchant churn; 120 / 350 / 900 / 2,000 / 4,000 new merchants per year; fee-bearing transaction penetration 0 / 15 / 25 / 35 / 45%; 40 monthly orders per enabled merchant; $65 average basket; 1.5% hypothetical fee; $0.65 per order startup-borne cost (optimistic); $15 per merchant per month support and infrastructure; $250 acquisition and onboarding per new merchant.

| Metric | Y1 | Y2 | Y3 | Y4 | Y5 |
|---|---:|---:|---:|---:|---:|
| Year-end paying merchants | 120 | 453 | 1,290 | 3,109 | 6,674 |
| Retained SaaS revenue | $60K | $288K | $875K | $2.21M | $4.91M |
| Transaction-service revenue | $0 | $20K | $102K | $360K | $1.03M |
| **Total modelled revenue** | **$60K** | **$308K** | **$977K** | **$2.57M** | **$5.94M** |
| Direct support, order and acquisition cost | $41K | $153K | $450K | $1.14M | $2.57M |
| Central fixed operating expense | $250K | $500K | $1.05M | $1.90M | $3.00M |
| **Modelled operating result** | **-$231K** | **-$345K** | **-$523K** | **-$468K** | **+$374K** |

This accumulates roughly **$1.19M of operating loss** before turning positive in Year 5, and it has not been validated against real demand. Sensitivities: +$150 CAC in Year 5 costs about $600K; +$1 per order across about 1.06M enabled orders costs about $1.06M. Legal, cash-flow, refund, fraud and provider-fee exposure are not fully modelled. It is a stress test of assumptions, not a fundraising requirement or a statement about PayPal revenue.

**Decision logic.** Track separately: merchant activation CAC; monthly merchant contribution; merchant lifetime; support and connector cost; shopper acquisition cost; revenue retained per order; true merchant incremental contribution; refund and cancellation loss; and cost per reliable reservation.

## 9. Go-to-market

### 9.1 Sequence

| Horizon | Focus | Evidence needed to advance |
|---|---|---|
| **First 30 days after** | Real onboarding design, Shopify and WooCommerce test stores, one real POS connector, stock-version tests | Written API rights, authorisation, reproducible results |
| **90-day merchant pilot** | 12 to 20 real stores, two categories, physical stock audits, paid ROI | See [pilot gates](#10-validation-plan) |
| **6 to 12 months** | Certified connectors, self-service onboarding, permitted Google local distribution | Lower CAC and payback, healthy connector uptime, profitable incremental orders |
| **Year 2+, conditional** | More cities, agentic channels, approved PayPal partner capabilities, optional delivery and promotion | Signed agreements, network density, repeatable economics |
| **When load justifies** | Outbox to Kafka, Elasticsearch, Kubernetes | Real benchmarks (see [ARCHITECTURE.md](ARCHITECTURE.md)) |

### 9.2 Winning merchants

- **Pitch the outcome, not the dashboard:** "make the inventory you already own discoverable and purchasable nearby." Analytics and forecasting are supporting features, and their value must be measured.
- **Keep onboarding honest.** The target experience is "connect your POS, pick your stores, review the catalogue, go live". It is strongest for supported POS with clean identifiers and accurate counts. Messy or legacy catalogues need CSV import, photos and manual matching. Publish median time-to-live-catalogue, self-service completion rate, errors per 1,000 SKUs and support minutes per merchant; do not claim "one click for every shop".
- **Do not force PayPal.** A merchant without PayPal can publish eligible products and use a supported existing checkout or reserve-and-pay-at-store, with an optional guided PayPal Business signup. For Shopify, an approved sales channel generally sends the buyer to Shopify Checkout, and discovery rights do not authorise rerouting payment.
- **Decline bespoke builds.** Support only repeatable, tiered connectors.

### 9.3 Winning shoppers

Demand has to be earned locally, not assumed. Lead with the urgent, exact-product moment ("I need it today"), where a wasted trip is expensive. Keep search usable without an account. Rank on compatibility first, then ability to fulfil by the requested time, evidence and freshness, travel burden, price and merchant reliability. Any paid placement must be labelled and must never override availability or fitment.

### 9.4 Online stores as supply, not the enemy

An online merchant installs an authorised catalogue connector (WooCommerce is the practical independent test; Shopify within its app and sales-channel rules). Checkout stays on the merchant's compliant storefront. PayFound shows online results as complements or fallback, and labels them ONLINE so they are never mistaken for local stock. Marketplace feeds from Amazon, eBay or Etsy need explicit permission.

## 10. Validation plan

### 10.1 Merchant experiment

Recruit about 12 to 20 pilot stores in a dense test area, two categories at most, and at least two materially different inventory systems. Before intervening, capture baselines: 50 to 100 audited branch-SKU observations per merchant, POS errors, current pickup failures, staff time and historical sales. Record consent, data rights and payment terms.

### 10.2 Evidence gates (targets, not achievements)

| Metric | Proposed gate |
|---|---|
| Self-service onboarding | At least 80% of supported setups with no bespoke code |
| Time to live catalogue | Track median and p95; under 30 minutes for clean supported merchants |
| Physical availability accuracy | At least 95% on a defined audited sample |
| False in-stock purchases | Under 3%, with confidence intervals by category |
| Pickup ready within the promised window | At least 95% |
| Payment safety | Zero platform-caused duplicate captures; 100% of uncertain outcomes reconciled |
| Paid adoption | At least five pilot merchants paying and retained after introductory offers |
| Merchant ROI | Positive net incremental contribution or labour saving after added costs |
| Local intent fulfilment | Measured share of qualified local searches that become confirmed offers or collections |
| Agent accuracy | Correct compatible SKU and grounded status, calibrated confidence |
| Platform economics | Positive unit contribution after CAC amortisation, source API fees and support |

A pilot of this size shows feasibility and operational performance. It cannot establish a national causal sales uplift.

### 10.3 The A/B/C test

- **A. Baseline:** the merchant's existing stock, visibility and checkout.
- **B. Connected inventory:** authorised publication, freshness labels, store status and basic accuracy tools.
- **C. Connected execution:** B plus confirmed hold and pickup, eligible PayPal or merchant checkout, and merchant order tools.

The comparison that matters is **C versus B**: does the reservation-and-payment layer create *additional profitable completed orders* beyond inventory distribution alone? It avoids assuming every referred order would otherwise be lost.

### 10.4 Written answers needed from PayPal

1. Which country and entity structures qualify for partner, seller-onboarding and embedded-account models?
2. What approval permits seller-directed platform fees, and which payment methods support the pickup transaction?
3. Which countries support PayPal POS/Zettle **inventory** APIs (not only payment SDKs), and do the account and location models allow branch-level stock?
4. Can a merchant-authorised POS aggregator join Store Sync, and is there an accessible sandbox or partner path?
5. What servicing, reporting, refund, dispute and reconciliation entitlements can PayFound embed?
6. Are PayPal consumer or merchant distribution, account linking or partner economics available by contract, as opposed to merely technically possible?
7. What are the settlement timing, withdrawal and KYC/KYB constraints in the launch geographies?

Zettle caution: PayPal's own pages conflict on region. The broad overview lists the U.S., while the detailed matrix and FAQ say Zettle APIs are not supported there and offer no general sandbox. Prioritise independent POS connectors until PayPal confirms country, account, API and location semantics in writing.

## 11. Risks

| Risk | Severity | Mitigation and proof required |
|---|---|---|
| Overclaiming that local product search is novel | High | Cite Google, Locally and NearSt; show underserved coverage or better execution |
| No real branch stock or hold mechanism | **Critical** | Capability tiers, source timestamps, merchant confirmation, honest uncertainty, physical audits |
| PayPal multiparty approval absent | Critical for that model only | One merchant per order; merchant checkout plus SaaS; apply for approval separately |
| PayPal association overstated | High | Describe PayPal as a technology provider and potential partner; never imply an agreement |
| Shopify checkout or data-use violation | **Critical** | Compliant sales channel, consent, legal review, no unauthorised redirects or model training |
| Merchant funds and withdrawal misconceptions | High | Seller-of-record model; accurate cash-out descriptions |
| Too little qualified local demand | **Critical** | Density tests by geography and category; measure incremental orders |
| Costly merchant integrations | High | Tiered connectors, support budgets, decline bespoke work |
| AI stock hallucination | **Critical** | Grounded tools, evidence state, confidence thresholds, mandatory confirmation |
| Double capture or partial payment inconsistency | **Critical** | Idempotency, provider reconciliation, separate payment states, failure-injection tests |
| Sensitive merchant or shopper data misuse | **Critical** | Tenant isolation, purpose-scoped grants, model-data governance, deletion workflows |
| Overengineering | Medium to high | Modular monolith first; measured triggers for Elastic, Kafka and Kubernetes |

### What not to build first

No competitor to Shopify's storefront builder. No merchant funds custody or vendor withdrawal portal. No cross-seller cart that needs PayPal platform approval. No own credit underwriting. No courier fleet. No compulsory hardware. No AI training on private merchant history. No Kafka or Kubernetes cluster for perceived scale.

## 12. Pitch narrative

1. **Hook.** The world has connected payments, but local products remain disconnected. A shopper needs an exact item that a nearby store already holds.
2. **The missing three-way connection.** Merchants need visibility, shoppers need convenience, agents need trustworthy real-time context.
3. **Why now.** Most U.S. retail sales are not classified as e-commerce; agentic commerce needs grounded merchant tools and local supply; mature payment rails mean no new gateway.
4. **Alternatives and their limits.** Google, Locally and NearSt do important parts of local visibility. PayFound targets the reliable availability-to-pickup execution layer for an underserved segment.
5. **Solution.** Branch-level products, store status, stock freshness and evidence, merchant holds, map-first search, an AI agent and eligible payments.
6. **PayPal leverage.** Familiar checkout and approved seller services; never an assumed partnership, zero effort, or instant bank disbursement.
7. **Network effect, honestly.** Each authorised connection enriches discovery. The durable metric is quality and completed transactions, not listing count.
8. **Business model.** Paid merchant value first, permitted execution fees later. GMV is not revenue.
9. **Evidence.** A real PayPal sandbox transaction, source-labelled stock and merchant readiness. No fictional traction presented as real.
10. **Ask.** First category and geography, partner approval requests, a merchant pilot and objective decision gates.

### One-minute positioning

**PayFound connects the real-world commerce data that digital payments and AI need.** A shopper may know where the nearest store is yet still cannot tell whether that branch has the exact product right now. Independent merchants own stock and payment systems, but their products stay invisible to digital purchase intent. PayFound links merchant-authorised POS and branch data into a local-first network: shoppers find, compare, reserve and buy nearby; merchants gain visibility and completed sales; AI agents gain reliable live context and permissioned tools. With PayPal's eligible payment infrastructure, merchants stay the seller instead of PayFound reinventing a pooled-funds marketplace. Online stores join through lightweight authorised plugins when local supply is not the best answer. **The ambition is not to replace e-commerce. It is to connect physical commerce to the next generation of AI-assisted purchasing.**

## Sources

Figures and terms were current at the 23 October 2026 research synthesis. Reconfirm before external publication or any contractual reliance.

- U.S. Census Bureau, Quarterly Retail E-Commerce Sales, Q2 2026: https://www.census.gov/retail/ecommerce.html
- PayPal Holdings, Form 10-Q for Q2 2026: https://www.sec.gov/Archives/edgar/data/1633917/000163391726000082/pypl-20260630.htm
- PayPal U.S. business fees: https://www.paypal.com/us/business/fees
- PayPal Orders API v2: https://developer.paypal.com/api/rest/integration/orders-api/
- PayPal multiparty payments: https://developer.paypal.com/platforms/checkout/standard/customize/multiseller-payments
- PayPal platform onboarding and approval: https://developer.paypal.com/platforms/get-started
- PayPal Store Sync: https://developer.paypal.com/store-sync/overview
- PayPal AI Toolkit: https://github.com/paypal/AI-Toolkit
- Google Merchant local inventory (30-minute propagation): https://developers.google.com/merchant/api/samples/insert-local-inventory
- Locally retailer pricing: https://join.locally.com/pricing-for-retailers
- NearSt: https://start.near.st/loyverse
- Shopify sales channels: https://shopify.dev/docs/apps/build/sales-channels
- Shopify API terms: https://www.shopify.com/legal/api-terms
- Square Orders API: https://developer.squareup.com/docs/orders-api/what-it-does
- Zettle API regions and FAQ: https://developer.zettle.com/docs/api and https://developer.zettle.com/docs/faq
- Supabase row-level security: https://supabase.com/docs/guides/database/postgres/row-level-security
- Channel3 developer platform: https://www.trychannel3.com/developers/
