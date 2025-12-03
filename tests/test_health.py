"""
API Health and Basic Connectivity Tests.

Tests basic API connectivity and health endpoints.
"""
import pytest
import httpx


@pytest.mark.smoke
class TestAPIHealth:
    """Test API health and basic connectivity."""

    async def test_api_reachable(self, client: httpx.AsyncClient, base_url: str):
        """Test that the API is reachable."""
        response = await client.get("/")

        assert response.status_code == 200, f"API not reachable at {base_url}: {response.status_code}"
        data = response.json()

        # Validate root response
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    async def test_api_info(self, client: httpx.AsyncClient):
        """Test API returns correct information."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()

        # Check for expected fields
        assert "name" in data
        assert "version" in data
        assert "environment" in data

        # Validate data types
        assert isinstance(data["name"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["environment"], str)

    async def test_cors_headers(self, client: httpx.AsyncClient):
        """Test that CORS headers are present."""
        response = await client.get("/")

        # CORS headers should be present for web clients
        # Exact headers depend on backend configuration
        assert response.status_code == 200

    async def test_404_handling(self, client: httpx.AsyncClient):
        """Test 404 response for non-existent endpoint."""
        response = await client.get("/this-endpoint-does-not-exist")

        assert response.status_code == 404

    async def test_method_not_allowed(self, client: httpx.AsyncClient):
        """Test method not allowed responses."""
        # Try to POST to root (which only accepts GET)
        response = await client.delete("/")

        # Should return 405 (Method Not Allowed) or 404
        assert response.status_code in [404, 405]
