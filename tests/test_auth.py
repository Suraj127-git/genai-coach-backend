"""
Authentication API endpoint tests.

Tests all authentication-related endpoints:
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- GET /auth/me
- PUT /auth/me
"""
import pytest
import httpx
from typing import Dict, Any


@pytest.mark.auth
@pytest.mark.smoke
class TestAuthRegistration:
    """Test user registration endpoint."""

    async def test_register_success(self, client: httpx.AsyncClient, valid_user_data: Dict[str, str]):
        """Test successful user registration."""
        response = await client.post("/auth/register", json=valid_user_data)

        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()

        # Validate response structure
        assert "user" in data
        assert "token" in data
        assert "refresh_token" in data

        # Validate user data
        user = data["user"]
        assert user["email"] == valid_user_data["email"]
        assert user["name"] == valid_user_data["name"]
        assert "id" in user
        assert user["is_active"] is True
        assert "created_at" in user

        # Validate tokens
        assert isinstance(data["token"], str)
        assert len(data["token"]) > 0
        assert isinstance(data["refresh_token"], str)
        assert len(data["refresh_token"]) > 0

    async def test_register_duplicate_email(self, client: httpx.AsyncClient, test_user: Dict[str, Any]):
        """Test registration with duplicate email fails."""
        duplicate_data = {
            "email": test_user["email"],
            "password": "different_password123",
            "name": "Different Name",
        }

        response = await client.post("/auth/register", json=duplicate_data)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already registered" in data["detail"].lower()

    async def test_register_invalid_email(self, client: httpx.AsyncClient, random_password: str):
        """Test registration with invalid email format fails."""
        invalid_data = {
            "email": "not-an-email",
            "password": random_password,
            "name": "Test User",
        }

        response = await client.post("/auth/register", json=invalid_data)

        assert response.status_code == 422  # Validation error

    async def test_register_short_password(self, client: httpx.AsyncClient, random_email: str):
        """Test registration with password less than 6 characters fails."""
        invalid_data = {
            "email": random_email,
            "password": "12345",  # Only 5 characters
            "name": "Test User",
        }

        response = await client.post("/auth/register", json=invalid_data)

        assert response.status_code == 422  # Validation error

    async def test_register_missing_fields(self, client: httpx.AsyncClient):
        """Test registration with missing required fields fails."""
        # Missing password
        response = await client.post("/auth/register", json={
            "email": "test@example.com",
            "name": "Test User",
        })
        assert response.status_code == 422

        # Missing email
        response = await client.post("/auth/register", json={
            "password": "password123",
            "name": "Test User",
        })
        assert response.status_code == 422


