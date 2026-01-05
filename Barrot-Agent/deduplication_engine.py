#!/usr/bin/env python3
"""
Deduplication Engine
Prevents ingesting the same content multiple times
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Set
from datetime import datetime, timezone


class DeduplicationEngine:
    """Detect and prevent duplicate content ingestion"""
    
    def __init__(self, repo_root: Path = None):
        """Initialize the deduplication engine"""
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.memory_bundles = self.repo_root / "memory-bundles"
        self.dedup_db_path = self.memory_bundles / "deduplication_db.json"
        
        # Load or initialize deduplication database
        self.dedup_db = self._load_dedup_db()
        
        # Statistics
        self.stats = {
            "total_hashes": 0,
            "duplicates_detected": 0,
            "unique_content": 0
        }
    
    def _load_dedup_db(self) -> Dict[str, Any]:
        """Load existing deduplication database"""
        if self.dedup_db_path.exists():
            with open(self.dedup_db_path, 'r') as f:
                return json.load(f)
        
        return {
            "content_hashes": {},
            "semantic_hashes": {},
            "metadata": {
                "created": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0"
            }
        }
    
    def _save_dedup_db(self):
        """Save deduplication database"""
        self.memory_bundles.mkdir(parents=True, exist_ok=True)
        self.dedup_db["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        with open(self.dedup_db_path, 'w') as f:
            json.dump(self.dedup_db, f, indent=2)
    
    def hash_content(self, content: str) -> str:
        """Generate SHA-256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def is_duplicate(self, content: str, source: str = None) -> bool:
        """
        Check if content is a duplicate
        
        Args:
            content: Content string to check
            source: Optional source identifier
            
        Returns:
            True if duplicate, False otherwise
        """
        content_hash = self.hash_content(content)
        
        if content_hash in self.dedup_db["content_hashes"]:
            self.stats["duplicates_detected"] += 1
            print(f"[Dedup] Duplicate detected: {content_hash[:16]}...")
            return True
        
        return False
    
    def add_content(self, content: str, source: str = None, metadata: Dict[str, Any] = None):
        """
        Add content to deduplication database
        
        Args:
            content: Content string
            source: Source identifier
            metadata: Additional metadata
        """
        content_hash = self.hash_content(content)
        
        self.dedup_db["content_hashes"][content_hash] = {
            "source": source,
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
        
        self.stats["unique_content"] += 1
        self.stats["total_hashes"] = len(self.dedup_db["content_hashes"])
        
        # Save periodically
        if self.stats["unique_content"] % 100 == 0:
            self._save_dedup_db()
    
    def check_and_add(self, content: str, source: str = None, metadata: Dict[str, Any] = None) -> bool:
        """
        Check for duplicate and add if unique
        
        Returns:
            True if content is unique (added), False if duplicate
        """
        if self.is_duplicate(content, source):
            return False
        
        self.add_content(content, source, metadata)
        return True
    
    def compute_semantic_similarity(self, content1: str, content2: str) -> float:
        """
        Compute semantic similarity between two content strings
        
        Returns:
            Similarity score between 0 and 1
        """
        # Placeholder for actual semantic similarity
        # In production, would use embeddings and cosine similarity
        
        # Simple word overlap for now
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def find_similar_content(self, content: str, threshold: float = 0.8) -> list:
        """
        Find content similar to given content
        
        Args:
            content: Content to compare
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar content hashes
        """
        similar = []
        
        # In production, would use more sophisticated similarity search
        # For now, return empty list as placeholder
        
        return similar
    
    def get_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics"""
        self.stats["total_hashes"] = len(self.dedup_db["content_hashes"])
        return self.stats.copy()
    
    def clear_old_entries(self, days: int = 365):
        """Clear entries older than specified days"""
        # Placeholder for cleanup logic
        pass
    
    def finalize(self):
        """Save deduplication database"""
        self._save_dedup_db()
        print(f"[Dedup] Database saved: {self.stats['total_hashes']} unique items")


def main():
    """Main execution"""
    engine = DeduplicationEngine()
    
    # Test deduplication
    test_content = "This is a test content for deduplication"
    
    # First add
    is_unique = engine.check_and_add(test_content, "test_source")
    print(f"First add - Unique: {is_unique}")
    
    # Second add (should be duplicate)
    is_unique = engine.check_and_add(test_content, "test_source")
    print(f"Second add - Unique: {is_unique}")
    
    # Print stats
    stats = engine.get_stats()
    print(f"\nDeduplication Statistics:")
    print(f"  Total Hashes: {stats['total_hashes']}")
    print(f"  Unique Content: {stats['unique_content']}")
    print(f"  Duplicates Detected: {stats['duplicates_detected']}")
    
    engine.finalize()
    
    return engine


if __name__ == "__main__":
    main()
