"""SQLAlchemy ORM model for usage logging."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.db import Base


class UsageLog(Base):
    """A log entry for LLM API usage per request.

    Args:
        id: Primary key.
        user_id: Foreign key to users.id.
        tokens_used: Total tokens (input + output) for this request.
        cost_usd: Computed cost in USD for this request.
        status_code: HTTP response status code.
        latency_ms: Request latency in milliseconds.
        created_at: When this log entry was recorded.
    """

    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    tokens_used: Mapped[int]
    cost_usd: Mapped[float]
    status_code: Mapped[int]
    latency_ms: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
