"""SQLAlchemy ORM models for the exchange planner (Postgres)."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from backend.db import Base


class PlannerPhase(str, enum.Enum):
    """Stages of a student's exchange planning journey."""

    RESEARCHING = "researching"
    APPLYING = "applying"
    NOMINATED = "nominated"
    COURSE_MATCHING = "course_matching"
    PRE_DEPARTURE = "pre_departure"
    ON_EXCHANGE = "on_exchange"
    COMPLETED = "completed"


class HostSchoolStatus(str, enum.Enum):
    """Status of a candidate host school in a student's plan."""

    RESEARCHING = "researching"
    SHORTLISTED = "shortlisted"
    APPLIED = "applied"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CONFIRMED = "confirmed"


class CourseMatchStatus(str, enum.Enum):
    """Status of a course equivalency match."""

    RESEARCHING = "researching"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class ExchangePlan(Base):
    """A student's single exchange plan: phase tracker + top-level notes.

    Args:
        id: Primary key.
        user_id: Foreign key to users.id (unique — one plan per user).
        current_phase: The student's current stage in the exchange process.
        target_term: The term the student intends to go on exchange (free text).
        notes: Free-text plan-level notes.
        created_at: When this plan was created.
        updated_at: When this plan was last updated.
    """

    __tablename__ = "exchange_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    current_phase: Mapped[PlannerPhase] = mapped_column(
        SAEnum(PlannerPhase, native_enum=False, validate_strings=True),
        default=PlannerPhase.RESEARCHING,
        server_default=PlannerPhase.RESEARCHING.value,
    )
    target_term: Mapped[str | None] = mapped_column(String(), default=None)
    notes: Mapped[str | None] = mapped_column(Text(), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class HostSchool(Base):
    """A candidate or confirmed host institution in a student's plan.

    Args:
        id: Primary key.
        exchange_plan_id: Foreign key to exchange_plans.id.
        school_name: Name of the host institution.
        country: Country the host institution is located in.
        program_url: URL to the host institution's exchange program page.
        status: Where this school stands in the student's shortlist.
        notes: Free-text research notes.
        created_at: When this row was created.
        updated_at: When this row was last updated.
    """

    __tablename__ = "host_schools"

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_plan_id: Mapped[int] = mapped_column(ForeignKey("exchange_plans.id", ondelete="CASCADE"), index=True)
    school_name: Mapped[str] = mapped_column(String())
    country: Mapped[str | None] = mapped_column(String(), default=None)
    program_url: Mapped[str | None] = mapped_column(String(), default=None)
    status: Mapped[HostSchoolStatus] = mapped_column(
        SAEnum(HostSchoolStatus, native_enum=False, validate_strings=True),
        default=HostSchoolStatus.RESEARCHING,
        server_default=HostSchoolStatus.RESEARCHING.value,
    )
    notes: Mapped[str | None] = mapped_column(Text(), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CourseMatch(Base):
    """A UWaterloo course paired against a host-school course equivalent.

    Args:
        id: Primary key.
        exchange_plan_id: Foreign key to exchange_plans.id.
        host_school_id: Foreign key to host_schools.id.
        uwaterloo_course_code: UWaterloo course code (e.g. "CS 341").
        uwaterloo_course_title: UWaterloo course title.
        host_course_code: Host institution's course code.
        host_course_title: Host institution's course title.
        credits: Credit value of the host course.
        status: Approval status of this equivalency.
        notes: Free-text notes.
        created_at: When this row was created.
        updated_at: When this row was last updated.
    """

    __tablename__ = "course_matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_plan_id: Mapped[int] = mapped_column(ForeignKey("exchange_plans.id", ondelete="CASCADE"), index=True)
    host_school_id: Mapped[int] = mapped_column(ForeignKey("host_schools.id", ondelete="CASCADE"), index=True)
    uwaterloo_course_code: Mapped[str | None] = mapped_column(String(), default=None)
    uwaterloo_course_title: Mapped[str | None] = mapped_column(String(), default=None)
    host_course_code: Mapped[str] = mapped_column(String())
    host_course_title: Mapped[str | None] = mapped_column(String(), default=None)
    credits: Mapped[float | None] = mapped_column(default=None)
    status: Mapped[CourseMatchStatus] = mapped_column(
        SAEnum(CourseMatchStatus, native_enum=False, validate_strings=True),
        default=CourseMatchStatus.RESEARCHING,
        server_default=CourseMatchStatus.RESEARCHING.value,
    )
    notes: Mapped[str | None] = mapped_column(Text(), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
