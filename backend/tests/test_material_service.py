"""Tests for MaterialService — ingestion pipeline and material management."""
import pytest
from app.services.material_service import MaterialService
from app.models.material import MaterialStatus


@pytest.mark.asyncio
async def test_ingest_text_creates_sections_and_concepts(db):
    """ingest_text parses text, produces summary, sections, and concepts."""
    svc = MaterialService(db)
    mat = await svc.ingest_text(
        title="Python Intro",
        raw_text="Python variables and data types",
        description="Test material"
    )

    assert mat.id is not None
    assert mat.title == "Python Intro"
    assert mat.status == MaterialStatus.READY
    assert mat.summary is not None

    detail = await svc.get_material_detail(mat.id)
    assert detail["id"] == mat.id
    assert len(detail["sections"]) > 0
    assert "content" in detail["sections"][0]


@pytest.mark.asyncio
async def test_ingest_file_decodes_bytes(db):
    """ingest_file decodes utf-8 text file bytes and calls ingest_text."""
    svc = MaterialService(db)
    file_bytes = b"Machine learning basics, neural networks and deep learning."
    mat = await svc.ingest_file(
        title="ML File",
        file_bytes=file_bytes,
        filename="ml.txt",
    )

    assert mat.id is not None
    assert mat.status == MaterialStatus.READY


@pytest.mark.asyncio
async def test_list_and_delete_material(db):
    """list_materials returns all materials, delete_material removes it."""
    svc = MaterialService(db)
    mat = await svc.ingest_text(title="ToDelete", raw_text="Short text")

    materials = await svc.list_materials()
    assert any(m.id == mat.id for m in materials)

    deleted = await svc.delete_material(mat.id)
    assert deleted is True

    detail = await svc.get_material_detail(mat.id)
    assert detail == {}
