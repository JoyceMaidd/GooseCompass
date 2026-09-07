"""Tests for the host-school research agent.

Integration tests: require Atlas indexes (vector_index, text_index) to be
Active, the chunks collection populated, and a live OpenRouter API key.
"""

import pytest

from backend.config import settings
from backend.db import connect, connect_postgres, disconnect, disconnect_postgres, get_database, get_session
from backend.monitoring.quota import DEMO_USER_ID
from backend.planner import service
from backend.planner.agents.deps import PlannerDeps
from backend.planner.agents.host_school_agent import host_school_agent
from backend.planner.agents.models import HostSchoolResearchResult


@pytest.fixture(autouse=True)
async def db_connection():
    """Connect Mongo and Postgres for each test."""
    await connect()
    await connect_postgres()
    yield
    await disconnect_postgres()
    await disconnect()


async def _build_deps() -> PlannerDeps:
    """Build real PlannerDeps for the current demo user."""
    db = get_database()
    collection = db[settings.mongodb_collection_chunks]
    async for session in get_session():
        plan = await service.get_or_create_plan(session, DEMO_USER_ID)
        return PlannerDeps(
            session=session, user_id=DEMO_USER_ID, exchange_plan_id=plan.id, chunks_collection=collection
        )
    raise RuntimeError("get_session yielded no session")


@pytest.mark.integration
async def test_host_school_agent_grounds_findings_in_retrieval():
    """A real, in-corpus question must yield grounded (or honestly empty) findings."""
    deps = await _build_deps()
    result = await host_school_agent.run(
        "What exchange programs or host schools does UWaterloo have information about?", deps=deps
    )
    output = result.output
    assert isinstance(output, HostSchoolResearchResult)
    # Never claim sufficient context while returning nothing to back it up.
    assert output.insufficient_context or len(output.findings) > 0
    for finding in output.findings:
        assert finding.summary.strip() != ""


@pytest.mark.integration
async def test_host_school_agent_flags_insufficient_context_for_out_of_corpus_question():
    """A question unrelated to the institutional corpus must be flagged honestly."""
    deps = await _build_deps()
    result = await host_school_agent.run(
        "What is the boiling point of liquid nitrogen at standard atmospheric pressure?", deps=deps
    )
    output = result.output
    assert isinstance(output, HostSchoolResearchResult)
    assert output.insufficient_context is True
    assert output.findings == []
