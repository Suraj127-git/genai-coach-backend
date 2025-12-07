"""
AI Service API endpoint tests.

Tests all AI-related endpoints:
- POST /ai/chat

NOTE: These tests require a valid Groq API key configured on the backend.
If the Groq API key is invalid or missing, these tests will fail with 500 errors.
This is expected behavior and indicates the backend needs proper API key configuration.
"""
import pytest
import httpx
from typing import Dict, Any


@pytest.mark.ai
@pytest.mark.smoke
class TestAIChat:
    """Test AI chat endpoint."""

    async def test_chat_success(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
        valid_chat_message: Dict[str, str]
    ):
        """Test successful chat interaction with AI."""
        response = await client.post(
            "/ai/chat",
            json=valid_chat_message,
            headers=auth_headers,
        )

        # AI tests may fail if Groq API key is not configured
        if response.status_code == 500 and "API key" in response.text:
            pytest.skip("Groq API key not configured on backend")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        # Validate response structure
        assert "reply" in data
        assert isinstance(data["reply"], str)
        assert len(data["reply"]) > 0

    async def test_chat_interview_question(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test chat with interview-related question."""
        chat_data = {
            "message": "What are common behavioral interview questions?",
        }

        response = await client.post(
            "/ai/chat",
            json=chat_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert len(data["reply"]) > 0

    async def test_chat_technical_question(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test chat with technical interview question."""
        chat_data = {
            "message": "Explain the STAR method for answering behavioral questions.",
        }

        response = await client.post(
            "/ai/chat",
            json=chat_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "STAR" in data["reply"] or "star" in data["reply"].lower()

    async def test_chat_empty_message(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test chat with empty message."""
        chat_data = {
            "message": "",
        }

        response = await client.post(
            "/ai/chat",
            json=chat_data,
            headers=auth_headers,
        )

        # Should either succeed with generic response or fail validation
        assert response.status_code in [200, 422]

    async def test_chat_long_message(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test chat with very long message."""
        long_message = " ".join([
            "This is a very long message with lots of context about interview preparation.",
            "I want to know how to prepare for technical interviews at major tech companies.",
            "What are the best strategies for algorithm and data structure problems?",
            "How should I practice system design questions?",
            "What about behavioral interview preparation?",
        ] * 10)  # Make it really long

        chat_data = {
            "message": long_message,
        }

        response = await client.post(
            "/ai/chat",
            json=chat_data,
            headers=auth_headers,
        )

        # Should handle long messages
        assert response.status_code in [200, 413, 422]

    async def test_chat_special_characters(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test chat with special characters."""
        chat_data = {
            "message": "How do I answer: 'What's your greatest weakness?' 😊",
        }

        response = await client.post(
            "/ai/chat",
            json=chat_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "reply" in data

    async def test_chat_unauthorized(
        self,
        client: httpx.AsyncClient,
        valid_chat_message: Dict[str, str]
    ):
        """Test chat without authentication fails."""
        response = await client.post("/ai/chat", json=valid_chat_message)

        assert response.status_code in [401, 403]

    async def test_chat_invalid_token(
        self,
        client: httpx.AsyncClient,
        valid_chat_message: Dict[str, str]
    ):
        """Test chat with invalid token fails."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await client.post(
            "/ai/chat",
            json=valid_chat_message,
            headers=headers,
        )

        assert response.status_code in [401, 403]

    async def test_chat_missing_message(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test chat with missing message field fails."""
        response = await client.post(
            "/ai/chat",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.ai
@pytest.mark.integration
class TestAIChatIntegration:
    """Integration tests for AI chat functionality."""

    async def test_multiple_chat_messages(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test sending multiple chat messages in sequence."""
        messages = [
            "Tell me about technical interviews.",
            "What about behavioral interviews?",
            "How do I prepare for system design?",
        ]

        for message in messages:
            response = await client.post(
                "/ai/chat",
                json={"message": message},
                headers=auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert "reply" in data
            assert len(data["reply"]) > 0

    async def test_chat_context_awareness(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test if chat maintains or handles context appropriately."""
        # First message
        response1 = await client.post(
            "/ai/chat",
            json={"message": "What is the STAR method?"},
            headers=auth_headers,
        )
        assert response1.status_code == 200

        # Follow-up question (may or may not maintain context)
        response2 = await client.post(
            "/ai/chat",
            json={"message": "Can you give me an example?"},
            headers=auth_headers,
        )
        assert response2.status_code == 200
        data = response2.json()
        assert "reply" in data

    async def test_chat_various_topics(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test chat with various interview-related topics."""
        topics = [
            "How do I negotiate salary?",
            "What should I ask the interviewer?",
            "How do I handle difficult interview questions?",
            "Tell me about resume tips.",
            "What are common interview mistakes?",
        ]

        for topic in topics:
            response = await client.post(
                "/ai/chat",
                json={"message": topic},
                headers=auth_headers,
            )
            assert response.status_code == 200, f"Failed for topic: {topic}"
            data = response.json()
            assert "reply" in data
            assert len(data["reply"]) > 10  # Should have meaningful response


@pytest.mark.ai
class TestAIChatEdgeCases:
    """Edge case tests for AI chat."""

    async def test_chat_code_in_message(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test chat with code snippets in message."""
        chat_data = {
            "message": """
            How would you explain this code in an interview?

            def fibonacci(n):
                if n <= 1:
                    return n
                return fibonacci(n-1) + fibonacci(n-2)
            """,
        }

        response = await client.post(
            "/ai/chat",
            json=chat_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "reply" in data

    async def test_chat_markdown_in_message(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test chat with markdown formatting."""
        chat_data = {
            "message": """
            # Interview Prep

            1. **Technical Skills**
            2. *Behavioral Questions*
            3. `System Design`

            How do I improve in these areas?
            """,
        }

        response = await client.post(
            "/ai/chat",
            json=chat_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "reply" in data

    async def test_chat_non_english(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test chat with non-English characters."""
        chat_data = {
            "message": "¿Cómo preparo para una entrevista? 面试准备",
        }

        response = await client.post(
            "/ai/chat",
            json=chat_data,
            headers=auth_headers,
        )

        # Should handle gracefully
        assert response.status_code in [200, 422]

    async def test_chat_with_urls(
        self,
        client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test chat with URLs in message."""
        chat_data = {
            "message": "I found this article https://example.com/interview-tips. What do you think?",
        }

        response = await client.post(
            "/ai/chat",
            json=chat_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
