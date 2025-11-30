from typing import Any
from ..repositories.memory_repository import MemoryRepository

class DocumentAgent:
    def __init__(self, llm: Any, memory: MemoryRepository):
        self.llm = llm
        self.memory = memory

    def ingest(self, doc_id: str, text: str) -> bool:
        return self.memory.add_texts([doc_id], [text])

    def answer(self, question: str) -> str:
        ids = self.memory.similar_ids(question, k=3)
        ctx = " ".join(ids)
        return self.llm.predict(f"{question}\nContext: {ctx}")
