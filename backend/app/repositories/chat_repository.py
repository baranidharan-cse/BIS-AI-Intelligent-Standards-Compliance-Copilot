"""
ChatMessage repository.

Pure data access — no business logic.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage
from app.repositories.base import BaseRepository


class ChatMessageRepository(BaseRepository[ChatMessage]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(ChatMessage, db)

    async def get_session_history(
        self, session_id: str, *, limit: int = 50
    ) -> list[ChatMessage]:
        """Return messages for a session in chronological order."""
        result = await self._db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())
