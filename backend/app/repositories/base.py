"""
Base repository with generic CRUD operations.

Repositories contain ZERO business logic — only data access.
All business rules live in the service layer.
"""

from typing import Any, Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Generic async repository for a single SQLAlchemy model.

    Usage:
        class MaterialRepository(BaseRepository[Material]):
            def __init__(self, db: AsyncSession):
                super().__init__(Material, db)
    """

    def __init__(self, model: Type[ModelT], db: AsyncSession) -> None:
        self._model = model
        self._db = db

    async def get_by_id(self, record_id: int) -> ModelT | None:
        """Fetch a single record by primary key."""
        return await self._db.get(self._model, record_id)

    async def get_all(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]:
        """Fetch all records with optional pagination."""
        result = await self._db.execute(
            select(self._model).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> ModelT:
        """Create and persist a new record."""
        instance = self._model(**kwargs)
        self._db.add(instance)
        await self._db.flush()
        await self._db.refresh(instance)
        return instance

    async def update(self, record_id: int, **kwargs: Any) -> ModelT | None:
        """Update fields on an existing record. Returns None if not found."""
        instance = await self.get_by_id(record_id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self._db.flush()
        await self._db.refresh(instance)
        return instance

    async def delete(self, record_id: int) -> bool:
        """Delete a record by primary key. Returns True if deleted."""
        instance = await self.get_by_id(record_id)
        if instance is None:
            return False
        await self._db.delete(instance)
        await self._db.flush()
        return True
