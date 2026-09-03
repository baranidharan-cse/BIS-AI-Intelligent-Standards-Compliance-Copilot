"""
LearningPathService — generate and manage AI-driven learning paths.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning_path import LearningPath, LearningStep, StepStatus
from app.models.progress import MaterialProgress
from app.repositories.learning_path_repository import (
    LearningPathRepository,
    LearningStepRepository,
)
from app.repositories.material_repository import (
    ConceptRepository,
    MaterialRepository,
)
from app.repositories.progress_repository import MaterialProgressRepository
from app.services.llm.base import get_llm_service


class LearningPathService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._paths = LearningPathRepository(db)
        self._steps = LearningStepRepository(db)
        self._materials = MaterialRepository(db)
        self._concepts = ConceptRepository(db)
        self._progress = MaterialProgressRepository(db)

    async def generate_for_material(
        self,
        material_id: int,
        learner_goal: str = "",
    ) -> LearningPath:
        """Generate and persist a learning path for a material."""
        material = await self._materials.get_with_sections(material_id)
        if material is None:
            raise ValueError(f"Material {material_id} not found")

        sections_list: list[dict] = []
        for section in material.sections:
            concepts = await self._concepts.get_by_section(section.id)
            sections_list.append(
                {
                    "title": section.title,
                    "concepts": [{"name": c.name} for c in concepts],
                }
            )

        generated = await get_llm_service().generate_learning_path(
            material.title, sections_list, learner_goal
        )

        path = await self._paths.create(
            material_id=material_id,
            title=generated.title,
            description=generated.description,
            estimated_duration_minutes=generated.estimated_duration_minutes,
        )

        for step_data in generated.steps:
            prerequisites_raw = step_data.get("prerequisites", [])
            prerequisites_str = (
                ",".join(str(p) for p in prerequisites_raw) if prerequisites_raw else None
            )
            await self._steps.create(
                learning_path_id=path.id,
                title=step_data.get("title", ""),
                description=step_data.get("description"),
                order_index=step_data.get("order_index", 0),
                estimated_minutes=step_data.get("estimated_minutes", 10),
                prerequisites=prerequisites_str,
                status=StepStatus.NOT_STARTED,
            )

        await self._db.commit()
        await self._db.refresh(path)
        return path

    async def get_path_with_steps(self, path_id: int) -> dict:
        """Return a learning path and its ordered steps as a dict."""
        path = await self._paths.get_by_id(path_id)
        if path is None:
            return {}
        steps = await self._steps.get_by_path(path_id)
        return {
            "id": path.id,
            "material_id": path.material_id,
            "title": path.title,
            "description": path.description,
            "estimated_duration_minutes": path.estimated_duration_minutes,
            "created_at": path.created_at.isoformat(),
            "steps": [
                {
                    "id": s.id,
                    "title": s.title,
                    "description": s.description,
                    "order_index": s.order_index,
                    "estimated_minutes": s.estimated_minutes,
                    "status": s.status,
                    "prerequisites": s.prerequisites,
                }
                for s in steps
            ],
        }

    async def update_step_status(self, step_id: int, status: str) -> LearningStep:
        """Update a step's status and recalculate MaterialProgress.steps_completion."""
        step = await self._steps.get_by_id(step_id)
        if step is None:
            raise ValueError(f"LearningStep {step_id} not found")

        await self._steps.update(step_id, status=StepStatus(status))

        # Recalculate steps_completion for the material
        path = await self._paths.get_by_id(step.learning_path_id)
        if path is not None:
            all_steps = await self._steps.get_by_path(path.id)
            if all_steps:
                completed = sum(
                    1 for s in all_steps if s.status == StepStatus.COMPLETED
                )
                completion = completed / len(all_steps)
                mp = await self._progress.get_by_material(path.material_id)
                if mp is None:
                    await self._progress.create(
                        material_id=path.material_id,
                        steps_completion=completion,
                    )
                else:
                    await self._progress.update(mp.id, steps_completion=completion)

        await self._db.commit()
        updated = await self._steps.get_by_id(step_id)
        return updated
