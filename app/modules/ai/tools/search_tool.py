from typing import List
from ..adapters.search.duckduckgo import ddg_search

def web_search(query: str, k: int = 5) -> List[str]:
    return ddg_search(query, max_results=k)

