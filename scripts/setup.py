"""Idempotent local setup. Never prints credentials or overwrites existing keys."""
import argparse
import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tooling', action='store_true', help='Move PayPal MCP authentication into the project wrapper')
    args = parser.parse_args()
    env = ROOT / 'apps/api/.env'
    values = dotenv_values(env)
    if not values.get('CONNECTOR_ENCRYPTION_KEY'):
        with env.open('a') as target:
            target.write('\n# Server-only; retain this key when redeploying encrypted connectors.\nCONNECTOR_ENCRYPTION_KEY=' + Fernet.generate_key().decode() + '\n')
        os.chmod(env, 0o600)
        print('Connector encryption: generated local key')
    else:
        print('Connector encryption: existing key preserved')
    if args.tooling:
        wrapper = str(WORKSPACE / '.opencode/paypal-mcp.mjs')
        for name in ('opencode.json', '.mcp.json'):
            path = WORKSPACE / name
            if not path.exists():
                continue
            config = json.loads(path.read_text())
            servers = config.get('mcp', config.get('mcpServers', {}))
            for server_name, server in servers.items():
                if server_name not in ('paypal', 'paypal-mcp-server'):
                    continue
                envkey = 'environment' if 'mcp' in config else 'env'
                environment = server.get(envkey, {})
                environment.pop('PAYPAL_ACCESS_TOKEN', None)
                environment['PAYPAL_ENVIRONMENT'] = 'SANDBOX'
                server[envkey] = environment
                if 'mcp' in config:
                    server['command'] = ['node', wrapper]
                else:
                    server['command'], server['args'] = 'node', [wrapper]
            path.write_text(json.dumps(config, indent=2) + '\n')
        print('PayPal MCP: project wrapper configured; restart OpenCode to reload')
    shared = dotenv_values(WORKSPACE / '.env')
    combined = {**shared, **dotenv_values(env)}
    for label, names in {
        'PayPal application': ('PAYPAL_CLIENT_ID', 'PAYPAL_PLATFORM_APP_CLIENT_ID'),
        'Supabase API': ('SUPABASE_URL', 'SUPABASE_PROJECT_URL'),
        'PostgreSQL connection': ('DATABASE_URL',),
        'Cloud AI model': ('LLM_MODEL',),
        'Shopify app': ('SHOPIFY_CLIENT_ID',),
        'Channel3': ('CHANNEL3_API_KEY',),
    }.items():
        print(f'{label}: ' + ('configured' if any(combined.get(key) for key in names) else 'not configured'))


if __name__ == '__main__':
    main()
