"""SQLAlchemy ORM models for usage logging and users."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.db import Base


class User(Base):
    """A user account (seeded demo user for quota tracking).

    Args:
        id: Primary key.
        email: User's email address (unique).
        created_at: When this user was created.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=False)


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
