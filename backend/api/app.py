"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.query import router as query_router
from backend.config import settings
from backend.db import connect, disconnect


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open the MongoDB connection on startup and close it on shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        None
    """
    await connect()
    yield
    await disconnect()


app = FastAPI(title="GooseCompass", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_private_network=True,
)

app.include_router(query_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        A dict with status 'ok'.
    """
    return {"status": "ok"}
