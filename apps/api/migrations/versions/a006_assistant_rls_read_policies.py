"""Read-only RLS policies for the assistant's optional database-enforced scoping (PostgreSQL only; see supabase/migrations)."""
from alembic import op

revision = 'a006assistantrls'
down_revision = 'a005sku'
branch_labels = None
depends_on = None

SQL = r'''
-- Read-only RLS policies so a database session running as `authenticated` with the caller's JWT claims
-- (request.jwt.claims) can only read what that user may see. Used by the assistant when ASSISTANT_DB_RLS=true.
-- The API itself still connects with a privileged role and enforces the same rules in application code.
-- No INSERT/UPDATE/DELETE policy is created: browsers and the assistant can never write through these grants.

CREATE OR REPLACE FUNCTION public.pf_uid() RETURNS text LANGUAGE sql STABLE
  AS $fn$ SELECT nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'sub' $fn$;

CREATE OR REPLACE FUNCTION public.pf_is_admin() RETURNS boolean LANGUAGE sql STABLE
  AS $fn$ SELECT coalesce(nullif(current_setting('request.jwt.claims', true), '')::jsonb -> 'app_metadata' ->> 'payfound_role', '') = 'admin' $fn$;

-- SECURITY DEFINER so the lookup is not itself subject to the memberships policy (avoids recursion).
CREATE OR REPLACE FUNCTION public.pf_manages(mid text) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = ''
  AS $fn$ SELECT public.pf_is_admin()
    OR EXISTS (SELECT 1 FROM public.merchant_memberships m WHERE m.merchant_id = mid AND m.subject = public.pf_uid() AND m.active)
    OR EXISTS (SELECT 1 FROM public.merchants x WHERE x.id = mid AND x.owner_subject = public.pf_uid()
               AND NOT EXISTS (SELECT 1 FROM public.merchant_memberships r WHERE r.merchant_id = mid AND r.subject = public.pf_uid() AND NOT r.active)) $fn$;

CREATE OR REPLACE FUNCTION public.pf_can_see_order(oid text) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = ''
  AS $fn$ SELECT EXISTS (SELECT 1 FROM public.orders o WHERE o.id = oid
    AND (o.buyer_subject = public.pf_uid() OR public.pf_manages(o.merchant_id))) $fn$;

REVOKE ALL ON FUNCTION public.pf_uid(), public.pf_is_admin(), public.pf_manages(text), public.pf_can_see_order(text) FROM PUBLIC;

DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
    GRANT EXECUTE ON FUNCTION public.pf_uid(), public.pf_is_admin(), public.pf_manages(text), public.pf_can_see_order(text) TO authenticated;
    GRANT SELECT ON public.merchants, public.merchant_locations, public.products, public.canonical_products, public.reviews,
      public.pickup_slots, public.orders, public.order_items, public.pickup_bookings, public.fulfilment_proofs,
      public.merchant_memberships, public.ai_consent_grants TO authenticated;

    -- Public catalogue.
    CREATE POLICY pf_read_merchants ON public.merchants FOR SELECT TO authenticated USING (true);
    CREATE POLICY pf_read_canonical ON public.canonical_products FOR SELECT TO authenticated USING (true);
    CREATE POLICY pf_read_pickup_slots ON public.pickup_slots FOR SELECT TO authenticated USING (true);
    CREATE POLICY pf_read_locations ON public.merchant_locations FOR SELECT TO authenticated USING (active OR public.pf_manages(merchant_id));
    CREATE POLICY pf_read_products ON public.products FOR SELECT TO authenticated USING (active OR public.pf_manages(merchant_id));
    CREATE POLICY pf_read_reviews ON public.reviews FOR SELECT TO authenticated
      USING (visible OR buyer_subject = public.pf_uid() OR public.pf_manages(merchant_id));
    -- Own orders, or orders of stores the user manages (admins: all).
    CREATE POLICY pf_read_orders ON public.orders FOR SELECT TO authenticated
      USING (buyer_subject = public.pf_uid() OR public.pf_manages(merchant_id));
    CREATE POLICY pf_read_order_items ON public.order_items FOR SELECT TO authenticated USING (public.pf_can_see_order(order_id));
    CREATE POLICY pf_read_pickup_bookings ON public.pickup_bookings FOR SELECT TO authenticated USING (public.pf_can_see_order(order_id));
    CREATE POLICY pf_read_fulfilment_proofs ON public.fulfilment_proofs FOR SELECT TO authenticated USING (public.pf_can_see_order(order_id));
    -- Memberships and AI consent: own membership rows, or stores the user manages.
    CREATE POLICY pf_read_memberships ON public.merchant_memberships FOR SELECT TO authenticated
      USING (subject = public.pf_uid() OR public.pf_manages(merchant_id));
    CREATE POLICY pf_read_ai_consent ON public.ai_consent_grants FOR SELECT TO authenticated USING (public.pf_manages(merchant_id));
    -- Everything else (payments, webhooks, outbox, audit, agent_runs, connectors, invitations) stays deny-all.
  END IF;
END $$;
'''


def upgrade():
    if op.get_bind().dialect.name != 'postgresql':
        return
    op.execute(SQL)


def downgrade():
    # Like a002: never silently widen or narrow database access on downgrade.
    pass
