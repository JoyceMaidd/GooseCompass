"""CRUD and query functions for planner data, scoped to a user's exchange plan."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.planner.models import CourseMatch, ExchangePlan, HostSchool
from backend.planner.schemas import (
    CourseMatchCreate,
    CourseMatchUpdate,
    ExchangePlanUpdate,
    HostSchoolCreate,
    HostSchoolUpdate,
)


async def get_or_create_plan(session: AsyncSession, user_id: int) -> ExchangePlan:
    """Return the user's exchange plan, creating one if it doesn't exist yet.

    Args:
        session: Postgres async session.
        user_id: The current user's ID.

    Returns:
        The user's ExchangePlan row.
    """
    stmt = select(ExchangePlan).where(ExchangePlan.user_id == user_id)
    plan = (await session.execute(stmt)).scalar_one_or_none()
    if plan is not None:
        return plan

    plan = ExchangePlan(user_id=user_id)
    session.add(plan)
    await session.commit()
    await session.refresh(plan)
    return plan


async def update_plan(session: AsyncSession, plan: ExchangePlan, update: ExchangePlanUpdate) -> ExchangePlan:
    """Apply manual edits to an exchange plan.

    Args:
        session: Postgres async session.
        plan: The plan to update.
        update: Fields to change (unset fields are left as-is).

    Returns:
        The updated ExchangePlan row.
    """
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    await session.commit()
    await session.refresh(plan)
    return plan


async def list_host_schools(session: AsyncSession, plan_id: int) -> list[HostSchool]:
    """List all host schools in a plan.

    Args:
        session: Postgres async session.
        plan_id: The owning exchange plan's ID.

    Returns:
        Host schools belonging to the plan.
    """
    stmt = select(HostSchool).where(HostSchool.exchange_plan_id == plan_id)
    return list((await session.execute(stmt)).scalars().all())


async def create_host_school(session: AsyncSession, plan_id: int, data: HostSchoolCreate) -> HostSchool:
    """Add a host school to a plan.

    Args:
        session: Postgres async session.
        plan_id: The owning exchange plan's ID.
        data: New host school fields.

    Returns:
        The created HostSchool row.
    """
    school = HostSchool(exchange_plan_id=plan_id, **data.model_dump())
    session.add(school)
    await session.commit()
    await session.refresh(school)
    return school


async def get_host_school(session: AsyncSession, plan_id: int, school_id: int) -> HostSchool | None:
    """Fetch a host school scoped to its owning plan.

    Args:
        session: Postgres async session.
        plan_id: The owning exchange plan's ID.
        school_id: The host school's ID.

    Returns:
        The HostSchool row, or None if it doesn't exist or belongs to another plan.
    """
    stmt = select(HostSchool).where(HostSchool.id == school_id, HostSchool.exchange_plan_id == plan_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def update_host_school(session: AsyncSession, school: HostSchool, update: HostSchoolUpdate) -> HostSchool:
    """Apply manual edits to a host school.

    Args:
        session: Postgres async session.
        school: The host school to update.
        update: Fields to change (unset fields are left as-is).

    Returns:
        The updated HostSchool row.
    """
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(school, field, value)
    await session.commit()
    await session.refresh(school)
    return school


async def delete_host_school(session: AsyncSession, school: HostSchool) -> None:
    """Delete a host school (cascades to its course matches).

    Args:
        session: Postgres async session.
        school: The host school to delete.

    Returns:
        None
    """
    await session.delete(school)
    await session.commit()


async def list_course_matches(
    session: AsyncSession, plan_id: int, host_school_id: int | None = None
) -> list[CourseMatch]:
    """List course matches in a plan, optionally filtered by host school.

    Args:
        session: Postgres async session.
        plan_id: The owning exchange plan's ID.
        host_school_id: If given, only return matches for this host school.

    Returns:
        Course matches belonging to the plan.
    """
    stmt = select(CourseMatch).where(CourseMatch.exchange_plan_id == plan_id)
    if host_school_id is not None:
        stmt = stmt.where(CourseMatch.host_school_id == host_school_id)
    return list((await session.execute(stmt)).scalars().all())


async def create_course_match(session: AsyncSession, plan_id: int, data: CourseMatchCreate) -> CourseMatch:
    """Add a course match to a plan.

    Args:
        session: Postgres async session.
        plan_id: The owning exchange plan's ID.
        data: New course match fields.

    Returns:
        The created CourseMatch row.
    """
    match = CourseMatch(exchange_plan_id=plan_id, **data.model_dump())
    session.add(match)
    await session.commit()
    await session.refresh(match)
    return match


async def get_course_match(session: AsyncSession, plan_id: int, match_id: int) -> CourseMatch | None:
    """Fetch a course match scoped to its owning plan.

    Args:
        session: Postgres async session.
        plan_id: The owning exchange plan's ID.
        match_id: The course match's ID.

    Returns:
        The CourseMatch row, or None if it doesn't exist or belongs to another plan.
    """
    stmt = select(CourseMatch).where(CourseMatch.id == match_id, CourseMatch.exchange_plan_id == plan_id)
    return (await session.execute(stmt)).scalar_one_or_none()


async def update_course_match(session: AsyncSession, match: CourseMatch, update: CourseMatchUpdate) -> CourseMatch:
    """Apply manual edits to a course match.

    Args:
        session: Postgres async session.
        match: The course match to update.
        update: Fields to change (unset fields are left as-is).

    Returns:
        The updated CourseMatch row.
    """
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(match, field, value)
    await session.commit()
    await session.refresh(match)
    return match


async def delete_course_match(session: AsyncSession, match: CourseMatch) -> None:
    """Delete a course match.

    Args:
        session: Postgres async session.
        match: The course match to delete.

    Returns:
        None
    """
    await session.delete(match)
    await session.commit()
