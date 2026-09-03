"""
QuizService — generate quizzes, serve questions, and score attempts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz import Quiz, QuizAttempt, QuizDifficulty, QuizQuestion
from app.repositories.material_repository import (
    ConceptRepository,
    SectionRepository,
)
from app.repositories.progress_repository import (
    ConceptMasteryRepository,
    MaterialProgressRepository,
)
from app.repositories.quiz_repository import (
    QuizAttemptRepository,
    QuizQuestionRepository,
    QuizRepository,
)
from app.services.llm.base import get_llm_service


class QuizService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._quizzes = QuizRepository(db)
        self._questions = QuizQuestionRepository(db)
        self._attempts = QuizAttemptRepository(db)
        self._sections = SectionRepository(db)
        self._concepts = ConceptRepository(db)
        self._mastery = ConceptMasteryRepository(db)
        self._progress = MaterialProgressRepository(db)

    async def generate_for_material(
        self,
        material_id: int,
        num_questions: int = 5,
        difficulty: str = "mixed",
    ) -> Quiz:
        """Generate and persist a quiz from all concepts for a material."""
        sections = await self._sections.get_by_material(material_id)
        all_concepts = []
        for section in sections:
            concepts = await self._concepts.get_by_section(section.id)
            all_concepts.extend(concepts)

        concepts_list = [
            {"name": c.name, "definition": c.definition or ""}
            for c in all_concepts
        ]

        generated = await get_llm_service().generate_quiz(
            concepts_list, num_questions, difficulty
        )

        quiz = await self._quizzes.create(
            material_id=material_id,
            title=generated.title,
            difficulty=QuizDifficulty(generated.difficulty)
            if generated.difficulty in QuizDifficulty._value2member_map_
            else QuizDifficulty.MIXED,
        )

        # Build a name→concept lookup so we can attach concept_id when possible
        name_to_concept = {c.name: c for c in all_concepts}

        for q_data in generated.questions:
            options = q_data.get("options")
            concept_name = q_data.get("concept_name")
            # Try to resolve concept_id from question text if not provided
            matched_concept = None
            if concept_name:
                matched_concept = name_to_concept.get(concept_name)

            q_difficulty = q_data.get("difficulty", "medium")
            await self._questions.create(
                quiz_id=quiz.id,
                concept_id=matched_concept.id if matched_concept else None,
                question_type=q_data.get("question_type", "multiple_choice"),
                question_text=q_data.get("question_text", ""),
                options=json.dumps(options) if options else None,
                correct_answer=q_data.get("correct_answer", ""),
                explanation=q_data.get("explanation"),
                difficulty=QuizDifficulty(q_difficulty)
                if q_difficulty in QuizDifficulty._value2member_map_
                else QuizDifficulty.MEDIUM,
                order_index=q_data.get("order_index", 0),
            )

        await self._db.commit()
        await self._db.refresh(quiz)
        return quiz

    async def get_quiz_with_questions(self, quiz_id: int) -> dict:
        """Return quiz metadata and questions (correct_answer hidden)."""
        quiz = await self._quizzes.get_by_id(quiz_id)
        if quiz is None:
            return {}
        questions = await self._questions.get_by_quiz(quiz_id)
        return {
            "id": quiz.id,
            "material_id": quiz.material_id,
            "title": quiz.title,
            "difficulty": quiz.difficulty,
            "created_at": quiz.created_at.isoformat(),
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "options": json.loads(q.options) if q.options else [],
                    "difficulty": q.difficulty,
                    "order_index": q.order_index,
                }
                for q in questions
            ],
        }

    async def submit_attempt(
        self,
        quiz_id: int,
        answers: dict[str, str],
    ) -> dict:
        """Score an attempt, update mastery, and return detailed feedback."""
        quiz = await self._quizzes.get_by_id(quiz_id)
        if quiz is None:
            raise ValueError(f"Quiz {quiz_id} not found")

        questions = await self._questions.get_by_quiz(quiz_id)
        total = len(questions)
        correct_count = 0
        per_question: list[dict] = []

        for q in questions:
            user_answer = answers.get(str(q.id), "")
            is_correct = (
                user_answer.strip().lower() == q.correct_answer.strip().lower()
            )
            if is_correct:
                correct_count += 1
            per_question.append(
                {
                    "question_id": q.id,
                    "correct": is_correct,
                    "user_answer": user_answer,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                }
            )

            # Update ConceptMastery for this question's concept
            if q.concept_id is not None:
                mastery = await self._mastery.get_by_concept(q.concept_id)
                if mastery is None:
                    await self._mastery.create(
                        concept_id=q.concept_id,
                        score=(1.0 if is_correct else 0.0),
                        review_count=1,
                        last_reviewed_at=datetime.now(timezone.utc),
                    )
                else:
                    new_score = (
                        mastery.score * mastery.review_count + (1.0 if is_correct else 0.0)
                    ) / (mastery.review_count + 1)
                    await self._mastery.update(
                        mastery.id,
                        score=new_score,
                        review_count=mastery.review_count + 1,
                        last_reviewed_at=datetime.now(timezone.utc),
                    )

        score = (correct_count / total) if total > 0 else 0.0

        attempt = await self._attempts.create(
            quiz_id=quiz_id,
            answers=json.dumps(answers),
            score=score,
            total_questions=total,
            correct_count=correct_count,
            completed=True,
            completed_at=datetime.now(timezone.utc),
        )

        # Update MaterialProgress.mastery_score for this quiz's material
        quiz = await self._quizzes.get_by_id(quiz_id)
        if quiz is not None:
            sections = await self._sections.get_by_material(quiz.material_id)
            all_concept_ids: list[int] = []
            for section in sections:
                concepts = await self._concepts.get_by_section(section.id)
                all_concept_ids.extend(c.id for c in concepts)

            if all_concept_ids:
                masteries = [
                    await self._mastery.get_by_concept(cid)
                    for cid in all_concept_ids
                ]
                scored = [m.score for m in masteries if m is not None]
                avg_mastery = sum(scored) / len(all_concept_ids) if all_concept_ids else 0.0

                mp = await self._progress.get_by_material(quiz.material_id)
                if mp is None:
                    await self._progress.create(
                        material_id=quiz.material_id,
                        mastery_score=avg_mastery,
                    )
                else:
                    await self._progress.update(mp.id, mastery_score=avg_mastery)

        await self._db.commit()

        return {

            "id": attempt.id,
            "quiz_id": quiz_id,
            "score": round(score, 4),
            "correct_count": correct_count,
            "total_questions": total,
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
            "per_question": per_question,
        }
