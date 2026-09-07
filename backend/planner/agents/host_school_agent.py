"""PydanticAI specialist agent: host-school research, grounded via retrieval."""

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from backend.config import settings
from backend.planner.agents.deps import PlannerDeps
from backend.planner.agents.models import HostSchoolResearchResult
from backend.planner.retrieval_tool import research_lookup
from backend.retrieval.models import SearchResult

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

_SYSTEM_PROMPT = (
    "You help a University of Waterloo exchange student research host schools. "
    "Always call research_lookup_tool before answering, using a focused search "
    "query derived from the student's question. Only state facts it returned — "
    "never invent institutional facts from your own knowledge. If it returns "
    "nothing relevant to the question, set insufficient_context=True and leave "
    "findings empty rather than guessing."
)


def _make_agent() -> Agent[PlannerDeps, HostSchoolResearchResult]:
    """Build the host-school research agent pointed at OpenRouter.

    Returns:
        A configured Agent that returns HostSchoolResearchResult instances.
    """
    provider = OpenAIProvider(base_url=_OPENROUTER_BASE_URL, api_key=settings.openrouter_api_key)
    model = OpenAIChatModel(model_name=settings.openrouter_planner_model, provider=provider)
    return Agent(
        model,
        deps_type=PlannerDeps,
        output_type=HostSchoolResearchResult,
        retries=3,
        system_prompt=_SYSTEM_PROMPT,
    )


host_school_agent = _make_agent()


@host_school_agent.tool
async def research_lookup_tool(ctx: RunContext[PlannerDeps], query: str) -> list[SearchResult]:
    """Search institutional documents for host-school/program information.

    Args:
        ctx: Run context carrying PlannerDeps.
        query: Natural-language research query.

    Returns:
        Retrieved chunks relevant to the query.
    """
    return await research_lookup(query, ctx.deps.chunks_collection)
