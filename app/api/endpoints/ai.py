"""
AI service API endpoints for chat.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.ai import ChatRequest, ChatResponse
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Send a chat message to AI assistant.

    Args:
        request: Chat message request
        current_user: Current authenticated user

    Returns:
        AI assistant's response

    Raises:
        HTTPException: If chat fails
    """
    try:
        reply = await ai_service.chat(request.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat service error: {str(e)}",
        )
