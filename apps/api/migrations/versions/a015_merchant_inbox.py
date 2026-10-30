"""Merchant replies to reviews."""
from alembic import op
import sqlalchemy as sa

revision = 'a015merchantinbox'
down_revision = 'a014paypalpool'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('reviews', sa.Column('reply', sa.String(1500), nullable=False, server_default=''))
    op.add_column('reviews', sa.Column('replied_at', sa.DateTime, nullable=True))


def downgrade():
    op.drop_column('reviews', 'replied_at')
    op.drop_column('reviews', 'reply')
