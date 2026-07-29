"""FastAPI dependency gating routes behind a valid session token."""

import jwt
from fastapi import Header, HTTPException

from backend.auth.tokens import decode_session_token

_BEARER_PREFIX = "Bearer "


async def require_auth(authorization: str = Header(default="")) -> str:
    """Require a valid `Authorization: Bearer <token>` header.

    Uses `Header(default="")` rather than a required header so a missing
    header is handled here (as a 401) instead of FastAPI's own validation
    returning a 422 before this function runs.

    Args:
        authorization: The raw Authorization header value.

    Returns:
        The verified email address embedded in the token.

    Raises:
        HTTPException: 401 if the header is missing, malformed, or the
            token is invalid or expired.
    """
    if not authorization.startswith(_BEARER_PREFIX):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header.")

    token = authorization.removeprefix(_BEARER_PREFIX)
    try:
        return decode_session_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
