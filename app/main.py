from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.auth import router as auth_router
from .api.routes.upload import router as upload_router
from .db.session import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="AI Mock Interview Coach API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    init_db()

    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(upload_router, prefix="/upload", tags=["upload"])

    return app


app = create_app()
