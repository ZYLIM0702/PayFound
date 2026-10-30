"""Idempotent, tenant-scoped in-app notifications from the durable outbox."""
from alembic import op
import sqlalchemy as sa

revision = 'a004notifications'
down_revision = 'a003indexes'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('notifications',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('merchant_id', sa.String(48), sa.ForeignKey('merchants.id'), nullable=False),
        sa.Column('order_id', sa.String(48), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('audience', sa.String(20), nullable=False),
        sa.Column('buyer_subject', sa.String(160), nullable=True),
        sa.Column('event_type', sa.String(80), nullable=False),
        sa.Column('message', sa.String(300), nullable=False),
        sa.Column('seen_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('order_id', 'event_type', 'audience', name='uq_notification_effect'))
    for field in ('merchant_id', 'order_id', 'buyer_subject'):
        op.create_index('ix_notifications_' + field, 'notifications', [field])
    if op.get_bind().dialect.name == 'postgresql':
        op.execute('ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY')
        op.execute("DO $$ BEGIN IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='anon') THEN REVOKE ALL ON TABLE public.notifications FROM anon,authenticated; END IF; END $$")


def downgrade():
    op.drop_table('notifications')
