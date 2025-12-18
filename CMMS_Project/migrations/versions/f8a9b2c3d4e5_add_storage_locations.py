"""add_storage_locations

Revision ID: f8a9b2c3d4e5
Revises: 43octa2khhce
Create Date: 2025-12-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8a9b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = '43octa2khhce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create storage_locations table
    op.create_table('storage_locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('location_type', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_by_user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['storage_locations.id'], ),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_storage_locations_parent_id', 'storage_locations', ['parent_id'], unique=False)
    op.create_index('idx_storage_locations_code', 'storage_locations', ['code'], unique=False)
    op.create_index('idx_storage_locations_is_active', 'storage_locations', ['is_active'], unique=False)
    
    # Create part_locations table
    op.create_table('part_locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('part_id', sa.Integer(), nullable=False),
    sa.Column('storage_location_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('assigned_date', sa.DateTime(), nullable=False),
    sa.Column('last_movement_date', sa.DateTime(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
    sa.ForeignKeyConstraint(['storage_location_id'], ['storage_locations.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('part_id', 'storage_location_id', name='uq_part_location')
    )
    op.create_index('idx_part_locations_part_id', 'part_locations', ['part_id'], unique=False)
    op.create_index('idx_part_locations_storage_location_id', 'part_locations', ['storage_location_id'], unique=False)
    op.create_index('idx_part_locations_assigned_date', 'part_locations', ['assigned_date'], unique=False)
    
    # Add storage_location_id to stock_batches table
    op.add_column('stock_batches', sa.Column('storage_location_id', sa.Integer(), nullable=True))
    op.create_index('idx_stock_batches_storage_location_id', 'stock_batches', ['storage_location_id'], unique=False)
    op.create_foreign_key(None, 'stock_batches', 'storage_locations', ['storage_location_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove storage_location_id from stock_batches
    op.drop_constraint(None, 'stock_batches', type_='foreignkey')
    op.drop_index('idx_stock_batches_storage_location_id', table_name='stock_batches')
    op.drop_column('stock_batches', 'storage_location_id')
    
    # Drop part_locations table
    op.drop_index('idx_part_locations_assigned_date', table_name='part_locations')
    op.drop_index('idx_part_locations_storage_location_id', table_name='part_locations')
    op.drop_index('idx_part_locations_part_id', table_name='part_locations')
    op.drop_table('part_locations')
    
    # Drop storage_locations table
    op.drop_index('idx_storage_locations_is_active', table_name='storage_locations')
    op.drop_index('idx_storage_locations_code', table_name='storage_locations')
    op.drop_index('idx_storage_locations_parent_id', table_name='storage_locations')
    op.drop_table('storage_locations')


