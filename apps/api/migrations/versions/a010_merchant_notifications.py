"""Per-staff in-app merchant notifications (reservation to prepare)."""
from alembic import op
import sqlalchemy as sa

revision = 'a010merchantnotify'
down_revision = 'a009accounthub'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('merchant_notifications',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('merchant_id', sa.String(48), sa.ForeignKey('merchants.id'), nullable=False),
        sa.Column('recipient_subject', sa.String(160), nullable=False),
        sa.Column('order_id', sa.String(48), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('event_type', sa.String(40), nullable=False),
        sa.Column('message', sa.String(300), nullable=False),
        sa.Column('seen_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('order_id', 'event_type', 'recipient_subject', name='uq_merchant_notification'))
    op.create_index('ix_merchant_notifications_merchant_id', 'merchant_notifications', ['merchant_id'])
    op.create_index('ix_merchant_notifications_recipient_subject', 'merchant_notifications', ['recipient_subject'])
    op.create_index('ix_merchant_notifications_order_id', 'merchant_notifications', ['order_id'])
    if op.get_bind().dialect.name == 'postgresql':
        # API-only table (like notifications): RLS on, no direct client access.
        op.execute('ALTER TABLE public.merchant_notifications ENABLE ROW LEVEL SECURITY')


def downgrade():
    op.drop_table('merchant_notifications')
