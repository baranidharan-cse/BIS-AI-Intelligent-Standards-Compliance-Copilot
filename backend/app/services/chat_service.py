"""
ChatService — multi-turn chatbot with optional material context.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage, MessageRole
from app.repositories.chat_repository import ChatMessageRepository
from app.repositories.material_repository import MaterialRepository
from app.services.llm.base import get_llm_service


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._messages = ChatMessageRepository(db)
        self._materials = MaterialRepository(db)

    async def send_message(
        self,
        session_id: str,
        user_message: str,
        material_id: int | None = None,
    ) -> dict:
        """Persist user message, call LLM, persist and return assistant reply."""
        # 1. Save the user's message
        await self._messages.create(
            session_id=session_id,
            material_id=material_id,
            role=MessageRole.USER,
            content=user_message,
        )

        # 2. Load the last 10 messages for session history (the one we just
        #    saved is already included because flush happened inside create())
        history_rows = await self._messages.get_session_history(session_id, limit=10)
        history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in history_rows
        ]

        # 3. Retrieval-based context selection with similarity threshold & refusal logic
        context = ""
        follow_ups: list[str] = []
        if material_id is not None:
            material = await self._materials.get_with_sections(material_id)
            if material:
                query_tokens = set(user_message.lower().split())
                # Filter out short stop words
                query_words = {w for w in query_tokens if len(w) > 3}

                section_scores = []
                all_concept_names = []

                for sec in material.sections:
                    sec_text = f"{sec.title} {sec.summary or ''} {sec.content or ''}".lower()
                    sec_tokens = set(sec_text.split())
                    
                    # Fetch concept names for this section
                    from app.repositories.material_repository import ConceptRepository
                    con_repo = ConceptRepository(self._db)
                    concepts = await con_repo.get_by_section(sec.id)
                    con_names = [c.name for c in concepts]
                    all_concept_names.extend(con_names)

                    # Compute token match score
                    match_count = sum(1 for w in query_words if w in sec_text or any(w in c.lower() for c in con_names))
                    score = match_count / len(query_words) if query_words else 0.0
                    section_scores.append((score, sec, con_names))

                section_scores.sort(key=lambda x: x[0], reverse=True)
                top_score = section_scores[0][0] if section_scores else 0.0

                # Threshold check: if material is selected but query is completely unrelated (score < 0.10)
                if query_words and top_score < 0.10:
                    topic_suggestions = [c for c in all_concept_names[:3]] if all_concept_names else [s.title for s in material.sections[:3]]
                    refusal_msg = (
                        f"The selected material '{material.title}' does not contain information about your question. "
                        f"Please ask a question related to this material (e.g. {', '.join(topic_suggestions) if topic_suggestions else 'its core topics'}), "
                        "or clear the material context selector to ask general questions."
                    )
                    
                    await self._messages.create(
                        session_id=session_id,
                        material_id=material_id,
                        role=MessageRole.ASSISTANT,
                        content=refusal_msg,
                    )
                    await self._db.commit()
                    return {
                        "role": "assistant",
                        "content": refusal_msg,
                        "follow_up_suggestions": topic_suggestions,
                        "session_id": session_id,
                    }

                # Construct relevant context from top matching sections
                relevant_blocks = []
                for _, sec, _ in section_scores[:2]:
                    block = f"Section: {sec.title}\n{sec.summary or ''}\n{sec.content or ''}".strip()
                    relevant_blocks.append(block)
                context = "\n\n".join(relevant_blocks)[:2000]

        # 4. Ask the LLM
        answer = await get_llm_service().answer_question(user_message, history, context)

        # 5. Persist the assistant reply
        await self._messages.create(
            session_id=session_id,
            material_id=material_id,
            role=MessageRole.ASSISTANT,
            content=answer.answer,
            prompt_tokens=answer.prompt_tokens or None,
            completion_tokens=answer.completion_tokens or None,
        )

        await self._db.commit()

        return {
            "role": "assistant",
            "content": answer.answer,
            "follow_up_suggestions": answer.follow_up_suggestions,
            "session_id": session_id,
        }

    async def get_session_history(self, session_id: str) -> list[dict]:
        """Return all messages for a session as a list of dicts."""
        messages = await self._messages.get_session_history(session_id)
        return [
            {
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]
