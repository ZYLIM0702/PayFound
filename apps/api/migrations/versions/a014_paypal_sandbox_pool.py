"""Sandbox PayPal receiving-account pool (email + label only) and demo sandbox payment records."""
from alembic import op
import sqlalchemy as sa

revision = 'a014paypalpool'
down_revision = 'a013threadsurface'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('paypal_sandbox_accounts',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('email', sa.String(190), nullable=False, unique=True),
        sa.Column('display_label', sa.String(120), nullable=False, server_default=''),
        sa.Column('country', sa.String(2), nullable=False, server_default='US'),
        sa.Column('account_type', sa.String(16), nullable=False, server_default='BUSINESS'),
        sa.Column('assigned_to_subject', sa.String(160), nullable=True),
        sa.Column('assigned_to_merchant_id', sa.String(48), sa.ForeignKey('merchants.id'), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime, nullable=False))
    op.create_table('paypal_demo_payments',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('merchant_id', sa.String(48), sa.ForeignKey('merchants.id'), nullable=False, index=True),
        sa.Column('order_id', sa.String(48), nullable=True),
        sa.Column('provider', sa.String(24), nullable=False, server_default='paypal_sandbox'),
        sa.Column('stage', sa.String(24), nullable=False),
        sa.Column('amount_cents', sa.Integer, nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('reference', sa.String(64), nullable=False),
        sa.Column('demo_seeded', sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime, nullable=False))


def downgrade():
    op.drop_table('paypal_demo_payments')
    op.drop_table('paypal_sandbox_accounts')
