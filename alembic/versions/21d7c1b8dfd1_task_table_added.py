"""Task table added

Revision ID: 21d7c1b8dfd1
Revises: 70f67c4c33f6
Create Date: 2025-04-27 00:17:05.214561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21d7c1b8dfd1'
down_revision: Union[str, None] = '70f67c4c33f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
