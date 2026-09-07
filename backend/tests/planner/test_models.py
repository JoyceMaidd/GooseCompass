"""Tests for planner ORM models: constraints and cascade behavior."""

import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from backend.db import connect_postgres, disconnect_postgres, get_session
from backend.monitoring.quota import DEMO_USER_ID
from backend.planner.models import CourseMatch, ExchangePlan, HostSchool


@pytest.fixture(autouse=True)
async def db_lifecycle():
    """Connect to Postgres and clear this user's planner rows around each test."""
    await connect_postgres()
    async for session in get_session():
        await session.execute(delete(ExchangePlan).where(ExchangePlan.user_id == DEMO_USER_ID))
        await session.commit()
        break
    yield
    async for session in get_session():
        await session.execute(delete(ExchangePlan).where(ExchangePlan.user_id == DEMO_USER_ID))
        await session.commit()
        break
    await disconnect_postgres()


@pytest.mark.integration
async def test_exchange_plan_user_id_is_unique():
    """A second plan for the same user must violate the unique constraint."""
    async for session in get_session():
        session.add(ExchangePlan(user_id=DEMO_USER_ID))
        await session.commit()

        session.add(ExchangePlan(user_id=DEMO_USER_ID))
        with pytest.raises(IntegrityError):
            await session.commit()
        await session.rollback()
        break


@pytest.mark.integration
async def test_deleting_plan_cascades_to_host_schools_and_course_matches():
    """Deleting a plan must cascade-delete its host schools and course matches."""
    async for session in get_session():
        plan = ExchangePlan(user_id=DEMO_USER_ID)
        session.add(plan)
        await session.commit()
        await session.refresh(plan)

        school = HostSchool(exchange_plan_id=plan.id, school_name="ETH Zurich")
        session.add(school)
        await session.commit()
        await session.refresh(school)

        match = CourseMatch(exchange_plan_id=plan.id, host_school_id=school.id, host_course_code="252-0061-00L")
        session.add(match)
        await session.commit()

        await session.delete(plan)
        await session.commit()

        remaining_schools = (
            (await session.execute(select(HostSchool).where(HostSchool.exchange_plan_id == plan.id))).scalars().all()
        )
        remaining_matches = (
            (await session.execute(select(CourseMatch).where(CourseMatch.exchange_plan_id == plan.id)))
            .scalars()
            .all()
        )
        assert remaining_schools == []
        assert remaining_matches == []
        break
