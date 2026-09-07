"""Create planner tables: exchange_plans, host_schools, course_matches

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-07

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "exchange_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("current_phase", sa.String(), nullable=False, server_default="researching"),
        sa.Column("target_term", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_exchange_plans_user_id", "exchange_plans", ["user_id"], unique=True)

    op.create_table(
        "host_schools",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exchange_plan_id", sa.Integer(), nullable=False),
        sa.Column("school_name", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("program_url", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="researching"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["exchange_plan_id"], ["exchange_plans.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_host_schools_exchange_plan_id", "host_schools", ["exchange_plan_id"])

    op.create_table(
        "course_matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exchange_plan_id", sa.Integer(), nullable=False),
        sa.Column("host_school_id", sa.Integer(), nullable=False),
        sa.Column("uwaterloo_course_code", sa.String(), nullable=True),
        sa.Column("uwaterloo_course_title", sa.String(), nullable=True),
        sa.Column("host_course_code", sa.String(), nullable=False),
        sa.Column("host_course_title", sa.String(), nullable=True),
        sa.Column("credits", sa.Float(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="researching"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["exchange_plan_id"], ["exchange_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["host_school_id"], ["host_schools.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_course_matches_exchange_plan_id", "course_matches", ["exchange_plan_id"])
    op.create_index("ix_course_matches_host_school_id", "course_matches", ["host_school_id"])


def downgrade() -> None:
    op.drop_index("ix_course_matches_host_school_id", table_name="course_matches")
    op.drop_index("ix_course_matches_exchange_plan_id", table_name="course_matches")
    op.drop_table("course_matches")
    op.drop_index("ix_host_schools_exchange_plan_id", table_name="host_schools")
    op.drop_table("host_schools")
    op.drop_index("ix_exchange_plans_user_id", table_name="exchange_plans")
    op.drop_table("exchange_plans")
