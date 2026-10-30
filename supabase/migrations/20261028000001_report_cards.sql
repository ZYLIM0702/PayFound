-- NOT APPLIED to any remote database. Review before running.
-- Running upgrade a011pospluginconn -> a012reportcards
-- Assistant-built report cards. The API (service role) writes; store owners/staff may READ their own rows.
-- Requires pf_manages() from 20261022000001.

BEGIN;

CREATE TABLE public.merchant_report_cards (
    id VARCHAR(48) NOT NULL,
    merchant_id VARCHAR(48) NOT NULL REFERENCES public.merchants (id),
    name VARCHAR(120) NOT NULL,
    kind VARCHAR(16) NOT NULL,
    days INTEGER NOT NULL,
    focus VARCHAR(120),
    created_by VARCHAR(160),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT ck_report_card_days CHECK (days BETWEEN 1 AND 90)
);
CREATE INDEX ix_merchant_report_cards_merchant_id ON public.merchant_report_cards (merchant_id);

ALTER TABLE public.merchant_report_cards ENABLE ROW LEVEL SECURITY;
DO $$ BEGIN
IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
  GRANT SELECT ON public.merchant_report_cards TO authenticated;
  CREATE POLICY pf_read_merchant_report_cards ON public.merchant_report_cards FOR SELECT TO authenticated USING (public.pf_manages(merchant_id));
END IF; END $$;

UPDATE alembic_version SET version_num = 'a012reportcards' WHERE alembic_version.version_num = 'a011pospluginconn';

COMMIT;
