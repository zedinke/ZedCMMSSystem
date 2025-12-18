"""add_shift_override_and_rotation

Revision ID: 43octa2khhce
Revises: eebcbbfa2914
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '43octa2khhce'
down_revision = 'de9c675ae5a3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add ShiftOverride table and rotation fields to ShiftSchedule"""
    
    # Add rotation fields to shift_schedules table
    conn = op.get_bind()
    
    # Check if columns exist (SQLite compatible)
    result = conn.execute(text("PRAGMA table_info(shift_schedules)"))
    existing_columns = [row[1] for row in result.fetchall()]
    
    # Add rotation_start_date if it doesn't exist
    if 'rotation_start_date' not in existing_columns:
        op.execute(text("ALTER TABLE shift_schedules ADD COLUMN rotation_start_date DATE"))
    
    # Add initial_shift if it doesn't exist
    if 'initial_shift' not in existing_columns:
        op.execute(text("ALTER TABLE shift_schedules ADD COLUMN initial_shift VARCHAR(10)"))
    
    # Add rotation_pattern if it doesn't exist
    if 'rotation_pattern' not in existing_columns:
        op.execute(text("ALTER TABLE shift_schedules ADD COLUMN rotation_pattern VARCHAR(20) DEFAULT 'weekly'"))
    
    # Create shift_overrides table if it doesn't exist
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='shift_overrides'"))
    table_exists = result.fetchone() is not None
    
    if not table_exists:
        op.create_table(
            'shift_overrides',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('override_date', sa.Date(), nullable=False),
            sa.Column('shift_type', sa.String(length=10), nullable=False),
            sa.Column('start_time', sa.String(length=10), nullable=True),
            sa.Column('end_time', sa.String(length=10), nullable=True),
            sa.Column('created_by_user_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'override_date', name='uq_user_date_override')
        )
        
        # Create indexes
        op.create_index('idx_shift_overrides_user_date', 'shift_overrides', ['user_id', 'override_date'])
    else:
        # Check if index exists
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_shift_overrides_user_date'"))
        index_exists = result.fetchone() is not None
        if not index_exists:
            op.create_index('idx_shift_overrides_user_date', 'shift_overrides', ['user_id', 'override_date'])


def downgrade() -> None:
    """Remove ShiftOverride table and rotation fields from ShiftSchedule"""
    
    # Drop shift_overrides table
    op.drop_index('idx_shift_overrides_user_date', table_name='shift_overrides')
    op.drop_table('shift_overrides')
    
    # Remove rotation fields from shift_schedules (SQLite workaround - recreate table)
    conn = op.get_bind()
    
    # Create new table without rotation columns
    op.execute(text("""
        CREATE TABLE shift_schedules_new AS 
        SELECT id, user_id, shift_type, start_time, end_time, 
               effective_from, effective_to, created_at
        FROM shift_schedules
    """))
    
    op.drop_table('shift_schedules')
    op.execute(text("ALTER TABLE shift_schedules_new RENAME TO shift_schedules"))
    
    # Recreate indexes
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_shift_schedules_user_id ON shift_schedules(user_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS idx_shift_schedules_effective ON shift_schedules(effective_from, effective_to)"))

