"""Dependency seam for identifying the current planner user.

Real auth (backend/auth/) doesn't exist yet — the whole app currently
identifies "the user" via DEMO_USER_ID, seeded as a stub (see
backend/monitoring/quota.py). This wrapper exists so swapping in real auth
later only requires changing this one function, not every planner route.
"""

from backend.monitoring.quota import DEMO_USER_ID


async def get_current_user_id() -> int:
    """Resolve the current user's ID.

    Returns:
        The current (stub) user's ID.
    """
    return DEMO_USER_ID
