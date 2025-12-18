"""Add extended fields and version tracking to machines table

Revision ID: d5ec03ccf66a
Revises: 43f00839f94b
Create Date: 2025-12-13 16:22:26.013459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'd5ec03ccf66a'
down_revision: Union[str, Sequence[str], None] = '43f00839f94b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add extended fields and version tracking to machines table."""
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
    
    # Helper function to add column if it doesn't exist
    def add_column_if_not_exists(table_name: str, column_name: str, column_def: str):
        """Add a column only if it doesn't exist"""
        if not column_exists(table_name, column_name):
            op.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def};")
    
    # Add columns only if they don't exist
    add_column_if_not_exists('machines', 'asset_tag', 'VARCHAR(50)')
    add_column_if_not_exists('machines', 'purchase_date', 'DATETIME')
    add_column_if_not_exists('machines', 'purchase_price', 'FLOAT')
    add_column_if_not_exists('machines', 'warranty_expiry_date', 'DATETIME')
    add_column_if_not_exists('machines', 'supplier', 'VARCHAR(200)')
    add_column_if_not_exists('machines', 'operating_hours', 'FLOAT DEFAULT 0.0')
    add_column_if_not_exists('machines', 'last_service_date', 'DATETIME')
    add_column_if_not_exists('machines', 'next_service_date', 'DATETIME')
    add_column_if_not_exists('machines', 'criticality_level', 'VARCHAR(50)')
    add_column_if_not_exists('machines', 'energy_consumption', 'VARCHAR(100)')
    add_column_if_not_exists('machines', 'power_requirements', 'VARCHAR(200)')
    add_column_if_not_exists('machines', 'operating_temperature_range', 'VARCHAR(100)')
    add_column_if_not_exists('machines', 'weight', 'FLOAT')
    add_column_if_not_exists('machines', 'dimensions', 'VARCHAR(200)')
    add_column_if_not_exists('machines', 'notes', 'TEXT')
    add_column_if_not_exists('machines', 'version', 'INTEGER DEFAULT 1')
    add_column_if_not_exists('machines', 'created_by_user_id', 'INTEGER')
    add_column_if_not_exists('machines', 'updated_by_user_id', 'INTEGER')
    
    # Create indexes (with error handling)
    try:
        op.create_index('idx_asset_tag', 'machines', ['asset_tag'], unique=False)
    except Exception:
        # Index might already exist
        pass
    
    # Helper function to check if table exists
    def table_exists(table_name: str) -> bool:
        """Check if a table exists"""
        result = conn.execute(text("""
            SELECT COUNT(*) as table_count
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = :table_name
        """), {"table_name": table_name})
        return result.fetchone()[0] > 0
    
    # Create machine_versions table only if it doesn't exist
    if not table_exists('machine_versions'):
        op.create_table(
            'machine_versions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('machine_id', sa.Integer(), nullable=False),
            sa.Column('version', sa.Integer(), nullable=False),
            sa.Column('changed_fields', sa.JSON(), nullable=True),
            sa.Column('changed_by_user_id', sa.Integer(), nullable=False),
            sa.Column('change_description', sa.Text(), nullable=True),
            sa.Column('timestamp', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ),
            sa.ForeignKeyConstraint(['changed_by_user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_machine_versions_machine_id', 'machine_versions', ['machine_id'], unique=False)
        op.create_index('idx_machine_versions_timestamp', 'machine_versions', ['timestamp'], unique=False)
        op.create_index('idx_machine_versions_version', 'machine_versions', ['version'], unique=False)
    else:
        # Table exists, but check if indexes exist
        def index_exists(table_name: str, index_name: str) -> bool:
            """Check if an index exists"""
            result = conn.execute(text("""
                SELECT COUNT(*) as idx_count
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = :table_name
                AND INDEX_NAME = :index_name
            """), {"table_name": table_name, "index_name": index_name})
            return result.fetchone()[0] > 0
        
        # Create indexes if they don't exist
        if not index_exists('machine_versions', 'idx_machine_versions_machine_id'):
            try:
                op.create_index('idx_machine_versions_machine_id', 'machine_versions', ['machine_id'], unique=False)
            except Exception:
                pass
        if not index_exists('machine_versions', 'idx_machine_versions_timestamp'):
            try:
                op.create_index('idx_machine_versions_timestamp', 'machine_versions', ['timestamp'], unique=False)
            except Exception:
                pass
        if not index_exists('machine_versions', 'idx_machine_versions_version'):
            try:
                op.create_index('idx_machine_versions_version', 'machine_versions', ['version'], unique=False)
            except Exception:
                pass


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes (with error handling for SQLite)
    try:
        op.drop_index('idx_asset_tag', table_name='machines')
    except:
        pass
    try:
        op.drop_index('idx_machine_versions_version', table_name='machine_versions')
    except:
        pass
    try:
        op.drop_index('idx_machine_versions_timestamp', table_name='machine_versions')
    except:
        pass
    try:
        op.drop_index('idx_machine_versions_machine_id', table_name='machine_versions')
    except:
        pass
    
    # Drop machine_versions table
    try:
        op.drop_table('machine_versions')
    except:
        pass
    
    # Note: SQLite doesn't support DROP COLUMN easily, so we'll leave the columns
    # They will be ignored by the application if not present in the model
