from typing import Any

class BaseLLM:
    def predict(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError

