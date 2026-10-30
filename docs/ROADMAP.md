# Roadmap

Each stage has a gate. Moving on without the evidence repeats the mistake the product exists to fix: promising availability that is not real. Commercial reasoning: [BUSINESS_STRATEGY.md](BUSINESS_STRATEGY.md). Scaling steps: [ARCHITECTURE.md](ARCHITECTURE.md#path-to-scale).

| Stage | Focus | Gate to advance |
|---|---|---|
| **1. First 30 days after** | Real onboarding design, WooCommerce and Shopify test stores, **one real POS connector**, stock-version tests, exception handling | Written API rights; authorisation; reproducible end-to-end results |
| **2. 90-day merchant pilot** | 12 to 20 real stores, two categories, physical stock audits, paid ROI, real pickup reliability | Accuracy at least 95% on an audited sample; false in-stock under 3%; pickup ready at least 95% on time; five merchants paying and retained; positive incremental contribution |
| **3. Months 6 to 12** | Certified connectors, self-service onboarding, permitted Google local distribution, merchant operations depth, local density | Lower merchant CAC and payback; connector uptime; profitable incremental orders |
| **4. Year 2+, conditional** | More cities, agentic channels, approved PayPal partner capabilities, optional delivery and promotion | Signed agreements; network coverage; repeatable economics |
| **When load demands it** | Transactional outbox to Kafka, Elasticsearch, Kubernetes | Benchmarks and reliability data justify the cost |

## Next engineering work

Ordered by what unblocks the most trust.

1. **Distinct sandbox buyer** and a recorded wallet capture, so the demo shows a full PayPal-approved purchase end to end.
2. **Run FastAPI against the provisioned PostgreSQL**, with tenant-isolation tests on the real database and a connection-pool review.
3. **Deploy staging on Render** and register the permanent webhook with its own ID.
4. **One real POS connector** (an independent POS with a documented API) at capability tier 2 or 3, with source-version tests and a ten-minute outage drill.
5. **Merchant-confirmation flow** for non-synthetic stock, with an acknowledgement SLA and a visible "awaiting merchant" state.
6. **Availability calibration**: measure stated versus audited accuracy per connector and feed it into the "likely available" label.
7. **Assistant evaluation set**: scripted photo and text cases scored on correct SKU, truthful status and accepted pickup, run in CI against the scripted model and periodically against the real one.
8. **Observability**: structured logs with request IDs, metrics for the reliability gates, alerting on captured-but-unfulfillable orders and refund uncertainty.
9. **Load tests**: search at 100, 500 and 1,000 requests per second with a mock payment provider only; never load the PayPal sandbox.
10. **Licensing clean-up** so a public build has no restricted template code ([THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)).

## Deliberately not now

No generic storefront builder; no merchant funds custody or withdrawal portal; no cross-seller cart that needs PayPal platform approval; no own credit underwriting; no courier fleet; no mandatory hardware; no AI training on private merchant history; no Kafka or Kubernetes for perceived scale. Each would weaken the first product or add risk before the core claim (honest local availability that converts into collected orders) is proven.
