"""Tests for the planner CRUD routes: /planner/plan, /planner/host-schools, /planner/course-matches."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

import backend.db
from backend.api.app import app
from backend.db import connect, connect_postgres, disconnect, disconnect_postgres
from backend.monitoring.quota import DEMO_USER_ID
from backend.planner.models import ExchangePlan


@pytest.fixture(autouse=True)
async def db_connection():
    """Set up database connections and clear planner rows for each test."""
    await connect()
    await connect_postgres()

    sessionmaker = backend.db._pg_sessionmaker
    if sessionmaker is not None:
        async with sessionmaker() as session:
            # Deleting the plan cascades to its host schools and course matches.
            await session.execute(delete(ExchangePlan).where(ExchangePlan.user_id == DEMO_USER_ID))
            await session.commit()

    yield

    try:
        await disconnect_postgres()
    except Exception:
        pass
    try:
        await disconnect()
    except Exception:
        pass


@pytest.mark.asyncio
async def test_get_plan_creates_one_if_missing():
    """GET /planner/plan must get-or-create a plan for the current user."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/planner/plan")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == DEMO_USER_ID
    assert body["current_phase"] == "researching"


@pytest.mark.asyncio
async def test_patch_plan_updates_fields():
    """PATCH /planner/plan must persist manual edits."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch("/planner/plan", json={"target_term": "Fall 2027"})
    assert response.status_code == 200
    assert response.json()["target_term"] == "Fall 2027"


@pytest.mark.asyncio
async def test_host_school_and_course_match_round_trip():
    """POST/GET/PATCH/DELETE round-trip for host schools and course matches."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/planner/host-schools", json={"school_name": "ETH Zurich", "country": "Switzerland"}
        )
        assert create_resp.status_code == 201
        school_id = create_resp.json()["id"]

        list_resp = await client.get("/planner/host-schools")
        assert any(s["id"] == school_id for s in list_resp.json())

        patch_resp = await client.patch(f"/planner/host-schools/{school_id}", json={"status": "shortlisted"})
        assert patch_resp.json()["status"] == "shortlisted"

        match_resp = await client.post(
            "/planner/course-matches",
            json={"host_school_id": school_id, "host_course_code": "252-0061-00L"},
        )
        assert match_resp.status_code == 201
        match_id = match_resp.json()["id"]

        matches_resp = await client.get("/planner/course-matches", params={"host_school_id": school_id})
        assert any(m["id"] == match_id for m in matches_resp.json())

        delete_match_resp = await client.delete(f"/planner/course-matches/{match_id}")
        assert delete_match_resp.status_code == 204

        delete_school_resp = await client.delete(f"/planner/host-schools/{school_id}")
        assert delete_school_resp.status_code == 204


@pytest.mark.asyncio
async def test_get_host_school_404_for_unknown_id():
    """GET /planner/host-schools/{id} must 404 for a nonexistent school."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/planner/host-schools/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_course_match_404_for_unknown_host_school():
    """POST /planner/course-matches must 404 if the host school doesn't belong to the user's plan."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/planner/course-matches",
            json={"host_school_id": 999999, "host_course_code": "252-0061-00L"},
        )
    assert response.status_code == 404
