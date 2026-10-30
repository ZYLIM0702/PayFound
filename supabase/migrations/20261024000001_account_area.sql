-- NOT APPLIED to any remote database. Review before running.
-- Running upgrade a007assistantthreads -> a008accountarea
-- Requires public.pf_uid() from 20261022000001_assistant_rls_read_policies.sql.

BEGIN;

CREATE TABLE public.wishlist_items (
    id VARCHAR(48) NOT NULL,
    owner_subject VARCHAR(160) NOT NULL,
    product_id VARCHAR(48) NOT NULL REFERENCES public.products (id),
    saved_price_cents INTEGER NOT NULL,
    saved_in_stock BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    PRIMARY KEY (id),
    CONSTRAINT uq_wishlist_owner_product UNIQUE (owner_subject, product_id)
);
CREATE INDEX ix_wishlist_items_owner_subject ON public.wishlist_items (owner_subject);
CREATE INDEX ix_wishlist_items_product_id ON public.wishlist_items (product_id);

CREATE TABLE public.delivery_requests (
    id VARCHAR(48) NOT NULL,
    order_id VARCHAR(48) NOT NULL REFERENCES public.orders (id),
    owner_subject VARCHAR(160) NOT NULL,
    provider_id VARCHAR(40) NOT NULL,
    address VARCHAR(300) NOT NULL,
    notes VARCHAR(300) NOT NULL DEFAULT '',
    status VARCHAR(20) NOT NULL DEFAULT 'requested',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    PRIMARY KEY (id)
);
CREATE INDEX ix_delivery_requests_order_id ON public.delivery_requests (order_id);
CREATE INDEX ix_delivery_requests_owner_subject ON public.delivery_requests (owner_subject);
CREATE INDEX ix_delivery_order_status ON public.delivery_requests (order_id, status);

CREATE TABLE public.account_profiles (
    owner_subject VARCHAR(160) NOT NULL,
    display_name VARCHAR(130) NOT NULL DEFAULT '',
    addresses JSONB NOT NULL DEFAULT '[]'::jsonb,
    notifications JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    PRIMARY KEY (owner_subject)
);

ALTER TABLE public.wishlist_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.delivery_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.account_profiles ENABLE ROW LEVEL SECURITY;

-- Owner-only. The subject is the JWT `sub` claim (public.pf_uid()); the API also enforces this in application code.
DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
  GRANT SELECT, INSERT, UPDATE, DELETE ON public.wishlist_items, public.delivery_requests, public.account_profiles TO authenticated;
  CREATE POLICY pf_wishlist_owner ON public.wishlist_items FOR ALL TO authenticated USING (owner_subject = public.pf_uid()) WITH CHECK (owner_subject = public.pf_uid());
  CREATE POLICY pf_delivery_owner ON public.delivery_requests FOR ALL TO authenticated USING (owner_subject = public.pf_uid()) WITH CHECK (owner_subject = public.pf_uid());
  CREATE POLICY pf_profile_owner ON public.account_profiles FOR ALL TO authenticated USING (owner_subject = public.pf_uid()) WITH CHECK (owner_subject = public.pf_uid());
END IF; END $$;

REVOKE ALL ON public.wishlist_items, public.delivery_requests, public.account_profiles FROM anon;

COMMIT;
