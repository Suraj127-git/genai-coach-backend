from typing import Any
import logging
from opentelemetry import trace

class OllamaLLM:
    def __init__(self, model: str):
        self.model = model
        self.client = None
        self.logger = logging.getLogger("ai.adapter.ollama")
        self.tracer = trace.get_tracer("ai.adapter.ollama")
        try:
            from langchain_community.llms import Ollama
            self.client = Ollama(model=model)
        except Exception:
            self.client = None

    def predict(self, prompt: str, **kwargs: Any) -> str:
        with self.tracer.start_as_current_span("ollama.predict") as span:
            span.set_attribute("ai.model", self.model)
            span.set_attribute("ai.input_length", len(prompt))
            if self.client:
                try:
                    out = self.client.invoke(prompt)
                    span.set_attribute("ai.output_length", len(str(out)))
                    self.logger.info(f"{{\"evt\":\"ollama_invoke\",\"model\":\"{self.model}\"}}")
                    return out
                except Exception:
                    self.logger.error(f"{{\"evt\":\"ollama_error\",\"model\":\"{self.model}\"}}")
            return f"{prompt}"
