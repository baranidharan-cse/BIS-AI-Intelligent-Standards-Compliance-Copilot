"""
Material, Section, and Concept repositories.

Pure data access — no business logic.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.material import Concept, Material, MaterialStatus, Section
from app.repositories.base import BaseRepository


class MaterialRepository(BaseRepository[Material]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Material, db)

    async def get_by_status(self, status: MaterialStatus) -> list[Material]:
        """Return all materials with a given processing status."""
        result = await self._db.execute(
            select(Material).where(Material.status == status)
        )
        return list(result.scalars().all())

    async def get_with_sections(self, material_id: int) -> Material | None:
        """Fetch a material and eagerly load its sections."""
        from sqlalchemy.orm import selectinload

        result = await self._db.execute(
            select(Material)
            .where(Material.id == material_id)
            .options(selectinload(Material.sections))
        )
        return result.scalars().first()


class SectionRepository(BaseRepository[Section]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Section, db)

    async def get_by_material(self, material_id: int) -> list[Section]:
        """Return all sections for a material, ordered by index."""
        result = await self._db.execute(
            select(Section)
            .where(Section.material_id == material_id)
            .order_by(Section.order_index)
        )
        return list(result.scalars().all())


class ConceptRepository(BaseRepository[Concept]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Concept, db)

    async def get_by_section(self, section_id: int) -> list[Concept]:
        """Return all concepts for a section, ordered by index."""
        result = await self._db.execute(
            select(Concept)
            .where(Concept.section_id == section_id)
            .order_by(Concept.order_index)
        )
        return list(result.scalars().all())
