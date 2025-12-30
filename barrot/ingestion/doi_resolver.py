# barrot/ingestion/doi_resolver.py
import requests
from typing import Optional, Dict

class DOIResolver:
    """Resolve DOI identifiers to paper metadata"""
    
    def __init__(self, base_url: str = "https://doi.org"):
        self.base_url = base_url
    
    def resolve(self, doi: str) -> Optional[Dict]:
        """Resolve a DOI to metadata"""
        headers = {"Accept": "application/json"}
        url = f"{self.base_url}/{doi}"
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error resolving DOI {doi}: {e}")
            return None