@pytest.mark.auth
@pytest.mark.smoke
class TestAuthLogin:
    """Test user login endpoint."""

    async def test_login_success(self, client: httpx.AsyncClient, test_user: Dict[str, Any]):
        """Test successful login with valid credentials."""
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"],
        }

        response = await client.post("/auth/login", json=login_data)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        # Validate response structure
        assert "user" in data
        assert "token" in data
        assert "refresh_token" in data

        # Validate user data
        user = data["user"]
        assert user["email"] == test_user["email"]
        assert "id" in user

        # Validate tokens
        assert isinstance(data["token"], str)
        assert len(data["token"]) > 0
        assert isinstance(data["refresh_token"], str)
        assert len(data["refresh_token"]) > 0

    async def test_login_wrong_password(self, client: httpx.AsyncClient, test_user: Dict[str, Any]):
        """Test login with incorrect password fails."""
        login_data = {
            "email": test_user["email"],
            "password": "wrong_password123",
        }

        response = await client.post("/auth/login", json=login_data)

        assert response.status_code in [401, 403]
        data = response.json()
        assert "detail" in data

    async def test_login_nonexistent_user(self, client: httpx.AsyncClient, random_email: str, random_password: str):
        """Test login with non-existent email fails."""
        login_data = {
            "email": random_email,
            "password": random_password,
        }

        response = await client.post("/auth/login", json=login_data)

        assert response.status_code in [401, 403]

    async def test_login_invalid_email_format(self, client: httpx.AsyncClient, random_password: str):
        """Test login with invalid email format fails."""
        login_data = {
            "email": "not-an-email",
            "password": random_password,
        }

        response = await client.post("/auth/login", json=login_data)

        assert response.status_code == 422  # Validation error

    async def test_login_missing_fields(self, client: httpx.AsyncClient):
        """Test login with missing fields fails."""
        # Missing password
        response = await client.post("/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422

        # Missing email
        response = await client.post("/auth/login", json={"password": "password123"})
        assert response.status_code == 422


@pytest.mark.auth
class TestAuthRefreshToken:
    """Test token refresh endpoint."""

    async def test_refresh_token_success(self, client: httpx.AsyncClient, test_user: Dict[str, Any]):
        """Test successful token refresh."""
        refresh_data = {
            "refresh_token": test_user["refresh_token"],
        }

        response = await client.post("/auth/refresh", json=refresh_data)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        # Validate response structure
        assert "access_token" in data
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

        # May also return new refresh token
        if "refresh_token" in data:
            assert isinstance(data["refresh_token"], str)
            assert len(data["refresh_token"]) > 0

    async def test_refresh_token_invalid(self, client: httpx.AsyncClient):
        """Test refresh with invalid token fails."""
        refresh_data = {
            "refresh_token": "invalid.token.here",
        }

        response = await client.post("/auth/refresh", json=refresh_data)

        assert response.status_code in [401, 403]

    async def test_refresh_token_missing(self, client: httpx.AsyncClient):
        """Test refresh with missing token fails."""
        response = await client.post("/auth/refresh", json={})

        assert response.status_code == 422  # Validation error


@pytest.mark.auth
class TestAuthProfile:
    """Test profile management endpoints."""

    async def test_get_profile_success(self, client: httpx.AsyncClient, auth_headers: Dict[str, str], test_user: Dict[str, Any]):
        """Test getting current user profile."""
        response = await client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        # Validate user data
        assert data["email"] == test_user["email"]
        assert data["name"] == test_user["name"]
        assert "id" in data
        assert data["is_active"] is True
        assert "created_at" in data

    async def test_get_profile_unauthorized(self, client: httpx.AsyncClient):
        """Test getting profile without authentication fails."""
        response = await client.get("/auth/me")

        assert response.status_code in [401, 403]

    async def test_get_profile_invalid_token(self, client: httpx.AsyncClient):
        """Test getting profile with invalid token fails."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await client.get("/auth/me", headers=headers)

        assert response.status_code in [401, 403]

    async def test_update_profile_name(self, client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test updating user name."""
        update_data = {
            "name": "Updated Name",
        }

        response = await client.put("/auth/me", json=update_data, headers=auth_headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        assert data["name"] == "Updated Name"

    async def test_update_profile_email(self, client: httpx.AsyncClient, auth_headers: Dict[str, str], random_email: str):
        """Test updating user email."""
        update_data = {
            "email": random_email,
        }

        response = await client.put("/auth/me", json=update_data, headers=auth_headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        assert data["email"] == random_email

    async def test_update_profile_password(self, client: httpx.AsyncClient, auth_headers: Dict[str, str], test_user: Dict[str, Any]):
        """Test updating user password."""
        new_password = "new_secure_password123"
        update_data = {
            "currentPassword": test_user["password"],
            "newPassword": new_password,
        }

        response = await client.put("/auth/me", json=update_data, headers=auth_headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        # Verify can login with new password
        login_response = await client.post("/auth/login", json={
            "email": test_user["email"],
            "password": new_password,
        })
        assert login_response.status_code == 200

    async def test_update_profile_unauthorized(self, client: httpx.AsyncClient):
        """Test updating profile without authentication fails."""
        update_data = {"name": "New Name"}
        response = await client.put("/auth/me", json=update_data)

        assert response.status_code in [401, 403]


@pytest.mark.auth
class TestAuthLogout:
    """Test logout endpoint."""

    async def test_logout_success(self, client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test successful logout."""
        response = await client.post("/auth/logout", headers=auth_headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        assert "message" in data

    async def test_logout_unauthorized(self, client: httpx.AsyncClient):
        """Test logout without authentication fails."""
        response = await client.post("/auth/logout")

        assert response.status_code in [401, 403]
