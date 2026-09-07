"""PydanticAI coordinator agent: delegates to the planner's specialist agents."""

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from backend.config import settings
from backend.planner.agents.deps import PlannerDeps
from backend.planner.agents.host_school_agent import host_school_agent
from backend.planner.agents.models import HostSchoolResearchResult, PhaseTrackingUpdate, PlannerAssistantReply
from backend.planner.agents.phase_tracking_agent import phase_tracking_agent

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

_SYSTEM_PROMPT = (
    "You are the University of Waterloo exchange planner assistant. Delegate "
    "to research_host_schools and/or track_phase based on what the student is "
    "asking — call more than one if the question touches both — then "
    "synthesize their results into one helpful reply. Never answer from your "
    "own knowledge without delegating first."
)


def _make_agent() -> Agent[PlannerDeps, PlannerAssistantReply]:
    """Build the coordinator agent pointed at OpenRouter.

    Returns:
        A configured Agent that returns PlannerAssistantReply instances.
    """
    provider = OpenAIProvider(base_url=_OPENROUTER_BASE_URL, api_key=settings.openrouter_api_key)
    model = OpenAIChatModel(model_name=settings.openrouter_planner_model, provider=provider)
    return Agent(
        model,
        deps_type=PlannerDeps,
        output_type=PlannerAssistantReply,
        retries=3,
        system_prompt=_SYSTEM_PROMPT,
    )


coordinator_agent = _make_agent()


@coordinator_agent.tool
async def research_host_schools(ctx: RunContext[PlannerDeps], question: str) -> HostSchoolResearchResult:
    """Delegate to the host-school research specialist.

    Args:
        ctx: Run context carrying PlannerDeps.
        question: The student's host-school research question.

    Returns:
        Grounded host-school research findings.
    """
    result = await host_school_agent.run(question, deps=ctx.deps, usage=ctx.usage)
    return result.output


@coordinator_agent.tool
async def track_phase(ctx: RunContext[PlannerDeps], question: str) -> PhaseTrackingUpdate:
    """Delegate to the phase-tracking specialist.

    Args:
        ctx: Run context carrying PlannerDeps.
        question: The student's phase/progress-tracking question.

    Returns:
        A grounded phase-tracking recommendation.
    """
    result = await phase_tracking_agent.run(question, deps=ctx.deps, usage=ctx.usage)
    return result.output


async def run_planner_assistant(message: str, deps: PlannerDeps) -> tuple[PlannerAssistantReply, int, int]:
    """Run one planner-assistant turn.

    Args:
        message: The student's natural-language message.
        deps: PlannerDeps for this request.

    Returns:
        A tuple of (PlannerAssistantReply, input_tokens, output_tokens). Usage
        totals already aggregate all delegated specialist calls because
        ctx.usage is threaded through each specialist's .run().
    """
    result = await coordinator_agent.run(message, deps=deps)
    return result.output, result.usage.input_tokens, result.usage.output_tokens
