"""Clean recreate

Revision ID: 783a509744d3
Revises:
Create Date: 2025-04-20 19:11:05.441436

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "783a509744d3"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    inspector = inspect(op.get_bind())
    if "Users" in inspector.get_table_names():
        op.drop_table("Users")

    op.create_table(
        "Users",
        sa.Column("idUsers", sa.INTEGER(), nullable=False),
        sa.Column("name", sa.VARCHAR(length=45), nullable=False),
        sa.Column("surname", sa.VARCHAR(length=45), nullable=False),
        sa.Column("age", sa.INTEGER(), nullable=True),
        sa.Column("country", sa.VARCHAR(length=50), nullable=False),
        sa.Column("city", sa.VARCHAR(length=50), nullable=False),
        sa.Column("phone", sa.VARCHAR(length=45), nullable=True),
        sa.Column("email", sa.VARCHAR(length=100), nullable=False),
        sa.Column("description", sa.VARCHAR(length=250), nullable=True),
        sa.Column("image_path", sa.VARCHAR(length=250), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False),
        sa.Column("categories", sa.VARCHAR(length=500), nullable=True),
        sa.PrimaryKeyConstraint("idUsers"),
        sa.UniqueConstraint("email"),
    )
    inspector = inspect(op.get_bind())
    if "Requests" in inspector.get_table_names():
        op.drop_table("Requests")

    op.create_table(
        "Requests",
        sa.Column("idRequests", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=70), nullable=False),
        sa.Column("description", sa.String(length=400)),
        sa.Column("image_path", sa.String(length=255)),
        sa.Column("created_at", sa.TIMESTAMP()),
        sa.Column("state", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "id_author",
            sa.Integer(),
            sa.ForeignKey("Users.idUsers"),
            nullable=False,
        ),
        sa.Column("categories", sa.String(length=500)),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("Requests")
    op.drop_table("Users")
    # ### end Alembic commands ###
