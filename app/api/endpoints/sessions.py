"""
Interview session API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.session import (
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewSessionList,
    InterviewFeedback,
)
from app.services.session_service import SessionService
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


@router.post("", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: InterviewSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new interview session.

    Args:
        session_data: Session creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created session data
    """
    session = await SessionService.create_session(db, current_user.id, session_data)
    await db.commit()
    return InterviewSessionResponse.from_orm_model(session)


@router.get("", response_model=InterviewSessionList)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of user's interview sessions with statistics.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of sessions with stats
    """
    return await SessionService.get_sessions_list(db, current_user.id)


@router.get("/{session_id}", response_model=InterviewSessionResponse)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific interview session.

    Args:
        session_id: Session ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Session data

    Raises:
        HTTPException: If session not found
    """
    session = await SessionService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return InterviewSessionResponse.from_orm_model(session)


@router.get("/{session_id}/feedback", response_model=InterviewFeedback)
async def get_session_feedback(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get feedback for a completed interview session.

    Args:
        session_id: Session ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Interview feedback

    Raises:
        HTTPException: If session not found or not completed
    """
    session = await SessionService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Generate feedback if not already generated
    if not session.overall_score and session.transcript:
        try:
            feedback_data = await ai_service.generate_feedback(
                session.question or "General interview question",
                session.transcript,
                session.duration_seconds or 0,
            )
            session = await SessionService.complete_session(
                db, session, feedback_data, session.duration_seconds or 0
            )
            await db.commit()
        except Exception as e:
            # Return partial feedback if AI generation fails
            pass

    return SessionService.format_feedback(session)


@router.post("/{session_id}/complete", response_model=InterviewSessionResponse)
async def complete_session(
    session_id: int,
    duration_seconds: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a session as complete and generate feedback.

    Args:
        session_id: Session ID
        duration_seconds: Duration of the interview in seconds
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated session data

    Raises:
        HTTPException: If session not found
    """
    session = await SessionService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Generate feedback using AI
    try:
        feedback_data = await ai_service.generate_feedback(
            session.question or "General interview question",
            session.transcript or "",
            duration_seconds,
        )
    except Exception:
        # Use default feedback if AI fails
        feedback_data = {
            "overall_score": 70.0,
            "communication_score": 70.0,
            "technical_score": 70.0,
            "clarity_score": 70.0,
            "strengths": ["Completed the interview"],
            "improvements": ["Practice more"],
            "detailed_feedback": "Keep practicing to improve your interview skills.",
        }

    session = await SessionService.complete_session(db, session, feedback_data, duration_seconds)
    await db.commit()

    return InterviewSessionResponse.from_orm_model(session)
