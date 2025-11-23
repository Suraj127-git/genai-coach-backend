from __future__ import annotations

from alembic import context
from sqlalchemy import engine_from_config, pool
import os

# Import SQLAlchemy metadata from app
from app.db.session import Base

config = context.config

def get_url() -> str:
    url = os.getenv("DATABASE_URL", "sqlite:///aimic.db")
    # Alembic requires full path for sqlite
    if url.startswith("sqlite") and ":////" not in url:
        url = "sqlite:////" + url.split("sqlite:///")[-1]
    return url

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    cfg = config.get_section(config.config_ini_section) or {}
    cfg["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
