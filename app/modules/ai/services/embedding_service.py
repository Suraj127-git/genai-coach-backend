import logging
from opentelemetry import trace

class EmbeddingService:
    def __init__(self, model: str):
        self.model = model
        self.client = None
        self.logger = logging.getLogger("ai.service.embed")
        self.tracer = trace.get_tracer("ai.service.embed")
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            self.client = HuggingFaceEmbeddings(model_name=model)
        except Exception:
            try:
                from langchain_community.embeddings import OllamaEmbeddings
                self.client = OllamaEmbeddings(model=model)
            except Exception:
                self.client = None

    def embed(self, text: str) -> list[float]:
        with self.tracer.start_as_current_span("embed") as span:
            span.set_attribute("ai.model", self.model)
            span.set_attribute("ai.input_length", len(text))
            if self.client:
                try:
                    v = list(self.client.embed_query(text))
                    span.set_attribute("ai.vector_size", len(v))
                    self.logger.info(f"{{\"evt\":\"embed\",\"model\":\"{self.model}\",\"len\":{len(text)} }}")
                    return v
                except Exception:
                    self.logger.error(f"{{\"evt\":\"embed_error\",\"model\":\"{self.model}\"}}")
            return [0.0] * 384

