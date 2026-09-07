"""Tests for the phase-tracking agent.

Integration tests: require Postgres connectivity and a live OpenRouter API key.
"""

import pytest
from sqlalchemy import delete

from backend.config import settings
from backend.db import connect, connect_postgres, disconnect, disconnect_postgres, get_database, get_session
from backend.monitoring.quota import DEMO_USER_ID
from backend.planner import service
from backend.planner.agents.deps import PlannerDeps
from backend.planner.agents.models import PhaseTrackingUpdate
from backend.planner.agents.phase_tracking_agent import phase_tracking_agent
from backend.planner.models import ExchangePlan, PlannerPhase
from backend.planner.schemas import CourseMatchCreate, ExchangePlanUpdate, HostSchoolCreate


@pytest.fixture(autouse=True)
async def db_connection():
    """Connect Mongo and Postgres, and clear this user's planner rows around each test."""
    await connect()
    await connect_postgres()
    async for session in get_session():
        await session.execute(delete(ExchangePlan).where(ExchangePlan.user_id == DEMO_USER_ID))
        await session.commit()
        break
    yield
    await disconnect_postgres()
    await disconnect()


async def _build_deps_with_seeded_plan() -> PlannerDeps:
    """Build real PlannerDeps for the demo user, with a seeded plan in progress."""
    db = get_database()
    collection = db[settings.mongodb_collection_chunks]
    async for session in get_session():
        plan = await service.get_or_create_plan(session, DEMO_USER_ID)
        plan = await service.update_plan(session, plan, ExchangePlanUpdate(current_phase=PlannerPhase.APPLYING))

        school = await service.create_host_school(session, plan.id, HostSchoolCreate(school_name="ETH Zurich"))
        await service.create_course_match(
            session, plan.id, CourseMatchCreate(host_school_id=school.id, host_course_code="252-0061-00L")
        )

        return PlannerDeps(
            session=session, user_id=DEMO_USER_ID, exchange_plan_id=plan.id, chunks_collection=collection
        )
    raise RuntimeError("get_session yielded no session")


@pytest.mark.integration
async def test_phase_tracking_agent_grounds_recommendation_in_plan_state():
    """The agent must return a sensible, grounded PhaseTrackingUpdate for a seeded plan."""
    deps = await _build_deps_with_seeded_plan()
    result = await phase_tracking_agent.run("What should I do next in my exchange planning?", deps=deps)
    output = result.output

    assert isinstance(output, PhaseTrackingUpdate)
    assert isinstance(output.current_phase, PlannerPhase)
    assert len(output.recommended_next_steps) >= 1
    assert all(step.strip() != "" for step in output.recommended_next_steps)
    assert output.rationale.strip() != ""
