"""Tests for CORS configuration."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.api.app import app
from backend.config import settings


@pytest.mark.asyncio
async def test_preflight_returns_allow_origin_header():
    """OPTIONS preflight must include Access-Control-Allow-Origin header."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.options(
            "/query",
            headers={
                "Origin": settings.frontend_origin,
                "Access-Control-Request-Method": "POST",
            },
        )
    assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_preflight_reflects_configured_origin():
    """Access-Control-Allow-Origin must match the configured frontend origin."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.options(
            "/query",
            headers={
                "Origin": settings.frontend_origin,
                "Access-Control-Request-Method": "POST",
            },
        )
    assert response.headers["access-control-allow-origin"] == settings.frontend_origin
