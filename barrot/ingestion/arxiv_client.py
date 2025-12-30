# barrot/ingestion/arxiv_client.py
import requests
from typing import List, Dict

class ArxivClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        params = {
            "search_query": query,
            "max_results": max_results,
        }
        # NOTE: you'd parse Atom XML here; keeping it simple
        resp = requests.get(self.base_url, params=params, timeout=30)
        resp.raise_for_status()
        return [{"raw": resp.text}]  # placeholder
