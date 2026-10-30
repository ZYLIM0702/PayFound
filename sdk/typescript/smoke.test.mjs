// Smoke test: local sandbox API only. Skips if http://127.0.0.1:8000 is down.
import { Configuration, HealthApi, MerchantApi } from './dist/index.js';

const BASE = 'http://127.0.0.1:8000';
try { await fetch(`${BASE}/api/health`); } catch { console.log('SKIP: local API on :8000 is not running'); process.exit(0); }

const cfg = new Configuration({ basePath: BASE, headers: { 'X-Demo-Role': 'merchant' } });
const health = await new HealthApi(cfg).healthApiHealthGet();
console.log('health ->', JSON.stringify(health).slice(0, 120));
const dash = await new MerchantApi(cfg).dashboardApiMerchantDashboardGet();
console.log('merchant dashboard keys ->', Object.keys(dash ?? {}).slice(0, 6));
console.log('PASS');
