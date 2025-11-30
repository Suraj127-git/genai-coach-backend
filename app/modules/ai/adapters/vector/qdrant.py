from typing import List, Tuple

class QdrantAdapter:
    def __init__(self, url: str | None, api_key: str | None):
        self.client = None
        self.url = url
        self.api_key = api_key
        try:
            from qdrant_client import QdrantClient
            if url:
                self.client = QdrantClient(url=url, api_key=api_key)
        except Exception:
            self.client = None

    def upsert(self, collection: str, points: List[Tuple[str, List[float]]]) -> bool:
        if not self.client:
            return False
        try:
            from qdrant_client.models import PointStruct, VectorParams, Distance
            try:
                self.client.get_collection(collection)
            except Exception:
                self.client.create_collection(collection, vectors_config=VectorParams(size=len(points[0][1]), distance=Distance.COSINE))
            self.client.upsert(collection_name=collection, points=[PointStruct(id=p[0], vector=p[1]) for p in points])
            return True
        except Exception:
            return False

    def search(self, collection: str, vector: List[float], limit: int = 5) -> List[str]:
        if not self.client:
            return []
        try:
            res = self.client.search(collection_name=collection, query_vector=vector, limit=limit)
            return [str(r.id) for r in res]
        except Exception:
            return []

