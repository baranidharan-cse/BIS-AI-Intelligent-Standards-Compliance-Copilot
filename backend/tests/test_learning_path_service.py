"""Tests for LearningPathService — path generation and step updates."""
import pytest
from app.services.learning_path_service import LearningPathService
from app.services.material_service import MaterialService
from app.models.learning_path import StepStatus


@pytest.mark.asyncio
async def test_generate_and_update_learning_path(db):
    """generate_for_material creates a path; update_step_status updates completion."""
    mat_svc = MaterialService(db)
    mat = await mat_svc.ingest_text(title="Calculus", raw_text="Derivatives and integrals")

    lp_svc = LearningPathService(db)
    path = await lp_svc.generate_for_material(mat.id, learner_goal="Master calculus")

    assert path.id is not None
    assert path.material_id == mat.id

    detail = await lp_svc.get_path_with_steps(path.id)
    assert len(detail["steps"]) > 0

    first_step = detail["steps"][0]
    updated_step = await lp_svc.update_step_status(first_step["id"], "completed")
    assert updated_step.status == StepStatus.COMPLETED


@pytest.mark.asyncio
async def test_invalid_material_raises_error(db):
    """generate_for_material raises ValueError for invalid material_id."""
    lp_svc = LearningPathService(db)
    with pytest.raises(ValueError, match="Material 99999 not found"):
        await lp_svc.generate_for_material(99999)
