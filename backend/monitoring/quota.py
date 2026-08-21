"""Per-user monthly token quota enforcement."""

from fastapi import Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.db import get_session
from backend.monitoring.models import User, UsageLog
from backend.monitoring.period import start_of_current_month

DEMO_USER_ID = 1


async def check_user_quota(session: AsyncSession = Depends(get_session)) -> int:
    """Check if the demo user has exceeded their monthly token quota.

    Returns the user's ID for use in logging if under quota.

    Args:
        session: Postgres async session.

    Returns:
        The demo user's ID.

    Raises:
        HTTPException(429): If the user has reached their monthly quota.
    """
    month_start = start_of_current_month()
    stmt = select(func.sum(UsageLog.tokens_used)).where(
        UsageLog.user_id == DEMO_USER_ID,
        UsageLog.created_at >= month_start,
    )
    total_tokens = (await session.execute(stmt)).scalar() or 0

    if total_tokens >= settings.user_monthly_quota_tokens:
        raise HTTPException(status_code=429, detail="Monthly usage quota exceeded.")

    return DEMO_USER_ID
