"""Create users and usage_logs tables with seeded demo user

Revision ID: 0001
Revises:
Create Date: 2026-08-20

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.bulk_insert(
        sa.table("users", sa.column("id"), sa.column("email")),
        [{"id": 1, "email": "demo@uwaterloo.ca"}],
    )

    op.create_table(
        "usage_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tokens_used", sa.Integer(), nullable=False),
        sa.Column("cost_usd", sa.Float(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
    )
    op.create_index("ix_usage_logs_user_id_created_at", "usage_logs", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_usage_logs_user_id_created_at", table_name="usage_logs")
    op.drop_table("usage_logs")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
