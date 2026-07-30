"""Global monthly spend-cap circuit breaker."""

from fastapi import Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.db import get_session
from backend.monitoring.models import UsageLog
from backend.monitoring.period import start_of_current_month


async def check_spend_cap(
    session: AsyncSession = Depends(get_session),
) -> None:
    """Check if global monthly LLM spend has exceeded the hard cap.

    Args:
        session: Postgres async session.

    Raises:
        HTTPException(503): If global month-to-date spend has reached the cap.
    """
    month_start = start_of_current_month()
    stmt = select(func.sum(UsageLog.cost_usd)).where(
        UsageLog.created_at >= month_start,
    )
    total_cost = (await session.execute(stmt)).scalar() or 0.0

    if total_cost >= settings.monthly_spend_cap_usd:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable.")
