"""
File upload API endpoints for S3 presigned URLs.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.models.upload import Upload
from app.schemas.upload import PresignRequest, PresignResponse, UploadConfirm
from app.services.s3_service import S3Service

router = APIRouter()
s3_service = S3Service()


@router.post("/s3-presign", response_model=PresignResponse)
async def create_presigned_url(
    request: PresignRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate S3 presigned URL for file upload.

    Args:
        request: Presign request with content type and extension
        current_user: Current authenticated user

    Returns:
        Presigned URL and S3 key

    Raises:
        HTTPException: If presigned URL generation fails
    """
    try:
        # Generate unique S3 key
        s3_key = s3_service.generate_s3_key(current_user.id, request.extension)

        # Generate presigned URL
        presigned_url = s3_service.generate_presigned_url(s3_key, request.content_type)

        return PresignResponse(url=presigned_url, key=s3_key)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate presigned URL: {str(e)}",
        )


@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm_upload(
    confirm: UploadConfirm,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm file upload completion and record in database.

    Args:
        confirm: Upload confirmation with S3 key and timestamp
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If confirmation fails
    """
    try:
        # Get file size from S3
        file_size = await s3_service.get_file_size(confirm.key)

        # Determine content type from key extension
        extension = confirm.key.split(".")[-1]
        content_type_map = {
            "m4a": "audio/m4a",
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "mp4": "video/mp4",
        }
        content_type = content_type_map.get(extension, "application/octet-stream")

        # Convert timestamp from milliseconds to datetime
        uploaded_at = datetime.fromtimestamp(confirm.uploaded_at / 1000, tz=timezone.utc)

        # Create upload record
        upload = Upload(
            user_id=current_user.id,
            s3_key=confirm.key,
            content_type=content_type,
            file_size=file_size,
            uploaded_at=uploaded_at,
        )
        db.add(upload)
        await db.commit()

        return {"message": "Upload confirmed successfully", "key": confirm.key}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm upload: {str(e)}",
        )
