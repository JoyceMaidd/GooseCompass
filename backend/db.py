from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from backend.config import settings

_client: AsyncIOMotorClient | None = None


async def connect() -> None:
    """Open the Motor client connection.

    Args:
        None

    Returns:
        None
    """
    global _client
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
