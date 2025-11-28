"""Add provider and model tags

Revision ID: 002
Revises: 001
Create Date: 2025-11-28 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('providers', sa.Column('tags', sa.Text(), nullable=True))

    op.add_column('models', sa.Column('system_tags', sa.Text(), nullable=False, server_default='[]'))
    op.add_column('models', sa.Column('user_tags', sa.Text(), nullable=True))

    # Backfill system_tags for existing rows
    op.execute("UPDATE models SET system_tags = '[]' WHERE system_tags IS NULL")

    # Drop the server default now that rows are initialized
    op.alter_column('models', 'system_tags', server_default=None)


def downgrade() -> None:
    op.drop_column('models', 'user_tags')
    op.drop_column('models', 'system_tags')
    op.drop_column('providers', 'tags')
