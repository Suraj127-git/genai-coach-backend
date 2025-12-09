"""
RAG (Retrieval-Augmented Generation) service for user context retrieval.
LIGHTWEIGHT VERSION: Uses database queries instead of vector embeddings.
This version doesn't require ChromaDB, HuggingFace, or PyTorch dependencies.
"""
from typing import Dict, List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import get_logger
from app.core.sentry import add_breadcrumb
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.session import InterviewSession

logger = get_logger(__name__)


class RAGService:
    """
    Lightweight RAG service using direct database queries.
    This version is compatible with minimal dependencies (no PyTorch).
    """

    def __init__(self):
        """Initialize lightweight RAG service."""
        logger.info("Initializing lightweight RAG service (no vector embeddings)")

        add_breadcrumb(
            "RAG Service Initialization",
            category="rag",
            level="info",
            data={
                "mode": "lightweight",
                "vector_store": "none (using database queries)"
            }
        )

        logger.info("Lightweight RAG service initialization complete")

    async def index_user_context(self, db: AsyncSession, user_id: int) -> bool:
        """
        Index user context (lightweight - just validates user exists).
        In this version, we don't use vector embeddings - context is fetched on-demand.

        Args:
            db: Database session
            user_id: User ID to index

        Returns:
            True if user exists, False otherwise
        """
        logger.info(f"Lightweight RAG indexing for user {user_id}", extra={
            "user_id": user_id,
            "operation": "index_user_context"
        })

        add_breadcrumb(
            "RAG Indexing (Lightweight)",
            category="rag",
            level="info",
            data={"user_id": user_id}
        )

        try:
            # Just verify user exists
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if not user:
                logger.warning(f"User {user_id} not found for indexing", extra={
                    "user_id": user_id,
                    "reason": "user_not_found"
                })
                return False

            logger.info(f"User {user_id} validated for RAG", extra={
                "user_id": user_id,
                "email": user.email
            })
            return True

        except Exception as e:
            logger.error(f"Error validating user context: {e}", exc_info=True)
            return False

    async def retrieve_user_context(
        self,
        db: AsyncSession,
        user_id: int,
        query: Optional[str] = None,
        k: int = 5
    ) -> List[Dict]:
        """
        Retrieve user context using direct database queries (lightweight version).

        Args:
            db: Database session
            user_id: User ID to retrieve context for
            query: Optional query (ignored in lightweight version)
            k: Number of documents to retrieve (ignored in lightweight version)

        Returns:
            List of context documents from database
        """
        try:
            logger.info(f"Retrieving user context for user {user_id}")

            context_docs = []

            # Fetch user
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()

            if user:
                basic_info = f"User: {user.name or user.email}\nEmail: {user.email}"
                context_docs.append({
                    "content": basic_info,
                    "metadata": {"user_id": user_id, "type": "basic_info"},
                    "type": "basic_info"
                })

            # Fetch profile
            profile_result = await db.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            profile = profile_result.scalar_one_or_none()

            if profile:
                profile_text = f"Job Title: {profile.job_title or 'Not specified'}\n"
                if profile.bio:
                    profile_text += f"Bio: {profile.bio}\n"
                context_docs.append({
                    "content": profile_text,
                    "metadata": {"user_id": user_id, "type": "profile"},
                    "type": "profile"
                })

            return context_docs

        except Exception as e:
            logger.error(f"Error retrieving user context: {e}", exc_info=True)
            return []

    async def build_personalized_prompt(
        self,
        db: AsyncSession,
        user_id: int,
        interview_type: str = "general"
    ) -> str:
        """
        Build a personalized system prompt using database-retrieved context.

        Args:
            db: Database session
            user_id: User ID
            interview_type: Type of interview (behavioral, technical, etc.)

        Returns:
            Personalized system prompt
        """
        try:
            # Retrieve user context from database
            context_docs = await self.retrieve_user_context(
                db=db,
                user_id=user_id,
                query=f"{interview_type} interview preparation",
                k=5
            )

            # Build context string
            context_parts = []
            for doc in context_docs:
                context_parts.append(doc["content"])

            user_context = "\n\n".join(context_parts) if context_parts else "No previous context available."

            # Build personalized prompt
            prompt = f"""You are an experienced interview coach conducting a {interview_type} interview.

**Candidate Context:**
{user_context}

**Your Role:**
- Conduct a realistic {interview_type} interview
- Ask relevant questions based on the candidate's background and experience
- Provide real-time feedback and encouragement
- Adapt questions based on the candidate's responses
- Be supportive but maintain professional interview standards
- After each response, provide brief constructive feedback before moving to the next question

**Interview Guidelines:**
- Start with a personalized introduction that references the candidate's background
- Ask 3-5 relevant questions for this interview session
- Listen carefully to responses and ask follow-up questions when needed
- Provide balanced feedback highlighting both strengths and areas for improvement
- End with actionable recommendations for improvement

Begin the interview now with a warm, personalized introduction."""

            return prompt

        except Exception as e:
            logger.error(f"Error building personalized prompt: {e}", exc_info=True)
            # Return fallback prompt
            return f"""You are an experienced interview coach conducting a {interview_type} interview.
Introduce yourself and begin asking relevant interview questions."""

    async def get_user_summary(self, db: AsyncSession, user_id: int) -> str:
        """
        Get a concise summary of user for quick reference.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User summary string
        """
        try:
            context_docs = await self.retrieve_user_context(db=db, user_id=user_id, k=3)

            if not context_docs:
                return "New candidate with no previous interview history."

            # Extract key information
            profile_info = next((doc["content"] for doc in context_docs if doc["type"] == "profile"), "")
            basic_info = next((doc["content"] for doc in context_docs if doc["type"] == "basic_info"), "")

            summary_parts = []
            if basic_info:
                summary_parts.append(basic_info)
            if profile_info:
                summary_parts.append(profile_info)

            return "\n".join(summary_parts) if summary_parts else "Limited candidate information available."

        except Exception as e:
            logger.error(f"Error getting user summary: {e}", exc_info=True)
            return "Error retrieving candidate information."
