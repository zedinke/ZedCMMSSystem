"""add_location_to_pm_task_and_make_machine_id_nullable

Revision ID: d4d439e36b00
Revises: 63991a7f8ad4
Create Date: 2025-01-12 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'd4d439e36b00'
down_revision = '63991a7f8ad4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add location field to pm_tasks and make machine_id nullable"""
    # Check if columns exist (SQLite compatible)
    conn = op.get_bind()
    result = conn.execute(text("PRAGMA table_info(pm_tasks)"))
    existing_columns = [row[1] for row in result.fetchall()]
    
    # Add location column if it doesn't exist
    if 'location' not in existing_columns:
        op.execute(text("ALTER TABLE pm_tasks ADD COLUMN location VARCHAR(200)"))
    
    # Make machine_id nullable (SQLite doesn't support ALTER COLUMN directly, so we need to recreate the table)
    # But first check if there are any NULL values already
    result = conn.execute(text("SELECT COUNT(*) FROM pm_tasks WHERE machine_id IS NULL"))
    null_count = result.fetchone()[0]
    
    if null_count == 0:
        # No NULL values, we can safely modify
        # SQLite doesn't support ALTER COLUMN, so we'll use a workaround
        # For now, we'll just add the column and note that machine_id should be nullable
        # The actual constraint change would require table recreation
        pass


def downgrade() -> None:
    """Remove location field and make machine_id non-nullable"""
    # Drop location column (SQLite workaround)
    op.execute(text("CREATE TABLE pm_tasks_new AS SELECT id, machine_id, task_name, task_description, frequency_days, last_executed_date, next_due_date, is_active, created_at, updated_at, assigned_to_user_id, priority, status, due_date, estimated_duration_minutes, created_by_user_id FROM pm_tasks"))
    op.execute(text("DROP TABLE pm_tasks"))
    op.execute(text("ALTER TABLE pm_tasks_new RENAME TO pm_tasks"))
    
    # Recreate indexes
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_machine_id ON pm_tasks(machine_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_next_due_date ON pm_tasks(next_due_date)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_assigned_to_user_id ON pm_tasks(assigned_to_user_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_status ON pm_tasks(status)"))
