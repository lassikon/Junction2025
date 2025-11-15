"""add active_subscriptions field

Revision ID: b1234567890a
Revises: aed006ffbb88
Create Date: 2025-11-15 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = 'b1234567890a'
down_revision: Union[str, None] = 'aed006ffbb88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add active_subscriptions JSON column to game_states table
    op.add_column('game_states', sa.Column('active_subscriptions', sa.JSON(), nullable=True, server_default='{}'))


def downgrade() -> None:
    # Remove active_subscriptions column
    op.drop_column('game_states', 'active_subscriptions')

