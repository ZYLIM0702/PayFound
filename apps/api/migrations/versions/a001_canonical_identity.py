"""Canonical product identity and merchant-authorized images."""
from alembic import op
import sqlalchemy as sa

revision = 'a001canonical'
down_revision = '38a40c4d740c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('canonical_products',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('gtin', sa.String(14), nullable=False, unique=True),
        sa.Column('name', sa.String(180), nullable=False),
        sa.Column('brand', sa.String(100), nullable=False),
        sa.Column('category', sa.String(90), nullable=False),
        sa.Column('attributes', sa.Text(), nullable=False))
    with op.batch_alter_table('products') as batch:
        batch.add_column(sa.Column('canonical_product_id', sa.String(48), nullable=True))
        batch.add_column(sa.Column('image_url', sa.String(2000), nullable=True))
        batch.create_foreign_key('fk_product_canonical', 'canonical_products', ['canonical_product_id'], ['id'])
        batch.create_index('ix_products_canonical_product_id', ['canonical_product_id'])


def downgrade():
    with op.batch_alter_table('products') as batch:
        batch.drop_index('ix_products_canonical_product_id')
        batch.drop_constraint('fk_product_canonical', type_='foreignkey')
        batch.drop_column('image_url')
        batch.drop_column('canonical_product_id')
    op.drop_table('canonical_products')
