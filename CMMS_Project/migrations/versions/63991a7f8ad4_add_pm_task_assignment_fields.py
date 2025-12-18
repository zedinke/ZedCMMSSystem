"""add_pm_task_assignment_fields

Revision ID: 63991a7f8ad4
Revises: 10cb2fe8ea7c
Create Date: 2025-01-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '63991a7f8ad4'
down_revision = '10cb2fe8ea7c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add assignment and priority fields to pm_tasks table"""
    # Check and add columns only if they don't exist (SQLite compatible)
    conn = op.get_bind()
    result = conn.execute(text("PRAGMA table_info(pm_tasks)"))
    existing_columns = [row[1] for row in result.fetchall()]
    
    # Add assigned_to_user_id column if it doesn't exist
    if 'assigned_to_user_id' not in existing_columns:
        op.execute(text("ALTER TABLE pm_tasks ADD COLUMN assigned_to_user_id INTEGER"))
        op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_assigned_to_user_id ON pm_tasks(assigned_to_user_id)"))
    
    # Add priority column if it doesn't exist
    if 'priority' not in existing_columns:
        op.execute(text("ALTER TABLE pm_tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'normal'"))
    
    # Add status column if it doesn't exist
    if 'status' not in existing_columns:
        op.execute(text("ALTER TABLE pm_tasks ADD COLUMN status VARCHAR(50) DEFAULT 'pending'"))
        op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_status ON pm_tasks(status)"))
    
    # Add due_date column if it doesn't exist
    if 'due_date' not in existing_columns:
        op.execute(text("ALTER TABLE pm_tasks ADD COLUMN due_date DATETIME"))
    
    # Add estimated_duration_minutes column if it doesn't exist
    if 'estimated_duration_minutes' not in existing_columns:
        op.execute(text("ALTER TABLE pm_tasks ADD COLUMN estimated_duration_minutes INTEGER"))
    
    # Add created_by_user_id column if it doesn't exist
    if 'created_by_user_id' not in existing_columns:
        op.execute(text("ALTER TABLE pm_tasks ADD COLUMN created_by_user_id INTEGER"))
    
    # Note: SQLite doesn't support adding foreign key constraints via ALTER TABLE
    # Foreign keys are enforced at the application level


def downgrade() -> None:
    """Remove assignment and priority fields from pm_tasks table"""
    # Drop foreign keys
    op.drop_constraint('fk_pm_tasks_created_by_user', 'pm_tasks', type_='foreignkey')
    op.drop_constraint('fk_pm_tasks_assigned_to_user', 'pm_tasks', type_='foreignkey')
    
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_pm_tasks_status")
    op.execute("DROP INDEX IF EXISTS idx_pm_tasks_assigned_to_user_id")
    
    # SQLite doesn't support DROP COLUMN directly, so we'll use a workaround
    # For SQLite, we need to recreate the table
    op.execute("""
        CREATE TABLE pm_tasks_new (
            id INTEGER NOT NULL PRIMARY KEY,
            machine_id INTEGER NOT NULL,
            task_name VARCHAR(150) NOT NULL,
            task_description TEXT,
            frequency_days INTEGER NOT NULL,
            last_executed_date DATETIME,
            next_due_date DATETIME,
            is_active BOOLEAN,
            created_at DATETIME,
            updated_at DATETIME,
            FOREIGN KEY(machine_id) REFERENCES machines (id)
        )
    """)
    op.execute("""
        INSERT INTO pm_tasks_new 
        (id, machine_id, task_name, task_description, frequency_days, last_executed_date, next_due_date, is_active, created_at, updated_at)
        SELECT id, machine_id, task_name, task_description, frequency_days, last_executed_date, next_due_date, is_active, created_at, updated_at
        FROM pm_tasks
    """)
    op.execute("DROP TABLE pm_tasks")
    op.execute("ALTER TABLE pm_tasks_new RENAME TO pm_tasks")
    
    # Recreate indexes
    op.execute("CREATE INDEX idx_pm_tasks_machine_id ON pm_tasks(machine_id)")
    op.execute("CREATE INDEX idx_pm_tasks_next_due_date ON pm_tasks(next_due_date)")
