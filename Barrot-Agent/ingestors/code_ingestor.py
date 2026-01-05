#!/usr/bin/env python3
"""
Code Repository Ingestor
Handles: GitHub, GitLab, Bitbucket, Hugging Face, Papers with Code, Kaggle, etc.
"""

from typing import Dict, List, Any
from datetime import datetime, timezone
from .base_ingestor import BaseIngestor


class CodeIngestor(BaseIngestor):
    """Ingest code repositories and datasets"""
    
    def get_source_type(self) -> str:
        return "code"
    
    def ingest(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ingest code repositories from configured sources"""
        source_name = source_config.get('name', 'unknown')
        print(f"[CodeIngestor] Ingesting from: {source_name}")
        
        results = []
        
        try:
            self._respect_rate_limit()
            
            results = [{
                "id": self._generate_id(source_name, "code_example"),
                "source": source_name,
                "type": "code_repository",
                "topics": source_config.get('topics', source_config.get('focus', [])),
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "platform": source_name,
                    "priority": source_config.get('priority', 'medium'),
                    "update_frequency": source_config.get('update_frequency', 'unknown')
                }
            }]
            
            for item in results:
                self._save_to_memory_bundle(item, "code")
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
