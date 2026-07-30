"""Per-user monthly token quota enforcement."""

from fastapi import Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependency import require_auth
from backend.auth.models import User
from backend.config import settings
from backend.db import get_session
from backend.monitoring.models import UsageLog
from backend.monitoring.period import start_of_current_month


async def check_user_quota(
    email: str = Depends(require_auth),
    session: AsyncSession = Depends(get_session),
) -> int:
    """Check if a user has exceeded their monthly token quota.

    Returns the user's ID for use in logging if under quota.

    Args:
        email: The verified user's email (from require_auth dependency).
        session: Postgres async session.

    Returns:
        The user's ID.

    Raises:
        HTTPException(401): If the user is not found (shouldn't happen if
            require_auth is working correctly).
        HTTPException(429): If the user has reached their monthly quota.
    """
    user = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    month_start = start_of_current_month()
    stmt = select(func.sum(UsageLog.tokens_used)).where(
        UsageLog.user_id == user.id,
        UsageLog.created_at >= month_start,
    )
    total_tokens = (await session.execute(stmt)).scalar() or 0

    if total_tokens >= settings.user_monthly_quota_tokens:
        raise HTTPException(status_code=429, detail="Monthly usage quota exceeded.")

    return user.id
