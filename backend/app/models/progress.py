"""
Progress and Mastery models.

Mastery tracks how well a user knows each Concept (0.0 – 1.0).
Progress tracks aggregate completion at the Material level.
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ConceptMastery(Base):
    """
    Per-concept mastery score for the user.
    Score ranges from 0.0 (unseen) to 1.0 (fully mastered).
    Updated after each quiz attempt and revision task completion.
    """

    __tablename__ = "concept_mastery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    concept_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("concepts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # How many times the concept has been reviewed
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ConceptMastery concept_id={self.concept_id} score={self.score:.2f}>"


class MaterialProgress(Base):
    """
    Aggregate progress for the user on a Material.
    Derived from step completion and concept mastery — kept in sync by services.
    """

    __tablename__ = "material_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    material_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    # 0.0 – 1.0 completion of learning path steps
    steps_completion: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # 0.0 – 1.0 average concept mastery across the material
    mastery_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Total time studied in minutes
    time_studied_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<MaterialProgress material_id={self.material_id} "
            f"mastery={self.mastery_score:.2f}>"
        )
