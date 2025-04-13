"""Drop Categories, RequestCategories; recreate Requests

Revision ID: 160f0af0d0e4
Revises: 80e5eae1aa25
Create Date: 2025-04-13 17:03:03.885249

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "160f0af0d0e4"
down_revision: Union[str, None] = "80e5eae1aa25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    conn = op.get_bind()
    inspector = inspect(conn)

    op.drop_table("Users")

    # if "RequestCategories" in inspector.get_table_names():
    #     op.drop_table("RequestCategories")

    # if "Categories" in inspector.get_table_names():
    #     op.drop_table("Categories")

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
            "id_author", sa.Integer(), sa.ForeignKey("Users.idUsers"), nullable=False
        ),
        sa.Column("categories", sa.String(length=500)),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "Categories",
        sa.Column("idCategories", sa.Integer(), primary_key=True),
        sa.Column("category", sa.String(length=55), nullable=False),
    )

    op.create_table(
        "RequestCategories",
        sa.Column("idRequest", sa.Integer(), nullable=False),
        sa.Column("idCategory", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["idRequest"], ["Requests.idRequests"]),
        sa.ForeignKeyConstraint(["idCategory"], ["Categories.idCategories"]),
        sa.PrimaryKeyConstraint("idRequest", "idCategory"),
    )

    op.drop_table("Requests")
