"""
Interview session service for business logic.
"""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import InterviewSession
from app.schemas.session import (
    InterviewSessionCreate,
    InterviewSessionList,
    InterviewSessionListItem,
    InterviewSessionStats,
    InterviewFeedback,
)


class SessionService:
    """Service class for interview session operations."""

    @staticmethod
    async def create_session(
        db: AsyncSession, user_id: int, session_data: InterviewSessionCreate
    ) -> InterviewSession:
        """Create a new interview session."""
        db_session = InterviewSession(
            user_id=user_id,
            title=session_data.title,
            question=session_data.question,
        )
        db.add(db_session)
        await db.flush()
        await db.refresh(db_session)
        return db_session

    @staticmethod
    async def get_session(
        db: AsyncSession, session_id: int, user_id: int
    ) -> Optional[InterviewSession]:
        """Get a specific interview session."""
        result = await db.execute(
            select(InterviewSession).where(
                InterviewSession.id == session_id,
                InterviewSession.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_sessions(
        db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[InterviewSession]:
        """Get all sessions for a user."""
        result = await db.execute(
            select(InterviewSession)
            .where(InterviewSession.user_id == user_id)
            .order_by(desc(InterviewSession.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_sessions_list(db: AsyncSession, user_id: int) -> InterviewSessionList:
        """Get formatted list of sessions with statistics."""
        sessions = await SessionService.get_user_sessions(db, user_id)

        # Format sessions for display
        session_items = []
        scores = []

        for session in sessions:
            # Format date
            date_str = session.created_at.strftime("%B %d, %Y")

            # Format duration
            duration_str = "N/A"
            if session.duration_seconds:
                minutes = session.duration_seconds // 60
                seconds = session.duration_seconds % 60
                duration_str = f"{minutes}m {seconds}s"

            session_items.append(
                InterviewSessionListItem(
                    id=str(session.id),
                    title=session.title,
                    date=date_str,
                    duration=duration_str,
                    score=session.overall_score,
                )
            )

            if session.overall_score is not None:
                scores.append(session.overall_score)

        # Calculate statistics
        total = len(sessions)
        average = sum(scores) / len(scores) if scores else 0.0

        # Calculate improvement (compare recent vs older scores)
        improvement = 0.0
        if len(scores) >= 2:
            mid = len(scores) // 2
            recent_avg = sum(scores[:mid]) / mid
            older_avg = sum(scores[mid:]) / (len(scores) - mid)
            improvement = recent_avg - older_avg

        stats = InterviewSessionStats(
            total=total, average=round(average, 2), improvement=round(improvement, 2)
        )

        return InterviewSessionList(sessions=session_items, stats=stats)

    @staticmethod
    async def update_session_transcript(
        db: AsyncSession, session: InterviewSession, transcript: str
    ) -> InterviewSession:
        """Update session transcript."""
        session.transcript = transcript
        await db.flush()
        await db.refresh(session)
        return session

    @staticmethod
    async def update_session_audio(
        db: AsyncSession, session: InterviewSession, audio_s3_key: str
    ) -> InterviewSession:
        """Update session audio reference."""
        session.audio_s3_key = audio_s3_key
        await db.flush()
        await db.refresh(session)
        return session

    @staticmethod
    async def complete_session(
        db: AsyncSession,
        session: InterviewSession,
        feedback_data: dict,
        duration_seconds: int,
    ) -> InterviewSession:
        """Mark session as complete with feedback."""
        session.completed_at = datetime.now(timezone.utc)
        session.duration_seconds = duration_seconds
        session.overall_score = feedback_data.get("overall_score")
        session.communication_score = feedback_data.get("communication_score")
        session.technical_score = feedback_data.get("technical_score")
        session.clarity_score = feedback_data.get("clarity_score")
        session.strengths = feedback_data.get("strengths", [])
        session.improvements = feedback_data.get("improvements", [])
        session.detailed_feedback = feedback_data.get("detailed_feedback")

        await db.flush()
        await db.refresh(session)
        return session

    @staticmethod
    def format_feedback(session: InterviewSession) -> InterviewFeedback:
        """Format session feedback for response."""
        return InterviewFeedback(
            overall_score=session.overall_score or 0.0,
            communication_score=session.communication_score,
            technical_score=session.technical_score,
            clarity_score=session.clarity_score,
            strengths=session.strengths or [],
            improvements=session.improvements or [],
            detailed_feedback=session.detailed_feedback or "",
            transcript=session.transcript,
        )
