"""
LearningPath and LearningStep models.

A LearningPath is an AI-generated, ordered sequence of steps for mastering
a Material. Each LearningStep corresponds to a Concept or Section and carries
estimated study time and prerequisites.
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


class StepStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    material_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Estimated total duration in minutes
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
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
    steps: Mapped[list["LearningStep"]] = relationship(
        "LearningStep", back_populates="learning_path", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<LearningPath id={self.id} title={self.title!r}>"


class LearningStep(Base):
    __tablename__ = "learning_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    learning_path_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("learning_paths.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Optional FK to a concept or section (nullable — some steps may be synthetic)
    concept_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True
    )
    section_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("sections.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    status: Mapped[StepStatus] = mapped_column(
        Enum(StepStatus), nullable=False, default=StepStatus.NOT_STARTED
    )
    # Comma-separated step IDs this step depends on (kept simple for SQLite)
    prerequisites: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    learning_path: Mapped["LearningPath"] = relationship(
        "LearningPath", back_populates="steps"
    )

    def __repr__(self) -> str:
        return f"<LearningStep id={self.id} title={self.title!r} order={self.order_index}>"
