"""Rate limiting setup for the /auth/request-code endpoint."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.config import settings


def _get_rate_limit_string() -> str:
    """Convert window_seconds to appropriate granularity for limits library."""
    if settings.rate_limit_window_seconds == 1:
        granularity = "second"
    elif settings.rate_limit_window_seconds == 60:
        granularity = "minute"
    elif settings.rate_limit_window_seconds == 3600:
        granularity = "hour"
    elif settings.rate_limit_window_seconds == 86400:
        granularity = "day"
    else:
        # Default to minute for non-standard windows
        granularity = "minute"
    return f"{settings.rate_limit_requests}/{granularity}"


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_uri,
    default_limits=[_get_rate_limit_string()],
    in_memory_fallback_enabled=True,
)
