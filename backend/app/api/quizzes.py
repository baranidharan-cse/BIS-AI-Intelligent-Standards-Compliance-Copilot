"""
Quizzes router.

POST /api/quizzes/generate           — generate a quiz for a material
GET  /api/quizzes/{quiz_id}          — get quiz with questions (no answers)
POST /api/quizzes/{quiz_id}/attempts — submit a quiz attempt
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


class GenerateQuizRequest(BaseModel):
    material_id: int
    num_questions: int = 5
    difficulty: str = "mixed"


class SubmitAttemptRequest(BaseModel):
    answers: dict[str, str]


@router.post("/generate")
async def generate_quiz(
    body: GenerateQuizRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generate a quiz for a material and return it without correct answers."""
    try:
        svc = QuizService(db)
        quiz = await svc.generate_for_material(
            material_id=body.material_id,
            num_questions=body.num_questions,
            difficulty=body.difficulty,
        )
        result = await svc.get_quiz_with_questions(quiz.id)
        if not result:
            raise HTTPException(status_code=404, detail="Not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{quiz_id}")
async def get_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return a quiz with questions (correct answers hidden)."""
    try:
        svc = QuizService(db)
        result = await svc.get_quiz_with_questions(quiz_id)
        if not result:
            raise HTTPException(status_code=404, detail="Not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{quiz_id}/attempts")
async def submit_attempt(
    quiz_id: int,
    body: SubmitAttemptRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Submit answers for a quiz attempt and receive scored feedback."""
    try:
        svc = QuizService(db)
        result = await svc.submit_attempt(quiz_id=quiz_id, answers=body.answers)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
