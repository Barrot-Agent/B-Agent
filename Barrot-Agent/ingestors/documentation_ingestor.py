#!/usr/bin/env python3
"""
Documentation Sites Ingestor
Handles: LangChain, LlamaIndex, Transformers, spaCy, etc.
"""

from typing import Dict, List, Any
from datetime import datetime, timezone
from .base_ingestor import BaseIngestor


class DocumentationIngestor(BaseIngestor):
    """Ingest documentation from framework and library sites"""
    
    def get_source_type(self) -> str:
        return "documentation"
    
    def ingest(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ingest documentation from configured sources"""
        source_name = source_config.get('name', 'unknown')
        print(f"[DocumentationIngestor] Ingesting from: {source_name}")
        
        results = []
        
        try:
            self._respect_rate_limit()
            
            results = [{
                "id": self._generate_id(source_name, "docs_example"),
                "source": source_name,
                "type": "documentation",
                "focus": source_config.get('focus', []),
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "platform": source_name,
                    "priority": source_config.get('priority', 'medium'),
                    "update_frequency": source_config.get('update_frequency', 'weekly')
                }
            }]
            
            for item in results:
                self._save_to_memory_bundle(item, "documentation")
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
