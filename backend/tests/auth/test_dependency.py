from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from backend.auth.dependency import require_auth
from backend.auth.tokens import create_session_token
from backend.config import settings

_EMAIL = "student@uwaterloo.ca"


async def test_valid_token_passes_through():
    token = create_session_token(_EMAIL)
    result = await require_auth(authorization=f"Bearer {token}")
    assert result == _EMAIL


async def test_missing_header_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        await require_auth(authorization="")
    assert exc_info.value.status_code == 401


async def test_bad_scheme_raises_401():
    token = create_session_token(_EMAIL)
    with pytest.raises(HTTPException) as exc_info:
        await require_auth(authorization=f"Basic {token}")
    assert exc_info.value.status_code == 401


async def test_expired_token_raises_401():
    now = datetime.now(timezone.utc)
    payload = {"sub": _EMAIL, "iat": now - timedelta(minutes=10), "exp": now - timedelta(minutes=1)}
    expired_token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    with pytest.raises(HTTPException) as exc_info:
        await require_auth(authorization=f"Bearer {expired_token}")
    assert exc_info.value.status_code == 401


async def test_tampered_token_raises_401():
    token = create_session_token(_EMAIL)
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
    with pytest.raises(HTTPException) as exc_info:
        await require_auth(authorization=f"Bearer {tampered}")
    assert exc_info.value.status_code == 401
