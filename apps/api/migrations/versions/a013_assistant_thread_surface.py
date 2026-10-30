"""Separate assistant chat history by surface (shopper | merchant)."""
from alembic import op
import sqlalchemy as sa

revision = 'a013threadsurface'
down_revision = 'a012reportcards'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('assistant_threads') as batch:
        batch.add_column(sa.Column('surface', sa.String(16), nullable=False, server_default='shopper'))
        batch.create_check_constraint('ck_assistant_threads_surface', "surface IN ('shopper','merchant')")
    op.create_index('ix_assistant_threads_owner_surface', 'assistant_threads', ['owner_subject', 'surface', 'updated_at'])


def downgrade():
    op.drop_index('ix_assistant_threads_owner_surface', table_name='assistant_threads')
    with op.batch_alter_table('assistant_threads') as batch:
        batch.drop_constraint('ck_assistant_threads_surface', type_='check')
        batch.drop_column('surface')
