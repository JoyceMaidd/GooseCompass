import pytest

from backend.db import connect, disconnect, get_database


@pytest.fixture(autouse=True)
async def db_lifecycle():
    """Open and close the DB connection around each test."""
    await connect()
    yield
    await disconnect()


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
