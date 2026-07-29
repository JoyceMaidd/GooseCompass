import pytest
from sqlalchemy import text

from backend.db import (
    connect,
    connect_postgres,
    disconnect,
    disconnect_postgres,
    get_database,
    get_session,
)


@pytest.fixture(autouse=True)
async def db_lifecycle():
    """Open and close the DB connection around each test."""
    await connect()
    yield
    await disconnect()


@pytest.mark.integration
async def test_ping():
    """Connection succeeds and Atlas responds with ok: 1."""
    db = get_database()
    result = await db.command("ping")
    assert result.get("ok") == 1.0


async def test_get_database_raises_before_connect():
    """get_database raises RuntimeError when called without a connection."""
    await disconnect()
    with pytest.raises(RuntimeError):
        get_database()


@pytest.mark.integration
async def test_postgres_session_select_one():
    """Connection succeeds and a real Postgres instance answers SELECT 1."""
    await connect_postgres()
    try:
        async for session in get_session():
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
    finally:
        await disconnect_postgres()


async def test_get_session_raises_before_connect():
    """get_session raises RuntimeError when called without a connection."""
    await disconnect_postgres()
    with pytest.raises(RuntimeError):
        async for _ in get_session():
            pass
