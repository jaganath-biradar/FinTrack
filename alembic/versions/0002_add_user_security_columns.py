"""add user security columns

Revision ID: 0002_add_user_security_columns
Revises: 0001_initial
Create Date: 2026-06-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_user_security_columns"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("verification_token", sa.String(length=128), nullable=True))
    op.add_column("users", sa.Column("reset_token", sa.String(length=128), nullable=True))
    op.add_column("users", sa.Column("reset_token_expires", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("users", "reset_token_expires")
    op.drop_column("users", "reset_token")
    op.drop_column("users", "verification_token")
    op.drop_column("users", "is_verified")
