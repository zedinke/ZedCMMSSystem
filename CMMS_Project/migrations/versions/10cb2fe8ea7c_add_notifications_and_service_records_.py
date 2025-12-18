"""Add notifications and service records tables

Revision ID: 10cb2fe8ea7c
Revises: d5ec03ccf66a
Create Date: 2025-12-13 16:35:13.387983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10cb2fe8ea7c'
down_revision: Union[str, Sequence[str], None] = 'd5ec03ccf66a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add notifications and service records tables."""
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('related_entity_type', sa.String(length=50), nullable=True),
        sa.Column('related_entity_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'], unique=False)
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'], unique=False)
    op.create_index('idx_notifications_is_read', 'notifications', ['is_read'], unique=False)
    
    # Create service_records table
    op.create_table(
        'service_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('machine_id', sa.Integer(), nullable=False),
        sa.Column('service_date', sa.DateTime(), nullable=False),
        sa.Column('service_type', sa.String(length=100), nullable=True),
        sa.Column('performed_by', sa.String(length=200), nullable=True),
        sa.Column('technician_name', sa.String(length=200), nullable=True),
        sa.Column('service_cost', sa.Float(), nullable=True),
        sa.Column('service_duration_hours', sa.Float(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('next_service_date', sa.DateTime(), nullable=True),
        sa.Column('parts_replaced', sa.Text(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_service_records_machine_id', 'service_records', ['machine_id'], unique=False)
    op.create_index('idx_service_records_service_date', 'service_records', ['service_date'], unique=False)
    op.create_index('idx_service_records_next_service_date', 'service_records', ['next_service_date'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_service_records_next_service_date', table_name='service_records')
    op.drop_index('idx_service_records_service_date', table_name='service_records')
    op.drop_index('idx_service_records_machine_id', table_name='service_records')
    op.drop_table('service_records')
    
    op.drop_index('idx_notifications_is_read', table_name='notifications')
    op.drop_index('idx_notifications_created_at', table_name='notifications')
    op.drop_index('idx_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')
