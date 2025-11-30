from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..config import load_settings
from ..adapters.llms.ollama import OllamaLLM
from ..adapters.llms.hf import HuggingFaceLLM
from ..agents.chat_agent import ChatAgent
from ..agents.voice_agent import VoiceAgent
import json
import logging
from opentelemetry import trace

router = APIRouter()
logger = logging.getLogger("ai.voice")
tracer = trace.get_tracer("ai.voice")

def _llm_from_settings():
    s = load_settings()
    if s.llm_provider == "hf":
        return HuggingFaceLLM(s.hf_model)
    return OllamaLLM(s.ollama_model)

@router.websocket("/ws/transcribe")
async def ws_transcribe(ws: WebSocket):
    await ws.accept()
    llm = _llm_from_settings()
    chat = ChatAgent(llm)
    voice = VoiceAgent(chat)
    logger.info('{"evt":"ws_open"}')
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                msg = {"type": "text", "text": raw}
            t = msg.get("type")
            if t == "session_start":
                logger.info('{"evt":"session_start"}')
                await ws.send_text(json.dumps({"type": "ack"}))
            elif t == "audio_uri":
                txt = (msg.get("uri") or "").strip()
                with tracer.start_as_current_span("voice.audio") as span:
                    span.set_attribute("ai.uri_len", len(txt))
                    logger.info(f"{{\"evt\":\"audio_uri\",\"len\":{len(txt)}}}")
                    res = voice.handle_text(txt)
                    await ws.send_text(json.dumps({"type": "transcript", "text": res.get("transcript", "")}))
            elif t == "text":
                text = msg.get("text") or ""
                with tracer.start_as_current_span("voice.text") as span:
                    span.set_attribute("ai.input_len", len(text))
                    logger.info(f"{{\"evt\":\"text\",\"len\":{len(text)}}}")
                    out = chat.run(text)
                    span.set_attribute("ai.output_len", len(out))
                for i in range(0, len(out), 32):
                    await ws.send_text(json.dumps({"type": "chunk", "text": out[i:i+32]}))
                await ws.send_text(json.dumps({"type": "done"}))
            else:
                logger.warning(f"{{\"evt\":\"unknown\",\"type\":\"{t}\"}}")
                await ws.send_text(json.dumps({"type": "error", "error": "unknown"}))
    except WebSocketDisconnect:
        logger.info('{"evt":"ws_close"}')
        return

