"""PydanticAI agent for structured response generation via OpenRouter."""

import asyncio

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from backend.config import settings
from backend.generation.models import GeneratedResponse

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _make_agent() -> Agent[None, GeneratedResponse]:
    """Build a PydanticAI agent pointed at OpenRouter.

    Returns:
        A configured Agent that returns GeneratedResponse instances.
    """
    provider = OpenAIProvider(
        base_url=_OPENROUTER_BASE_URL,
        api_key=settings.openrouter_api_key,
    )
    model = OpenAIChatModel(
        model_name=settings.openrouter_generation_model,
        provider=provider,
    )
    return Agent(model, output_type=GeneratedResponse, retries=3)


_agent = _make_agent()


async def generate_response(prompt: str) -> GeneratedResponse:
    """Generate a structured, cited response for the given prompt.

    Runs the PydanticAI agent against OpenRouter and validates the output
    against the GeneratedResponse schema. Retries up to 3 times on transient
    model errors (e.g. finish_reason='error' from OpenRouter free-tier models).

    Args:
        prompt: Fully assembled prompt from ``build_prompt``, including the
            system instruction, context chunks, and user query.

    Returns:
        A GeneratedResponse with paragraph-level citations.

    Raises:
        Exception: Re-raises the last exception if all retries are exhausted.
    """
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            result = await _agent.run(prompt)
            return result.output
        except Exception as exc:
            last_exc = exc
            if attempt < 2:
                await asyncio.sleep(2.0)
    raise last_exc  # type: ignore[misc]
