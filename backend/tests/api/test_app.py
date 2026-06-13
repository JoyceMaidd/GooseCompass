"""Tests for backend/api/app.py."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.api.app import app


@pytest.mark.asyncio
async def test_health_returns_200():
    """GET /health must return 200 OK."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_returns_status_ok():
    """GET /health must return {"status": "ok"}."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.json() == {"status": "ok"}
