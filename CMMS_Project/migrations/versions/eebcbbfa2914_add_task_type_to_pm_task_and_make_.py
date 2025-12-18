"""add_task_type_to_pm_task_and_make_frequency_nullable

Revision ID: eebcbbfa2914
Revises: d4d439e36b00
Create Date: 2025-01-12 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'eebcbbfa2914'
down_revision = 'd4d439e36b00'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add task_type field and make frequency_days nullable"""
    # Check if columns exist (SQLite compatible)
    conn = op.get_bind()
    result = conn.execute(text("PRAGMA table_info(pm_tasks)"))
    existing_columns = [row[1] for row in result.fetchall()]
    
    # Add task_type column if it doesn't exist
    if 'task_type' not in existing_columns:
        op.execute(text("ALTER TABLE pm_tasks ADD COLUMN task_type VARCHAR(20) DEFAULT 'recurring'"))
        # Update existing records to be recurring
        op.execute(text("UPDATE pm_tasks SET task_type = 'recurring' WHERE task_type IS NULL"))
    
    # Note: SQLite doesn't support changing NOT NULL constraint directly
    # The frequency_days column will remain as is, but application logic will handle NULL values


def downgrade() -> None:
    """Remove task_type field"""
    # Drop task_type column (SQLite workaround)
    op.execute(text("CREATE TABLE pm_tasks_new AS SELECT id, machine_id, task_name, task_description, frequency_days, last_executed_date, next_due_date, is_active, created_at, updated_at, assigned_to_user_id, priority, status, due_date, estimated_duration_minutes, created_by_user_id, location FROM pm_tasks"))
    op.execute(text("DROP TABLE pm_tasks"))
    op.execute(text("ALTER TABLE pm_tasks_new RENAME TO pm_tasks"))
    
    # Recreate indexes
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_machine_id ON pm_tasks(machine_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_next_due_date ON pm_tasks(next_due_date)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_assigned_to_user_id ON pm_tasks(assigned_to_user_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_status ON pm_tasks(status)"))
