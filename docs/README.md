# PayFound documentation

| Read this | When you want to |
|---|---|
| [BUSINESS_STRATEGY.md](BUSINESS_STRATEGY.md) | Understand why PayFound exists, who it serves, how it makes money and how it gets its first merchants |
| [PRODUCT.md](PRODUCT.md) | See what each role does, how availability is labelled, and the page map |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Understand the system, data model, state machines, store placement and the path to scale |
| [ASSISTANT.md](ASSISTANT.md) | Work on the AI agent: tools, guardrails, search widening, Channel3 fallback, voice |
| [PAYMENTS_AND_SECURITY.md](PAYMENTS_AND_SECURITY.md) | Work on checkout, refunds, webhooks, auth, tenancy or data handling |
| [CONNECTORS.md](CONNECTORS.md) | Connect WooCommerce, Shopify or a custom POS, and understand the capability tiers |
| [STATUS.md](STATUS.md) | Know what is built, what has been verified, and what still depends on outside access |
| [ROADMAP.md](ROADMAP.md) | See what comes next and the gates between stages |
| [TESTING.md](TESTING.md) | Run the checks and understand the failure-injection matrix |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Configure environments, migrate a database, deploy to Render |
| [PILOT_RUNBOOK.md](PILOT_RUNBOOK.md) | Operate the stack: setup detail, provider activation, recovery |

Component-level references live beside the code:

- [apps/api/docs/pos-plugin.md](../apps/api/docs/pos-plugin.md): the custom POS contract (v1).
- [apps/api/docs/forecast-drivers.md](../apps/api/docs/forecast-drivers.md): the explainable demand forecast.
- [api/index.html](api/index.html) and [api/openapi.json](api/openapi.json): the exported API contract.

Documentation rules for contributors: say what is verified and what is not; keep fictional data labelled; never describe a sandbox result as production, or imply a PayPal partnership that does not exist.
