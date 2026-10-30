"""Export the exact Alembic chain as a Supabase migration (no DB connection)."""
import io
import os
from pathlib import Path
from alembic.config import Config
from alembic import command

ROOT = Path(__file__).resolve().parents[1]
os.environ['PAYFOUND_TESTING'] = '1'
os.environ['DATABASE_URL'] = 'postgresql+psycopg://postgres@localhost/postgres'
os.chdir(ROOT / 'apps/api')
buffer = io.StringIO()
config = Config('alembic.ini', output_buffer=buffer)
command.upgrade(config, 'head', sql=True)
target = ROOT / 'supabase/migrations/20261021000001_pilot.sql'
target.write_text('-- Generated from the reviewed Alembic revision chain. Do not edit independently.\n' + buffer.getvalue())
print(f'Exported {target.relative_to(ROOT)}')
