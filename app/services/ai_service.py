"""
AI service for chat and transcription using OpenAI.
"""
import tempfile
from typing import Dict, List

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger
from app.core.sentry import start_span, capture_exception, add_breadcrumb, set_context
from app.services.s3_service import S3Service

logger = get_logger(__name__)


class AIService:
    """Service class for AI operations using OpenAI."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.whisper_model = settings.OPENAI_WHISPER_MODEL
        self.s3_service = S3Service()

    async def chat(self, message: str, context: List[Dict[str, str]] = None) -> str:
        """
        Send a chat message and get AI response.

        Args:
            message: User's message
            context: Optional conversation history

        Returns:
            AI assistant's response
        """
        with start_span("ai.chat", "OpenAI Chat Completion"):
            add_breadcrumb(
                "Starting AI chat",
                category="ai",
                level="info",
                data={"model": self.model, "message_length": len(message)}
            )

            messages = context or []

            # Add system message if not present
            if not messages or messages[0]["role"] != "system":
                system_message = {
                    "role": "system",
                    "content": (
                        "You are an experienced interview coach helping users practice for job interviews. "
                        "Provide constructive feedback, ask relevant follow-up questions, and help users "
                        "improve their interview skills. Be supportive but honest in your assessments."
                    ),
                }
                messages = [system_message] + messages

            # Add user message
            messages.append({"role": "user", "content": message})

            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500,
                )

                set_context("ai_response", {
                    "model": self.model,
                    "tokens_used": response.usage.total_tokens if response.usage else None,
                    "response_length": len(response.choices[0].message.content) if response.choices else 0,
                })

                return response.choices[0].message.content

            except Exception as e:
                logger.error(f"Chat API error: {e}")
                capture_exception(
                    e,
                    tags={"service": "ai", "operation": "chat"},
                    extra={"model": self.model, "message_length": len(message)}
                )
                raise

    async def transcribe_audio(self, audio_s3_key: str) -> str:
        """
        Transcribe audio file from S3 using Whisper API.

        Args:
            audio_s3_key: S3 key of the audio file

        Returns:
            Transcribed text
        """
        with start_span("ai.transcribe", "OpenAI Whisper Transcription"):
            add_breadcrumb(
                "Starting audio transcription",
                category="ai",
                level="info",
                data={"s3_key": audio_s3_key, "model": self.whisper_model}
            )

            # Download audio from S3 to temp file
            with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as temp_file:
                temp_path = temp_file.name

            try:
                with start_span("s3.download", "Download audio from S3"):
                    self.s3_service.download_file(audio_s3_key, temp_path)

                # Transcribe using Whisper
                with start_span("ai.whisper", "Whisper API call"):
                    with open(temp_path, "rb") as audio_file:
                        response = await self.client.audio.transcriptions.create(
                            model=self.whisper_model,
                            file=audio_file,
                            response_format="text",
                        )

                set_context("transcription", {
                    "s3_key": audio_s3_key,
                    "model": self.whisper_model,
                    "transcript_length": len(response) if isinstance(response, str) else 0,
                })

                return response

            except Exception as e:
                logger.error(f"Transcription error: {e}")
                capture_exception(
                    e,
                    tags={"service": "ai", "operation": "transcribe"},
                    extra={"s3_key": audio_s3_key, "model": self.whisper_model}
                )
                raise
            finally:
                # Clean up temp file
                import os
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    async def generate_feedback(
        self, question: str, transcript: str, duration_seconds: int
    ) -> Dict:
        """
        Generate interview feedback based on transcript.

        Args:
            question: Interview question asked
            transcript: User's response transcript
            duration_seconds: Duration of the response

        Returns:
            Feedback dictionary with scores and recommendations
        """
        prompt = f"""Analyze this interview response and provide detailed feedback.

Question: {question}

Response: {transcript}

Duration: {duration_seconds} seconds

Please provide:
1. An overall score (0-100)
2. Communication score (0-100)
3. Technical score (0-100)
4. Clarity score (0-100)
5. Top 3 strengths
6. Top 3 areas for improvement
7. Detailed feedback paragraph

Format your response as JSON with keys: overall_score, communication_score, technical_score, clarity_score, strengths (array), improvements (array), detailed_feedback (string)."""

        with start_span("ai.feedback", "Generate Interview Feedback"):
            add_breadcrumb(
                "Generating interview feedback",
                category="ai",
                level="info",
                data={
                    "model": self.model,
                    "transcript_length": len(transcript),
                    "duration_seconds": duration_seconds
                }
            )

            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert interview coach. Analyze interview responses and provide constructive, actionable feedback.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.5,
                )

                import json
                feedback = json.loads(response.choices[0].message.content)

                set_context("feedback_generation", {
                    "model": self.model,
                    "tokens_used": response.usage.total_tokens if response.usage else None,
                    "overall_score": feedback.get("overall_score"),
                })

                return feedback

            except Exception as e:
                logger.error(f"Feedback generation error: {e}")
                capture_exception(
                    e,
                    tags={"service": "ai", "operation": "generate_feedback"},
                    extra={
                        "model": self.model,
                        "transcript_length": len(transcript),
                        "duration": duration_seconds
                    }
                )
            # Return default feedback on error
            return {
                "overall_score": 70.0,
                "communication_score": 70.0,
                "technical_score": 70.0,
                "clarity_score": 70.0,
                "strengths": [
                    "Attempted to answer the question",
                    "Showed engagement",
                    "Completed the response",
                ],
                "improvements": [
                    "Provide more specific examples",
                    "Structure your response better",
                    "Expand on technical details",
                ],
                "detailed_feedback": "Your response shows effort. Focus on providing more concrete examples and structuring your answers using frameworks like STAR (Situation, Task, Action, Result).",
            }
