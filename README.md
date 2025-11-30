# AI Mock Interview Coach — Backend

A FastAPI backend for an AI-powered mock interview coach. It provides authentication, file uploads, conversational AI agents, observability, and data storage. The architecture is modular and designed for scalability, tracing, and multiple LLM providers.

## Project Structure

- `app/` — application code
  - `main.py` — FastAPI app factory, CORS, tracing, routes, access logs
  - `api/` — REST routes and dependencies
    - `routes/auth.py` — register/login/me/refresh/logout
    - `routes/upload.py` — presigned S3 upload
    - `deps.py` — DB and auth dependency helpers
  - `ai/` — modular AI architecture
    - `adapters/` — external integrations
      - `llms/` — Ollama and HuggingFace LLM adapters
      - `search/` — DuckDuckGo search adapter
      - `speech/` — speech-to-text and text-to-speech stubs
      - `vector/` — Qdrant client adapter
    - `agents/` — reusable agents
      - `chat_agent.py` — conversational interview coach
      - `voice_agent.py` — voice pipeline (STT → chat → TTS)
      - `data_agent.py` — SQL-aware agent
      - `document_agent.py` — ingestion + QA via memory
    - `repositories/` — persistence-facing modules
      - `memory_repository.py` — vector storage + search in Qdrant
      - `user_repository.py` — user updates via SQLAlchemy
    - `routers/` — FastAPI integration
      - `chat.py` — `POST /ai/chat`
      - `voice.py` — `WS /ws/transcribe`
    - `services/` — domain services
      - `embedding_service.py` — embeddings via HF/Ollama
      - `tracing.py` — LangSmith env setup
    - `tools/` — tool wrappers (search, SQL, memory)
    - `workflows/` — LangGraph workflows (optional)
    - `config.py` — AI provider/model settings
  - `db/` — database setup
    - `session.py` — SQLAlchemy engine and `init_db`
    - `models.py` — `User` model
  - `schemas/` — Pydantic models for API
  - `security/jwt.py` — JWT issue/verify helpers
- `migrations/` — Alembic migrations
- `observability/` — Prometheus/Promtail configs
- `Dockerfile`, `docker-compose.yml` — containerization
- `requirements.txt` — Python dependencies

## Purpose

- Provide reliable APIs for user auth and uploads
- Orchestrate AI agents for interview coaching
- Support choice of local/remote LLMs (Ollama/HuggingFace)
- Persist structured data in SQL and unstructured vectors in Qdrant
- Emit logs and traces to Grafana-compatible backends

## Key Endpoints

- `GET /health` — service health (`app/main.py`)
- `GET /metrics` — simple metrics (`app/main.py`)
- `POST /auth/register` — create user (`app/api/routes/auth.py`)
- `POST /auth/login` — login and receive tokens (`app/api/routes/auth.py`)
- `GET /auth/me` — current user (`app/api/routes/auth.py`)
- `POST /auth/refresh` — exchange refresh for new access (`app/api/routes/auth.py`)
- `POST /auth/logout` — clear refresh cookie (`app/api/routes/auth.py`)
- `POST /upload/s3-presign` — presigned URL for uploads (`app/api/routes/upload.py`)
- `POST /ai/chat` — chat reply (`app/ai/routers/chat.py`)
- `WS /ws/transcribe` — voice session streaming (`app/ai/routers/voice.py`)

## Data Flow

- Auth: JWT access and refresh tokens; `OAuth2PasswordBearer` dependency gate
- Uploads: client requests presign → uploads audio directly to S3/compatible storage
- AI chat: request → LLM adapter → agent response → logs + traces
- Voice: WebSocket receives `session_start`/`audio_uri`/`text` → emits transcript and streamed chunks
- Memory: texts embedded → Qdrant upsert; similarity search used in QA

## Observability

- Logs: JSON via standard Python logging; access logs middleware
- Traces: OpenTelemetry OTLP exporter; FastAPI and requests instrumented
- Optional LangSmith (LangChain) tracing: enable via env

### Environment Variables (observability)

- `OTLP_TRACES_ENDPOINT` — OTLP HTTP endpoint (Tempo)
- `GRAFANA_OTLP_USER` — basic auth user
- `GRAFANA_OTLP_TOKEN` — basic auth token
- `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` — LangSmith

## Configuration

### Database

- `DATABASE_URL` — default `sqlite:///aimic.db`
  - For MySQL: `mysql+pymysql://user:pass@host:3306/dbname`

### Security

- `JWT_SECRET` — HMAC secret
- `ACCESS_TOKEN_EXPIRE_MINUTES` — default 60
- `REFRESH_TOKEN_EXPIRE_DAYS` — default 30

### Uploads

- `AWS_S3_BUCKET`, `AWS_REGION`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Optional: `S3_ENDPOINT`, `S3_PUBLIC_ENDPOINT` for S3-compatible providers

### AI Providers

- `LLM_PROVIDER=ollama|hf`
- `OLLAMA_MODEL=llama3` (example)
- `HF_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1`
- `EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2`
- `QDRANT_URL`, `QDRANT_API_KEY`

## Quick Start

### Local (Python)

```bash
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --port 8000
```

Open `http://localhost:8000/health` to verify.

### Docker

```bash
docker compose up -d
```

### Authentication & Chat

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"secret123","name":"User"}'

# Chat (replace TOKEN)
curl -X POST http://localhost:8000/ai/chat \
  -H "Authorization: Bearer TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hello AI"}'
```

## Migrations

```bash
# Create a migration
alembic revision --autogenerate -m "change"
# Apply
alembic upgrade head
```

## Testing

```bash
pytest -q
```

## Design Notes

- Clean architecture: adapters ↔ services ↔ repositories ↔ agents, exposed via routers
- Pluggable LLMs: switch via environment without code changes
- Streaming: WebSocket for voice; REST for chat (extendable to SSE)
- Safe fallbacks: adapters and services guard optional dependencies and degrade gracefully
