"""Rename litellm provider type to openai and add compat type

Revision ID: 003
Revises: 002
Create Date: 2025-11-28 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns for access_groups and sync_enabled
    op.add_column('providers', sa.Column('access_groups', sa.Text(), nullable=True))
    op.add_column('providers', sa.Column('sync_enabled', sa.Boolean(), nullable=False, server_default='1'))

    op.add_column('models', sa.Column('access_groups', sa.Text(), nullable=True))
    op.add_column('models', sa.Column('sync_enabled', sa.Boolean(), nullable=False, server_default='1'))

    # Add compat model mapping fields
    op.add_column('models', sa.Column('mapped_provider_id', sa.Integer(), nullable=True))
    op.add_column('models', sa.Column('mapped_model_id', sa.String(), nullable=True))

    # Update existing 'litellm' provider types to 'openai'
    op.execute("UPDATE providers SET type = 'openai' WHERE type = 'litellm'")

    # Drop the old check constraint
    op.drop_constraint('check_provider_type', 'providers', type_='check')

    # Create new check constraint that allows 'ollama', 'openai', and 'compat'
    op.create_check_constraint(
        'check_provider_type',
        'providers',
        "type IN ('ollama', 'openai', 'compat')"
    )

    # Drop server defaults now that rows are initialized
    op.alter_column('providers', 'sync_enabled', server_default=None)
    op.alter_column('models', 'sync_enabled', server_default=None)


def downgrade() -> None:
    # Revert 'openai' back to 'litellm'
    op.execute("UPDATE providers SET type = 'litellm' WHERE type = 'openai'")

    # Drop the new check constraint
    op.drop_constraint('check_provider_type', 'providers', type_='check')

    # Recreate old check constraint
    op.create_check_constraint(
        'check_provider_type',
        'providers',
        "type IN ('ollama', 'litellm')"
    )

    # Drop new columns
    op.drop_column('models', 'mapped_model_id')
    op.drop_column('models', 'mapped_provider_id')
    op.drop_column('models', 'sync_enabled')
    op.drop_column('models', 'access_groups')
    op.drop_column('providers', 'sync_enabled')
    op.drop_column('providers', 'access_groups')
