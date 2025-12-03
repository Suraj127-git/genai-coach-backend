"""
Interview session schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class InterviewSessionBase(BaseModel):
    """Base interview session schema."""
    title: str
    question: Optional[str] = None


class InterviewSessionCreate(InterviewSessionBase):
    """Schema for creating a new interview session."""
    pass


class InterviewSessionResponse(InterviewSessionBase):
    """Schema for interview session response."""
    id: str
    user_id: str
    transcript: Optional[str] = None
    audio_s3_key: Optional[str] = None
    duration_seconds: Optional[int] = None
    overall_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_model(cls, session):
        """Convert ORM model to response schema."""
        return cls(
            id=str(session.id),
            user_id=str(session.user_id),
            title=session.title,
            question=session.question,
            transcript=session.transcript,
            audio_s3_key=session.audio_s3_key,
            duration_seconds=session.duration_seconds,
            overall_score=session.overall_score,
            created_at=session.created_at,
            completed_at=session.completed_at,
        )


class InterviewSessionListItem(BaseModel):
    """Schema for interview session list item."""
    id: str
    title: str
    date: str  # Formatted date string
    duration: str  # Formatted duration string
    score: Optional[float] = None


class InterviewSessionStats(BaseModel):
    """Schema for interview session statistics."""
    total: int
    average: float
    improvement: float


class InterviewSessionList(BaseModel):
    """Schema for interview session list response."""
    sessions: List[InterviewSessionListItem]
    stats: InterviewSessionStats


class InterviewFeedback(BaseModel):
    """Schema for interview feedback response."""
    overall_score: float
    communication_score: Optional[float] = None
    technical_score: Optional[float] = None
    clarity_score: Optional[float] = None
    strengths: List[str]
    improvements: List[str]
    detailed_feedback: str
    transcript: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
