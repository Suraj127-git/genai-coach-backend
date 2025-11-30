from typing import List
from ..services.embedding_service import EmbeddingService
from ..adapters.vector.qdrant import QdrantAdapter

class MemoryRepository:
    def __init__(self, embed: EmbeddingService, qdrant: QdrantAdapter, collection: str = "conversations"):
        self.embed = embed
        self.qdrant = qdrant
        self.collection = collection

    def add_texts(self, ids: List[str], texts: List[str]) -> bool:
        vectors = [self.embed.embed(t) for t in texts]
        points = list(zip(ids, vectors))
        return self.qdrant.upsert(self.collection, points)

    def similar_ids(self, text: str, k: int = 5) -> List[str]:
        v = self.embed.embed(text)
        return self.qdrant.search(self.collection, v, limit=k)

