"""
RevisionService — spaced-repetition revision plans and task management.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revision import RevisionPlan, RevisionTask, TaskStatus
from app.repositories.material_repository import ConceptRepository, SectionRepository
from app.repositories.progress_repository import ConceptMasteryRepository
from app.repositories.revision_repository import (
    RevisionPlanRepository,
    RevisionTaskRepository,
)

# Standard spaced-repetition intervals in days
_SR_INTERVALS = [1, 3, 7, 14, 30]


class RevisionService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._plans = RevisionPlanRepository(db)
        self._tasks = RevisionTaskRepository(db)
        self._sections = SectionRepository(db)
        self._concepts = ConceptRepository(db)
        self._mastery = ConceptMasteryRepository(db)

    async def create_plan_for_material(self, material_id: int) -> RevisionPlan:
        """Create a spaced-repetition plan for every concept in the material."""
        sections = await self._sections.get_by_material(material_id)
        all_concepts = []
        for section in sections:
            concepts = await self._concepts.get_by_section(section.id)
            all_concepts.extend(concepts)

        today = date.today()
        end = today + timedelta(days=_SR_INTERVALS[-1])

        plan = await self._plans.create(
            material_id=material_id,
            title=f"Revision Plan — Material {material_id}",
            description="Auto-generated spaced-repetition plan.",
            start_date=today,
            end_date=end,
        )

        for concept in all_concepts:
            for interval in _SR_INTERVALS:
                due = today + timedelta(days=interval)
                await self._tasks.create(
                    revision_plan_id=plan.id,
                    concept_id=concept.id,
                    title=f"Review: {concept.name}",
                    due_date=due,
                    interval_days=interval,
                    status=TaskStatus.PENDING,
                    completed=False,
                )

        await self._db.commit()
        await self._db.refresh(plan)
        return plan

    async def get_due_tasks(self) -> list[dict]:
        """Return all pending tasks due today or earlier, with concept name."""
        tasks = await self._tasks.get_due_today()
        result = []
        for task in tasks:
            concept_name = None
            if task.concept_id is not None:
                concept = await self._concepts.get_by_id(task.concept_id)
                concept_name = concept.name if concept else None
            result.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "due_date": task.due_date.isoformat(),
                    "interval_days": task.interval_days,
                    "status": task.status,
                    "concept_id": task.concept_id,
                    "concept_name": concept_name,
                    "revision_plan_id": task.revision_plan_id,
                }
            )
        return result

    async def complete_task(self, task_id: int) -> RevisionTask:
        """Mark a task complete, update mastery, and schedule next interval."""
        task = await self._tasks.get_by_id(task_id)
        if task is None:
            raise ValueError(f"RevisionTask {task_id} not found")

        now = datetime.now(timezone.utc)
        await self._tasks.update(
            task_id,
            completed=True,
            status=TaskStatus.COMPLETED,
            completed_at=now,
        )

        # Update ConceptMastery
        if task.concept_id is not None:
            mastery = await self._mastery.get_by_concept(task.concept_id)
            if mastery is None:
                await self._mastery.create(
                    concept_id=task.concept_id,
                    score=0.1,
                    review_count=1,
                    last_reviewed_at=now,
                )
            else:
                new_score = min(1.0, mastery.score + 0.1)
                await self._mastery.update(
                    mastery.id,
                    score=new_score,
                    review_count=mastery.review_count + 1,
                    last_reviewed_at=now,
                )

        # Schedule next task at the next interval in the sequence
        current_interval = task.interval_days
        try:
            next_idx = _SR_INTERVALS.index(current_interval) + 1
        except ValueError:
            next_idx = len(_SR_INTERVALS)  # unknown interval → no next task

        if next_idx < len(_SR_INTERVALS):
            next_interval = _SR_INTERVALS[next_idx]
            next_due = date.today() + timedelta(days=next_interval)
            await self._tasks.create(
                revision_plan_id=task.revision_plan_id,
                concept_id=task.concept_id,
                title=task.title,
                due_date=next_due,
                interval_days=next_interval,
                status=TaskStatus.PENDING,
                completed=False,
            )

        await self._db.commit()
        updated = await self._tasks.get_by_id(task_id)
        return updated
