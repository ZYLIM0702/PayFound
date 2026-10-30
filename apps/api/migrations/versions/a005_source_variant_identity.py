"""Source variants retain identity even when a merchant reuses a SKU."""
from alembic import op
import sqlalchemy as sa

revision = 'a005sku'
down_revision = 'a004notifications'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('products') as batch:
        batch.drop_constraint('uq_location_sku', type_='unique')
        batch.create_index('uq_manual_location_sku', ['merchant_id', 'location_id', 'sku'], unique=True,
            sqlite_where=sa.text("inventory_source IN ('manual','merchant_manual','synthetic_local')"),
            postgresql_where=sa.text("inventory_source IN ('manual','merchant_manual','synthetic_local')"))


def downgrade():
    # Do not silently discard legitimate duplicate source variants to downgrade.
    raise RuntimeError('Review source SKU duplicates before an explicit schema downgrade')
