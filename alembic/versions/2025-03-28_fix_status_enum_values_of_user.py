"""fix status_enum values of user

Revision ID: ccd8d0394a61
Revises: be7472cdfb11
Create Date: 2025-03-28 15:43:57.413369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccd8d0394a61'
down_revision: Union[str, None] = 'be7472cdfb11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE status_enum ADD VALUE IF NOT EXISTS 'active'")
    op.execute("ALTER TYPE status_enum ADD VALUE IF NOT EXISTS 'offline'")
    op.execute("ALTER TYPE status_enum ADD VALUE IF NOT EXISTS 'do_not_disturb'")


def downgrade() -> None:
    pass
