"""Rate limiting setup for the /auth/request-code endpoint."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_uri,
    default_limits=[f"{settings.rate_limit_requests}/{settings.rate_limit_window_seconds}s"],
    in_memory_fallback_enabled=True,
)
