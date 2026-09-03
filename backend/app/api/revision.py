"""
Revision router.

POST  /api/revision/plans/generate        — generate a revision plan for a material
GET   /api/revision/tasks/due             — get tasks due today
PATCH /api/revision/tasks/{task_id}/complete — mark a task complete
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.revision_service import RevisionService

router = APIRouter(prefix="/api/revision", tags=["revision"])


class GeneratePlanRequest(BaseModel):
    material_id: int


@router.post("/plans/generate")
async def generate_revision_plan(
    body: GeneratePlanRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generate a spaced-repetition revision plan for a material."""
    try:
        svc = RevisionService(db)
        plan = await svc.create_plan_for_material(body.material_id)
        return {
            "id": plan.id,
            "title": plan.title,
            "material_id": plan.material_id,
            "created_at": plan.created_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/due")
async def get_due_tasks(db: AsyncSession = Depends(get_db)) -> list[dict]:
    """Return all revision tasks that are due today or overdue."""
    try:
        svc = RevisionService(db)
        return await svc.get_due_tasks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Mark a revision task as complete and schedule the next review."""
    try:
        svc = RevisionService(db)
        task = await svc.complete_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Not found")
        return {
            "id": task.id,
            "revision_plan_id": task.revision_plan_id,
            "concept_id": task.concept_id,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "interval_days": task.interval_days,
            "status": task.status,
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
