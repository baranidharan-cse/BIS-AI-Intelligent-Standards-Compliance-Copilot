"""
ProgressService — dashboard statistics aggregated across all materials.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.material import Material, MaterialStatus
from app.models.progress import ConceptMastery, MaterialProgress
from app.models.quiz import QuizAttempt
from app.models.revision import RevisionTask, TaskStatus


class ProgressService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_dashboard_stats(self) -> dict:
        """Return aggregated progress statistics for the dashboard."""
        # total_materials — count of READY materials
        result = await self._db.execute(
            select(func.count()).where(Material.status == MaterialStatus.READY)
        )
        total_materials: int = result.scalar_one()

        # total_concepts — count of all concepts (via ConceptMastery rows or
        # directly from the concepts table — use ConceptMastery which tracks
        # reviewed concepts; fall back to raw concept count via a join-free query)
        from app.models.material import Concept

        result = await self._db.execute(select(func.count()).select_from(Concept))
        total_concepts: int = result.scalar_one()

        # mastered_concepts — ConceptMastery rows with score >= 0.8
        result = await self._db.execute(
            select(func.count()).where(ConceptMastery.score >= 0.8)
        )
        mastered_concepts: int = result.scalar_one()

        avg_mastery_pct = (
            round(mastered_concepts / total_concepts * 100, 1)
            if total_concepts > 0
            else 0.0
        )

        # due_today — pending revision tasks due on or before today
        today = date.today()
        result = await self._db.execute(
            select(func.count()).where(
                RevisionTask.due_date <= today,
                RevisionTask.status == TaskStatus.PENDING,
            )
        )
        due_today: int = result.scalar_one()

        # total_quizzes_taken — completed QuizAttempt rows
        result = await self._db.execute(
            select(func.count()).where(QuizAttempt.completed == True)  # noqa: E712
        )
        total_quizzes_taken: int = result.scalar_one()

        # avg_quiz_score — average score of completed attempts (0–100)
        result = await self._db.execute(
            select(func.avg(QuizAttempt.score)).where(QuizAttempt.completed == True)  # noqa: E712
        )
        raw_avg = result.scalar_one()
        avg_quiz_score = round((raw_avg or 0.0) * 100, 1)

        return {
            "total_materials": total_materials,
            "total_concepts": total_concepts,
            "mastered_concepts": mastered_concepts,
            "avg_mastery_pct": avg_mastery_pct,
            "due_today": due_today,
            "total_quizzes_taken": total_quizzes_taken,
            "avg_quiz_score": avg_quiz_score,
        }

    async def get_profile_stats(self) -> dict:
        """Return detailed profile metrics, per-material progress, and achievements."""
        dashboard = await self.get_dashboard_stats()

        # Per-material progress
        m_result = await self._db.execute(
            select(Material).where(Material.status == MaterialStatus.READY)
        )
        ready_materials = list(m_result.scalars().all())

        materials_progress = []
        total_study_time = 0
        for mat in ready_materials:
            mp_result = await self._db.execute(
                select(MaterialProgress).where(MaterialProgress.material_id == mat.id)
            )
            mp = mp_result.scalars().first()
            mastery_pct = round((mp.mastery_score if mp else 0.0) * 100)
            completion_pct = round((mp.steps_completion if mp else 0.0) * 100)
            time_studied = mp.time_studied_minutes if mp else 0
            total_study_time += time_studied

            materials_progress.append(
                {
                    "id": mat.id,
                    "title": mat.title,
                    "mastery_pct": mastery_pct,
                    "completion_pct": completion_pct,
                    "time_studied_minutes": time_studied,
                }
            )

        # Total tasks completed
        t_result = await self._db.execute(
            select(func.count()).where(RevisionTask.status == TaskStatus.COMPLETED)
        )
        total_tasks_completed: int = t_result.scalar_one()

        # Badges evaluation
        badges = [
            {
                "id": "starter",
                "title": "Quick Starter",
                "icon": "🚀",
                "description": "Ingested your first study material",
                "unlocked": dashboard["total_materials"] >= 1,
            },
            {
                "id": "quiz_apprentice",
                "title": "Quiz Apprentice",
                "icon": "✏️",
                "description": "Completed at least 1 quiz attempt",
                "unlocked": dashboard["total_quizzes_taken"] >= 1,
            },
            {
                "id": "mastery_pro",
                "title": "Concept Master",
                "icon": "🧠",
                "description": "Mastered 5 or more concepts",
                "unlocked": dashboard["mastered_concepts"] >= 5,
            },
            {
                "id": "revision_hero",
                "title": "Revision Hero",
                "icon": "🔁",
                "description": "Completed 3 or more spaced-repetition reviews",
                "unlocked": total_tasks_completed >= 1,
            },
            {
                "id": "scholar",
                "title": "Scholar",
                "icon": "🎓",
                "description": "Achieved average quiz score >= 80%",
                "unlocked": dashboard["avg_quiz_score"] >= 80.0 and dashboard["total_quizzes_taken"] > 0,
            },
        ]

        return {
            "dashboard": dashboard,
            "materials_progress": materials_progress,
            "total_study_time_minutes": total_study_time,
            "total_tasks_completed": total_tasks_completed,
            "badges": badges,
        }

