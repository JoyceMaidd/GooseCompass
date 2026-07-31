from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.auth import service
from backend.auth.models import AuthCode, User
from backend.auth.otp import hash_code
from backend.auth.tokens import decode_session_token

_EMAIL = "student@uwaterloo.ca"


def _mock_session(scalar_result=None):
    """Build a mock AsyncSession whose execute() always returns scalar_result."""
    session = MagicMock()
    session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=scalar_result)))
    session.commit = AsyncMock()
    session.add = MagicMock()
    return session


async def test_request_code_rejects_non_waterloo_domain():
    """Domain rejection happens before any DB call."""
    session = _mock_session()
    with pytest.raises(service.DomainError):
        await service.request_code(session, "student@gmail.com")
    session.execute.assert_not_called()
    session.add.assert_not_called()


async def test_request_code_domain_check_is_case_insensitive():
    session = _mock_session()
    with pytest.raises(service.DomainError):
        await service.request_code(session, "student@GMAIL.COM")


async def test_request_code_cooldown_rejection(mocker):
    """A recent unconsumed code blocks a new request."""
    mocker.patch("backend.auth.service.send_otp_email", new=AsyncMock())
    recent = AuthCode(email=_EMAIL, code_hash="x", expires_at=datetime.now(timezone.utc))
    session = _mock_session(scalar_result=recent)
    with pytest.raises(service.CooldownError):
        await service.request_code(session, _EMAIL)
    session.add.assert_not_called()


async def test_request_code_happy_path(mocker):
    """A fresh request writes an AuthCode row and sends the email."""
    send_mock = mocker.patch("backend.auth.service.send_otp_email", new=AsyncMock())
    session = _mock_session(scalar_result=None)

    await service.request_code(session, _EMAIL)

    session.add.assert_called_once()
    added = session.add.call_args[0][0]
    assert isinstance(added, AuthCode)
    assert added.email == _EMAIL
    session.commit.assert_called()
    send_mock.assert_awaited_once()
    assert send_mock.call_args[0][0] == _EMAIL


async def test_verify_code_no_code_found():
    session = _mock_session(scalar_result=None)
    with pytest.raises(service.InvalidCodeError):
        await service.verify_code(session, _EMAIL, "123456")


async def test_verify_code_expired():
    expired = AuthCode(
        email=_EMAIL,
        code_hash="x",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        attempts=0,
    )
    session = _mock_session(scalar_result=expired)
    with pytest.raises(service.InvalidCodeError):
        await service.verify_code(session, _EMAIL, "123456")


async def test_verify_code_attempts_exhausted():
    exhausted = AuthCode(
        email=_EMAIL,
        code_hash="x",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        attempts=5,
    )
    session = _mock_session(scalar_result=exhausted)
    with pytest.raises(service.InvalidCodeError):
        await service.verify_code(session, _EMAIL, "123456")


async def test_verify_code_wrong_code_increments_attempts():
    code_hash = await hash_code("111111")
    auth_code = AuthCode(
        email=_EMAIL,
        code_hash=code_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        attempts=0,
        consumed=False,
    )
    session = _mock_session(scalar_result=auth_code)

    with pytest.raises(service.InvalidCodeError):
        await service.verify_code(session, _EMAIL, "999999")

    assert auth_code.attempts == 1
    assert auth_code.consumed is False
    session.commit.assert_called()


async def test_verify_code_happy_path_returns_token_and_upserts_user():
    code_hash = await hash_code("123456")
    auth_code = AuthCode(
        email=_EMAIL,
        code_hash=code_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        attempts=0,
        consumed=False,
    )
    session = MagicMock()
    session.execute = AsyncMock(
        side_effect=[
            MagicMock(scalar_one_or_none=MagicMock(return_value=auth_code)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=None)),
        ]
    )
    session.commit = AsyncMock()
    session.add = MagicMock()

    token = await service.verify_code(session, _EMAIL, "123456")

    assert decode_session_token(token) == _EMAIL
    assert auth_code.consumed is True
    session.add.assert_called_once()
    added_user = session.add.call_args[0][0]
    assert isinstance(added_user, User)
    assert added_user.email == _EMAIL


async def test_verify_code_happy_path_skips_user_insert_if_exists():
    code_hash = await hash_code("123456")
    auth_code = AuthCode(
        email=_EMAIL,
        code_hash=code_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        attempts=0,
        consumed=False,
    )
    existing_user = User(email=_EMAIL)
    session = MagicMock()
    session.execute = AsyncMock(
        side_effect=[
            MagicMock(scalar_one_or_none=MagicMock(return_value=auth_code)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=existing_user)),
        ]
    )
    session.commit = AsyncMock()
    session.add = MagicMock()

    await service.verify_code(session, _EMAIL, "123456")

    session.add.assert_not_called()
