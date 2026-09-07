"""Pydantic request/response schemas for the exchange planner API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.planner.models import CourseMatchStatus, HostSchoolStatus, PlannerPhase


class ExchangePlanRead(BaseModel):
    """Serialized exchange plan."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    current_phase: PlannerPhase
    target_term: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ExchangePlanUpdate(BaseModel):
    """Fields a student can manually edit on their plan."""

    current_phase: PlannerPhase | None = None
    target_term: str | None = None
    notes: str | None = None


class HostSchoolRead(BaseModel):
    """Serialized host school."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    exchange_plan_id: int
    school_name: str
    country: str | None
    program_url: str | None
    status: HostSchoolStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime


class HostSchoolCreate(BaseModel):
    """Fields required to add a host school to a plan."""

    school_name: str
    country: str | None = None
    program_url: str | None = None
    status: HostSchoolStatus = HostSchoolStatus.RESEARCHING
    notes: str | None = None


class HostSchoolUpdate(BaseModel):
    """Fields a student can manually edit on a host school."""

    school_name: str | None = None
    country: str | None = None
    program_url: str | None = None
    status: HostSchoolStatus | None = None
    notes: str | None = None


class CourseMatchRead(BaseModel):
    """Serialized course match."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    exchange_plan_id: int
    host_school_id: int
    uwaterloo_course_code: str | None
    uwaterloo_course_title: str | None
    host_course_code: str
    host_course_title: str | None
    credits: float | None
    status: CourseMatchStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime


class CourseMatchCreate(BaseModel):
    """Fields required to add a course match to a plan."""

    host_school_id: int
    uwaterloo_course_code: str | None = None
    uwaterloo_course_title: str | None = None
    host_course_code: str
    host_course_title: str | None = None
    credits: float | None = None
    status: CourseMatchStatus = CourseMatchStatus.RESEARCHING
    notes: str | None = None


class CourseMatchUpdate(BaseModel):
    """Fields a student can manually edit on a course match."""

    uwaterloo_course_code: str | None = None
    uwaterloo_course_title: str | None = None
    host_course_code: str | None = None
    host_course_title: str | None = None
    credits: float | None = None
    status: CourseMatchStatus | None = None
    notes: str | None = None
