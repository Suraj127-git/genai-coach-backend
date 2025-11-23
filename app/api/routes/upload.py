from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import os
import uuid
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from ...api.deps import get_current_user_id
from urllib.parse import urlparse, urlunparse
import logging

router = APIRouter()
logger = logging.getLogger("upload")


class PresignRequest(BaseModel):
    content_type: str
    extension: str


@router.post("/s3-presign")
def s3_presign_upload(payload: PresignRequest, user_id: str = Depends(get_current_user_id)):
    try:
        logger.info("presign request", extra={"user_id": user_id})
        bucket = os.getenv("AWS_S3_BUCKET")
        region = os.getenv("AWS_REGION")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        if not bucket or not region:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="S3 configuration missing")

        ext = payload.extension.lower().strip(".")
        if ext not in {"m4a", "mp3", "wav"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported extension")

        key = f"recordings/{user_id}/{uuid.uuid4()}.{ext}"

        endpoint = os.getenv("S3_ENDPOINT")
        public_endpoint = os.getenv("S3_PUBLIC_ENDPOINT")
        session = boto3.session.Session(region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        client = session.client("s3", endpoint_url=endpoint) if endpoint else session.client("s3")
        url = client.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": bucket, "Key": key, "ContentType": payload.content_type},
            ExpiresIn=300,
        )
        if public_endpoint and endpoint:
            try:
                ep = urlparse(endpoint)
                u = urlparse(url)
                url = urlunparse((ep.scheme, ep.netloc, u.path, u.params, u.query, u.fragment))
            except Exception:
                pass
        return {"url": url, "key": key}
    except (BotoCoreError, NoCredentialsError) as e:
        logger.critical("presign failed", extra={"error": str(e)})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"S3 presign failed: {e}")
    else:
        logger.error("presign success", extra={"key": key})
