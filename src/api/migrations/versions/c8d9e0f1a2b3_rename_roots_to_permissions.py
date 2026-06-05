"""rename roots to permissions

Revision ID: c8d9e0f1a2b3
Revises: db3f4a6aa279
Create Date: 2026-06-03 08:45:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c8d9e0f1a2b3"
down_revision: Union[str, Sequence[str], None] = "db3f4a6aa279"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename table roots to permissions
    op.rename_table("roots", "permissions")

    # Rename column root_id to permission_id in jobs table
    op.alter_column("jobs", "root_id", new_column_name="permission_id")


def downgrade() -> None:
    """Downgrade schema."""
    # Rename column permission_id back to root_id in jobs table
    op.alter_column("jobs", "permission_id", new_column_name="root_id")

    # Rename table permissions back to roots
    op.rename_table("permissions", "roots")
