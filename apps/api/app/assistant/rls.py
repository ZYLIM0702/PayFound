"""Optional database-enforced row level security for assistant tool reads (PostgreSQL only; default off)."""
from __future__ import annotations

import json
import os

from sqlalchemy import text


def enabled(db) -> bool:
    return os.getenv('ASSISTANT_DB_RLS', 'false').lower() == 'true' and db.get_bind().dialect.name == 'postgresql'


def apply(db, principal) -> None:
    claims = {'sub': principal.subject, 'role': 'authenticated', 'email': principal.email,
              'app_metadata': {'payfound_role': principal.role}}
    db.execute(text("SELECT set_config('request.jwt.claims', :claims, true)"), {'claims': json.dumps(claims)})
    db.execute(text('SET LOCAL ROLE authenticated'))
