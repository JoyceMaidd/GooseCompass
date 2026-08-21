"""Idempotently seed the demo user

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-21

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute(sa.text("INSERT INTO users (id, email) VALUES (1, 'demo@uwaterloo.ca') ON CONFLICT (id) DO NOTHING"))


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM users WHERE id = 1 AND email = 'demo@uwaterloo.ca'"))
