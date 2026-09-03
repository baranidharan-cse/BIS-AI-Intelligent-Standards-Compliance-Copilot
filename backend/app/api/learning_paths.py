"""
Learning paths router.

POST  /api/learning-paths/generate            — generate a path for a material
GET   /api/learning-paths/{path_id}           — get path with steps
PATCH /api/learning-paths/steps/{step_id}/status — update step status
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.learning_path_service import LearningPathService

router = APIRouter(prefix="/api/learning-paths", tags=["learning-paths"])


class GeneratePathRequest(BaseModel):
    material_id: int
    learner_goal: str = ""


class UpdateStepStatusRequest(BaseModel):
    status: str


@router.post("/generate")
async def generate_learning_path(
    body: GeneratePathRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generate a learning path for a material."""
    try:
        svc = LearningPathService(db)
        path = await svc.generate_for_material(
            material_id=body.material_id,
            learner_goal=body.learner_goal,
        )
        return await svc.get_path_with_steps(path.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{path_id}")
async def get_learning_path(
    path_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return a learning path and its ordered steps."""
    try:
        svc = LearningPathService(db)
        path = await svc.get_path_with_steps(path_id)
        if not path:
            raise HTTPException(status_code=404, detail="Not found")
        return path
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/steps/{step_id}/status")
async def update_step_status(
    step_id: int,
    body: UpdateStepStatusRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Update the status of a learning path step."""
    try:
        svc = LearningPathService(db)
        step = await svc.update_step_status(step_id=step_id, status=body.status)
        if step is None:
            raise HTTPException(status_code=404, detail="Not found")
        return {
            "id": step.id,
            "learning_path_id": step.learning_path_id,
            "title": step.title,
            "description": step.description,
            "order_index": step.order_index,
            "estimated_minutes": step.estimated_minutes,
            "status": step.status,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
