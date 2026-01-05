#!/usr/bin/env python3
"""
Base Ingestor Class
Provides common functionality for all content ingestors
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml


class BaseIngestor(ABC):
    """Base class for all content ingestors"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the ingestor with configuration"""
        self.repo_root = Path(__file__).resolve().parent.parent.parent
        self.config_path = config_path or self.repo_root / "Barrot-Agent" / "ingestion_config.yaml"
        self.config = self._load_config()
        self.memory_bundles = self.repo_root / "memory-bundles"
        self.memory_bundles.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting
        self.last_request_time = 0
        self.request_interval = 60 / self.config.get('global_settings', {}).get('rate_limiting', {}).get('default_requests_per_minute', 10)
        
        # Statistics
        self.stats = {
            "total_ingested": 0,
            "successful": 0,
            "failed": 0,
            "duplicates": 0,
            "filtered": 0
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load ingestion configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _respect_rate_limit(self):
        """Respect rate limiting to avoid overwhelming sources"""
        if not self.config.get('global_settings', {}).get('rate_limiting', {}).get('enabled', True):
            return
        
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _hash_content(self, content: str) -> str:
        """Generate SHA-256 hash of content for deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _generate_id(self, source: str, identifier: str) -> str:
        """Generate unique ID for ingested content"""
        return hashlib.sha256(f"{source}:{identifier}".encode()).hexdigest()[:16]
    
    def _save_to_memory_bundle(self, content: Dict[str, Any], bundle_name: str):
        """Save content to memory bundle"""
        bundle_path = self.memory_bundles / "auto-ingested" / bundle_name
        bundle_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        content_id = content.get('id', 'unknown')
        filename = f"{timestamp}_{content_id}.json"
        
        with open(bundle_path / filename, 'w') as f:
            json.dump(content, f, indent=2)
    
    def _log_ingestion(self, source: str, status: str, details: Dict[str, Any]):
        """Log ingestion activity"""
        log_path = self.memory_bundles / "data-ingestion-log.md"
        
        log_entry = f"""
## Ingestion: {datetime.now(timezone.utc).isoformat()}

**Source**: {source}
**Status**: {status}
**Type**: {self.__class__.__name__}

### Details
"""
        for key, value in details.items():
            log_entry += f"- **{key}**: {value}\n"
        
        log_entry += "\n---\n"
        
        with open(log_path, 'a') as f:
            f.write(log_entry)
    
    def _update_stats(self, success: bool = True, duplicate: bool = False, filtered: bool = False):
        """Update ingestion statistics"""
        self.stats["total_ingested"] += 1
        if success:
            self.stats["successful"] += 1
        else:
            self.stats["failed"] += 1
        if duplicate:
            self.stats["duplicates"] += 1
        if filtered:
            self.stats["filtered"] += 1
    
    @abstractmethod
    def ingest(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Ingest content from the specified source
        
        Args:
            source_config: Configuration for the specific source
            
        Returns:
            List of ingested content items
        """
        pass
    
    @abstractmethod
    def get_source_type(self) -> str:
        """Return the type of source this ingestor handles"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        return self.stats.copy()
