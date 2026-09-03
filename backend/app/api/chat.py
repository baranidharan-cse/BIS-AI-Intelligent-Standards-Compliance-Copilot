"""
Chat router.

POST /api/chat/message                  — send a message in a session
GET  /api/chat/sessions/{session_id}    — get full session history
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])


class SendMessageRequest(BaseModel):
    session_id: str
    message: str
    material_id: int | None = None


@router.post("/message")
async def send_message(
    body: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Send a user message and receive an assistant reply."""
    try:
        svc = ChatService(db)
        return await svc.send_message(
            session_id=body.session_id,
            user_message=body.message,
            material_id=body.material_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Return the full message history for a chat session."""
    try:
        svc = ChatService(db)
        return await svc.get_session_history(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
