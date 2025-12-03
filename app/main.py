"""
Main FastAPI application module.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.sentry import init_sentry
from app.middleware.cors import setup_cors
from app.middleware.error_handler import setup_error_handlers
from app.middleware.sentry_middleware import setup_sentry_middleware
from app.api.endpoints import auth, upload, sessions, ai, websocket, debug

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize Sentry
init_sentry()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered mock interview coach backend API",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Setup middleware
setup_cors(app)
setup_sentry_middleware(app)
setup_error_handlers(app)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
    }


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

# Debug endpoints (only for testing Sentry)
if settings.DEBUG or settings.ENVIRONMENT == "development":
    app.include_router(debug.router, prefix="/debug", tags=["Debug"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
