"""
Debug endpoints for testing Sentry integration.
Only available in development mode.
"""
from fastapi import APIRouter, HTTPException, Depends

from app.core.config import settings
from app.core.sentry import capture_message, add_breadcrumb, capture_exception
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/sentry-test-error")
async def test_sentry_error():
    """
    Test endpoint to trigger a Sentry error.
    Only works when Sentry is configured.
    """
    if not settings.SENTRY_DSN:
        return {"message": "Sentry not configured. Set SENTRY_DSN environment variable."}

    add_breadcrumb(
        "Testing Sentry error tracking",
        category="test",
        level="info"
    )

    # Trigger an intentional error
    division_by_zero = 1 / 0
    return {"message": "This won't be reached"}


@router.get("/sentry-test-message")
async def test_sentry_message():
    """
    Test endpoint to send a message to Sentry.
    """
    if not settings.SENTRY_DSN:
        return {"message": "Sentry not configured. Set SENTRY_DSN environment variable."}

    capture_message(
        "Test message from GenAI Coach Backend",
        level="info",
        tags={"test": "true"},
        extra={"endpoint": "/debug/sentry-test-message"}
    )

    return {"message": "Test message sent to Sentry. Check your dashboard."}


@router.get("/sentry-test-exception")
async def test_sentry_exception():
    """
    Test endpoint to capture a handled exception.
    """
    if not settings.SENTRY_DSN:
        return {"message": "Sentry not configured. Set SENTRY_DSN environment variable."}

    try:
        # Simulate an error
        raise ValueError("This is a test exception")
    except Exception as e:
        capture_exception(
            e,
            tags={"test": "true", "type": "handled"},
            extra={"message": "This was caught and handled"}
        )
        return {
            "message": "Exception captured and sent to Sentry",
            "error": str(e),
            "status": "handled"
        }


@router.get("/sentry-test-auth")
async def test_sentry_with_auth(current_user: User = Depends(get_current_user)):
    """
    Test endpoint to verify user context is sent to Sentry.
    Requires authentication.
    """
    if not settings.SENTRY_DSN:
        return {"message": "Sentry not configured. Set SENTRY_DSN environment variable."}

    add_breadcrumb(
        f"Authenticated user testing Sentry: {current_user.email}",
        category="auth",
        level="info",
        data={"user_id": str(current_user.id)}
    )

    # Trigger an error with user context
    raise HTTPException(status_code=500, detail="Test error with user context")


@router.get("/sentry-status")
async def sentry_status():
    """
    Check Sentry configuration status.
    """
    return {
        "sentry_enabled": bool(settings.SENTRY_DSN),
        "environment": settings.SENTRY_ENVIRONMENT,
        "traces_sample_rate": settings.SENTRY_TRACES_SAMPLE_RATE,
        "profiles_sample_rate": settings.SENTRY_PROFILES_SAMPLE_RATE,
        "app_version": settings.APP_VERSION,
    }
