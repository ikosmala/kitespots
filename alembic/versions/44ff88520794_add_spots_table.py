"""add spots table

Revision ID: 44ff88520794
Revises: 06a2ffe3c2fe
Create Date: 2023-09-04 16:11:49.033105

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "44ff88520794"
down_revision: Union[str, None] = "06a2ffe3c2fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "spots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "user_spots",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("spot_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["spot_id"], ["spots.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "spot_id"),
    )


def downgrade() -> None:
    op.drop_table("user_spots")
    op.drop_table("spots")
