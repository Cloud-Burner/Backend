"""Book tok

Revision ID: 5011e70402fc
Revises: 862d799bf99b
Create Date: 2025-04-26 18:03:01.053333

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5011e70402fc"
down_revision: Union[str, None] = "862d799bf99b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("bookings", sa.Column("session_token", sa.String(), nullable=False))
    op.create_index(
        op.f("ix_bookings_session_token"), "bookings", ["session_token"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_bookings_session_token"), table_name="bookings")
    op.drop_column("bookings", "session_token")
    # ### end Alembic commands ###
