"""Explicit project environment loading. Process variables always win."""
from pathlib import Path
import os
from dotenv import dotenv_values

def environment_roots(module_file):
    api = Path(module_file).resolve().parents[1]
    # A container/service can contain only /app/app, without the monorepo's
    # apps/api hierarchy or even two parent directories.
    app = api.parent.parent if api.name == 'api' and api.parent.name == 'apps' else api
    return api, app, app.parent


API_ROOT, APP_ROOT, WORKSPACE_ROOT = environment_roots(__file__)


def load_environment():
    if os.getenv('PAYFOUND_TESTING') == '1':
        return
    values = {}
    shared = WORKSPACE_ROOT / '.env' if (WORKSPACE_ROOT / 'opencode.json').exists() else WORKSPACE_ROOT / '.payfound-no-shared-env'
    for path in (shared, APP_ROOT / '.env', API_ROOT / '.env'):
        values.update({k: v for k, v in dotenv_values(path).items() if v is not None})
    for key, value in values.items():
        os.environ.setdefault(key, value)
    aliases = {
        'PAYPAL_CLIENT_ID': 'PAYPAL_PLATFORM_APP_CLIENT_ID',
        'PAYPAL_CLIENT_SECRET': 'PAYPAL_PLATFORM_APP_SECRET_KEY',
        'SUPABASE_PROJECT_URL': 'SUPABASE_URL',
    }
    for target, source in aliases.items():
        if not os.getenv(target) and os.getenv(source):
            os.environ[target] = os.environ[source]
    os.environ.setdefault('PAYPAL_ENV', 'sandbox')
    if os.getenv('SUPABASE_PROJECT_URL'):
        os.environ.setdefault('SUPABASE_JWKS_URL', os.environ['SUPABASE_PROJECT_URL'].rstrip('/') + '/auth/v1/.well-known/jwks.json')
    studio = dotenv_values(APP_ROOT / 'apps/web/.env').get('VITE_AG_STUDIO_LICENSE_KEY') or os.getenv('VITE_AG_STUDIO_LICENSE_KEY')
    if studio:
        os.environ.setdefault('AG_STUDIO_LICENSE_KEY', studio)


load_environment()
