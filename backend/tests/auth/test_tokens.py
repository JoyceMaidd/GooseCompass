from datetime import datetime, timedelta, timezone

import jwt
import pytest

from backend.auth.tokens import create_session_token, decode_session_token
from backend.config import settings


def test_roundtrip():
    """A freshly created token decodes back to the same email."""
    token = create_session_token("student@uwaterloo.ca")
    assert decode_session_token(token) == "student@uwaterloo.ca"


def test_tampered_token_raises():
    """A token with a flipped character fails signature verification."""
    token = create_session_token("student@uwaterloo.ca")
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
    with pytest.raises(jwt.InvalidTokenError):
        decode_session_token(tampered)


def test_expired_token_raises():
    """A token whose exp claim is in the past raises."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "student@uwaterloo.ca",
        "iat": now - timedelta(minutes=10),
        "exp": now - timedelta(minutes=1),
    }
    expired_token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_session_token(expired_token)
