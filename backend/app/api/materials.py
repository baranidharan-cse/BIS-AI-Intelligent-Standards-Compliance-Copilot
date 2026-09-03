"""
Materials router.

POST /api/materials/upload — ingest an uploaded file
POST /api/materials/        — ingest raw text
GET  /api/materials/        — list all materials
GET  /api/materials/{id}    — material detail (sections + concepts)
DELETE /api/materials/{id}  — delete a material
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.material_service import MaterialService

router = APIRouter(prefix="/api/materials", tags=["materials"])


class CreateMaterialRequest(BaseModel):
    title: str
    raw_text: str
    description: str = ""


@router.get("")
async def list_materials(db: AsyncSession = Depends(get_db)) -> list[dict]:
    """Return a summary list of all materials."""
    try:
        svc = MaterialService(db)
        materials = await svc.list_materials()
        return [
            {
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "status": m.status,
                "material_type": m.material_type,
                "created_at": m.created_at.isoformat(),
                "summary": m.summary,
            }
            for m in materials
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_material(
    body: CreateMaterialRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Ingest raw text and return the created material."""
    try:
        svc = MaterialService(db)
        material = await svc.ingest_text(
            title=body.title,
            raw_text=body.raw_text,
            description=body.description,
        )
        return await svc.get_material_detail(material.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_material(
    file: UploadFile,
    title: str | None = Form(default=None),
    description: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Upload a txt/pdf file and ingest its content."""
    try:
        file_bytes = await file.read()
        resolved_title = title or file.filename or "Untitled"
        svc = MaterialService(db)
        material = await svc.ingest_file(
            title=resolved_title,
            file_bytes=file_bytes,
            filename=file.filename or "",
            description=description,
        )
        return await svc.get_material_detail(material.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{material_id}")
async def get_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return a material with its sections and concepts."""
    try:
        svc = MaterialService(db)
        detail = await svc.get_material_detail(material_id)
        if not detail:
            raise HTTPException(status_code=404, detail="Not found")
        return detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{material_id}")
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete a material by ID."""
    try:
        svc = MaterialService(db)
        deleted = await svc.delete_material(material_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Not found")
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ExplainConceptRequest(BaseModel):
    topic_name: str
    context: str = ""
    difficulty_level: str = "high_school"  # "eli10" | "high_school" | "exam_summary"


@router.post("/explain")
async def explain_topic(
    body: ExplainConceptRequest,
) -> dict:
    """Generate an AI topic explanation at specified difficulty level (eli10, high_school, exam_summary)."""
    try:
        from app.services.llm.base import get_llm_service
        explanation = await get_llm_service().explain_topic(
            topic_name=body.topic_name,
            context=body.context,
            difficulty_level=body.difficulty_level,
        )
        return {
            "topic": explanation.topic,
            "explanation": explanation.explanation,
            "examples": explanation.examples,
            "key_points": explanation.key_points,
            "analogies": explanation.analogies,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

