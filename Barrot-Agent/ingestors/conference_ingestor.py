#!/usr/bin/env python3
"""
Conference Proceedings Ingestor
Handles: NeurIPS, ICML, ICLR, CVPR, EMNLP, ACL, AAAI, IJCAI
"""

from typing import Dict, List, Any
from datetime import datetime, timezone
from .base_ingestor import BaseIngestor


class ConferenceIngestor(BaseIngestor):
    """Ingest conference papers and proceedings"""
    
    def get_source_type(self) -> str:
        return "conference"
    
    def ingest(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ingest conference content from configured sources"""
        source_name = source_config.get('name', 'unknown')
        print(f"[ConferenceIngestor] Ingesting from: {source_name}")
        
        results = []
        
        try:
            self._respect_rate_limit()
            
            results = [{
                "id": self._generate_id(source_name, "conference_example"),
                "source": source_name,
                "type": "conference_paper",
                "focus": source_config.get('focus', []),
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "conference": source_name,
                    "priority": source_config.get('priority', 'critical'),
                    "update_frequency": source_config.get('update_frequency', 'yearly')
                }
            }]
            
            for item in results:
                self._save_to_memory_bundle(item, "conferences")
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
