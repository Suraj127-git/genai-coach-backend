from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
import logging

from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///aimic.db")
logger = logging.getLogger("db.session")

try:
    logger.info("creating engine")
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    )
except Exception as e:
    logger.critical("engine creation failed", extra={"error": str(e)})
    raise
else:
    logger.info("engine created")

# 🔹 Instrument SQLAlchemy so all DB queries become spans in Tempo
SQLAlchemyInstrumentor().instrument(engine=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    try:
        logger.info("init_db start")
        from . import models  # noqa: F401
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.critical("init_db failed", extra={"error": str(e)})
        raise
    else:
        logger.info("init_db success")
