#!/usr/bin/env python3
"""
Forum & Communities Ingestor
Handles: Reddit, Hacker News, Stack Overflow, Cross Validated, AI Stack Exchange
"""

from typing import Dict, List, Any
from datetime import datetime, timezone
from .base_ingestor import BaseIngestor


class ForumIngestor(BaseIngestor):
    """Ingest forum discussions and community content"""
    
    def get_source_type(self) -> str:
        return "forum"
    
    def ingest(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ingest forum content from configured sources"""
        source_name = source_config.get('name', 'unknown')
        print(f"[ForumIngestor] Ingesting from: {source_name}")
        
        results = []
        
        try:
            self._respect_rate_limit()
            
            results = [{
                "id": self._generate_id(source_name, "forum_example"),
                "source": source_name,
                "type": "forum_discussion",
                "subreddits": source_config.get('subreddits', []),
                "tags": source_config.get('tags', source_config.get('focus', [])),
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "platform": source_name,
                    "priority": source_config.get('priority', 'medium'),
                    "update_frequency": source_config.get('update_frequency', 'unknown')
                }
            }]
            
            for item in results:
                self._save_to_memory_bundle(item, "forums")
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
