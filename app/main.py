# C:\Users\Suraj\code\python\genai-coach\backend\app\main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
import os
 

from .api.routes.auth import router as auth_router
from .api.routes.upload import router as upload_router
from .db.session import init_db


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

    
    # Initialize DB (db.session will create engine etc.)
    init_db()

    # Health check endpoint
    @app.get("/health", tags=["monitoring"]) 
    async def health_check():
        return JSONResponse(
            status_code=200,
            content={"status": "healthy", "service": "genai-coach-backend", "version": "0.1.0"}
        )

    # Metrics endpoint
    @app.get("/metrics", tags=["monitoring"], response_class=PlainTextResponse)
    async def metrics():
        return PlainTextResponse(
            content="# HELP app_info Application information\n"
                    "# TYPE app_info gauge\n"
                    'app_info{version="0.1.0",service="genai-coach-backend"} 1\n'
        )

    # Routers
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(upload_router, prefix="/upload", tags=["upload"])

    return app


app = create_app()
