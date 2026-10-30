"""Export the application's actual OpenAPI contract, without loading credentials."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ['PAYFOUND_TESTING'] = '1'
sys.path.insert(0, str(ROOT / 'apps/api'))
from app.main import app

target = ROOT / 'postman/PayFound.openapi.json'
target.write_text(json.dumps(app.openapi(), indent=2) + '\n')
print(f'Exported {target.relative_to(ROOT)} with {len(app.openapi()["paths"])} paths')
