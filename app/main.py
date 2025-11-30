# C:\Users\Suraj\code\python\genai-coach\backend\app\main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
import logging
import time
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from .core.config import SERVICE_NAME, ENV
from .core.logging import configure_logging
from .core.observability.opentelemetry import configure_tracing
from .db.session import init_db
from .modules.auth.routes import router as auth_router
from .modules.upload.routes import router as upload_router
from .modules.ai.routers.chat import router as ai_chat_router
from .modules.ai.routers.voice import router as ai_voice_router


# -------------------------------------------------------------------------
# Tracing Configuration - MUST BE DEFINED BEFORE create_app()
# -------------------------------------------------------------------------
def _configure_logging_and_tracing():
    configure_logging(SERVICE_NAME)
    configure_tracing(SERVICE_NAME, ENV)


# -------------------------------------------------------------------------
# FastAPI application factory
# -------------------------------------------------------------------------
def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(title="AI Mock Interview Coach API", version="0.1.0")

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configure logging and tracing BEFORE instrumenting
    _configure_logging_and_tracing()
    
    # Instrument FastAPI and requests
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()

    # Initialize database
    init_db()
    logging.getLogger(__name__).info("backend initialized")

    # -------------------------------------------------------------------------
    # Routes
    # -------------------------------------------------------------------------
    
    @app.get("/health", tags=["monitoring"]) 
    async def health_check():
        logging.getLogger(__name__).info("health")
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "genai-coach-backend",
                "version": "0.1.0"
            }
        )

    @app.get("/metrics", tags=["monitoring"], response_class=PlainTextResponse)
    async def metrics():
        logging.getLogger(__name__).info("metrics")
        from .core.observability.metrics import metrics_response
        return metrics_response()

    # Include API routers
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(upload_router, prefix="/upload", tags=["upload"])
    app.include_router(ai_chat_router, prefix="/ai", tags=["ai"])
    app.include_router(ai_voice_router, tags=["ai"])

    @app.middleware("http")
    async def access_log(request, call_next):
        started = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - started) * 1000)
        client = request.client
        addr = f"{client.host}:{client.port}" if client else "-"
        logging.getLogger("access").info(f"{addr} {request.method} {request.url.path} {response.status_code} {duration_ms}ms")
        return response

    return app


# Create the application instance
app = create_app()
