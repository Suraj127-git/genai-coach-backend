from typing import List

def ddg_search(query: str, max_results: int = 5) -> List[str]:
    results: List[str] = []
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                url = r.get("href") or r.get("url")
                if url:
                    results.append(url)
    except Exception:
        pass
    return results
