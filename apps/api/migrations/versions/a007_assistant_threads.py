"""Server-side assistant chat history (owner-only)."""
from alembic import op
import sqlalchemy as sa

revision = 'a007assistantthreads'
down_revision = 'a006assistantrls'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('assistant_threads',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('owner_subject', sa.String(160), nullable=False),
        sa.Column('title', sa.String(120), nullable=False),
        sa.Column('messages', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_index('ix_assistant_threads_owner_subject', 'assistant_threads', ['owner_subject'])
    op.create_index('ix_assistant_threads_owner_updated', 'assistant_threads', ['owner_subject', 'updated_at'])
    if op.get_bind().dialect.name == 'postgresql':
        op.execute('ALTER TABLE public.assistant_threads ENABLE ROW LEVEL SECURITY')
        op.execute("""DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
          GRANT SELECT, INSERT, UPDATE, DELETE ON public.assistant_threads TO authenticated;
          CREATE POLICY pf_threads_select ON public.assistant_threads FOR SELECT TO authenticated USING (owner_subject = public.pf_uid());
          CREATE POLICY pf_threads_insert ON public.assistant_threads FOR INSERT TO authenticated WITH CHECK (owner_subject = public.pf_uid());
          CREATE POLICY pf_threads_update ON public.assistant_threads FOR UPDATE TO authenticated USING (owner_subject = public.pf_uid()) WITH CHECK (owner_subject = public.pf_uid());
          CREATE POLICY pf_threads_delete ON public.assistant_threads FOR DELETE TO authenticated USING (owner_subject = public.pf_uid());
        END IF; END $$""")


def downgrade():
    op.drop_table('assistant_threads')
