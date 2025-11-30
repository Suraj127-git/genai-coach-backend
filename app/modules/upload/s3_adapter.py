import os
import uuid
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from urllib.parse import urlparse, urlunparse

def s3_presign(content_type: str, key: str) -> str:
    bucket = os.getenv("AWS_S3_BUCKET")
    region = os.getenv("AWS_REGION")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    endpoint = os.getenv("S3_ENDPOINT")
    public_endpoint = os.getenv("S3_PUBLIC_ENDPOINT")
    if not bucket or not region:
        raise RuntimeError("S3 configuration missing")
    session = boto3.session.Session(region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    client = session.client("s3", endpoint_url=endpoint) if endpoint else session.client("s3")
    url = client.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": bucket, "Key": key, "ContentType": content_type},
        ExpiresIn=300,
    )
    if public_endpoint and endpoint:
        ep = urlparse(endpoint)
        u = urlparse(url)
        url = urlunparse((ep.scheme, ep.netloc, u.path, u.params, u.query, u.fragment))
    return url

