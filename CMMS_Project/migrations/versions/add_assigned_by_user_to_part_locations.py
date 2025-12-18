"""add_assigned_by_user_to_part_locations

Revision ID: a1b2c3d4e5f6
Revises: f8a9b2c3d4e5
Create Date: 2025-12-16 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f8a9b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add assigned_by_user_id to part_locations table."""
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
    
    # Add assigned_by_user_id column if it doesn't exist
    if not column_exists('part_locations', 'assigned_by_user_id'):
        op.add_column('part_locations', sa.Column('assigned_by_user_id', sa.Integer(), nullable=True))
        op.create_foreign_key(
            'fk_part_locations_assigned_by_user',
            'part_locations',
            'users',
            ['assigned_by_user_id'],
            ['id']
        )
        op.create_index('idx_part_locations_assigned_by_user_id', 'part_locations', ['assigned_by_user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index and foreign key
    try:
        op.drop_index('idx_part_locations_assigned_by_user_id', table_name='part_locations')
    except Exception:
        pass
    
    try:
        op.drop_constraint('fk_part_locations_assigned_by_user', 'part_locations', type_='foreignkey')
    except Exception:
        pass
    
    # Drop column
    try:
        op.drop_column('part_locations', 'assigned_by_user_id')
    except Exception:
        pass

