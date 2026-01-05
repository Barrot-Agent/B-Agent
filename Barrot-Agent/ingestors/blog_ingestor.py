#!/usr/bin/env python3
"""
Blog & Articles Ingestor
Handles: Medium, Substack, Distill.pub, OpenAI Blog, DeepMind, etc.
"""

from typing import Dict, List, Any
from datetime import datetime, timezone
from .base_ingestor import BaseIngestor


class BlogIngestor(BaseIngestor):
    """Ingest blog posts and articles"""
    
    def get_source_type(self) -> str:
        return "blog"
    
    def ingest(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ingest blog content from configured sources"""
        source_name = source_config.get('name', 'unknown')
        print(f"[BlogIngestor] Ingesting from: {source_name}")
        
        results = []
        
        try:
            self._respect_rate_limit()
            
            results = [{
                "id": self._generate_id(source_name, "blog_example"),
                "source": source_name,
                "type": "blog_article",
                "tags": source_config.get('tags', source_config.get('focus', [])),
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "platform": source_name,
                    "priority": source_config.get('priority', 'medium'),
                    "update_frequency": source_config.get('update_frequency', 'unknown')
                }
            }]
            
            for item in results:
                self._save_to_memory_bundle(item, "blogs")
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
