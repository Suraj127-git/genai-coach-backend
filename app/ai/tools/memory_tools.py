from typing import List
from ..repositories.memory_repository import MemoryRepository

def add_memory(repo: MemoryRepository, ids: List[str], texts: List[str]) -> bool:
    return repo.add_texts(ids, texts)

def search_memory(repo: MemoryRepository, text: str, k: int = 5) -> List[str]:
    return repo.similar_ids(text, k=k)
