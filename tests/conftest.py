"""
Pytest configuration and shared fixtures for testing Railway API endpoints.
"""
import os
from typing import Generator, Dict, Any
import pytest
import httpx
from faker import Faker

# Railway API endpoint
BASE_URL = os.getenv("API_URL", "https://genai-coach-backend-production.up.railway.app")

fake = Faker()


@pytest.fixture(scope="session")
def base_url() -> str:
    """Get the base URL for API testing."""
    return BASE_URL


@pytest.fixture
async def client(base_url: str) -> Generator[httpx.AsyncClient, None, None]:
    """Create an async HTTP client for testing."""
    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        yield client


@pytest.fixture
def random_email() -> str:
    """Generate a random email for testing."""
    return fake.email()


@pytest.fixture
def random_name() -> str:
    """Generate a random name for testing."""
    return fake.name()


@pytest.fixture
def random_password() -> str:
    """Generate a random password for testing."""
    return fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)


@pytest.fixture
async def test_user(client: httpx.AsyncClient, random_email: str, random_password: str, random_name: str) -> Dict[str, Any]:
    """
    Create a test user and return user data with tokens.

    Returns:
        Dict containing user info, token, and refresh_token
    """
    user_data = {
        "email": random_email,
        "password": random_password,
        "name": random_name,
    }

    response = await client.post("/auth/register", json=user_data)

    if response.status_code != 201:
        raise Exception(f"Failed to create test user: {response.text}")

    data = response.json()
    return {
        "email": random_email,
        "password": random_password,
        "name": random_name,
        "user": data["user"],
        "token": data["token"],
        "refresh_token": data["refresh_token"],
    }


@pytest.fixture
async def auth_headers(test_user: Dict[str, Any]) -> Dict[str, str]:
    """
    Get authentication headers for authenticated requests.

    Returns:
        Dict with Authorization header
    """
    return {"Authorization": f"Bearer {test_user['token']}"}


@pytest.fixture
async def test_session(client: httpx.AsyncClient, auth_headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Create a test interview session.

    Returns:
        Dict containing session data
    """
    session_data = {
        "title": "Python Developer Interview Practice",
        "question": "Tell me about yourself and your experience with Python.",
    }

    response = await client.post(
        "/sessions",
        json=session_data,
        headers=auth_headers,
    )

    if response.status_code != 201:
        raise Exception(f"Failed to create test session: {response.text}")

    return response.json()


# Test data generators
@pytest.fixture
def valid_user_data(random_email: str, random_password: str, random_name: str) -> Dict[str, str]:
    """Generate valid user registration data."""
    return {
        "email": random_email,
        "password": random_password,
        "name": random_name,
    }


@pytest.fixture
def valid_session_data() -> Dict[str, str]:
    """Generate valid session creation data."""
    return {
        "title": "Backend Developer Interview",
        "question": "Describe your experience with RESTful APIs.",
    }


@pytest.fixture
def valid_chat_message() -> Dict[str, str]:
    """Generate valid chat message data."""
    return {
        "message": "Can you help me prepare for a technical interview?",
    }


# Cleanup fixtures
@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Cleanup after each test (if needed)."""
    yield
    # Add any cleanup logic here if needed
