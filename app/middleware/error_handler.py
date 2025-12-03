"""
Global error handler middleware.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import get_logger
from app.core.sentry import capture_exception

logger = get_logger(__name__)


def setup_error_handlers(app: FastAPI) -> None:
    """
    Configure global error handlers.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        errors = exc.errors()
        detail = [{"msg": error["msg"], "field": error["loc"][-1]} for error in errors]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": detail},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handle database errors."""
        logger.error(f"Database error: {exc}")

        # Capture in Sentry
        capture_exception(
            exc,
            tags={"error_type": "database"},
            extra={
                "path": request.url.path,
                "method": request.method,
            }
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Database error occurred"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected errors."""
        logger.error(f"Unexpected error: {exc}", exc_info=True)

        # Capture in Sentry
        capture_exception(
            exc,
            tags={"error_type": "unhandled"},
            extra={
                "path": request.url.path,
                "method": request.method,
                "query_params": dict(request.query_params),
            }
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
