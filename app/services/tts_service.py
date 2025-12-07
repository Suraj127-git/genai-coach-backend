"""
Text-to-Speech service for generating AI audio responses.
"""
import tempfile
import os
from typing import Optional
from gtts import gTTS

from app.core.config import settings
from app.core.logging import get_logger
from app.core.sentry import start_span, capture_exception, add_breadcrumb
from app.services.s3_service import S3Service

logger = get_logger(__name__)


class TTSService:
    """Service for converting text to speech and uploading to S3."""

    def __init__(self):
        """Initialize TTS service."""
        self.s3_service = S3Service()

    async def text_to_speech(self, text: str, session_id: int, interaction_id: int) -> Optional[str]:
        """
        Convert text to speech and upload to S3.

        Args:
            text: Text to convert to speech
            session_id: AI interview session ID
            interaction_id: Interaction ID for unique filename

        Returns:
            S3 key of the uploaded audio file, or None if failed
        """
        with start_span("tts.generate", "Generate TTS Audio"):
            add_breadcrumb(
                "Starting TTS generation",
                category="tts",
                level="info",
                data={
                    "text_length": len(text),
                    "session_id": session_id,
                    "interaction_id": interaction_id
                }
            )

            # Create temporary file for audio
            temp_file = None
            try:
                # Generate speech using gTTS
                tts = gTTS(text=text, lang='en', slow=False)

                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
                    temp_file = temp.name
                    tts.save(temp_file)

                # Generate S3 key
                s3_key = f"ai-audio/{session_id}/interaction-{interaction_id}.mp3"

                # Upload to S3
                with start_span("s3.upload", "Upload TTS audio to S3"):
                    self.s3_service.upload_file(temp_file, s3_key, content_type="audio/mpeg")

                logger.info(f"TTS audio generated and uploaded: {s3_key}")
                return s3_key

            except Exception as e:
                logger.error(f"TTS generation error: {e}")
                capture_exception(
                    e,
                    tags={"service": "tts", "operation": "text_to_speech"},
                    extra={
                        "text_length": len(text),
                        "session_id": session_id,
                        "interaction_id": interaction_id
                    }
                )
                return None

            finally:
                # Clean up temporary file
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        logger.warning(f"Failed to clean up temp file {temp_file}: {e}")

    async def get_audio_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Get presigned URL for an audio file.

        Args:
            s3_key: S3 key of the audio file
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned URL or None if failed
        """
        try:
            return self.s3_service.generate_presigned_url(
                s3_key,
                expiration=expiration,
                method="get_object"
            )
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {s3_key}: {e}")
            return None
