"""Validate deployment/tool configuration against current published schemas."""
import json
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError
import subprocess
import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]


def validate(path, schema_url, data):
    with urlopen(schema_url, timeout=30) as response:
        schema = json.load(response)
    jsonschema.validate(data, schema)
    print(f'{path.name}: schema valid')


validate(ROOT / 'render.yaml', 'https://render.com/schema/render.yaml.json', yaml.safe_load((ROOT / 'render.yaml').read_text()))
config = ROOT.parent / 'opencode.json'
if config.exists():
    try:
        validate(config, 'https://opencode.ai/config.json', json.loads(config.read_text()))
    except HTTPError as exc:
        if exc.code != 403:
            raise
        result = subprocess.run(['opencode', 'debug', 'config', '--pure'], cwd=config.parent,
                                capture_output=True, text=True, timeout=90)
        if result.returncode:
            raise RuntimeError('OpenCode runtime config validation failed; output withheld to protect provider settings')
        print('opencode.json: installed CLI validation passed (published schema access returned HTTP 403)')
