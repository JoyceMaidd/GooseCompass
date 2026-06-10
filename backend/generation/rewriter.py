"""Query rewriter that converts conversational queries into retrieval-optimized form."""

from openai import AsyncOpenAI

from backend.config import settings

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

_SYSTEM_PROMPT = (
    "You are a search query optimizer for an institutional document retrieval system. "
    "Rewrite the user's query into a concise, keyword-dense form that maximizes recall "
    "against University of Waterloo exchange program documentation. "
    "Use precise institutional terminology. Return only the rewritten query — no explanation, "
    "no punctuation beyond what belongs in the query itself."
)


async def rewrite_query(query: str) -> str:
    """Rewrite a conversational query into retrieval-optimized form.

    Calls the configured rewriter LLM via OpenRouter. The rewritten query is
    shorter and denser than the original, using institutional terminology to
    improve vector and full-text search recall.

    Args:
        query: The raw user question in natural language.

    Returns:
        A keyword-dense rewritten query string.

    Raises:
        openai.OpenAIError: If the OpenRouter API call fails.
    """
    client = AsyncOpenAI(
        api_key=settings.openrouter_api_key,
        base_url=_OPENROUTER_BASE_URL,
    )
    response = await client.chat.completions.create(
        model=settings.openrouter_rewriter_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        temperature=0.0,
    )
    return (response.choices[0].message.content or "").strip()
