"""
AI service schemas for request/response validation.
"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Schema for chat message request."""
    message: str = Field(..., min_length=1, description="User's chat message")


class ChatResponse(BaseModel):
    """Schema for chat response."""
    reply: str = Field(..., description="AI assistant's response")


class TranscriptionRequest(BaseModel):
    """Schema for transcription request."""
    audio_s3_key: str = Field(..., description="S3 key of audio file to transcribe")


class TranscriptionResponse(BaseModel):
    """Schema for transcription response."""
    text: str = Field(..., description="Transcribed text")
