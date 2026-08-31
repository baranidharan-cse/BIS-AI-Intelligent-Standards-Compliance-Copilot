"""
RevisionPlan and RevisionTask models.

A RevisionPlan is an AI-generated spaced-repetition schedule for a Material.
RevisionTasks are individual scheduled review events for a Concept.
"""

import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
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


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    OVERDUE = "overdue"


class RevisionPlan(Base):
    __tablename__ = "revision_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    material_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    tasks: Mapped[list["RevisionTask"]] = relationship(
        "RevisionTask", back_populates="revision_plan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<RevisionPlan id={self.id} title={self.title!r}>"


class RevisionTask(Base):
    __tablename__ = "revision_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    revision_plan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("revision_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    concept_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True
    )
    section_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("sections.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING
    )
    # Spaced-repetition interval in days (e.g. 1, 3, 7, 14, 30)
    interval_days: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    revision_plan: Mapped["RevisionPlan"] = relationship(
        "RevisionPlan", back_populates="tasks"
    )

    def __repr__(self) -> str:
        return f"<RevisionTask id={self.id} title={self.title!r} due={self.due_date}>"
