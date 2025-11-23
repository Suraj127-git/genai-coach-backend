# C:\Users\Suraj\code\python\genai-coach\backend\app\main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
import logging
import os
import time
from logging_loki.handlers import LokiHandler

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from .api.routes.auth import router as auth_router
from .api.routes.upload import router as upload_router
from .db.session import init_db


# -------------------------------------------------------------------------
# Logging filter: attach current otel trace/span ids to every LogRecord
# (defensive: only set if attribute missing to avoid KeyError)
# -------------------------------------------------------------------------
class TraceLoggingFilter(logging.Filter):
    """
    Add otelTraceID and otelSpanID attributes to logging.LogRecord so
    they can be included in formatter and sent to Loki.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            # Don't overwrite if already present
            if not hasattr(record, "otelTraceID"):
                record.otelTraceID = ""
            if not hasattr(record, "otelSpanID"):
                record.otelSpanID = ""

            span = trace.get_current_span()
            if not span:
                return True

            ctx = span.get_span_context()
            # trace_id and span_id are integers (0 if invalid). Format as hex.
            if ctx and getattr(ctx, "trace_id", 0):
                record.otelTraceID = f"{ctx.trace_id:032x}"
            if ctx and getattr(ctx, "span_id", 0):
                record.otelSpanID = f"{ctx.span_id:016x}"
        except Exception:
            # Never fail logging due to instrumentation issues
            if not hasattr(record, "otelTraceID"):
                record.otelTraceID = ""
            if not hasattr(record, "otelSpanID"):
                record.otelSpanID = ""
        return True


# -------------------------------------------------------------------------
# Configure OpenTelemetry Tracing (Tempo)
# -------------------------------------------------------------------------
def configure_tracing():
    resource = Resource.create({
        "service.name": "genai-coach-api",
        "environment": os.getenv("ENV", "dev"),
    })

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # OTLP HTTP exporter to Tempo (Tempo listens on 4318 for HTTP OTLP)
    otlp_exporter = OTLPSpanExporter(endpoint="http://tempo:4318/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    logging.getLogger(__name__).info("🚀 OpenTelemetry tracing initialized")


# -------------------------------------------------------------------------
# Configure Loki logging (with trace/span ID injection)
# -------------------------------------------------------------------------
def configure_logging():
    loki_url = os.getenv("LOKI_URL", "http://loki:3100/loki/api/v1/push")

    handler = LokiHandler(
        url=loki_url,
        tags={"service": "genai-coach-api", "environment": os.getenv("ENV", "dev")},
    )

    # 🚀 Updated: Use ISO 8601 timestamp format for better parsing
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"trace_id": "%(otelTraceID)s", "span_id": "%(otelSpanID)s", '
        '"service": "genai-coach-api", "logger": "%(name)s", "message": "%(message)s"}',
        datefmt='%Y-%m-%dT%H:%M:%S'  # ISO 8601 format without timezone (Promtail will handle)
    )
    handler.setFormatter(formatter)

    trace_filter = TraceLoggingFilter()
    handler.addFilter(trace_filter)

    # Also log to console for Docker logs collection by Promtail
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(trace_filter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    root.addHandler(console_handler)  # Add console handler for Promtail
    root.addFilter(trace_filter)

    # Instrument logging to propagate context
    LoggingInstrumentor().instrument(set_logging_format=False)

    logging.getLogger(__name__).info("🚀 Loki logging initialized (with trace IDs)")


# -------------------------------------------------------------------------
# FastAPI application factory
# -------------------------------------------------------------------------
def create_app() -> FastAPI:
    app = FastAPI(title="AI Mock Interview Coach API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize tracing first so filter can read span context
    configure_tracing()
    configure_logging()

    # Auto-instrument FastAPI + requests
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()

    # Initialize DB (db.session will create engine etc.)
    init_db()
    logging.getLogger(__name__).info("Database initialized successfully")

    # Middleware to log HTTP requests (do NOT pass 'extra' with otel keys)
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # We do NOT pass a conflicting `extra` that contains otelTraceID/otelSpanID.
        # The TraceLoggingFilter will add those attributes to the LogRecord.
        client = request.client
        client_addr = f"{client.host}:{client.port}" if client else "unknown"

        logger = logging.getLogger("access")
        logger.info(
            f'{client_addr} - "{request.method} {request.url.path}" {response.status_code} {duration_ms}ms'
        )

        return response

    # Health check endpoint
    @app.get("/health", tags=["monitoring"])
    async def health_check():
        logging.info("Health check endpoint accessed")
        return JSONResponse(
            status_code=200,
            content={"status": "healthy", "service": "genai-coach-backend", "version": "0.1.0"}
        )

    # Metrics endpoint
    @app.get("/metrics", tags=["monitoring"], response_class=PlainTextResponse)
    async def metrics():
        logging.info("Metrics endpoint accessed")
        return PlainTextResponse(
            content="# HELP app_info Application information\n"
                    "# TYPE app_info gauge\n"
                    'app_info{version="0.1.0",service="genai-coach-backend"} 1\n'
        )

    # Routers
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(upload_router, prefix="/upload", tags=["upload"])

    logging.getLogger(__name__).info("Application started successfully with tracing & logging")
    return app


app = create_app()
