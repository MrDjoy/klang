"""Add a start_time and end_time in Table monitor_tasks

Revision ID: 26c980391bd4
Revises: c3fdd8656286
Create Date: 2025-12-12 18:57:50.999587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import time
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision: str = '26c980391bd4'
down_revision: Union[str, Sequence[str], None] = 'c3fdd8656286'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('monitor_tasks',
                  sa.Column('start_time',
                            sa.Time(),
                            server_default=sa.text("'09:30:00'"),
                            nullable=False)
                  )
    op.add_column('monitor_tasks',
                  sa.Column('end_time',
                            sa.Time(),
                            server_default=sa.text("'15:30:00'"),
                            nullable=False)
                  )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
