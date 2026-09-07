"""Asynchronous usage logging to the database."""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.monitoring.models import UsageLog

_GENERATION_INPUT_COST_PER_1M_USD = 0.10
_GENERATION_OUTPUT_COST_PER_1M_USD = 0.40


async def log_usage_to_db(
    session: AsyncSession,
    user_id: int,
    input_tokens: int,
    output_tokens: int,
    status_code: int,
    latency_ms: int,
    input_cost_per_1m_usd: float = _GENERATION_INPUT_COST_PER_1M_USD,
    output_cost_per_1m_usd: float = _GENERATION_OUTPUT_COST_PER_1M_USD,
) -> None:
    """Log LLM usage to the database.

    Meant to be called via FastAPI BackgroundTasks, so runs asynchronously
    after the response is sent to the client. Computes cost from token counts
    using the given per-million-token pricing, defaulting to the generation
    model's rate so existing callers are unaffected.

    Args:
        session: Postgres async session.
        user_id: The user who made the request.
        input_tokens: Prompt tokens used.
        output_tokens: Completion tokens used.
        status_code: HTTP response status code.
        latency_ms: Request latency in milliseconds.
        input_cost_per_1m_usd: Input token price in USD per million tokens.
        output_cost_per_1m_usd: Output token price in USD per million tokens.
    """
    total_tokens = input_tokens + output_tokens
    cost_usd = (input_tokens / 1_000_000) * input_cost_per_1m_usd + (
        output_tokens / 1_000_000
    ) * output_cost_per_1m_usd

    log_entry = UsageLog(
        user_id=user_id,
        tokens_used=total_tokens,
        cost_usd=cost_usd,
        status_code=status_code,
        latency_ms=latency_ms,
    )
    session.add(log_entry)
    await session.commit()
