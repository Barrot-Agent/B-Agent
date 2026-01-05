#!/usr/bin/env python3
"""
Book & Textbooks Ingestor
Handles: AI textbooks, Deep Learning books, RL books, etc.
"""

from typing import Dict, List, Any
from datetime import datetime, timezone
from .base_ingestor import BaseIngestor


class BookIngestor(BaseIngestor):
    """Ingest books and textbooks"""
    
    def get_source_type(self) -> str:
        return "book"
    
    def ingest(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ingest book content from configured sources"""
        source_name = source_config.get('name', 'unknown')
        print(f"[BookIngestor] Ingesting from: {source_name}")
        
        results = []
        
        try:
            self._respect_rate_limit()
            
            results = [{
                "id": self._generate_id(source_name, "book_example"),
                "source": source_name,
                "type": "book",
                "authors": source_config.get('authors', []),
                "focus": source_config.get('focus', []),
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "title": source_name,
                    "priority": source_config.get('priority', 'high'),
                    "url": source_config.get('url', '')
                }
            }]
            
            for item in results:
                self._save_to_memory_bundle(item, "books")
                self._update_stats(success=True)
            
            self._log_ingestion(
                source_name, "success",
                {"items_ingested": len(results), "source_type": self.get_source_type()}
            )
            
        except Exception as e:
            self._log_ingestion(
                source_name, "failed",
                {"error": str(e), "source_type": self.get_source_type()}
            )
            self._update_stats(success=False)
        
        return results
