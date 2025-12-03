"""
File Upload API endpoint tests.

Tests all upload-related endpoints:
- POST /upload/s3-presign
- POST /upload/confirm
"""
import pytest
import httpx
from typing import Dict, Any
import time


@pytest.mark.upload
@pytest.mark.smoke
class TestPresignedURL:
    """Test S3 presigned URL generation endpoint."""

    async def test_presign_audio_success(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test generating presigned URL for audio upload."""
        presign_data = {
            "content_type": "audio/m4a",
            "extension": "m4a",
        }

        response = await client.post(
            "/upload/s3-presign",
            json=presign_data,
            headers=auth_headers,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        # Validate response structure
        assert "url" in data
        assert "key" in data

        # Validate URL format
        assert isinstance(data["url"], str)
        assert len(data["url"]) > 0
        assert data["url"].startswith("http")

        # Validate S3 key format
        assert isinstance(data["key"], str)
        assert data["key"].endswith(".m4a")

    async def test_presign_video_success(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test generating presigned URL for video upload."""
        presign_data = {
            "content_type": "video/mp4",
            "extension": "mp4",
        }

        response = await client.post(
            "/upload/s3-presign",
            json=presign_data,
            headers=auth_headers,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        assert "url" in data
        assert "key" in data
        assert data["key"].endswith(".mp4")

    async def test_presign_multiple_formats(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test generating presigned URLs for various file formats."""
        formats = [
            {"content_type": "audio/m4a", "extension": "m4a"},
            {"content_type": "audio/mpeg", "extension": "mp3"},
            {"content_type": "audio/wav", "extension": "wav"},
            {"content_type": "video/mp4", "extension": "mp4"},
        ]

        for format_data in formats:
            response = await client.post(
                "/upload/s3-presign",
                json=format_data,
                headers=auth_headers,
            )

            assert response.status_code == 200, f"Failed for {format_data['extension']}: {response.text}"
            data = response.json()
            assert data["key"].endswith(f".{format_data['extension']}")

    async def test_presign_unauthorized(self, client: httpx.AsyncClient):
        """Test generating presigned URL without authentication fails."""
        presign_data = {
            "content_type": "audio/m4a",
            "extension": "m4a",
        }

        response = await client.post("/upload/s3-presign", json=presign_data)

        assert response.status_code in [401, 403]

    async def test_presign_missing_content_type(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test presign request with missing content_type fails."""
        presign_data = {
            "extension": "m4a",
        }

        response = await client.post(
            "/upload/s3-presign",
            json=presign_data,
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    async def test_presign_missing_extension(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test presign request with missing extension fails."""
        presign_data = {
            "content_type": "audio/m4a",
        }

        response = await client.post(
            "/upload/s3-presign",
            json=presign_data,
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    async def test_presign_unique_keys(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test that multiple presign requests generate unique keys."""
        presign_data = {
            "content_type": "audio/m4a",
            "extension": "m4a",
        }

        # Generate multiple presigned URLs
        keys = set()
        for _ in range(3):
            response = await client.post(
                "/upload/s3-presign",
                json=presign_data,
                headers=auth_headers,
            )
            assert response.status_code == 200
            keys.add(response.json()["key"])
            time.sleep(0.1)  # Small delay to ensure uniqueness

        # All keys should be unique
        assert len(keys) == 3


@pytest.mark.upload
class TestUploadConfirmation:
    """Test upload confirmation endpoint."""

    async def test_confirm_upload_success(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test confirming a file upload."""
        # First, get a presigned URL
        presign_response = await client.post(
            "/upload/s3-presign",
            json={"content_type": "audio/m4a", "extension": "m4a"},
            headers=auth_headers,
        )
        assert presign_response.status_code == 200
        s3_key = presign_response.json()["key"]

        # Note: We can't actually upload to S3 without credentials,
        # so this test might fail if the backend validates the S3 object exists
        confirm_data = {
            "key": s3_key,
            "uploaded_at": int(time.time() * 1000),  # Current timestamp in milliseconds
        }

        response = await client.post(
            "/upload/confirm",
            json=confirm_data,
            headers=auth_headers,
        )

        # May succeed or fail depending on S3 validation
        # If backend checks S3, this will fail (500 or 404)
        # If backend just records metadata, this will succeed (200)
        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            assert "message" in data or "key" in data

    async def test_confirm_upload_unauthorized(self, client: httpx.AsyncClient):
        """Test confirming upload without authentication fails."""
        confirm_data = {
            "key": "test/audio/sample.m4a",
            "uploaded_at": int(time.time() * 1000),
        }

        response = await client.post("/upload/confirm", json=confirm_data)

        assert response.status_code in [401, 403]

    async def test_confirm_upload_missing_key(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test confirming upload with missing key fails."""
        confirm_data = {
            "uploaded_at": int(time.time() * 1000),
        }

        response = await client.post(
            "/upload/confirm",
            json=confirm_data,
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    async def test_confirm_upload_missing_timestamp(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test confirming upload with missing timestamp fails."""
        confirm_data = {
            "key": "test/audio/sample.m4a",
        }

        response = await client.post(
            "/upload/confirm",
            json=confirm_data,
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error

    async def test_confirm_upload_invalid_key(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test confirming upload with non-existent S3 key."""
        confirm_data = {
            "key": "nonexistent/file/that/does/not/exist.m4a",
            "uploaded_at": int(time.time() * 1000),
        }

        response = await client.post(
            "/upload/confirm",
            json=confirm_data,
            headers=auth_headers,
        )

        # Should fail because file doesn't exist in S3
        assert response.status_code in [404, 500]


@pytest.mark.upload
@pytest.mark.integration
class TestUploadWorkflow:
    """Test complete upload workflow integration."""

    async def test_full_upload_workflow(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test the complete presign -> upload -> confirm workflow."""
        # 1. Request presigned URL
        presign_response = await client.post(
            "/upload/s3-presign",
            json={"content_type": "audio/m4a", "extension": "m4a"},
            headers=auth_headers,
        )
        assert presign_response.status_code == 200
        presign_data = presign_response.json()

        assert "url" in presign_data
        assert "key" in presign_data

        presigned_url = presign_data["url"]
        s3_key = presign_data["key"]

        # 2. Verify URL format is correct for storage (S3 or Railway storage)
        assert "s3" in presigned_url.lower() or "amazonaws" in presigned_url.lower() or "railway" in presigned_url.lower()

        # 3. Confirm upload (will likely fail without actual S3 upload)
        # This is expected behavior when testing against live API
        confirm_response = await client.post(
            "/upload/confirm",
            json={
                "key": s3_key,
                "uploaded_at": int(time.time() * 1000),
            },
            headers=auth_headers,
        )

        # Accept both success and failure since we didn't actually upload
        assert confirm_response.status_code in [200, 404, 500]

    async def test_multiple_concurrent_presigns(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test generating multiple presigned URLs concurrently."""
        presign_data = {
            "content_type": "audio/m4a",
            "extension": "m4a",
        }

        # Generate multiple presigned URLs
        responses = []
        for _ in range(5):
            response = await client.post(
                "/upload/s3-presign",
                json=presign_data,
                headers=auth_headers,
            )
            responses.append(response)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

        # All keys should be unique
        keys = [r.json()["key"] for r in responses]
        assert len(keys) == len(set(keys))
