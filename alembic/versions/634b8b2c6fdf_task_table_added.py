"""Task table added

Revision ID: 634b8b2c6fdf
Revises: 21d7c1b8dfd1
Create Date: 2025-04-27 00:18:34.553254

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '634b8b2c6fdf'
down_revision: Union[str, None] = '21d7c1b8dfd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tasks',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('owner_id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('details', sa.String(), nullable=False),
    sa.Column('team_members', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('time', sa.String(), nullable=False),
    sa.Column('date', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')
    # ### end Alembic commands ###
