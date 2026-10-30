# payfound-sdk (Python) v0.1.0

Generated with OpenAPI Generator (`python`) from `docs/api/openapi.json`. **Sandbox/demo only.**

## Install
```
pip install -r sdk/python/requirements.txt && pip install -e sdk/python
```
## Base URL and auth
Operation paths already include `/api`, so `host` is `http://127.0.0.1:8000` (local sandbox API).
- Demo: header `X-Demo-Role: consumer` or `merchant`.
- Real use: `Authorization: Bearer <API_KEY>` (placeholder; never commit a real key).

## Example
```python
import payfound_sdk
cfg = payfound_sdk.Configuration(host="http://127.0.0.1:8000")
with payfound_sdk.ApiClient(cfg, header_name="X-Demo-Role", header_value="merchant") as c:
    print(payfound_sdk.HealthApi(c).health_api_health_get())
    print(payfound_sdk.MerchantApi(c).dashboard_api_merchant_dashboard_get())
# bearer: Configuration(host=..., access_token="<API_KEY>")
```

## Smoke test
`python sdk/python/smoke_test.py` (skips if the API on :8000 is down). Needs the deps in `requirements.txt`
(`python-dateutil`, `pydantic`, `urllib3`), which the apps/api venv lacks, so use a separate venv.
