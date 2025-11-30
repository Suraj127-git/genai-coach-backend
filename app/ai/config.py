from pydantic import BaseModel
import os

class AISettings(BaseModel):
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    hf_model: str = os.getenv("HF_MODEL", "mistralai/Mixtral-8x7B-Instruct-v0.1")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    qdrant_url: str | None = os.getenv("QDRANT_URL")
    qdrant_api_key: str | None = os.getenv("QDRANT_API_KEY")
    langsmith_api_key: str | None = os.getenv("LANGCHAIN_API_KEY")
    use_tracing: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"

def load_settings() -> AISettings:
    return AISettings()
