"""add_operating_hours_update_fields

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add operating hours update frequency fields to machines table."""
    # Get database connection to check column existence
    conn = op.get_bind()
    
    # Helper function to check if column exists
    def column_exists(table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table"""
        result = conn.execute(text("""
            SELECT COUNT(*) as col_count
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = :table_name
            AND COLUMN_NAME = :column_name
        """), {"table_name": table_name, "column_name": column_name})
        return result.fetchone()[0] > 0
    
    # Add operating_hours_update_frequency_type column if it doesn't exist
    if not column_exists('machines', 'operating_hours_update_frequency_type'):
        op.add_column('machines', sa.Column('operating_hours_update_frequency_type', sa.String(20), nullable=True))
    
    # Add operating_hours_update_frequency_value column if it doesn't exist
    if not column_exists('machines', 'operating_hours_update_frequency_value'):
        op.add_column('machines', sa.Column('operating_hours_update_frequency_value', sa.Integer(), nullable=True))
    
    # Add last_operating_hours_update column if it doesn't exist
    if not column_exists('machines', 'last_operating_hours_update'):
        op.add_column('machines', sa.Column('last_operating_hours_update', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop columns
    try:
        op.drop_column('machines', 'last_operating_hours_update')
    except Exception:
        pass
    
    try:
        op.drop_column('machines', 'operating_hours_update_frequency_value')
    except Exception:
        pass
    
    try:
        op.drop_column('machines', 'operating_hours_update_frequency_type')
    except Exception:
        pass

