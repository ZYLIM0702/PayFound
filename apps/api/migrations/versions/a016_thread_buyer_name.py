"""Store-facing display name for shopper conversations that are not tied to an order."""
from alembic import op
import sqlalchemy as sa

revision = 'a016threadbuyername'
down_revision = 'a015merchantinbox'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('message_threads', sa.Column('buyer_name', sa.String(130), nullable=False, server_default=''))


def downgrade():
    op.drop_column('message_threads', 'buyer_name')
