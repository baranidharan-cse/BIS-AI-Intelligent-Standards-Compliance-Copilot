"""
MaterialService — ingestion pipeline and material management.

Orchestrates text/file ingestion via the LLM service, persists ORM objects,
and provides read helpers for the API layer.
"""

from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.material import Material, MaterialStatus
from app.repositories.material_repository import (
    ConceptRepository,
    MaterialRepository,
    SectionRepository,
)
from app.services.llm.base import get_llm_service


class MaterialService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._materials = MaterialRepository(db)
        self._sections = SectionRepository(db)
        self._concepts = ConceptRepository(db)

    async def ingest_text(
        self,
        title: str,
        raw_text: str,
        description: str = "",
    ) -> Material:
        """Ingest raw text: analyse with LLM, persist sections + concepts."""
        material = await self._materials.create(
            title=title,
            description=description,
            status=MaterialStatus.PENDING,
        )
        try:
            await self._materials.update(material.id, status=MaterialStatus.PROCESSING)
            await self._db.commit()

            analysis = await get_llm_service().analyse_content(raw_text, title)

            await self._materials.update(
                material.id,
                summary=analysis.summary,
                status=MaterialStatus.READY,
                raw_text=raw_text,
            )

            for sec_data in analysis.sections:
                section = await self._sections.create(
                    material_id=material.id,
                    title=sec_data.get("title", ""),
                    order_index=sec_data.get("order_index", 0),
                    content=sec_data.get("content"),
                    summary=sec_data.get("summary"),
                )
                for concept_data in sec_data.get("concepts", []):
                    examples = concept_data.get("examples", [])
                    await self._concepts.create(
                        section_id=section.id,
                        name=concept_data.get("name", ""),
                        definition=concept_data.get("definition"),
                        explanation=concept_data.get("explanation"),
                        examples=json.dumps(examples) if examples else None,
                        order_index=concept_data.get("order_index", 0),
                    )

            await self._db.commit()
            await self._db.refresh(material)
            return material

        except Exception:
            await self._materials.update(material.id, status=MaterialStatus.ERROR)
            await self._db.commit()
            raise

    @staticmethod
    def _extract_text_from_file_bytes(file_bytes: bytes, filename: str) -> str:
        """Extract text from uploaded file bytes (.txt, .md, .pdf)."""
        if filename.lower().endswith(".pdf") or file_bytes.startswith(b"%PDF"):
            import re
            text_chunks = []
            for match in re.finditer(rb"\((.*?)\)\s*Tj", file_bytes, re.DOTALL):
                try:
                    text_chunks.append(match.group(1).decode("utf-8", errors="ignore"))
                except Exception:
                    pass
            for match in re.finditer(rb"\[(.*?)\]\s*TJ", file_bytes, re.DOTALL):
                try:
                    sub_matches = re.findall(rb"\((.*?)\)", match.group(1))
                    for sub in sub_matches:
                        text_chunks.append(sub.decode("utf-8", errors="ignore"))
                except Exception:
                    pass
            extracted = "\n".join(chunk for chunk in text_chunks if chunk.strip())
            if len(extracted.strip()) > 50:
                return extracted

        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1", errors="ignore")

    async def ingest_file(
        self,
        title: str,
        file_bytes: bytes,
        filename: str,
        description: str = "",
    ) -> Material:
        """Extract text from uploaded file bytes (TXT, PDF, MD), then ingest."""
        raw_text = self._extract_text_from_file_bytes(file_bytes, filename)
        return await self.ingest_text(title, raw_text, description)

    async def get_material_detail(self, material_id: int) -> dict:
        """Return a material with its sections and concepts as a nested dict."""
        material = await self._materials.get_with_sections(material_id)
        if material is None:
            return {}
        sections_out = []
        for section in material.sections:
            concepts = await self._concepts.get_by_section(section.id)
            sections_out.append(
                {
                    "id": section.id,
                    "title": section.title,
                    "order_index": section.order_index,
                    "summary": section.summary,
                    "content": section.content,
                    "concepts": [
                        {
                            "id": c.id,
                            "name": c.name,
                            "definition": c.definition,
                            "explanation": c.explanation,
                            "examples": json.loads(c.examples) if c.examples else [],
                            "order_index": c.order_index,
                        }
                        for c in concepts
                    ],
                }
            )
        return {
            "id": material.id,
            "title": material.title,
            "description": material.description,
            "status": material.status,
            "summary": material.summary,
            "created_at": material.created_at.isoformat(),
            "sections": sections_out,
        }

    async def list_materials(self) -> list[Material]:
        """Return all materials."""
        return await self._materials.get_all()

    async def delete_material(self, material_id: int) -> bool:
        """Delete a material by ID. Returns True if deleted."""
        result = await self._materials.delete(material_id)
        await self._db.commit()
        return result
