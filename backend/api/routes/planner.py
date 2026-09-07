"""Routes for the exchange planner: CRUD for plan/host schools/course matches, plus the AI assistant."""

import time

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.db import get_database, get_session
from backend.monitoring.logging import log_usage_to_db
from backend.monitoring.quota import check_user_quota
from backend.monitoring.spend_cap import check_spend_cap
from backend.planner import service
from backend.planner.agents.coordinator import run_planner_assistant
from backend.planner.agents.deps import PlannerDeps
from backend.planner.agents.models import PlannerAssistantReply
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

# Matches openrouter_planner_model's rate (currently openai/gpt-4.1-nano, same as generation).
_PLANNER_INPUT_COST_PER_1M_USD = 0.10
_PLANNER_OUTPUT_COST_PER_1M_USD = 0.40


class PlannerAssistantRequest(BaseModel):
    """Incoming planner assistant message.

    Args:
        message: The student's natural-language question or request.
    """

    message: str


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


@router.post("/assistant", response_model=PlannerAssistantReply)
async def planner_assistant(
    request: PlannerAssistantRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(check_user_quota),
    _: None = Depends(check_spend_cap),
) -> PlannerAssistantReply:
    """Run the planner coordinator agent for a student message.

    Delegates to the host-school research and/or phase-tracking specialists
    as needed. Checks quota before generation and spend-cap before the LLM
    call, matching /query. Logs usage asynchronously at the planner model's
    cost rate.

    Args:
        request: The assistant message payload.
        background_tasks: FastAPI background task runner.
        session: Postgres async session (for quota/spend-cap/logging).
        user_id: User ID (from quota check; returned if under limit).
        _: Spend-cap check (raises if exceeded).

    Returns:
        The coordinator's synthesized reply.
    """
    start_time = time.time()
    plan = await service.get_or_create_plan(session, user_id)
    db = get_database()
    collection = db[settings.mongodb_collection_chunks]
    deps = PlannerDeps(session=session, user_id=user_id, exchange_plan_id=plan.id, chunks_collection=collection)

    reply, input_tokens, output_tokens = await run_planner_assistant(request.message, deps)

    latency_ms = int((time.time() - start_time) * 1000)
    background_tasks.add_task(
        log_usage_to_db,
        session,
        user_id,
        input_tokens,
        output_tokens,
        200,
        latency_ms,
        _PLANNER_INPUT_COST_PER_1M_USD,
        _PLANNER_OUTPUT_COST_PER_1M_USD,
    )

    return reply
