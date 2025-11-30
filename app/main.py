# C:\Users\Suraj\code\python\genai-coach\backend\app\main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
import os
import base64
import logging
import time

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from .api.routes.auth import router as auth_router
from .api.routes.upload import router as upload_router
from .ai.routers.chat import router as ai_chat_router
from .ai.routers.voice import router as ai_voice_router
from .db.session import init_db


# -------------------------------------------------------------------------
# Tracing Configuration - MUST BE DEFINED BEFORE create_app()
# -------------------------------------------------------------------------
def configure_tracing():
    """Configure OpenTelemetry tracing for Grafana Cloud"""
    try:
        endpoint = os.getenv("OTLP_TRACES_ENDPOINT")
        user = os.getenv("GRAFANA_OTLP_USER")
        token = os.getenv("GRAFANA_OTLP_TOKEN")

        if not endpoint or not user or not token:
            print("⚠️  Tracing not configured: Missing OTLP credentials")
            return

        # Create base64 encoded auth header
        b64 = base64.b64encode(f"{user}:{token}".encode()).decode()
        
        # Configure resource with service information
        resource = Resource.create({
            "service.name": "genai-coach-backend",
            "deployment.environment": os.getenv("ENV", "dev"),
        })
        
        # Set up tracer provider
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)

        # Ensure endpoint has correct path
        if endpoint.endswith("/otlp"):
            endpoint = endpoint.rstrip("/") + "/v1/traces"
        
        # Create and configure exporter
        exporter = OTLPSpanExporter(
            endpoint=endpoint,
            headers={"Authorization": f"Basic {b64}"}
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        
        print(f"✅ Tracing configured successfully to {endpoint}")
    except Exception as e:
        print(f"⚠️  Failed to configure tracing: {e}")
        return

def configure_logging():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '{"t":"%(asctime)s","lvl":"%(levelname)s","logger":"%(name)s","msg":"%(message)s","service":"genai-coach-backend"}',
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = []
    root.setLevel(logging.INFO)
    root.addHandler(handler)


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

    # Configure tracing BEFORE instrumenting
    configure_logging()
    configure_tracing()
    
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
        return PlainTextResponse(
            content="# HELP app_info Application information\n"
                    "# TYPE app_info gauge\n"
                    'app_info{version="0.1.0",service="genai-coach-backend"} 1\n'
        )

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
