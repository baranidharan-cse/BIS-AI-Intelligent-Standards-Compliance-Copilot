"""
LearningPath and LearningStep repositories.

Pure data access — no business logic.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning_path import LearningPath, LearningStep
from app.repositories.base import BaseRepository


class LearningPathRepository(BaseRepository[LearningPath]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(LearningPath, db)

    async def get_by_material(self, material_id: int) -> list[LearningPath]:
        result = await self._db.execute(
            select(LearningPath).where(LearningPath.material_id == material_id)
        )
        return list(result.scalars().all())


class LearningStepRepository(BaseRepository[LearningStep]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(LearningStep, db)

    async def get_by_path(self, learning_path_id: int) -> list[LearningStep]:
        """Return all steps for a path, ordered by index."""
        result = await self._db.execute(
            select(LearningStep)
            .where(LearningStep.learning_path_id == learning_path_id)
            .order_by(LearningStep.order_index)
        )
        return list(result.scalars().all())
