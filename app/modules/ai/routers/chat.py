from fastapi import APIRouter, Depends
from backend.app.core.dependencies import get_current_user_id
from ..schemas.chat import ChatRequest
from ..config import load_settings
from ..adapters.llms.ollama import OllamaLLM
from ..adapters.llms.hf import HuggingFaceLLM
from ..agents.chat_agent import ChatAgent
import logging
from opentelemetry import trace

router = APIRouter()
logger = logging.getLogger("ai.chat")
tracer = trace.get_tracer("ai.chat")

class _ChatRequest(ChatRequest):
    pass

def _llm_from_settings():
    s = load_settings()
    if s.llm_provider == "hf":
        return HuggingFaceLLM(s.hf_model)
    return OllamaLLM(s.ollama_model)

@router.post("/chat")
def chat(req: _ChatRequest, user_id: str = Depends(get_current_user_id)):
    with tracer.start_as_current_span("chat") as span:
        llm = _llm_from_settings()
        span.set_attribute("ai.user_id", user_id)
        span.set_attribute("ai.input_length", len(req.message))
        provider = "hf" if isinstance(llm, HuggingFaceLLM) else "ollama"
        span.set_attribute("ai.provider", provider)
        logger.info(f"{{\"evt\":\"chat_request\",\"user\":\"{user_id}\",\"provider\":\"{provider}\",\"len\":{len(req.message)}}}")
        agent = ChatAgent(llm)
        out = agent.run(req.message)
        span.set_attribute("ai.output_length", len(out))
        logger.info(f"{{\"evt\":\"chat_reply\",\"user\":\"{user_id}\",\"len\":{len(out)}}}")
        return {"reply": out}

