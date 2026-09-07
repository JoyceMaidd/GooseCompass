"""Tests for planner CRUD service functions."""

import pytest
from sqlalchemy import delete

from backend.db import connect_postgres, disconnect_postgres, get_session
from backend.monitoring.quota import DEMO_USER_ID
from backend.planner import service
from backend.planner.models import ExchangePlan
from backend.planner.schemas import (
    CourseMatchCreate,
    CourseMatchUpdate,
    ExchangePlanUpdate,
    HostSchoolCreate,
    HostSchoolUpdate,
)


@pytest.fixture(autouse=True)
async def db_lifecycle():
    """Connect to Postgres and clear this user's planner rows around each test."""
    await connect_postgres()
    async for session in get_session():
        await session.execute(delete(ExchangePlan).where(ExchangePlan.user_id == DEMO_USER_ID))
        await session.commit()
        break
    yield
    await disconnect_postgres()


@pytest.mark.integration
async def test_get_or_create_plan_is_idempotent():
    """Calling get_or_create_plan twice must return the same plan row."""
    async for session in get_session():
        first = await service.get_or_create_plan(session, DEMO_USER_ID)
        second = await service.get_or_create_plan(session, DEMO_USER_ID)
        assert first.id == second.id
        break


@pytest.mark.integration
async def test_update_plan_applies_only_given_fields():
    """update_plan must leave unset fields untouched."""
    async for session in get_session():
        plan = await service.get_or_create_plan(session, DEMO_USER_ID)
        updated = await service.update_plan(session, plan, ExchangePlanUpdate(target_term="Fall 2027"))
        assert updated.target_term == "Fall 2027"
        assert updated.current_phase == plan.current_phase
        break


@pytest.mark.integration
async def test_host_school_crud_round_trip():
    """Create, fetch, update, and delete a host school."""
    async for session in get_session():
        plan = await service.get_or_create_plan(session, DEMO_USER_ID)

        created = await service.create_host_school(
            session, plan.id, HostSchoolCreate(school_name="ETH Zurich", country="Switzerland")
        )
        assert created.school_name == "ETH Zurich"

        fetched = await service.get_host_school(session, plan.id, created.id)
        assert fetched is not None
        assert fetched.id == created.id

        missing = await service.get_host_school(session, plan.id + 999, created.id)
        assert missing is None

        updated = await service.update_host_school(session, created, HostSchoolUpdate(country="CH"))
        assert updated.country == "CH"

        schools = await service.list_host_schools(session, plan.id)
        assert any(s.id == created.id for s in schools)

        await service.delete_host_school(session, updated)
        schools_after = await service.list_host_schools(session, plan.id)
        assert all(s.id != created.id for s in schools_after)
        break


@pytest.mark.integration
async def test_course_match_crud_round_trip():
    """Create, fetch, update, and delete a course match."""
    async for session in get_session():
        plan = await service.get_or_create_plan(session, DEMO_USER_ID)
        school = await service.create_host_school(session, plan.id, HostSchoolCreate(school_name="ETH Zurich"))

        created = await service.create_course_match(
            session,
            plan.id,
            CourseMatchCreate(host_school_id=school.id, host_course_code="252-0061-00L"),
        )
        assert created.host_course_code == "252-0061-00L"

        matches = await service.list_course_matches(session, plan.id, host_school_id=school.id)
        assert any(m.id == created.id for m in matches)

        updated = await service.update_course_match(
            session, created, CourseMatchUpdate(uwaterloo_course_code="CS 341")
        )
        assert updated.uwaterloo_course_code == "CS 341"

        await service.delete_course_match(session, updated)
        matches_after = await service.list_course_matches(session, plan.id, host_school_id=school.id)
        assert all(m.id != created.id for m in matches_after)
        break
