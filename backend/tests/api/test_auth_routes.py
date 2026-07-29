import pytest
from httpx import ASGITransport, AsyncClient

from backend.api.app import app
from backend.auth import service
from backend.db import get_session


async def _noop_session():
    yield None


@pytest.fixture(autouse=True)
def override_get_session():
    app.dependency_overrides[get_session] = _noop_session
    yield
    app.dependency_overrides.pop(get_session, None)


async def test_request_code_success_returns_204(mocker):
    mocker.patch("backend.api.routes.auth.service.request_code", return_value=None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/auth/request-code", json={"email": "student@uwaterloo.ca"})
    assert response.status_code == 204


async def test_request_code_domain_error_returns_400(mocker):
    mocker.patch(
        "backend.api.routes.auth.service.request_code",
        side_effect=service.DomainError("Email must be a @uwaterloo.ca address."),
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/auth/request-code", json={"email": "student@gmail.com"})
    assert response.status_code == 400


async def test_request_code_cooldown_returns_429(mocker):
    mocker.patch(
        "backend.api.routes.auth.service.request_code",
        side_effect=service.CooldownError("Please wait before requesting another code."),
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/auth/request-code", json={"email": "student@uwaterloo.ca"})
    assert response.status_code == 429


async def test_verify_code_success_returns_token(mocker):
    mocker.patch("backend.api.routes.auth.service.verify_code", return_value="fake.jwt.token")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/verify-code", json={"email": "student@uwaterloo.ca", "code": "123456"}
        )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "fake.jwt.token"
    assert body["token_type"] == "bearer"


async def test_verify_code_invalid_returns_401(mocker):
    mocker.patch(
        "backend.api.routes.auth.service.verify_code",
        side_effect=service.InvalidCodeError("Code is invalid, expired, or exhausted."),
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/auth/verify-code", json={"email": "student@uwaterloo.ca", "code": "000000"}
        )
    assert response.status_code == 401
