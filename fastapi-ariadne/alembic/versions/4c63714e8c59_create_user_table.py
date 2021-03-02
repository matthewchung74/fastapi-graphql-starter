"""create user table

Revision ID: 52806f8c65f9
Revises: 
Create Date: 2021-03-01 14:51:29.349974

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.sql.expression import func

# revision identifiers, used by Alembic.
revision = '4c63714e8c59'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, unique=True),
        sa.Column("email", sa.String(200), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(100), nullable=False),
        sa.Column("created_date", sa.DateTime, nullable=False, server_default=func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_email"), "users", ["email"], unique=True)

    op.create_table(
        "items",
        sa.Column("id", sa.Integer, primary_key=True, unique=True),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("owner_id", sa.Integer, nullable=False),
        sa.Column("created_date", sa.DateTime, nullable=False, server_default=func.now()),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"],),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_item_description"), "items", ["description"], unique=False)
    op.create_index(op.f("ix_item_title"), "items", ["title"], unique=False)

def downgrade():
    op.drop_index(op.f("ix_item_title"), table_name="items")
    op.drop_index(op.f("ix_item_description"), table_name="items")
    op.drop_table("items")
    op.drop_index(op.f("ix_user_email"), table_name="users")
    op.drop_table("users")
