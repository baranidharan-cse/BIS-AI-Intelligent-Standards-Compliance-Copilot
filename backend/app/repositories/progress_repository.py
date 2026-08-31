"""
Progress and Mastery repositories.

Pure data access — no business logic.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import ConceptMastery, MaterialProgress
from app.repositories.base import BaseRepository


class ConceptMasteryRepository(BaseRepository[ConceptMastery]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(ConceptMastery, db)

    async def get_by_concept(self, concept_id: int) -> ConceptMastery | None:
        result = await self._db.execute(
            select(ConceptMastery).where(ConceptMastery.concept_id == concept_id)
        )
        return result.scalars().first()


class MaterialProgressRepository(BaseRepository[MaterialProgress]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(MaterialProgress, db)

    async def get_by_material(self, material_id: int) -> MaterialProgress | None:
        result = await self._db.execute(
            select(MaterialProgress).where(MaterialProgress.material_id == material_id)
        )
        return result.scalars().first()
