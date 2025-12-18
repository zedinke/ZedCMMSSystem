"""Add fault_cause to worksheets and anonymized fields to users

Revision ID: cc7308902ed0
Revises: c6d436d3133d
Create Date: 2025-12-13 21:25:53.582109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc7308902ed0'
down_revision: Union[str, Sequence[str], None] = 'c6d436d3133d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite doesn't support ALTER TABLE for constraints, so we only add columns
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('anonymized_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('anonymized_by_user_id', sa.Integer(), nullable=True))
        # Note: email nullable change skipped for SQLite compatibility
    
    with op.batch_alter_table('worksheets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fault_cause', sa.Text(), nullable=True))
    
    # Note: Other constraints and indexes are skipped for SQLite compatibility
    # They should be handled in the model definitions or separate migrations


def downgrade() -> None:
    """Downgrade schema."""
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('worksheets', schema=None) as batch_op:
        batch_op.drop_column('fault_cause')
    
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('anonymized_by_user_id')
        batch_op.drop_column('anonymized_at')
