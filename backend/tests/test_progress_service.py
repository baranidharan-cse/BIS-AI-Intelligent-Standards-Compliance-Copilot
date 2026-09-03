"""Tests for ProgressService — dashboard statistics aggregation."""
import pytest
from app.services.progress_service import ProgressService
from app.services.material_service import MaterialService


@pytest.mark.asyncio
async def test_get_dashboard_stats(db):
    """get_dashboard_stats returns valid aggregated metrics."""
    mat_svc = MaterialService(db)
    await mat_svc.ingest_text(title="Demo Material", raw_text="Sample text content")

    prog_svc = ProgressService(db)
    stats = await prog_svc.get_dashboard_stats()

    assert "total_materials" in stats
    assert "total_concepts" in stats
    assert "mastered_concepts" in stats
    assert "avg_mastery_pct" in stats
    assert "due_today" in stats
    assert "total_quizzes_taken" in stats
    assert "avg_quiz_score" in stats
    assert stats["total_materials"] >= 1


@pytest.mark.asyncio
async def test_get_profile_stats(db):
    """get_profile_stats returns detailed material progress and badges."""
    mat_svc = MaterialService(db)
    await mat_svc.ingest_text(title="Profile Material", raw_text="Sample text content")

    prog_svc = ProgressService(db)
    profile = await prog_svc.get_profile_stats()

    assert "dashboard" in profile
    assert "materials_progress" in profile
    assert "total_study_time_minutes" in profile
    assert "total_tasks_completed" in profile
    assert "badges" in profile
    assert len(profile["badges"]) >= 5

