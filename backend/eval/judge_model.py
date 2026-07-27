"""Custom DeepEval judge model routed through OpenRouter.

DeepEval's built-in OpenAI integration reads OPENAI_API_KEY from the process
environment directly, but this app never calls load_dotenv() -- .env values
only ever reach the Settings object, not os.environ. Passing credentials
through Settings explicitly (as this wrapper does) sidesteps that gap.
"""

import asyncio
import time

from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

from deepeval.metrics.utils import trimAndLoadJson
from deepeval.models.base_model import DeepEvalBaseLLM

from backend.config import settings

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
_MAX_ATTEMPTS = 3
_RETRY_DELAY_SECONDS = 2.0


class OpenRouterJudgeModel(DeepEvalBaseLLM):
    """DeepEval judge model backed by an OpenRouter chat completion model."""

    def __init__(self, model_name: str = settings.openrouter_eval_judge_model):
        """Initialize OpenAI-compatible clients pointed at OpenRouter.

        Args:
            model_name: OpenRouter model identifier (e.g. "openai/gpt-4o-mini").
        """
        self._model_name = model_name
        self._client = OpenAI(base_url=_OPENROUTER_BASE_URL, api_key=settings.openrouter_api_key)
        self._async_client = AsyncOpenAI(
            base_url=_OPENROUTER_BASE_URL, api_key=settings.openrouter_api_key
        )
        super().__init__(model_name)

    def load_model(self) -> OpenAI:
        """Return the sync client used to score DeepEval test cases.

        Returns:
            The configured sync OpenAI-compatible client.
        """
        return self._client

    def _build_kwargs(self, prompt: str, schema: type[BaseModel] | None) -> dict:
        """Build shared chat-completion kwargs for sync/async calls.

        DeepEval always calls generate/a_generate with the internal Pydantic
        schema it expects back (e.g. verdict/reason schemas) so it can parse
        the result as JSON. Without response_format enforcement the model
        only has prompt instructions to go on and can emit malformed JSON
        (e.g. an unescaped quote inside a "reason" string) -- requesting
        JSON mode when a schema is given constrains the output at the API
        level instead of relying on instruction-following alone.

        Args:
            prompt: The evaluation prompt DeepEval constructs for a metric.
            schema: The Pydantic schema DeepEval expects the JSON to match.

        Returns:
            Keyword arguments for chat.completions.create.
        """
        kwargs: dict = {
            "model": self._model_name,
            "messages": [{"role": "user", "content": prompt}],
        }
        if schema is not None:
            kwargs["response_format"] = {"type": "json_object"}
        return kwargs

    @staticmethod
    def _matches_schema(content: str, schema: type[BaseModel]) -> bool:
        """Check whether content parses as JSON matching schema.

        Uses DeepEval's own trimAndLoadJson so markdown-fenced JSON (which
        DeepEval itself tolerates) isn't rejected here as invalid.

        Args:
            content: Raw model output to validate.
            schema: The Pydantic schema DeepEval expects the JSON to match.

        Returns:
            True if content parses and matches schema, False otherwise.
        """
        try:
            schema.model_validate(trimAndLoadJson(content))
            return True
        except Exception:
            return False

    def generate(self, prompt: str, schema: type[BaseModel] | None = None) -> str:
        """Run a synchronous judge completion, retrying on schema mismatch.

        A fast judge model occasionally returns JSON that's syntactically
        valid but doesn't match DeepEval's expected schema shape -- this is
        judge-model non-determinism, not a code bug, and DeepEval itself has
        no retry for it. Retrying here (mirroring the retry pattern in
        backend/generation/agent.py) trades a little latency for much more
        stable eval runs.

        Args:
            prompt: The evaluation prompt DeepEval constructs for a metric.
            schema: The Pydantic schema DeepEval expects the JSON to match.

        Returns:
            The judge model's raw text response.
        """
        kwargs = self._build_kwargs(prompt, schema)
        content = ""
        for attempt in range(_MAX_ATTEMPTS):
            response = self._client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""
            if schema is None or self._matches_schema(content, schema):
                return content
            if attempt < _MAX_ATTEMPTS - 1:
                time.sleep(_RETRY_DELAY_SECONDS)
        return content

    async def a_generate(self, prompt: str, schema: type[BaseModel] | None = None) -> str:
        """Run an asynchronous judge completion, retrying on schema mismatch.

        Args:
            prompt: The evaluation prompt DeepEval constructs for a metric.
            schema: The Pydantic schema DeepEval expects the JSON to match.

        Returns:
            The judge model's raw text response.
        """
        kwargs = self._build_kwargs(prompt, schema)
        content = ""
        for attempt in range(_MAX_ATTEMPTS):
            response = await self._async_client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""
            if schema is None or self._matches_schema(content, schema):
                return content
            if attempt < _MAX_ATTEMPTS - 1:
                await asyncio.sleep(_RETRY_DELAY_SECONDS)
        return content

    def get_model_name(self) -> str:
        """Return the OpenRouter model identifier used for judging.

        Returns:
            The configured model name.
        """
        return self._model_name
