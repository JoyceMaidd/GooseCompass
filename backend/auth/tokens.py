"""JWT session token issuance and verification."""

from datetime import datetime, timedelta, timezone

import jwt

from backend.config import settings

_ALGORITHM = "HS256"


def create_session_token(email: str) -> str:
    """Encode a stateless JWT session token for an email.

    Args:
        email: The verified email address to embed as the subject.

    Returns:
        A signed JWT string.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expiry_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=_ALGORITHM)


def decode_session_token(token: str) -> str:
    """Decode and validate a JWT session token.

    Args:
        token: The JWT string to decode.

    Returns:
        The email address embedded as the token's subject.

    Raises:
        jwt.InvalidTokenError: If the token is expired, tampered with, or malformed.
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[_ALGORITHM],
        options={"verify_signature": True},
    )
    return payload["sub"]
