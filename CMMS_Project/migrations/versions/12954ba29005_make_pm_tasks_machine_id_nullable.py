"""make_pm_tasks_machine_id_nullable

Revision ID: 12954ba29005
Revises: eebcbbfa2914
Create Date: 2025-01-12 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '12954ba29005'
down_revision = 'eebcbbfa2914'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Make machine_id nullable in pm_tasks table (SQLite workaround)"""
    conn = op.get_bind()
    
    # Check if machine_id is already nullable
    result = conn.execute(text("PRAGMA table_info(pm_tasks)"))
    columns = {row[1]: row for row in result.fetchall()}
    
    if 'machine_id' in columns:
        machine_id_info = columns['machine_id']
        # Column 3 is the "notnull" flag (1 = NOT NULL, 0 = nullable)
        if machine_id_info[3] == 1:
            # machine_id is NOT NULL, we need to make it nullable
            # SQLite doesn't support ALTER COLUMN, so we recreate the table
            
            # Step 1: Create new table with nullable machine_id
            op.execute(text("""
                CREATE TABLE pm_tasks_new (
                    id INTEGER NOT NULL PRIMARY KEY,
                    machine_id INTEGER,
                    task_name VARCHAR(150) NOT NULL,
                    task_description TEXT,
                    task_type VARCHAR(20) DEFAULT 'recurring',
                    frequency_days INTEGER,
                    last_executed_date DATETIME,
                    next_due_date DATETIME,
                    is_active BOOLEAN,
                    created_at DATETIME,
                    updated_at DATETIME,
                    assigned_to_user_id INTEGER,
                    priority VARCHAR(20) DEFAULT 'normal',
                    status VARCHAR(50) DEFAULT 'pending',
                    due_date DATETIME,
                    estimated_duration_minutes INTEGER,
                    created_by_user_id INTEGER,
                    location VARCHAR(200),
                    FOREIGN KEY(machine_id) REFERENCES machines (id),
                    FOREIGN KEY(assigned_to_user_id) REFERENCES users (id),
                    FOREIGN KEY(created_by_user_id) REFERENCES users (id)
                )
            """))
            
            # Step 2: Copy data from old table to new table
            op.execute(text("""
                INSERT INTO pm_tasks_new 
                (id, machine_id, task_name, task_description, task_type, frequency_days, 
                 last_executed_date, next_due_date, is_active, created_at, updated_at,
                 assigned_to_user_id, priority, status, due_date, estimated_duration_minutes,
                 created_by_user_id, location)
                SELECT 
                    id, machine_id, task_name, task_description, 
                    COALESCE(task_type, 'recurring') as task_type,
                    frequency_days, last_executed_date, next_due_date, is_active,
                    created_at, updated_at, assigned_to_user_id, priority, status,
                    due_date, estimated_duration_minutes, created_by_user_id, location
                FROM pm_tasks
            """))
            
            # Step 3: Drop old table
            op.execute(text("DROP TABLE pm_tasks"))
            
            # Step 4: Rename new table
            op.execute(text("ALTER TABLE pm_tasks_new RENAME TO pm_tasks"))
            
            # Step 5: Recreate indexes
            op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_machine_id ON pm_tasks(machine_id)"))
            op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_next_due_date ON pm_tasks(next_due_date)"))
            op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_assigned_to_user_id ON pm_tasks(assigned_to_user_id)"))
            op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_status ON pm_tasks(status)"))


def downgrade() -> None:
    """Make machine_id NOT NULL again (SQLite workaround)"""
    conn = op.get_bind()
    
    # Check if there are any NULL machine_id values
    result = conn.execute(text("SELECT COUNT(*) FROM pm_tasks WHERE machine_id IS NULL"))
    null_count = result.fetchone()[0]
    
    if null_count > 0:
        raise Exception(f"Cannot downgrade: {null_count} records have NULL machine_id. Please update them first.")
    
    # Recreate table with NOT NULL machine_id
    op.execute(text("""
        CREATE TABLE pm_tasks_new (
            id INTEGER NOT NULL PRIMARY KEY,
            machine_id INTEGER NOT NULL,
            task_name VARCHAR(150) NOT NULL,
            task_description TEXT,
            task_type VARCHAR(20) DEFAULT 'recurring',
            frequency_days INTEGER,
            last_executed_date DATETIME,
            next_due_date DATETIME,
            is_active BOOLEAN,
            created_at DATETIME,
            updated_at DATETIME,
            assigned_to_user_id INTEGER,
            priority VARCHAR(20) DEFAULT 'normal',
            status VARCHAR(50) DEFAULT 'pending',
            due_date DATETIME,
            estimated_duration_minutes INTEGER,
            created_by_user_id INTEGER,
            location VARCHAR(200),
            FOREIGN KEY(machine_id) REFERENCES machines (id),
            FOREIGN KEY(assigned_to_user_id) REFERENCES users (id),
            FOREIGN KEY(created_by_user_id) REFERENCES users (id)
        )
    """))
    
    op.execute(text("""
        INSERT INTO pm_tasks_new 
        (id, machine_id, task_name, task_description, task_type, frequency_days, 
         last_executed_date, next_due_date, is_active, created_at, updated_at,
         assigned_to_user_id, priority, status, due_date, estimated_duration_minutes,
         created_by_user_id, location)
        SELECT 
            id, machine_id, task_name, task_description, 
            COALESCE(task_type, 'recurring') as task_type,
            frequency_days, last_executed_date, next_due_date, is_active,
            created_at, updated_at, assigned_to_user_id, priority, status,
            due_date, estimated_duration_minutes, created_by_user_id, location
        FROM pm_tasks
    """))
    
    op.execute(text("DROP TABLE pm_tasks"))
    op.execute(text("ALTER TABLE pm_tasks_new RENAME TO pm_tasks"))
    
    # Recreate indexes
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_machine_id ON pm_tasks(machine_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_next_due_date ON pm_tasks(next_due_date)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_assigned_to_user_id ON pm_tasks(assigned_to_user_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_pm_tasks_status ON pm_tasks(status)"))
