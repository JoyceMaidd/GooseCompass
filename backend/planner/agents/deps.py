"""Shared dependency object injected into every planner agent run."""

from dataclasses import dataclass

from motor.motor_asyncio import AsyncIOMotorCollection
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class PlannerDeps:
    """Dependencies injected into every planner agent run.

    Args:
        session: Postgres async session scoped to the current request.
        user_id: The current (stub) user's ID.
        exchange_plan_id: The user's exchange_plans.id row.
        chunks_collection: Motor collection for read-only retrieval lookups.
    """

    session: AsyncSession
    user_id: int
    exchange_plan_id: int
    chunks_collection: AsyncIOMotorCollection
