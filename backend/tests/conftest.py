"""Pytest configuration for backend tests.

Runs Alembic migrations before tests to ensure database tables exist.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Run Alembic migrations to set up the test database schema.

    Args:
        None

    Returns:
        None
    """
    repo_root = Path(__file__).parent.parent.parent

    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Warning: Alembic migration failed: {result.stderr}")
    except Exception as e:
        print(f"Warning: Could not run Alembic migrations: {e}")

    yield


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests.

    Args:
        None

    Returns:
        asyncio.AbstractEventLoop: The event loop for the session.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
