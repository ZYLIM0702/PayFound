"""Per-user shopper basket."""
from alembic import op
import sqlalchemy as sa

revision = 'a019basket'
down_revision = 'a018suggestions'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('basket_lines',
        sa.Column('owner_subject', sa.String(160), primary_key=True),
        sa.Column('product_id', sa.String(48), sa.ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('position', sa.Integer, nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()))
    op.create_index('ix_basket_lines_product_id', 'basket_lines', ['product_id'])
    if op.get_bind().dialect.name == 'postgresql':
        op.execute('ALTER TABLE public.basket_lines ENABLE ROW LEVEL SECURITY')


def downgrade():
    op.drop_index('ix_basket_lines_product_id', table_name='basket_lines')
    op.drop_table('basket_lines')
