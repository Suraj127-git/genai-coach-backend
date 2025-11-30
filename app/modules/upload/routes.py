from fastapi import APIRouter, Depends, HTTPException, status
from ...core.dependencies import get_current_user_id
from .schemas import PresignRequest
from .service import make_key
from .s3_adapter import s3_presign

router = APIRouter()

@router.post("/s3-presign")
def s3_presign_upload(payload: PresignRequest, user_id: str = Depends(get_current_user_id)):
    try:
        key = make_key(user_id, payload.extension)
        url = s3_presign(payload.content_type, key)
        return {"url": url, "key": key}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (RuntimeError, Exception) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"S3 presign failed: {e}")

