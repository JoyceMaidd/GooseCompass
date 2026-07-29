"""SQLAlchemy ORM models for authentication: users and one-time codes."""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.db import Base


class User(Base):
    """A verified @uwaterloo.ca user.

    Args:
        id: Primary key.
        email: The verified @uwaterloo.ca email address.
        created_at: When this row was first inserted.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuthCode(Base):
    """A one-time OTP code issued for an email address.

    Keyed off email rather than a user_id foreign key, since a code can be
    requested before a corresponding User row exists.

    Args:
        id: Primary key.
        email: The email address this code was issued to.
        code_hash: Bcrypt hash of the code.
        expires_at: When this code stops being valid.
        attempts: Number of failed verification attempts so far.
        consumed: Whether this code has already been successfully used.
        created_at: When this row was first inserted.
    """

    __tablename__ = "auth_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(index=True)
    code_hash: Mapped[str]
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(default=0)
    consumed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
