FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    WEB_CONCURRENCY=1 \
    DATABASE_URL=sqlite:///aimic.db

# Ensure Python can import the application package when running Alembic
ENV PYTHONPATH=/app

WORKDIR /app

# System libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy application code and migrations
COPY app /app/app
COPY alembic.ini /app/alembic.ini
COPY migrations /app/migrations

# Run as non-root user
RUN useradd -ms /bin/bash appuser || adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Use shell form to allow env variable expansion for PORT/WEB_CONCURRENCY
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WEB_CONCURRENCY:-1} --proxy-headers"]
