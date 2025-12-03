"""
Interview session database model.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class InterviewSession(Base):
    """Interview session model for tracking interview practice sessions."""

    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=True)
    transcript: Mapped[str] = mapped_column(Text, nullable=True)
    audio_s3_key: Mapped[str] = mapped_column(String(500), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)

    # Feedback scores
    overall_score: Mapped[float] = mapped_column(Float, nullable=True)
    communication_score: Mapped[float] = mapped_column(Float, nullable=True)
    technical_score: Mapped[float] = mapped_column(Float, nullable=True)
    clarity_score: Mapped[float] = mapped_column(Float, nullable=True)

    # Detailed feedback
    strengths: Mapped[dict] = mapped_column(JSON, nullable=True)  # List of strengths
    improvements: Mapped[dict] = mapped_column(JSON, nullable=True)  # List of improvements
    detailed_feedback: Mapped[str] = mapped_column(Text, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<InterviewSession(id={self.id}, user_id={self.user_id}, title={self.title})>"
