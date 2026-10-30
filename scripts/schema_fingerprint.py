"""Fingerprint ORM columns for comparison with information_schema over MCP."""
import hashlib
import os
from pathlib import Path
import sys
import sqlalchemy as sa

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'apps/api'))
os.environ['PAYFOUND_TESTING'] = '1'
from app.main import app
from app.database import Base

rows = []
for table in sorted(Base.metadata.tables.values(), key=lambda t: t.name):
    for column in sorted(table.columns, key=lambda c: c.name):
        kind = column.type
        length = ''
        if isinstance(kind, sa.Text):
            name = 'text'
        elif isinstance(kind, sa.String):
            name, length = 'character varying', str(kind.length or '')
        elif isinstance(kind, sa.Integer):
            name = 'integer'
        elif isinstance(kind, sa.Float):
            name = 'double precision'
        elif isinstance(kind, sa.Boolean):
            name = 'boolean'
        elif isinstance(kind, sa.DateTime):
            name = 'timestamp without time zone'
        elif isinstance(kind, sa.JSON):
            name = 'json'
        else:
            raise TypeError(kind)
        rows.append('|'.join((table.name, column.name, name, length, 'YES' if column.nullable else 'NO')))
print('ORM tables:', len(Base.metadata.tables))
print('ORM columns:', len(rows))
print('Column fingerprint:', hashlib.md5('\n'.join(rows).encode()).hexdigest())
