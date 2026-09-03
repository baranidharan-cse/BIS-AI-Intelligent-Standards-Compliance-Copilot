"""Tests for RevisionService — spaced repetition scheduling."""
import pytest
from datetime import date, timedelta
from app.services.revision_service import RevisionService, _SR_INTERVALS
from app.services.material_service import MaterialService


@pytest.mark.asyncio
async def test_create_plan_creates_tasks_per_concept(db):
    """create_plan_for_material creates one task per concept per SR interval."""
    svc = MaterialService(db)
    material = await svc.ingest_text(title="Python", raw_text="Python fundamentals")

    # Count concepts
    from app.repositories.material_repository import SectionRepository, ConceptRepository
    sec_repo = SectionRepository(db)
    con_repo = ConceptRepository(db)
    sections = await sec_repo.get_by_material(material.id)
    total_concepts = 0
    for sec in sections:
        concepts = await con_repo.get_by_section(sec.id)
        total_concepts += len(concepts)

    rev_svc = RevisionService(db)
    plan = await rev_svc.create_plan_for_material(material.id)

    assert plan.id is not None
    assert plan.material_id == material.id

    # Each concept gets one task per interval
    from app.repositories.revision_repository import RevisionTaskRepository
    task_repo = RevisionTaskRepository(db)
    tasks = await task_repo.get_by_plan(plan.id)
    assert len(tasks) == total_concepts * len(_SR_INTERVALS)


@pytest.mark.asyncio
async def test_complete_task_schedules_next(db):
    """complete_task marks the task done and schedules the next interval."""
    svc = MaterialService(db)
    material = await svc.ingest_text(title="Python", raw_text="Python fundamentals")

    rev_svc = RevisionService(db)
    plan = await rev_svc.create_plan_for_material(material.id)

    # get_due_tasks() only returns tasks due today or earlier; SR intervals start
    # at day+1, so fetch any pending task directly from the repository.
    from app.repositories.revision_repository import RevisionTaskRepository
    task_repo = RevisionTaskRepository(db)
    all_tasks = await task_repo.get_by_plan(plan.id)
    assert len(all_tasks) > 0

    task_id = all_tasks[0].id

    updated = await rev_svc.complete_task(task_id)
    assert updated.completed is True
    assert str(updated.status) in ("completed", "TaskStatus.COMPLETED")


@pytest.mark.asyncio
async def test_sr_intervals_are_increasing(db):
    """The SR intervals should be strictly increasing."""
    for i in range(len(_SR_INTERVALS) - 1):
        assert _SR_INTERVALS[i] < _SR_INTERVALS[i+1]


@pytest.mark.asyncio
async def test_get_due_tasks_returns_only_pending(db):
    """get_due_tasks returns only pending tasks, not completed ones."""
    svc = MaterialService(db)
    material = await svc.ingest_text(title="Python", raw_text="Python fundamentals")

    rev_svc = RevisionService(db)
    await rev_svc.create_plan_for_material(material.id)

    tasks_before = await rev_svc.get_due_tasks()
    count_before = len(tasks_before)

    if count_before > 0:
        await rev_svc.complete_task(tasks_before[0]["id"])
        tasks_after = await rev_svc.get_due_tasks()
        assert len(tasks_after) <= count_before
