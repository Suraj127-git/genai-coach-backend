"""
Interview Session API endpoint tests.

Tests all session-related endpoints:
- POST /sessions
- GET /sessions
- GET /sessions/{session_id}
- GET /sessions/{session_id}/feedback
- POST /sessions/{session_id}/complete
"""
import pytest
import httpx
from typing import Dict, Any


@pytest.mark.sessions
@pytest.mark.smoke
class TestSessionCreation:
    """Test session creation endpoint."""

    async def test_create_session_success(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
        valid_session_data: Dict[str, str]
    ):
        """Test successful session creation."""
        response = await client.post(
            "/sessions",
            json=valid_session_data,
            headers=auth_headers,
        )

        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()

        # Validate response structure
        assert "id" in data
        assert data["title"] == valid_session_data["title"]
        assert data["question"] == valid_session_data["question"]
        assert "created_at" in data
        assert "user_id" in data

    async def test_create_session_minimal_data(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test creating session with minimal required data."""
        minimal_data = {
            "title": "Quick Interview Practice",
            "question": "What is your greatest strength?",
        }

        response = await client.post(
            "/sessions",
            json=minimal_data,
            headers=auth_headers,
        )

        # Should succeed with required fields
        assert response.status_code == 201

    async def test_create_session_unauthorized(
        self,
        client: httpx.AsyncClient,
        valid_session_data: Dict[str, str]
    ):
        """Test creating session without authentication fails."""
        response = await client.post("/sessions", json=valid_session_data)

        # API returns 403 for unauthorized requests
        assert response.status_code in [401, 403]

    async def test_create_session_missing_title(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test creating session without required title field."""
        invalid_data = {
            "question": "Sample question",
        }

        response = await client.post(
            "/sessions",
            json=invalid_data,
            headers=auth_headers,
        )

        # Should fail validation without title
        assert response.status_code == 422


@pytest.mark.sessions
@pytest.mark.smoke
class TestSessionList:
    """Test session listing endpoint."""

    async def test_list_sessions_success(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
        test_session: Dict[str, Any]
    ):
        """Test getting list of user sessions."""
        response = await client.get("/sessions", headers=auth_headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        # Validate response structure
        assert "sessions" in data or isinstance(data, list)

        # If it returns sessions list
        sessions = data.get("sessions", data)
        assert isinstance(sessions, list)
        assert len(sessions) >= 1  # At least our test session

        # Find our test session
        session_ids = [s["id"] for s in sessions]
        assert test_session["id"] in session_ids

    async def test_list_sessions_empty(
        self,
        client: httpx.AsyncClient,
        test_user: Dict[str, Any]
    ):
        """Test listing sessions for new user with no sessions."""
        # Login as the test user
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        # Delete the auto-created test_session by getting fresh user
        # For this test, we just verify the response format
        response = await client.get("/sessions", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Should return empty list or object with empty sessions
        if isinstance(data, dict):
            assert "sessions" in data
        else:
            assert isinstance(data, list)

    async def test_list_sessions_unauthorized(self, client: httpx.AsyncClient):
        """Test listing sessions without authentication fails."""
        response = await client.get("/sessions")

        assert response.status_code in [401, 403]


@pytest.mark.sessions
class TestSessionRetrieval:
    """Test individual session retrieval endpoint."""

    async def test_get_session_success(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
        test_session: Dict[str, Any]
    ):
        """Test getting a specific session."""
        session_id = test_session["id"]
        response = await client.get(f"/sessions/{session_id}", headers=auth_headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        # Validate session data
        assert data["id"] == session_id
        assert "question" in data
        assert "created_at" in data

    async def test_get_session_not_found(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test getting non-existent session returns 404."""
        response = await client.get("/sessions/999999", headers=auth_headers)

        assert response.status_code == 404

    async def test_get_session_unauthorized(
        self,
        client: httpx.AsyncClient,
        test_session: Dict[str, Any]
    ):
        """Test getting session without authentication fails."""
        session_id = test_session["id"]
        response = await client.get(f"/sessions/{session_id}")

        assert response.status_code in [401, 403]

    async def test_get_other_user_session(
        self,
        client: httpx.AsyncClient,
        test_session: Dict[str, Any],
        random_email: str,
        random_password: str,
        random_name: str
    ):
        """Test that users cannot access other users' sessions."""
        # Create a different user
        new_user_data = {
            "email": random_email,
            "password": random_password,
            "name": random_name,
        }
        register_response = await client.post("/auth/register", json=new_user_data)
        assert register_response.status_code == 201
        new_user_token = register_response.json()["token"]

        # Try to access the test session with different user
        other_headers = {"Authorization": f"Bearer {new_user_token}"}
        session_id = test_session["id"]
        response = await client.get(f"/sessions/{session_id}", headers=other_headers)

        # Should return 404 (not found) rather than 403 to avoid leaking session IDs
        assert response.status_code in [404, 403]


@pytest.mark.sessions
class TestSessionCompletion:
    """Test session completion endpoint."""

    async def test_complete_session_success(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
        test_session: Dict[str, Any]
    ):
        """Test completing a session and generating feedback."""
        session_id = test_session["id"]
        completion_data = {
            "duration_seconds": 180,  # 3 minutes
        }

        response = await client.post(
            f"/sessions/{session_id}/complete",
            params={"duration_seconds": 180},
            headers=auth_headers,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        # Validate completion data
        assert data["id"] == session_id
        assert "duration_seconds" in data or "duration" in data

    async def test_complete_session_not_found(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test completing non-existent session returns 404."""
        response = await client.post(
            "/sessions/999999/complete",
            params={"duration_seconds": 180},
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_complete_session_unauthorized(
        self,
        client: httpx.AsyncClient,
        test_session: Dict[str, Any]
    ):
        """Test completing session without authentication fails."""
        session_id = test_session["id"]
        response = await client.post(
            f"/sessions/{session_id}/complete",
            params={"duration_seconds": 180},
        )

        assert response.status_code in [401, 403]


@pytest.mark.sessions
class TestSessionFeedback:
    """Test session feedback endpoint."""

    async def test_get_feedback_success(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
        test_session: Dict[str, Any]
    ):
        """Test getting feedback for a session."""
        session_id = test_session["id"]

        # First complete the session if not already completed
        await client.post(
            f"/sessions/{session_id}/complete",
            params={"duration_seconds": 180},
            headers=auth_headers,
        )

        # Then get feedback
        response = await client.get(
            f"/sessions/{session_id}/feedback",
            headers=auth_headers,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        # Validate feedback structure - should have scoring and feedback fields
        assert "overall_score" in data
        assert "detailed_feedback" in data
        # May include: communication_score, strengths, improvements, etc.

    async def test_get_feedback_not_found(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test getting feedback for non-existent session returns 404."""
        response = await client.get(
            "/sessions/999999/feedback",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_get_feedback_unauthorized(
        self,
        client: httpx.AsyncClient,
        test_session: Dict[str, Any]
    ):
        """Test getting feedback without authentication fails."""
        session_id = test_session["id"]
        response = await client.get(f"/sessions/{session_id}/feedback")

        assert response.status_code in [401, 403]

    async def test_get_feedback_incomplete_session(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
        valid_session_data: Dict[str, str]
    ):
        """Test getting feedback for incomplete session."""
        # Create a new session
        create_response = await client.post(
            "/sessions",
            json=valid_session_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        # Try to get feedback without completing
        response = await client.get(
            f"/sessions/{session_id}/feedback",
            headers=auth_headers,
        )

        # May succeed with partial feedback or require completion
        assert response.status_code in [200, 400, 404]


@pytest.mark.sessions
@pytest.mark.integration
class TestSessionWorkflow:
    """Test complete session workflow integration."""

    async def test_full_session_lifecycle(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
        valid_session_data: Dict[str, str]
    ):
        """Test creating, completing, and retrieving feedback for a session."""
        # 1. Create session
        create_response = await client.post(
            "/sessions",
            json=valid_session_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        session_id = create_response.json()["id"]

        # 2. Retrieve session
        get_response = await client.get(
            f"/sessions/{session_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200

        # 3. Complete session
        complete_response = await client.post(
            f"/sessions/{session_id}/complete",
            params={"duration_seconds": 240},
            headers=auth_headers,
        )
        assert complete_response.status_code == 200

        # 4. Get feedback
        feedback_response = await client.get(
            f"/sessions/{session_id}/feedback",
            headers=auth_headers,
        )
        assert feedback_response.status_code == 200

        # 5. Verify session appears in list
        list_response = await client.get("/sessions", headers=auth_headers)
        assert list_response.status_code == 200
        sessions_data = list_response.json()
        sessions = sessions_data.get("sessions", sessions_data)
        session_ids = [s["id"] for s in sessions]
        assert session_id in session_ids
