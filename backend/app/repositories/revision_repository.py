"""
RevisionPlan and RevisionTask repositories.

Pure data access — no business logic.
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revision import RevisionPlan, RevisionTask, TaskStatus
from app.repositories.base import BaseRepository


class RevisionPlanRepository(BaseRepository[RevisionPlan]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(RevisionPlan, db)

    async def get_by_material(self, material_id: int) -> list[RevisionPlan]:
        result = await self._db.execute(
            select(RevisionPlan).where(RevisionPlan.material_id == material_id)
        )
        return list(result.scalars().all())


class RevisionTaskRepository(BaseRepository[RevisionTask]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(RevisionTask, db)

    async def get_by_plan(self, plan_id: int) -> list[RevisionTask]:
        result = await self._db.execute(
            select(RevisionTask)
            .where(RevisionTask.revision_plan_id == plan_id)
            .order_by(RevisionTask.due_date)
        )
        return list(result.scalars().all())

    async def get_due_today(self) -> list[RevisionTask]:
        """Return all pending tasks due on or before today."""
        today = date.today()
        result = await self._db.execute(
            select(RevisionTask)
            .where(
                RevisionTask.due_date <= today,
                RevisionTask.status == TaskStatus.PENDING,
            )
            .order_by(RevisionTask.due_date)
        )
        return list(result.scalars().all())
