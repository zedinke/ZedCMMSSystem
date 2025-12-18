"""add_workflow_constraints_and_audit_fields

Revision ID: 993d9bd26494
Revises: f8a9b2c3d4e5
Create Date: 2025-12-17 05:10:45.760193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '993d9bd26494'
down_revision: Union[str, Sequence[str], None] = 'f8a9b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add workflow constraints, audit fields, and stock reservations."""
    conn = op.get_bind()
    
    # Helper functions
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
    
    def table_exists(table_name: str) -> bool:
        """Check if a table exists"""
        result = conn.execute(text("""
            SELECT COUNT(*) as table_count
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = :table_name
        """), {"table_name": table_name})
        return result.fetchone()[0] > 0
    
    def constraint_exists(table_name: str, constraint_name: str) -> bool:
        """Check if a constraint exists"""
        result = conn.execute(text("""
            SELECT COUNT(*) as const_count
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = :table_name
            AND CONSTRAINT_NAME = :constraint_name
        """), {"table_name": table_name, "constraint_name": constraint_name})
        return result.fetchone()[0] > 0
    
    # Add version column to worksheets if not exists
    if not column_exists('worksheets', 'version'):
        op.add_column('worksheets', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
    
    # Add version column to pm_tasks if not exists
    if not column_exists('pm_tasks', 'version'):
        op.add_column('pm_tasks', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
    
    # Add ip_address and user_agent to system_logs if not exists
    if not column_exists('system_logs', 'ip_address'):
        op.add_column('system_logs', sa.Column('ip_address', sa.String(length=45), nullable=True))
    
    if not column_exists('system_logs', 'user_agent'):
        op.add_column('system_logs', sa.Column('user_agent', sa.String(length=500), nullable=True))
    
    # Create stock_reservations table if not exists
    if not table_exists('stock_reservations'):
        op.create_table(
            'stock_reservations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('part_id', sa.Integer(), nullable=False),
            sa.Column('worksheet_id', sa.Integer(), nullable=True),
            sa.Column('quantity_reserved', sa.Integer(), nullable=False),
            sa.Column('reserved_at', sa.DateTime(), nullable=True),
            sa.Column('expires_at', sa.DateTime(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
            sa.ForeignKeyConstraint(['worksheet_id'], ['worksheets.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_reservation_part', 'stock_reservations', ['part_id'], unique=False)
        op.create_index('idx_reservation_worksheet', 'stock_reservations', ['worksheet_id'], unique=False)
        op.create_index('idx_reservation_expires', 'stock_reservations', ['expires_at'], unique=False)
    
    # Add constraints if they don't exist
    if not constraint_exists('worksheets', 'chk_worksheet_dates'):
        op.create_check_constraint(
            'chk_worksheet_dates',
            'worksheets',
            'repair_finished_time IS NULL OR breakdown_time IS NULL OR repair_finished_time >= breakdown_time'
        )
    
    if not constraint_exists('worksheets', 'chk_worksheet_status_closed'):
        op.create_check_constraint(
            'chk_worksheet_status_closed',
            'worksheets',
            "status != 'Closed' OR (fault_cause IS NOT NULL AND fault_cause != '')"
        )
    
    if not constraint_exists('pm_tasks', 'chk_pm_task_dates'):
        op.create_check_constraint(
            'chk_pm_task_dates',
            'pm_tasks',
            'last_executed_date IS NULL OR next_due_date IS NULL OR next_due_date >= last_executed_date'
        )
    
    if not constraint_exists('inventory_levels', 'chk_inv_qty_on_hand'):
        op.create_check_constraint(
            'chk_inv_qty_on_hand',
            'inventory_levels',
            'quantity_on_hand >= 0'
        )
    
    if not constraint_exists('inventory_levels', 'chk_inv_qty_reserved'):
        op.create_check_constraint(
            'chk_inv_qty_reserved',
            'inventory_levels',
            'quantity_reserved >= 0'
        )
    
    if not constraint_exists('stock_transactions', 'chk_stock_quantity'):
        op.create_check_constraint(
            'chk_stock_quantity',
            'stock_transactions',
            'quantity != 0'
        )
    
    # Initialize version fields for existing records
    conn.execute(text("UPDATE worksheets SET version = 1 WHERE version IS NULL OR version = 0"))
    conn.execute(text("UPDATE pm_tasks SET version = 1 WHERE version IS NULL OR version = 0"))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop constraints
    try:
        op.drop_constraint('chk_stock_quantity', 'stock_transactions', type_='check')
    except:
        pass
    
    try:
        op.drop_constraint('chk_inv_qty_reserved', 'inventory_levels', type_='check')
    except:
        pass
    
    try:
        op.drop_constraint('chk_inv_qty_on_hand', 'inventory_levels', type_='check')
    except:
        pass
    
    try:
        op.drop_constraint('chk_pm_task_dates', 'pm_tasks', type_='check')
    except:
        pass
    
    try:
        op.drop_constraint('chk_worksheet_status_closed', 'worksheets', type_='check')
    except:
        pass
    
    try:
        op.drop_constraint('chk_worksheet_dates', 'worksheets', type_='check')
    except:
        pass
    
    # Drop stock_reservations table
    try:
        op.drop_index('idx_reservation_expires', table_name='stock_reservations')
        op.drop_index('idx_reservation_worksheet', table_name='stock_reservations')
        op.drop_index('idx_reservation_part', table_name='stock_reservations')
        op.drop_table('stock_reservations')
    except:
        pass
    
    # Note: SQLite doesn't support DROP COLUMN easily, so we'll leave the columns
    # They will be ignored by the application if not present in the model
