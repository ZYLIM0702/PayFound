"""Online price cache and shopper price watches."""
from alembic import op
import sqlalchemy as sa

revision = 'a018suggestions'
down_revision = 'a017paypalbilling'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('online_price_cache',
        sa.Column('product_id', sa.String(48), sa.ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('online_cents', sa.Integer, nullable=True),
        sa.Column('currency', sa.String(3), nullable=True),
        sa.Column('retailer', sa.String(250), nullable=True),
        sa.Column('url', sa.String(8192), nullable=True),
        sa.Column('checked_at', sa.DateTime, nullable=False, server_default=sa.func.now()))
    op.create_table('price_watches',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('buyer_subject', sa.String(160), nullable=False),
        sa.Column('product_id', sa.String(48), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('merchant_id', sa.String(48), sa.ForeignKey('merchants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('last_checked_at', sa.DateTime, nullable=True),
        sa.Column('last_online_cents', sa.Integer, nullable=True),
        sa.Column('last_local_cents', sa.Integer, nullable=True),
        sa.UniqueConstraint('buyer_subject', 'product_id', name='uq_price_watch_buyer_product'))
    op.create_index('ix_price_watches_buyer_subject', 'price_watches', ['buyer_subject'])


def downgrade():
    op.drop_index('ix_price_watches_buyer_subject', table_name='price_watches')
    op.drop_table('price_watches')
    op.drop_table('online_price_cache')
