"""OTP request/verify orchestration."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.email import send_otp_email
from backend.auth.models import AuthCode, User
from backend.auth.otp import generate_code, hash_code, verify_code_hash
from backend.auth.tokens import create_session_token
from backend.config import settings

_ALLOWED_DOMAIN = "@uwaterloo.ca"


class DomainError(ValueError):
    """Raised when an email is not a valid @uwaterloo.ca address."""


class CooldownError(Exception):
    """Raised when a code is requested again before the resend cooldown elapses."""


class InvalidCodeError(Exception):
    """Raised when a submitted code is missing, wrong, expired, or exhausted."""


async def request_code(session: AsyncSession, email: str) -> None:
    """Generate and email a one-time code for a @uwaterloo.ca address.

    Args:
        session: An open Postgres async session.
        email: The address requesting a code.

    Returns:
        None

    Raises:
        DomainError: If the email is not a @uwaterloo.ca address.
        CooldownError: If an unconsumed code was already issued to this
            email within the resend cooldown window.
    """
    if not email.lower().endswith(_ALLOWED_DOMAIN):
        raise DomainError("Email must be a @uwaterloo.ca address.")

    cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.otp_resend_cooldown_seconds)
    stmt = select(AuthCode).where(
        AuthCode.email == email,
        AuthCode.consumed.is_(False),
        AuthCode.created_at > cutoff,
    )
    recent = (await session.execute(stmt)).scalar_one_or_none()
    if recent is not None:
        raise CooldownError("Please wait before requesting another code.")

    code = generate_code()
    code_hash = await hash_code(code)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.otp_ttl_minutes)
    session.add(AuthCode(email=email, code_hash=code_hash, expires_at=expires_at))
    await session.commit()

    await send_otp_email(email, code)


async def verify_code(session: AsyncSession, email: str, code: str) -> str:
    """Verify a one-time code and issue a session token.

    Args:
        session: An open Postgres async session.
        email: The address being verified.
        code: The plaintext code submitted by the user.

    Returns:
        A signed JWT session token for the verified email.

    Raises:
        InvalidCodeError: If no valid code exists, it has expired, has
            exhausted its attempt limit, or the submitted code is wrong.
    """
    stmt = (
        select(AuthCode)
        .where(AuthCode.email == email, AuthCode.consumed.is_(False))
        .order_by(AuthCode.created_at.desc())
        .limit(1)
    )
    auth_code = (await session.execute(stmt)).scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if auth_code is None or auth_code.expires_at < now or auth_code.attempts >= settings.otp_max_attempts:
        raise InvalidCodeError("Code is invalid, expired, or exhausted.")

    if not await verify_code_hash(code, auth_code.code_hash):
        auth_code.attempts += 1
        await session.commit()
        raise InvalidCodeError("Incorrect code.")

    auth_code.consumed = True

    existing = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if existing is None:
        session.add(User(email=email))

    await session.commit()
    return create_session_token(email)
