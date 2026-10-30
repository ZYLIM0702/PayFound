"""Deny direct browser table access; FastAPI serves authorized projections."""
from alembic import op

revision = 'a002private'
down_revision = 'a001canonical'
branch_labels = None
depends_on = None

TABLES = ('agent_runs', 'ai_consent_grants', 'audit_events', 'canonical_products',
    'connector_connections', 'connector_events', 'connector_locations', 'connector_offers',
    'connector_sync_runs', 'fulfilment_proofs', 'inventory_reservations', 'merchant_locations',
    'merchant_memberships', 'merchant_reports', 'merchants', 'order_items', 'orders',
    'outbox_jobs', 'payment_attempts', 'payment_events', 'pickup_bookings', 'pickup_slots',
    'products', 'provider_operations', 'provider_webhooks', 'refunds', 'reviews',
    'staff_invitations', 'alembic_version')


def upgrade():
    if op.get_bind().dialect.name != 'postgresql':
        return
    for table in TABLES:
        op.execute(f'ALTER TABLE public."{table}" ENABLE ROW LEVEL SECURITY')
        # Standalone PostgreSQL test instances need not define Supabase roles.
        for role in ('anon', 'authenticated'):
            op.execute(f'''DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') THEN
                    REVOKE ALL ON TABLE public."{table}" FROM {role};
                END IF;
            END $$''')


def downgrade():
    # Never restore browser grants or disable RLS automatically on downgrade.
    pass
