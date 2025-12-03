"""
WebSocket endpoint for real-time transcription.
"""
import json
from typing import Dict, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.security import decode_token
from app.db.base import get_db
from app.services.user_service import UserService
from app.services.session_service import SessionService
from app.services.ai_service import AIService

logger = get_logger(__name__)
router = APIRouter()
ai_service = AIService()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        """Accept and store WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket connected for user {user_id}")

    def disconnect(self, user_id: int):
        """Remove WebSocket connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_message(self, user_id: int, message: dict):
        """Send message to specific user."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")


manager = ConnectionManager()


async def authenticate_websocket(websocket: WebSocket) -> Optional[int]:
    """
    Authenticate WebSocket connection via auth message.

    Args:
        websocket: WebSocket connection

    Returns:
        User ID if authenticated, None otherwise
    """
    try:
        # Wait for auth message
        data = await websocket.receive_json()

        if data.get("type") != "auth":
            await websocket.send_json({"type": "error", "message": "Authentication required"})
            return None

        token = data.get("token")
        if not token:
            await websocket.send_json({"type": "error", "message": "Token missing"})
            return None

        # Decode token
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            await websocket.send_json({"type": "error", "message": "Invalid token"})
            return None

        user_id = payload.get("sub")
        if not user_id:
            await websocket.send_json({"type": "error", "message": "Invalid token"})
            return None

        # Send auth success
        await websocket.send_json({"type": "auth_success"})
        return int(user_id)

    except Exception as e:
        logger.error(f"WebSocket auth error: {e}")
        return None


@router.websocket("/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket endpoint for real-time transcription.

    Message Types (Incoming):
        - auth: { type: 'auth', token: string }
        - session_start: { type: 'session_start', question: string }
        - audio_uri: { type: 'audio_uri', key: string, uri: string }

    Message Types (Outgoing):
        - auth_success: { type: 'auth_success' }
        - transcript: { type: 'transcript', text: string }
        - error: { type: 'error', message: string }
    """
    user_id = None

    try:
        # Authenticate
        user_id = await authenticate_websocket(websocket)
        if not user_id:
            await websocket.close(code=1008)
            return

        # Connect user
        await manager.connect(user_id, websocket)

        # Store session context
        current_question = None
        current_session_id = None

        # Message loop
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")

                if message_type == "session_start":
                    # Store question for context
                    current_question = data.get("question")
                    logger.info(f"Session started for user {user_id}: {current_question}")

                elif message_type == "audio_uri":
                    # Transcribe audio from S3
                    audio_key = data.get("key")
                    if audio_key:
                        try:
                            # Transcribe audio using AI service
                            transcript_text = await ai_service.transcribe_audio(audio_key)

                            # Send transcript back to client
                            await manager.send_message(
                                user_id,
                                {"type": "transcript", "text": transcript_text}
                            )

                            logger.info(f"Transcribed audio for user {user_id}")

                        except Exception as e:
                            logger.error(f"Transcription error: {e}")
                            await manager.send_message(
                                user_id,
                                {"type": "error", "message": "Transcription failed"}
                            )

                else:
                    logger.warning(f"Unknown message type: {message_type}")

            except json.JSONDecodeError:
                await manager.send_message(
                    user_id,
                    {"type": "error", "message": "Invalid JSON"}
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if user_id:
            manager.disconnect(user_id)
