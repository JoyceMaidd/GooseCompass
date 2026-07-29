from collections.abc import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings

_client: AsyncIOMotorClient | None = None


class Base(DeclarativeBase):
    """Shared declarative base for all Postgres ORM models."""


async def connect() -> None:
    """Open the Motor client connection.

    Args:
        None

    Returns:
        None
    """
    global _client
    if _client is not None:
        return
    _client = AsyncIOMotorClient(settings.mongodb_uri)


async def disconnect() -> None:
    """Close the Motor client connection.

    Args:
        None

    Returns:
        None
    """
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_database() -> AsyncIOMotorDatabase:
    """Return the configured database handle.

    Args:
        None

    Returns:
        AsyncIOMotorDatabase: The connected database.

    Raises:
        RuntimeError: If connect() has not been called.
    """
    if _client is None:
        raise RuntimeError("Database not connected — call connect() first.")
    return _client[settings.mongodb_db_name]


_pg_engine: AsyncEngine | None = None
_pg_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def _as_asyncpg_url(uri: str) -> str:
    """Ensure a Postgres URI specifies the asyncpg driver.

    POSTGRES_URI may be configured with a bare `postgresql://` scheme
    (e.g. copied from a sync tool); create_async_engine requires an async
    driver, so normalize it here rather than requiring every caller to
    remember the `+asyncpg` suffix. Alembic does the reverse normalization
    for its own sync psycopg2 engine.

    Args:
        uri: The configured Postgres URI.

    Returns:
        The URI with a `postgresql+asyncpg://` scheme.
    """
    if uri.startswith("postgresql://"):
        return uri.replace("postgresql://", "postgresql+asyncpg://", 1)
    return uri


async def connect_postgres() -> None:
    """Open the Postgres async engine and sessionmaker.

    Args:
        None

    Returns:
        None
    """
    global _pg_engine, _pg_sessionmaker
    if _pg_engine is not None:
        return
    _pg_engine = create_async_engine(_as_asyncpg_url(settings.postgres_uri))
    _pg_sessionmaker = async_sessionmaker(_pg_engine, expire_on_commit=False)


async def disconnect_postgres() -> None:
    """Dispose the Postgres async engine.

    Args:
        None

    Returns:
        None
    """
    global _pg_engine, _pg_sessionmaker
    if _pg_engine is not None:
        await _pg_engine.dispose()
        _pg_engine = None
        _pg_sessionmaker = None


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a Postgres session for use as a FastAPI dependency.

    Args:
        None

    Yields:
        AsyncSession: An open SQLAlchemy async session.

    Raises:
        RuntimeError: If connect_postgres() has not been called.
    """
    if _pg_sessionmaker is None:
        raise RuntimeError("Postgres not connected — call connect_postgres() first.")
    async with _pg_sessionmaker() as session:
        yield session
