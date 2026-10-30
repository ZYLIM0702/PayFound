-- NOT APPLIED to any remote database. Review before running.
-- Running upgrade a006assistantrls -> a007assistantthreads
-- Requires public.pf_uid() from 20261022000001_assistant_rls_read_policies.sql.

BEGIN;

CREATE TABLE public.assistant_threads (
    id VARCHAR(64) NOT NULL,
    owner_subject VARCHAR(160) NOT NULL,
    title VARCHAR(120) NOT NULL,
    messages JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    PRIMARY KEY (id)
);
CREATE INDEX ix_assistant_threads_owner_subject ON public.assistant_threads (owner_subject);
CREATE INDEX ix_assistant_threads_owner_updated ON public.assistant_threads (owner_subject, updated_at);

ALTER TABLE public.assistant_threads ENABLE ROW LEVEL SECURITY;

-- Owner-only. The subject is the JWT `sub` claim (public.pf_uid()); the API also enforces this in application code.
DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
  GRANT SELECT, INSERT, UPDATE, DELETE ON public.assistant_threads TO authenticated;
  CREATE POLICY pf_threads_select ON public.assistant_threads FOR SELECT TO authenticated USING (owner_subject = public.pf_uid());
  CREATE POLICY pf_threads_insert ON public.assistant_threads FOR INSERT TO authenticated WITH CHECK (owner_subject = public.pf_uid());
  CREATE POLICY pf_threads_update ON public.assistant_threads FOR UPDATE TO authenticated USING (owner_subject = public.pf_uid()) WITH CHECK (owner_subject = public.pf_uid());
  CREATE POLICY pf_threads_delete ON public.assistant_threads FOR DELETE TO authenticated USING (owner_subject = public.pf_uid());
END IF; END $$;

-- Anonymous users get nothing.
REVOKE ALL ON public.assistant_threads FROM anon;

COMMIT;
