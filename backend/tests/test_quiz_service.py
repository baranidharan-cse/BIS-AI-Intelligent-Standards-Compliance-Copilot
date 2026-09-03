"""Tests for QuizService — quiz generation and attempt scoring."""
import pytest
import pytest_asyncio
from app.services.quiz_service import QuizService
from app.services.material_service import MaterialService


@pytest.mark.asyncio
async def test_generate_quiz_creates_questions(db):
    """generate_for_material creates a quiz with the requested number of questions."""
    # First create a material with concepts
    svc = MaterialService(db)
    material = await svc.ingest_text(
        title="Python Basics",
        raw_text="Python variables, functions, loops, data types"
    )

    quiz_svc = QuizService(db)
    quiz = await quiz_svc.generate_for_material(
        material_id=material.id,
        num_questions=3,
        difficulty="mixed"
    )

    assert quiz.id is not None
    assert quiz.material_id == material.id

    detail = await quiz_svc.get_quiz_with_questions(quiz.id)
    assert len(detail["questions"]) == 3
    # Correct answers must be hidden
    for q in detail["questions"]:
        assert "correct_answer" not in q


@pytest.mark.asyncio
async def test_submit_attempt_scores_correctly(db):
    """submit_attempt calculates score based on correct answers."""
    svc = MaterialService(db)
    material = await svc.ingest_text(title="Python", raw_text="Python fundamentals")

    quiz_svc = QuizService(db)
    quiz = await quiz_svc.generate_for_material(material_id=material.id, num_questions=3)
    detail = await quiz_svc.get_quiz_with_questions(quiz.id)
    questions = detail["questions"]

    # Submit with no answers (all wrong)
    empty_answers = {str(q["id"]): "" for q in questions}
    result = await quiz_svc.submit_attempt(quiz.id, empty_answers)
    assert result["score"] == 0.0
    assert result["correct_count"] == 0
    assert result["total_questions"] == len(questions)


@pytest.mark.asyncio
async def test_get_quiz_returns_none_for_missing(db):
    """get_quiz_with_questions returns empty dict for non-existent quiz."""
    quiz_svc = QuizService(db)
    result = await quiz_svc.get_quiz_with_questions(99999)
    assert result == {}
