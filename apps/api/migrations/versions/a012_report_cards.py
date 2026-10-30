"""Assistant-built merchant report cards (merchant_report_cards)."""
from alembic import op
import sqlalchemy as sa

revision = 'a012reportcards'
down_revision = 'a011pospluginconn'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('merchant_report_cards',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('merchant_id', sa.String(48), sa.ForeignKey('merchants.id'), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('kind', sa.String(16), nullable=False),
        sa.Column('days', sa.Integer(), nullable=False),
        sa.Column('focus', sa.String(120)),
        sa.Column('created_by', sa.String(160)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('days BETWEEN 1 AND 90', name='ck_report_card_days'))
    op.create_index('ix_merchant_report_cards_merchant_id', 'merchant_report_cards', ['merchant_id'])


def downgrade():
    op.drop_index('ix_merchant_report_cards_merchant_id', table_name='merchant_report_cards')
    op.drop_table('merchant_report_cards')
