# barrot/core/synchronization.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class SyncState:
    """Manages synchronization state across distributed cognition processes"""
    last_sync: Optional[datetime] = None
    sync_version: int = 0
    
    def update(self) -> None:
        """Update synchronization state"""
        self.last_sync = datetime.now()
        self.sync_version += 1
    
    def is_stale(self, threshold_seconds: int = 300) -> bool:
        """Check if sync state is stale"""
        if self.last_sync is None:
            return True
        delta = datetime.now() - self.last_sync
        return delta.total_seconds() > threshold_seconds
