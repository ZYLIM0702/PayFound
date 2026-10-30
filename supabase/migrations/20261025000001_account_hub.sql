-- NOT APPLIED to any remote database. Review before running.
-- Running upgrade a008accountarea -> a009accounthub
-- Requires public.pf_uid() from 20261022000001_assistant_rls_read_policies.sql.
-- payment_methods holds a masked label and status only: never card numbers, passwords or tokens.

BEGIN;

CREATE TABLE public.payment_methods (
    id VARCHAR(48) NOT NULL,
    owner_subject VARCHAR(160) NOT NULL,
    provider VARCHAR(20) NOT NULL,
    masked_email VARCHAR(160) NOT NULL DEFAULT '',
    status VARCHAR(24) NOT NULL DEFAULT 'sandbox_linked',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    PRIMARY KEY (id)
);
CREATE INDEX ix_payment_methods_owner_subject ON public.payment_methods (owner_subject);

CREATE TABLE public.message_threads (
    id VARCHAR(48) NOT NULL,
    buyer_subject VARCHAR(160) NOT NULL,
    merchant_id VARCHAR(48) NOT NULL REFERENCES public.merchants (id),
    order_id VARCHAR(48) REFERENCES public.orders (id),
    subject VARCHAR(160) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    PRIMARY KEY (id)
);
CREATE INDEX ix_message_threads_buyer_subject ON public.message_threads (buyer_subject);
CREATE INDEX ix_message_threads_merchant_id ON public.message_threads (merchant_id);

CREATE TABLE public.thread_messages (
    id VARCHAR(48) NOT NULL,
    thread_id VARCHAR(48) NOT NULL REFERENCES public.message_threads (id),
    sender_role VARCHAR(12) NOT NULL,
    sender_subject VARCHAR(160) NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    PRIMARY KEY (id)
);
CREATE INDEX ix_thread_messages_thread_id ON public.thread_messages (thread_id);
CREATE INDEX ix_thread_messages_thread_created ON public.thread_messages (thread_id, created_at);

CREATE TABLE public.support_tickets (
    id VARCHAR(48) NOT NULL,
    owner_subject VARCHAR(160) NOT NULL,
    topic VARCHAR(24) NOT NULL,
    subject VARCHAR(120) NOT NULL,
    message TEXT NOT NULL,
    order_id VARCHAR(48),
    status VARCHAR(16) NOT NULL DEFAULT 'open',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    PRIMARY KEY (id)
);
CREATE INDEX ix_support_tickets_owner_subject ON public.support_tickets (owner_subject);

ALTER TABLE public.payment_methods ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.message_threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.thread_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_tickets ENABLE ROW LEVEL SECURITY;

-- Owner-only via the JWT `sub` claim (public.pf_uid()). Merchant staff access goes through the API (service role).
DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
  GRANT SELECT, INSERT, UPDATE, DELETE ON public.payment_methods, public.message_threads, public.thread_messages, public.support_tickets TO authenticated;
  CREATE POLICY pf_payment_methods_owner ON public.payment_methods FOR ALL TO authenticated USING (owner_subject = public.pf_uid()) WITH CHECK (owner_subject = public.pf_uid());
  CREATE POLICY pf_threads_owner ON public.message_threads FOR ALL TO authenticated USING (buyer_subject = public.pf_uid()) WITH CHECK (buyer_subject = public.pf_uid());
  CREATE POLICY pf_thread_messages_owner ON public.thread_messages FOR ALL TO authenticated USING (EXISTS (SELECT 1 FROM public.message_threads t WHERE t.id = thread_id AND t.buyer_subject = public.pf_uid())) WITH CHECK (sender_subject = public.pf_uid() AND EXISTS (SELECT 1 FROM public.message_threads t WHERE t.id = thread_id AND t.buyer_subject = public.pf_uid()));
  CREATE POLICY pf_tickets_owner ON public.support_tickets FOR ALL TO authenticated USING (owner_subject = public.pf_uid()) WITH CHECK (owner_subject = public.pf_uid());
END IF; END $$;

REVOKE ALL ON public.payment_methods, public.message_threads, public.thread_messages, public.support_tickets FROM anon;

COMMIT;
