"""Tests for the planner coordinator agent.

Integration tests: require Atlas indexes, populated chunks collection,
Postgres connectivity, and a live OpenRouter API key.
"""

import pytest
from sqlalchemy import delete

from backend.config import settings
from backend.db import connect, connect_postgres, disconnect, disconnect_postgres, get_database, get_session
from backend.monitoring.quota import DEMO_USER_ID
from backend.planner import service
from backend.planner.agents.coordinator import coordinator_agent, run_planner_assistant
from backend.planner.agents.deps import PlannerDeps
from backend.planner.agents.models import PlannerAssistantReply
from backend.planner.models import ExchangePlan, PlannerPhase
from backend.planner.schemas import ExchangePlanUpdate


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


async def _build_deps() -> PlannerDeps:
    """Build real PlannerDeps for the demo user, with a seeded plan in progress."""
    db = get_database()
    collection = db[settings.mongodb_collection_chunks]
    async for session in get_session():
        plan = await service.get_or_create_plan(session, DEMO_USER_ID)
        plan = await service.update_plan(session, plan, ExchangePlanUpdate(current_phase=PlannerPhase.APPLYING))
        return PlannerDeps(
            session=session, user_id=DEMO_USER_ID, exchange_plan_id=plan.id, chunks_collection=collection
        )
    raise RuntimeError("get_session yielded no session")


def _delegated_tool_names(result) -> set[str]:
    """Extract the names of tools invoked during an agent run, from its message history.

    Args:
        result: An AgentRunResult from Agent.run().

    Returns:
        The set of tool names called during the run.
    """
    names: set[str] = set()
    for message in result.all_messages():
        for part in getattr(message, "parts", []):
            tool_name = getattr(part, "tool_name", None)
            if tool_name is not None:
                names.add(tool_name)
    return names


@pytest.mark.integration
async def test_coordinator_delegates_to_phase_tracking_for_progress_question():
    """A phase/progress question must actually invoke the track_phase delegated tool."""
    deps = await _build_deps()
    result = await coordinator_agent.run("What phase am I in and what should I do next?", deps=deps)
    assert "track_phase" in _delegated_tool_names(result)
    assert isinstance(result.output, PlannerAssistantReply)


@pytest.mark.integration
async def test_coordinator_delegates_to_host_school_research_for_research_question():
    """A host-school research question must actually invoke the research_host_schools delegated tool."""
    deps = await _build_deps()
    result = await coordinator_agent.run(
        "What exchange programs or host schools does UWaterloo have information about?", deps=deps
    )
    assert "research_host_schools" in _delegated_tool_names(result)
    assert isinstance(result.output, PlannerAssistantReply)


@pytest.mark.integration
async def test_run_planner_assistant_returns_aggregated_usage():
    """run_planner_assistant must return a reply plus positive aggregated token usage.

    Usage must aggregate across the delegated specialist call (ctx.usage
    threaded through), not just the coordinator's own top-level completion.
    """
    deps = await _build_deps()
    reply, input_tokens, output_tokens = await run_planner_assistant(
        "What phase am I in and what should I do next?", deps
    )
    assert isinstance(reply, PlannerAssistantReply)
    assert reply.message.strip() != ""
    assert isinstance(input_tokens, int) and input_tokens > 0
    assert isinstance(output_tokens, int) and output_tokens > 0
