"""Export the OpenAPI spec to docs/api/openapi.json with export-time metadata fixes."""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
os.environ['PAYFOUND_TESTING'] = '1'
sys.path.insert(0, str(ROOT / 'apps/api'))
try:
    from app.main import app  # noqa: E402
except ImportError:  # transient circular import: retry with intelligence loaded first
    for _m in [m for m in sys.modules if m == 'app' or m.startswith('app.')]:
        del sys.modules[_m]
    import app.intelligence  # noqa: F401
    from app.main import app  # noqa: E402

METHODS = {'get', 'put', 'post', 'delete', 'patch', 'options', 'head'}
SERVERS = [{'url': 'http://127.0.0.1:8000', 'description': 'Local sandbox/demo server (sandbox only)'}]


def tag_for(path: str) -> str:
    if path == '/api/config':
        return 'Settings'  # 'config' would clash with the SDK's own Configuration object
    parts = [p for p in path.split('/') if p and not p.startswith('{')]
    if parts and parts[0] == 'api':
        parts = parts[1:]
    return (parts[0] if parts else 'root').replace('-', ' ').replace('_', ' ').title()


def _fix_exclusive_bounds(node):
    """OpenAPI 3.1 numeric exclusiveMinimum is what APIMatic rejects here: express it as minimum instead."""
    if isinstance(node, dict):
        if isinstance(node.get('exclusiveMinimum'), (int, float)) and not isinstance(node.get('exclusiveMinimum'), bool):
            bound = node.pop('exclusiveMinimum')
            step = 1 if node.get('type') == 'integer' else 0.01
            node['minimum'] = round(bound + step, 6) if node.get('type') in ('integer', 'number') else bound
        for value in node.values():
            _fix_exclusive_bounds(value)
    elif isinstance(node, list):
        for value in node:
            _fix_exclusive_bounds(value)


def _strip_titles(node):
    """Parameter schemas repeat FastAPI's auto titles; APIMatic rejects duplicates, so drop them."""
    if isinstance(node, dict):
        if isinstance(node.get('title'), str):  # a property literally named 'title' is a dict, keep it
            node.pop('title')
        for value in node.values():
            _strip_titles(value)
    elif isinstance(node, list):
        for value in node:
            _strip_titles(value)


def postprocess(spec: dict) -> dict:
    # FastAPI's auto titles repeat across operations (APIMatic reports them as duplicates). Titles are display-only.
    _strip_titles(spec.get('paths', {}))
    _strip_titles(spec.get('components', {}))
    _fix_exclusive_bounds(spec.get('components', {}))
    _fix_exclusive_bounds(spec.get('paths', {}))
    spec['info']['description'] = (spec['info'].get('description') or '') + ' SANDBOX / DEMO ONLY.'
    spec['info'].setdefault('license', {'name': 'Proprietary', 'identifier': 'LicenseRef-Proprietary'})
    spec['servers'] = SERVERS
    schemes = spec.setdefault('components', {}).setdefault('securitySchemes', {})
    schemes.setdefault('bearerAuth', {'type': 'http', 'scheme': 'bearer', 'description': 'Authorization: Bearer <API_KEY>'})
    schemes.setdefault('demoRole', {'type': 'apiKey', 'in': 'header', 'name': 'X-Demo-Role',
                                    'description': 'Demo only: consumer or merchant'})
    seen: dict[str, int] = {}
    tags = set()
    for path, item in spec['paths'].items():
        for method, op in item.items():
            if method not in METHODS:
                continue
            if not op.get('tags'):
                op['tags'] = [tag_for(path)]
            tags.update(op['tags'])
            oid = op.get('operationId') or f'{method}_{path}'
            if len(oid) > 50 and '_api_' in oid:
                oid = oid.split('_api_')[0]  # FastAPI appends the path to the name; keep the readable part
            seen[oid] = seen.get(oid, 0) + 1
            if seen[oid] > 1:
                oid = f'{oid}_{method}_{re.sub(r"[^a-zA-Z0-9]+", "_", path).strip("_")}'
            op['operationId'] = oid
            if not op.get('summary'):
                op['summary'] = f'{method.upper()} {path}'
            if not op.get('description'):
                op['description'] = f'{op["summary"]}. Sandbox and demo API; see the response schema for fields.'
            op.setdefault('security', [{'demoRole': []}, {'bearerAuth': []}])
            for code, resp in op.get('responses', {}).items():
                resp.setdefault('description', 'Response')
            if not op.get('responses'):
                op['responses'] = {'200': {'description': 'Successful response'}}
    spec['tags'] = [{'name': t} for t in sorted(tags)]
    return spec


if __name__ == '__main__':
    spec = postprocess(app.openapi())
    target = ROOT / 'docs/api/openapi.json'
    target.write_text(json.dumps(spec, indent=2) + '\n')
    print(f'Exported {target.relative_to(ROOT)} with {len(spec["paths"])} paths')
