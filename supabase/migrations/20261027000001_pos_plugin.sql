-- NOT APPLIED to any remote database. Review before running.
-- Running upgrade a010merchantnotify -> a011pospluginconn
-- Custom POS connector. The API (service role) writes; store owners/staff may READ their own rows,
-- never the encrypted credential column. Requires pf_manages() from 20261022000001.

BEGIN;

CREATE TABLE public.pos_connections (
    id VARCHAR(48) NOT NULL,
    merchant_id VARCHAR(48) NOT NULL REFERENCES public.merchants (id),
    name VARCHAR(80) NOT NULL,
    mode VARCHAR(8) NOT NULL,
    status VARCHAR(16) NOT NULL,
    base_url VARCHAR(500),
    products_path VARCHAR(200) NOT NULL,
    branches_path VARCHAR(200),
    health_path VARCHAR(200) NOT NULL,
    auth_scheme VARCHAR(16) NOT NULL,
    credentials_encrypted TEXT,
    credential_hint VARCHAR(16),
    schedule VARCHAR(8) NOT NULL,
    settings JSON NOT NULL,
    cursor_updated_at TIMESTAMP WITHOUT TIME ZONE,
    last_synced_at TIMESTAMP WITHOUT TIME ZONE,
    next_sync_at TIMESTAMP WITHOUT TIME ZONE,
    last_error VARCHAR(300),
    failure_count INTEGER NOT NULL,
    lease_until TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    disconnected_at TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (id)
);
CREATE INDEX ix_pos_connections_merchant_id ON public.pos_connections (merchant_id);
CREATE INDEX ix_pos_connections_due ON public.pos_connections (status, next_sync_at);

CREATE TABLE public.pos_sync_runs (
    id VARCHAR(48) NOT NULL,
    connection_id VARCHAR(48) NOT NULL REFERENCES public.pos_connections (id),
    trigger VARCHAR(12) NOT NULL,
    status VARCHAR(12) NOT NULL,
    started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    finished_at TIMESTAMP WITHOUT TIME ZONE,
    created INTEGER NOT NULL,
    updated INTEGER NOT NULL,
    skipped INTEGER NOT NULL,
    failed INTEGER NOT NULL,
    error VARCHAR(300),
    row_errors JSON NOT NULL,
    next_run_at TIMESTAMP WITHOUT TIME ZONE,
    delivery_id VARCHAR(80),
    PRIMARY KEY (id),
    CONSTRAINT uq_pos_run_delivery UNIQUE (connection_id, delivery_id)
);
CREATE INDEX ix_pos_sync_runs_connection_id ON public.pos_sync_runs (connection_id);

ALTER TABLE public.pos_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pos_sync_runs ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
  REVOKE ALL ON TABLE public.pos_connections, public.pos_sync_runs FROM anon, authenticated;
END IF;
IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
  -- Column-level grant: everything except credentials_encrypted.
  GRANT SELECT (id, merchant_id, name, mode, status, base_url, products_path, branches_path, health_path, auth_scheme,
                credential_hint, schedule, settings, cursor_updated_at, last_synced_at, next_sync_at, last_error,
                failure_count, created_at, disconnected_at) ON public.pos_connections TO authenticated;
  GRANT SELECT ON public.pos_sync_runs TO authenticated;
  CREATE POLICY pf_read_pos_connections ON public.pos_connections FOR SELECT TO authenticated USING (public.pf_manages(merchant_id));
  CREATE POLICY pf_read_pos_sync_runs ON public.pos_sync_runs FOR SELECT TO authenticated
    USING (EXISTS (SELECT 1 FROM public.pos_connections c WHERE c.id = connection_id AND public.pf_manages(c.merchant_id)));
END IF; END $$;

UPDATE alembic_version SET version_num = 'a011pospluginconn' WHERE alembic_version.version_num = 'a010merchantnotify';

COMMIT;
