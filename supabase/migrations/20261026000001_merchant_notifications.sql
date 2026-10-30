-- NOT APPLIED to any remote database. Review before running.
-- Running upgrade a009accounthub -> a010merchantnotify
-- One in-app notification per (order, event, active staff member). Written and read only by the API (service role).

BEGIN;

CREATE TABLE public.merchant_notifications (
    id VARCHAR(48) NOT NULL,
    merchant_id VARCHAR(48) NOT NULL REFERENCES public.merchants (id),
    recipient_subject VARCHAR(160) NOT NULL,
    order_id VARCHAR(48) NOT NULL REFERENCES public.orders (id),
    event_type VARCHAR(40) NOT NULL,
    message VARCHAR(300) NOT NULL,
    seen_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    PRIMARY KEY (id),
    CONSTRAINT uq_merchant_notification UNIQUE (order_id, event_type, recipient_subject)
);
CREATE INDEX ix_merchant_notifications_merchant_id ON public.merchant_notifications (merchant_id);
CREATE INDEX ix_merchant_notifications_recipient_subject ON public.merchant_notifications (recipient_subject);
CREATE INDEX ix_merchant_notifications_order_id ON public.merchant_notifications (order_id);

ALTER TABLE public.merchant_notifications ENABLE ROW LEVEL SECURITY;
DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
  REVOKE ALL ON TABLE public.merchant_notifications FROM anon, authenticated;
END IF; END $$;

UPDATE alembic_version SET version_num = 'a010merchantnotify' WHERE alembic_version.version_num = 'a009accounthub';

COMMIT;
