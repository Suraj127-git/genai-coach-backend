"""
Upload schemas for request/response validation.
"""
from pydantic import BaseModel, Field


class PresignRequest(BaseModel):
    """Schema for requesting S3 presigned URL."""
    content_type: str = Field(..., description="MIME type of the file")
    extension: str = Field(..., description="File extension (e.g., 'm4a')")


class PresignResponse(BaseModel):
    """Schema for S3 presigned URL response."""
    url: str = Field(..., description="Presigned S3 URL for upload")
    key: str = Field(..., description="S3 object key")


class UploadConfirm(BaseModel):
    """Schema for confirming upload completion."""
    key: str = Field(..., description="S3 object key")
    uploaded_at: int = Field(..., description="Upload timestamp (milliseconds since epoch)")
