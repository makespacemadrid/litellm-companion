"""Add pricing override fields for config, providers, and models

Revision ID: 004
Revises: 003
Create Date: 2025-12-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("config", sa.Column("default_pricing_profile", sa.String(), nullable=True))
    op.add_column("config", sa.Column("default_pricing_override", sa.Text(), nullable=True))

    op.add_column("providers", sa.Column("pricing_profile", sa.String(), nullable=True))
    op.add_column("providers", sa.Column("pricing_override", sa.Text(), nullable=True))

    op.add_column("models", sa.Column("pricing_profile", sa.String(), nullable=True))
    op.add_column("models", sa.Column("pricing_override", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("models", "pricing_override")
    op.drop_column("models", "pricing_profile")
    op.drop_column("providers", "pricing_override")
    op.drop_column("providers", "pricing_profile")
    op.drop_column("config", "default_pricing_override")
    op.drop_column("config", "default_pricing_profile")
