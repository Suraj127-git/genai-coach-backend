"""
Sentry compatibility stub - re-exports logging functions.
This module provides backward compatibility after Sentry removal.
All functions now use the enhanced core logging system.
"""
from app.core.logging import (
    get_logger,
    capture_exception as _capture_exception,
    capture_message as _capture_message,
    add_breadcrumb as _add_breadcrumb,
    set_user_context as _set_user_context,
    set_context as _set_context,
    start_span as _start_span,
)

logger = get_logger(__name__)


def init_sentry() -> None:
    """
    No-op function for backward compatibility.
    Sentry has been replaced with core logging.
    """
    logger.info("Sentry replaced with core logging system - no initialization needed")


def capture_exception(error: Exception, **kwargs) -> None:
    """
    Capture an exception using core logging.

    Args:
        error: Exception to capture
        **kwargs: Additional context (tags, extra, user, level)
    """
    _capture_exception(
        error,
        tags=kwargs.get('tags'),
        extra=kwargs.get('extra'),
        user=kwargs.get('user'),
        level=kwargs.get('level', 'error')
    )


def capture_message(message: str, level: str = "info", **kwargs) -> None:
    """
    Capture a message using core logging.

    Args:
        message: Message to capture
        level: Severity level
        **kwargs: Additional context (tags, extra)
    """
    _capture_message(
        message,
        level=level,
        tags=kwargs.get('tags'),
        extra=kwargs.get('extra')
    )


def set_user_context(user_id: str, email: str = None, **kwargs) -> None:
    """
    Set user context for logging.

    Args:
        user_id: User ID (converted to int if needed)
        email: User email
        **kwargs: Additional user data
    """
    # Convert string user_id to int if needed
    try:
        uid = int(user_id) if isinstance(user_id, str) else user_id
    except (ValueError, TypeError):
        uid = user_id

    _set_user_context(uid, email, **kwargs)


def set_context(key: str, data: dict) -> None:
    """
    Set custom context for logging.

    Args:
        key: Context key
        data: Context data dictionary
    """
    _set_context(key, data)


def add_breadcrumb(message: str, category: str = "custom", level: str = "info", **kwargs) -> None:
    """
    Add a breadcrumb for debugging context.

    Args:
        message: Breadcrumb message
        category: Category
        level: Severity level
        **kwargs: Additional data (passed as 'data' key)
    """
    _add_breadcrumb(
        message,
        category=category,
        level=level,
        data=kwargs.get('data')
    )


def start_transaction(name: str, op: str = "function"):
    """
    Start a logging span (replaces Sentry transaction).

    Args:
        name: Transaction/span name
        op: Operation type

    Returns:
        LogSpan context manager
    """
    return _start_span(op, name)


def start_span(operation: str, description: str = None):
    """
    Start a logging span for performance tracking.

    Args:
        operation: Span operation
        description: Span description

    Returns:
        LogSpan context manager
    """
    return _start_span(operation, description)


# Deprecated/unused Sentry functions (no-ops for compatibility)

def before_send_filter(event, hint):
    """No-op - Sentry removed."""
    return event


def before_breadcrumb_filter(crumb, hint):
    """No-op - Sentry removed."""
    return crumb
