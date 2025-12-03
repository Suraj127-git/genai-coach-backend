"""
Script to create a test user for development.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import async_session_maker
from app.core.security import get_password_hash
from app.models.user import User


async def create_test_user():
    """Create a test user."""
    email = "test@example.com"
    password = "test123"
    name = "Test User"

    async with async_session_maker() as session:
        # Check if user already exists
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"User {email} already exists!")
            return

        # Create new user
        user = User(
            email=email,
            name=name,
            hashed_password=get_password_hash(password),
            is_active=True,
        )

        session.add(user)
        await session.commit()

        print(f"Test user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")


if __name__ == "__main__":
    asyncio.run(create_test_user())
