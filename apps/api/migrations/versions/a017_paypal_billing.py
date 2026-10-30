"""PayPal sandbox plan billing and per-order invoices (ids and statuses only)."""
from alembic import op
import sqlalchemy as sa

revision = 'a017paypalbilling'
down_revision = 'a016threadbuyername'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('billing_plans',
        sa.Column('plan_id', sa.String(24), primary_key=True),
        sa.Column('paypal_product_id', sa.String(80), nullable=False),
        sa.Column('paypal_plan_id', sa.String(80), nullable=False),
        sa.Column('amount_cents', sa.Integer, nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()))
    op.create_table('business_subscriptions_paypal',
        sa.Column('owner_subject', sa.String(160), primary_key=True),
        sa.Column('paypal_subscription_id', sa.String(80), nullable=False),
        sa.Column('plan_id', sa.String(24), nullable=False),
        sa.Column('status', sa.String(24), nullable=False, server_default='APPROVAL_PENDING'),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()))
    op.create_index('ix_bsp_sub_id', 'business_subscriptions_paypal', ['paypal_subscription_id'])
    op.create_table('order_invoices',
        sa.Column('order_id', sa.String(48), primary_key=True),
        sa.Column('paypal_invoice_id', sa.String(80), nullable=True),
        sa.Column('status', sa.String(24), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()))


def downgrade():
    op.drop_table('order_invoices')
    op.drop_index('ix_bsp_sub_id', table_name='business_subscriptions_paypal')
    op.drop_table('business_subscriptions_paypal')
    op.drop_table('billing_plans')
