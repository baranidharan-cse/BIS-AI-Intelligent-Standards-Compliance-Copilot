"""
Quiz, QuizQuestion, and QuizAttempt repositories.

Pure data access — no business logic.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz import Quiz, QuizAttempt, QuizQuestion
from app.repositories.base import BaseRepository


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Quiz, db)

    async def get_by_material(self, material_id: int) -> list[Quiz]:
        result = await self._db.execute(
            select(Quiz).where(Quiz.material_id == material_id)
        )
        return list(result.scalars().all())


class QuizQuestionRepository(BaseRepository[QuizQuestion]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(QuizQuestion, db)

    async def get_by_quiz(self, quiz_id: int) -> list[QuizQuestion]:
        result = await self._db.execute(
            select(QuizQuestion)
            .where(QuizQuestion.quiz_id == quiz_id)
            .order_by(QuizQuestion.order_index)
        )
        return list(result.scalars().all())


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(QuizAttempt, db)

    async def get_by_quiz(self, quiz_id: int) -> list[QuizAttempt]:
        result = await self._db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.quiz_id == quiz_id)
            .order_by(QuizAttempt.started_at.desc())
        )
        return list(result.scalars().all())
