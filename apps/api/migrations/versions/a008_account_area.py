"""Shopper account area: wishlist, delivery requests (local records) and profile (owner-only)."""
from alembic import op
import sqlalchemy as sa

revision = 'a008accountarea'
down_revision = 'a007assistantthreads'
branch_labels = None
depends_on = None

TABLES = ('wishlist_items', 'delivery_requests', 'account_profiles')


def upgrade():
    op.create_table('wishlist_items',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('owner_subject', sa.String(160), nullable=False),
        sa.Column('product_id', sa.String(48), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('saved_price_cents', sa.Integer(), nullable=False),
        sa.Column('saved_in_stock', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('owner_subject', 'product_id', name='uq_wishlist_owner_product'))
    op.create_index('ix_wishlist_items_owner_subject', 'wishlist_items', ['owner_subject'])
    op.create_index('ix_wishlist_items_product_id', 'wishlist_items', ['product_id'])
    op.create_table('delivery_requests',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('order_id', sa.String(48), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('owner_subject', sa.String(160), nullable=False),
        sa.Column('provider_id', sa.String(40), nullable=False),
        sa.Column('address', sa.String(300), nullable=False),
        sa.Column('notes', sa.String(300), nullable=False, server_default=''),
        sa.Column('status', sa.String(20), nullable=False, server_default='requested'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_index('ix_delivery_requests_order_id', 'delivery_requests', ['order_id'])
    op.create_index('ix_delivery_requests_owner_subject', 'delivery_requests', ['owner_subject'])
    op.create_index('ix_delivery_order_status', 'delivery_requests', ['order_id', 'status'])
    op.create_table('account_profiles',
        sa.Column('owner_subject', sa.String(160), primary_key=True),
        sa.Column('display_name', sa.String(130), nullable=False, server_default=''),
        sa.Column('addresses', sa.JSON(), nullable=False),
        sa.Column('notifications', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False))
    if op.get_bind().dialect.name == 'postgresql':
        for t in TABLES:
            op.execute(f'ALTER TABLE public.{t} ENABLE ROW LEVEL SECURITY')
        op.execute("""DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
          GRANT SELECT, INSERT, UPDATE, DELETE ON public.wishlist_items, public.delivery_requests, public.account_profiles TO authenticated;
          CREATE POLICY pf_wishlist_owner ON public.wishlist_items FOR ALL TO authenticated USING (owner_subject = public.pf_uid()) WITH CHECK (owner_subject = public.pf_uid());
          CREATE POLICY pf_delivery_owner ON public.delivery_requests FOR ALL TO authenticated USING (owner_subject = public.pf_uid()) WITH CHECK (owner_subject = public.pf_uid());
          CREATE POLICY pf_profile_owner ON public.account_profiles FOR ALL TO authenticated USING (owner_subject = public.pf_uid()) WITH CHECK (owner_subject = public.pf_uid());
        END IF; END $$""")


def downgrade():
    for t in reversed(TABLES):
        op.drop_table(t)
