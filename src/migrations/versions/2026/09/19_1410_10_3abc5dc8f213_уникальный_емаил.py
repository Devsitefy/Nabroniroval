"""уникальный емаил

Revision ID: 3abc5dc8f213
Revises: b1c725a61d1a
Create Date: 2026-09-19 14:10:10.715292

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3abc5dc8f213"
down_revision: Union[str, Sequence[str], None] = "b1c725a61d1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_unique_constraint(None, "users", ["email"])



def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(None, "users", type_="unique")

