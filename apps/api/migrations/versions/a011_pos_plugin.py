"""Custom POS connector: pos_connections and pos_sync_runs."""
from alembic import op
import sqlalchemy as sa

revision = 'a011pospluginconn'
down_revision = 'a010merchantnotify'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('pos_connections',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('merchant_id', sa.String(48), sa.ForeignKey('merchants.id'), nullable=False),
        sa.Column('name', sa.String(80), nullable=False),
        sa.Column('mode', sa.String(8), nullable=False),
        sa.Column('status', sa.String(16), nullable=False),
        sa.Column('base_url', sa.String(500)),
        sa.Column('products_path', sa.String(200), nullable=False),
        sa.Column('branches_path', sa.String(200)),
        sa.Column('health_path', sa.String(200), nullable=False),
        sa.Column('auth_scheme', sa.String(16), nullable=False),
        sa.Column('credentials_encrypted', sa.Text()),
        sa.Column('credential_hint', sa.String(16)),
        sa.Column('schedule', sa.String(8), nullable=False),
        sa.Column('settings', sa.JSON(), nullable=False),
        sa.Column('cursor_updated_at', sa.DateTime()),
        sa.Column('last_synced_at', sa.DateTime()),
        sa.Column('next_sync_at', sa.DateTime()),
        sa.Column('last_error', sa.String(300)),
        sa.Column('failure_count', sa.Integer(), nullable=False),
        sa.Column('lease_until', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('disconnected_at', sa.DateTime()))
    op.create_index('ix_pos_connections_merchant_id', 'pos_connections', ['merchant_id'])
    op.create_index('ix_pos_connections_due', 'pos_connections', ['status', 'next_sync_at'])
    op.create_table('pos_sync_runs',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('connection_id', sa.String(48), sa.ForeignKey('pos_connections.id'), nullable=False),
        sa.Column('trigger', sa.String(12), nullable=False),
        sa.Column('status', sa.String(12), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('finished_at', sa.DateTime()),
        sa.Column('created', sa.Integer(), nullable=False),
        sa.Column('updated', sa.Integer(), nullable=False),
        sa.Column('skipped', sa.Integer(), nullable=False),
        sa.Column('failed', sa.Integer(), nullable=False),
        sa.Column('error', sa.String(300)),
        sa.Column('row_errors', sa.JSON(), nullable=False),
        sa.Column('next_run_at', sa.DateTime()),
        sa.Column('delivery_id', sa.String(80)),
        sa.UniqueConstraint('connection_id', 'delivery_id', name='uq_pos_run_delivery'))
    op.create_index('ix_pos_sync_runs_connection_id', 'pos_sync_runs', ['connection_id'])
    if op.get_bind().dialect.name == 'postgresql':
        op.execute('ALTER TABLE public.pos_connections ENABLE ROW LEVEL SECURITY')
        op.execute('ALTER TABLE public.pos_sync_runs ENABLE ROW LEVEL SECURITY')


def downgrade():
    op.drop_table('pos_sync_runs')
    op.drop_table('pos_connections')
