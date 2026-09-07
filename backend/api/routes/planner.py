"""CRUD routes for the exchange planner: plan, host schools, course matches."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_session
from backend.planner import service
from backend.planner.deps import get_current_user_id
from backend.planner.schemas import (
    CourseMatchCreate,
    CourseMatchRead,
    CourseMatchUpdate,
    ExchangePlanRead,
    ExchangePlanUpdate,
    HostSchoolCreate,
    HostSchoolRead,
    HostSchoolUpdate,
)

router = APIRouter(prefix="/planner")


@router.get("/plan", response_model=ExchangePlanRead)
async def get_plan(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> ExchangePlanRead:
    """Get the current user's exchange plan, creating one if it doesn't exist."""
    return await service.get_or_create_plan(session, user_id)


@router.patch("/plan", response_model=ExchangePlanRead)
async def patch_plan(
    update: ExchangePlanUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> ExchangePlanRead:
    """Manually edit the current user's exchange plan."""
    plan = await service.get_or_create_plan(session, user_id)
    return await service.update_plan(session, plan, update)


@router.get("/host-schools", response_model=list[HostSchoolRead])
async def list_host_schools(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> list[HostSchoolRead]:
    """List the current user's host schools."""
    plan = await service.get_or_create_plan(session, user_id)
    return await service.list_host_schools(session, plan.id)


@router.post("/host-schools", response_model=HostSchoolRead, status_code=201)
async def create_host_school(
    data: HostSchoolCreate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> HostSchoolRead:
    """Add a host school to the current user's plan."""
    plan = await service.get_or_create_plan(session, user_id)
    return await service.create_host_school(session, plan.id, data)


@router.get("/host-schools/{school_id}", response_model=HostSchoolRead)
async def get_host_school(
    school_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> HostSchoolRead:
    """Get one host school owned by the current user."""
    plan = await service.get_or_create_plan(session, user_id)
    school = await service.get_host_school(session, plan.id, school_id)
    if school is None:
        raise HTTPException(status_code=404, detail="Host school not found.")
    return school


@router.patch("/host-schools/{school_id}", response_model=HostSchoolRead)
async def patch_host_school(
    school_id: int,
    update: HostSchoolUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> HostSchoolRead:
    """Edit a host school owned by the current user."""
    plan = await service.get_or_create_plan(session, user_id)
    school = await service.get_host_school(session, plan.id, school_id)
    if school is None:
        raise HTTPException(status_code=404, detail="Host school not found.")
    return await service.update_host_school(session, school, update)


@router.delete("/host-schools/{school_id}", status_code=204)
async def delete_host_school(
    school_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> None:
    """Delete a host school owned by the current user."""
    plan = await service.get_or_create_plan(session, user_id)
    school = await service.get_host_school(session, plan.id, school_id)
    if school is None:
        raise HTTPException(status_code=404, detail="Host school not found.")
    await service.delete_host_school(session, school)


@router.get("/course-matches", response_model=list[CourseMatchRead])
async def list_course_matches(
    host_school_id: int | None = None,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> list[CourseMatchRead]:
    """List the current user's course matches, optionally filtered by host school."""
    plan = await service.get_or_create_plan(session, user_id)
    return await service.list_course_matches(session, plan.id, host_school_id)


@router.post("/course-matches", response_model=CourseMatchRead, status_code=201)
async def create_course_match(
    data: CourseMatchCreate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> CourseMatchRead:
    """Add a course match to the current user's plan."""
    plan = await service.get_or_create_plan(session, user_id)
    school = await service.get_host_school(session, plan.id, data.host_school_id)
    if school is None:
        raise HTTPException(status_code=404, detail="Host school not found.")
    return await service.create_course_match(session, plan.id, data)


@router.patch("/course-matches/{match_id}", response_model=CourseMatchRead)
async def patch_course_match(
    match_id: int,
    update: CourseMatchUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> CourseMatchRead:
    """Edit a course match owned by the current user."""
    plan = await service.get_or_create_plan(session, user_id)
    match = await service.get_course_match(session, plan.id, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Course match not found.")
    return await service.update_course_match(session, match, update)


@router.delete("/course-matches/{match_id}", status_code=204)
async def delete_course_match(
    match_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
) -> None:
    """Delete a course match owned by the current user."""
    plan = await service.get_or_create_plan(session, user_id)
    match = await service.get_course_match(session, plan.id, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Course match not found.")
    await service.delete_course_match(session, match)
