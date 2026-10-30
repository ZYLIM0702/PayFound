"""Account hub: sandbox payment-method link, merchant message threads, support tickets (owner-scoped)."""
from alembic import op
import sqlalchemy as sa

revision = 'a009accounthub'
down_revision = 'a008accountarea'
branch_labels = None
depends_on = None

TABLES = ('payment_methods', 'message_threads', 'thread_messages', 'support_tickets')


def upgrade():
    op.create_table('payment_methods',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('owner_subject', sa.String(160), nullable=False),
        sa.Column('provider', sa.String(20), nullable=False),
        sa.Column('masked_email', sa.String(160), nullable=False, server_default=''),
        sa.Column('status', sa.String(24), nullable=False, server_default='sandbox_linked'),
        sa.Column('created_at', sa.DateTime(), nullable=False))
    op.create_index('ix_payment_methods_owner_subject', 'payment_methods', ['owner_subject'])
    op.create_table('message_threads',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('buyer_subject', sa.String(160), nullable=False),
        sa.Column('merchant_id', sa.String(48), sa.ForeignKey('merchants.id'), nullable=False),
        sa.Column('order_id', sa.String(48), sa.ForeignKey('orders.id'), nullable=True),
        sa.Column('subject', sa.String(160), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_index('ix_message_threads_buyer_subject', 'message_threads', ['buyer_subject'])
    op.create_index('ix_message_threads_merchant_id', 'message_threads', ['merchant_id'])
    op.create_table('thread_messages',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('thread_id', sa.String(48), sa.ForeignKey('message_threads.id'), nullable=False),
        sa.Column('sender_role', sa.String(12), nullable=False),
        sa.Column('sender_subject', sa.String(160), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False))
    op.create_index('ix_thread_messages_thread_id', 'thread_messages', ['thread_id'])
    op.create_index('ix_thread_messages_thread_created', 'thread_messages', ['thread_id', 'created_at'])
    op.create_table('support_tickets',
        sa.Column('id', sa.String(48), primary_key=True),
        sa.Column('owner_subject', sa.String(160), nullable=False),
        sa.Column('topic', sa.String(24), nullable=False),
        sa.Column('subject', sa.String(120), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('order_id', sa.String(48), nullable=True),
        sa.Column('status', sa.String(16), nullable=False, server_default='open'),
        sa.Column('created_at', sa.DateTime(), nullable=False))
    op.create_index('ix_support_tickets_owner_subject', 'support_tickets', ['owner_subject'])
    if op.get_bind().dialect.name == 'postgresql':
        for t in TABLES:
            op.execute(f'ALTER TABLE public.{t} ENABLE ROW LEVEL SECURITY')
        op.execute("""DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
          GRANT SELECT, INSERT, UPDATE, DELETE ON public.payment_methods, public.message_threads, public.thread_messages, public.support_tickets TO authenticated;
          CREATE POLICY pf_payment_methods_owner ON public.payment_methods FOR ALL TO authenticated USING (owner_subject = public.pf_uid()) WITH CHECK (owner_subject = public.pf_uid());
          CREATE POLICY pf_threads_owner ON public.message_threads FOR ALL TO authenticated USING (buyer_subject = public.pf_uid()) WITH CHECK (buyer_subject = public.pf_uid());
          CREATE POLICY pf_thread_messages_owner ON public.thread_messages FOR ALL TO authenticated USING (EXISTS (SELECT 1 FROM public.message_threads t WHERE t.id = thread_id AND t.buyer_subject = public.pf_uid())) WITH CHECK (sender_subject = public.pf_uid() AND EXISTS (SELECT 1 FROM public.message_threads t WHERE t.id = thread_id AND t.buyer_subject = public.pf_uid()));
          CREATE POLICY pf_tickets_owner ON public.support_tickets FOR ALL TO authenticated USING (owner_subject = public.pf_uid()) WITH CHECK (owner_subject = public.pf_uid());
        END IF; END $$""")


def downgrade():
    for t in reversed(TABLES):
        op.drop_table(t)
