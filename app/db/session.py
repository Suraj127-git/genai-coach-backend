from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///aimic.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SQLAlchemyInstrumentor().instrument(engine=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from ..modules.auth import models as auth_models  # noqa: F401
    from .base import Base
    Base.metadata.create_all(bind=engine)

