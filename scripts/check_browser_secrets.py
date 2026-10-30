"""Check compiled browser assets for actual locally configured server secrets."""
from pathlib import Path
import sys
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
keys = ('PAYPAL_CLIENT_SECRET', 'PAYPAL_PLATFORM_APP_SECRET_KEY', 'SUPABASE_SECRET_KEY',
        'PAYPAL_ACCESS_TOKEN', 'CHANNEL3_API_KEY', 'APIMATIC_API_KEY', 'CONNECTOR_ENCRYPTION_KEY', 'LLM_API_KEY')
values = {}
for path in (ROOT.parent / '.env', ROOT / '.env', ROOT / 'apps/api/.env', ROOT.parent / '.opencode/.env'):
    values.update(dotenv_values(path))
assets = list((ROOT / 'apps/web/dist').rglob('*.js')) + list((ROOT / 'apps/web/dist').rglob('*.html'))
if not assets:
    raise SystemExit('Build frontend first.')
found = []
for asset in assets:
    content = asset.read_text()
    for key in keys:
        value = values.get(key)
        if value and len(value) >= 12 and value in content:
            found.append((key, str(asset.relative_to(ROOT))))
if found:
    for key, file in found:
        print(f'ERROR: {key} found in {file}; value withheld')
    sys.exit(1)
print(f'Checked {len(assets)} browser assets: no configured server secrets found.')
