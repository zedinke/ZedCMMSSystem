"""Initial schema with indexes

Revision ID: 43f00839f94b
Revises: 
Create Date: 2025-12-13 13:09:50.132036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43f00839f94b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite doesn't support ALTER COLUMN, so we skip this if column already exists
    # The email column is already nullable in the model, so this migration is a no-op for SQLite
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # SQLite doesn't support ALTER COLUMN
    pass
