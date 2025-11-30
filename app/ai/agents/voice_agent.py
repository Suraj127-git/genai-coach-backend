from typing import Any
import logging
from opentelemetry import trace
from ..adapters.speech.stt import SpeechToText
from ..adapters.speech.tts import TextToSpeech

class VoiceAgent:
    def __init__(self, chat_agent: Any, stt: SpeechToText | None = None, tts: TextToSpeech | None = None):
        self.chat = chat_agent
        self.stt = stt or SpeechToText()
        self.tts = tts or TextToSpeech()
        self.logger = logging.getLogger("ai.agent.voice")
        self.tracer = trace.get_tracer("ai.agent.voice")

    def handle_audio_uri(self, uri: str) -> dict:
        with self.tracer.start_as_current_span("agent.voice") as span:
            span.set_attribute("ai.uri_length", len(uri))
            self.logger.info(f"{{\"evt\":\"voice_handle\",\"uri_len\":{len(uri)}}}")
            text = self.stt.transcribe_uri(uri)
            span.set_attribute("ai.transcript_length", len(text))
            reply = self.chat.run(text)
            span.set_attribute("ai.reply_length", len(reply))
            audio = self.tts.synthesize(reply)
            return {"transcript": text, "reply": reply, "audio": audio}
