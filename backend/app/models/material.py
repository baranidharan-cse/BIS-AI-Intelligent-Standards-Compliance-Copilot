"""
Material, Section, and Concept models.

A Material is an uploaded study document (PDF, text, URL, etc.).
Sections are top-level chapters extracted during ingestion.
Concepts are atomic knowledge units extracted from a section.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MaterialType(str, enum.Enum):
    PDF = "pdf"
    TEXT = "text"
    URL = "url"
    VIDEO = "video"


class MaterialStatus(str, enum.Enum):
    PENDING = "pending"        # uploaded, not yet processed
    PROCESSING = "processing"  # ingestion pipeline running
    READY = "ready"            # fully ingested and indexed
    ERROR = "error"            # ingestion failed


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    material_type: Mapped[MaterialType] = mapped_column(
        Enum(MaterialType), nullable=False, default=MaterialType.TEXT
    )
    status: Mapped[MaterialStatus] = mapped_column(
        Enum(MaterialStatus), nullable=False, default=MaterialStatus.PENDING
    )
    # Path to original file on disk (or URL for web content)
    source_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    # Raw extracted text — populated during ingestion
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    # LLM-generated summary of the whole material
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    sections: Mapped[list["Section"]] = relationship(
        "Section", back_populates="material", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Material id={self.id} title={self.title!r} status={self.status}>"


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    material_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    material: Mapped["Material"] = relationship("Material", back_populates="sections")
    concepts: Mapped[list["Concept"]] = relationship(
        "Concept", back_populates="section", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Section id={self.id} title={self.title!r}>"


class Concept(Base):
    """An atomic knowledge unit extracted from a section."""

    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    section_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    examples: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as text
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    section: Mapped["Section"] = relationship("Section", back_populates="concepts")

    def __repr__(self) -> str:
        return f"<Concept id={self.id} name={self.name!r}>"
