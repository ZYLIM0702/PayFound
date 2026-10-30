"""Cover remaining foreign keys identified by Supabase's performance advisor."""
from alembic import op

revision = 'a003indexes'
down_revision = 'a002private'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_orders_product_id', 'orders', ['product_id'])
    op.create_index('ix_connector_locations_location_id', 'connector_locations', ['location_id'])


def downgrade():
    op.drop_index('ix_connector_locations_location_id', table_name='connector_locations')
    op.drop_index('ix_orders_product_id', table_name='orders')
