"""Tests for ChatService — multi-turn chatbot."""
import pytest
from app.services.chat_service import ChatService
from app.services.material_service import MaterialService


@pytest.mark.asyncio
async def test_chat_service_flow(db):
    """send_message stores history and returns assistant response with suggestions."""
    mat_svc = MaterialService(db)
    mat = await mat_svc.ingest_text(title="Python", raw_text="Python programming basics")

    chat_svc = ChatService(db)
    session_id = "test-session-123"

    res = await chat_svc.send_message(
        session_id=session_id,
        user_message="What is a variable?",
        material_id=mat.id
    )

    assert res["role"] == "assistant"
    assert len(res["content"]) > 0
    assert "session_id" in res

    history = await chat_svc.get_session_history(session_id)
    assert len(history) == 2  # user + assistant
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
