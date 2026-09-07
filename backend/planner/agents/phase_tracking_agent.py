"""PydanticAI specialist agent: phase tracking, grounded in the student's own plan."""

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from backend.config import settings
from backend.planner import service
from backend.planner.agents.deps import PlannerDeps
from backend.planner.agents.models import PhaseTrackingUpdate, PlanSnapshot

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

_SYSTEM_PROMPT = (
    "You help a University of Waterloo exchange student track their exchange "
    "planning progress. Always call get_plan_snapshot_tool before answering, "
    "so your recommendation reflects their actual recorded host schools and "
    "course matches rather than assumptions. Recommend the phase that best "
    "matches their recorded progress, with concrete next steps grounded in "
    "what the snapshot shows — never invent facts about their plan."
)


def _make_agent() -> Agent[PlannerDeps, PhaseTrackingUpdate]:
    """Build the phase-tracking agent pointed at OpenRouter.

    Returns:
        A configured Agent that returns PhaseTrackingUpdate instances.
    """
    provider = OpenAIProvider(base_url=_OPENROUTER_BASE_URL, api_key=settings.openrouter_api_key)
    model = OpenAIChatModel(model_name=settings.openrouter_planner_model, provider=provider)
    return Agent(
        model,
        deps_type=PlannerDeps,
        output_type=PhaseTrackingUpdate,
        retries=3,
        system_prompt=_SYSTEM_PROMPT,
    )


phase_tracking_agent = _make_agent()


@phase_tracking_agent.tool
async def get_plan_snapshot_tool(ctx: RunContext[PlannerDeps]) -> PlanSnapshot:
    """Read the current user's recorded plan phase, host schools, and course matches.

    Args:
        ctx: Run context carrying PlannerDeps.

    Returns:
        A snapshot of the student's plan state.
    """
    return await service.get_plan_snapshot(ctx.deps.session, ctx.deps.exchange_plan_id)
