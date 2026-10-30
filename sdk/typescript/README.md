# payfound-sdk (TypeScript) v0.1.0

Generated with OpenAPI Generator (`typescript-fetch`) from `docs/api/openapi.json`. **Sandbox/demo only.**

## Install
```
cd sdk/typescript && npm install   # builds to dist/
```
## Base URL and auth
Operation paths already include `/api`, so `basePath` is the host: `http://127.0.0.1:8000` (local sandbox API).
- Demo: header `X-Demo-Role: consumer` or `merchant`.
- Real use: `Authorization: Bearer <API_KEY>` (placeholder; never commit a real key).

## Example
```ts
import { Configuration, HealthApi, MerchantApi } from 'payfound-sdk';
const cfg = new Configuration({ basePath: 'http://127.0.0.1:8000', headers: { 'X-Demo-Role': 'merchant' } });
console.log(await new HealthApi(cfg).healthApiHealthGet());
console.log(await new MerchantApi(cfg).dashboardApiMerchantDashboardGet());
```
(For bearer auth use `headers: { Authorization: 'Bearer <API_KEY>' }`.)

## Smoke test
`node smoke.test.mjs` (skips if the API on :8000 is down). Regenerate: `apps/api/scripts/export_openapi.py` then openapi-generator.
