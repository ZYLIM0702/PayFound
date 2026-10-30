"""Smoke test against the local sandbox API only (http://127.0.0.1:8000). Skips if down.
Run: apps/api/.venv/bin/python sdk/python/smoke_test.py
"""
import os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import payfound_sdk

BASE = "http://127.0.0.1:8000"
try:
    urllib.request.urlopen(f"{BASE}/api/health", timeout=3)
except Exception:
    print("SKIP: local API on :8000 is not running"); sys.exit(0)

cfg = payfound_sdk.Configuration(host=BASE)
with payfound_sdk.ApiClient(cfg, header_name="X-Demo-Role", header_value="merchant") as client:
    print("health ->", payfound_sdk.HealthApi(client).health_api_health_get())
    dash = payfound_sdk.MerchantApi(client).dashboard_api_merchant_dashboard_get()
    print("merchant dashboard ->", list(dash)[:6] if isinstance(dash, dict) else type(dash))
print("PASS")
