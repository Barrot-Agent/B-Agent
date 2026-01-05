#!/usr/bin/env python3
"""
Storage Optimizer
Manages storage efficiently with compression, tiered storage, and archival strategies
"""

import gzip
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
import shutil


class StorageOptimizer:
    """Optimize storage for massive data volume"""
    
    def __init__(self, repo_root: Path = None):
        """Initialize the storage optimizer"""
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.memory_bundles = self.repo_root / "memory-bundles"
        
        # Storage tiers
        self.hot_storage = self.memory_bundles / "auto-ingested"  # Recent, frequently accessed
        self.warm_storage = self.memory_bundles / "warm-storage"  # Older, less accessed
        self.cold_storage = self.memory_bundles / "cold-storage"  # Archive, rarely accessed
        
        # Tier thresholds (days)
        self.hot_to_warm_days = 30
        self.warm_to_cold_days = 180
        
        # Statistics
        self.stats = {
            "total_files": 0,
            "hot_files": 0,
            "warm_files": 0,
            "cold_files": 0,
            "compressed_files": 0,
            "total_size_mb": 0,
            "space_saved_mb": 0
        }
    
    def compress_file(self, file_path: Path) -> Path:
        """
        Compress a file using gzip
        
        Args:
            file_path: Path to file to compress
            
        Returns:
            Path to compressed file
        """
        if file_path.suffix == '.gz':
            return file_path  # Already compressed
        
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Calculate space saved
            original_size = file_path.stat().st_size
            compressed_size = compressed_path.stat().st_size
            space_saved = original_size - compressed_size
            
            # Remove original
            file_path.unlink()
            
            self.stats["compressed_files"] += 1
            self.stats["space_saved_mb"] += space_saved / (1024 * 1024)
            
            return compressed_path
        
        except Exception as e:
            print(f"[StorageOptimizer] Error compressing {file_path}: {str(e)}")
            return file_path
    
    def decompress_file(self, file_path: Path) -> Path:
        """
        Decompress a gzip file
        
        Args:
            file_path: Path to compressed file
            
        Returns:
            Path to decompressed file
        """
        if file_path.suffix != '.gz':
            return file_path  # Not compressed
        
        decompressed_path = file_path.with_suffix('')
        
        try:
            with gzip.open(file_path, 'rb') as f_in:
                with open(decompressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return decompressed_path
        
        except Exception as e:
            print(f"[StorageOptimizer] Error decompressing {file_path}: {str(e)}")
            return file_path
    
    def move_to_tier(self, file_path: Path, tier: str) -> Path:
        """
        Move file to specified storage tier
        
        Args:
            file_path: Path to file
            tier: Target tier (hot, warm, cold)
            
        Returns:
            New path in target tier
        """
        tier_paths = {
            'hot': self.hot_storage,
            'warm': self.warm_storage,
            'cold': self.cold_storage
        }
        
        target_dir = tier_paths.get(tier, self.hot_storage)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Maintain subdirectory structure
        relative_path = file_path.relative_to(self.memory_bundles)
        target_path = target_dir / relative_path.name
        
        try:
            shutil.move(str(file_path), str(target_path))
            return target_path
        except Exception as e:
            print(f"[StorageOptimizer] Error moving {file_path} to {tier}: {str(e)}")
            return file_path
    
    def optimize_storage(self):
        """
        Optimize storage by:
        1. Compressing old files
        2. Moving files to appropriate tiers
        3. Cleaning up temp files
        """
        print("[StorageOptimizer] Starting storage optimization...")
        
        current_time = datetime.now(timezone.utc)
        
        # Process hot storage
        if self.hot_storage.exists():
            for file_path in self.hot_storage.rglob("*.json"):
                self.stats["total_files"] += 1
                
                # Get file age
                file_age = current_time - datetime.fromtimestamp(
                    file_path.stat().st_mtime, tz=timezone.utc
                )
                
                # Check if should move to warm
                if file_age.days > self.hot_to_warm_days:
                    compressed = self.compress_file(file_path)
                    self.move_to_tier(compressed, 'warm')
                    self.stats["warm_files"] += 1
                else:
                    self.stats["hot_files"] += 1
        
        # Process warm storage
        self.warm_storage.mkdir(parents=True, exist_ok=True)
        if self.warm_storage.exists():
            for file_path in self.warm_storage.rglob("*.json*"):
                # Check if should move to cold
                file_age = current_time - datetime.fromtimestamp(
                    file_path.stat().st_mtime, tz=timezone.utc
                )
                
                if file_age.days > self.warm_to_cold_days:
                    if not file_path.suffix.endswith('.gz'):
                        file_path = self.compress_file(file_path)
                    self.move_to_tier(file_path, 'cold')
                    self.stats["cold_files"] += 1
        
        # Calculate total size
        self._calculate_storage_size()
        
        print(f"[StorageOptimizer] Optimization complete!")
        print(f"  Hot: {self.stats['hot_files']} files")
        print(f"  Warm: {self.stats['warm_files']} files")
        print(f"  Cold: {self.stats['cold_files']} files")
        print(f"  Compressed: {self.stats['compressed_files']} files")
        print(f"  Space saved: {self.stats['space_saved_mb']:.2f} MB")
    
    def _calculate_storage_size(self):
        """Calculate total storage size"""
        total_size = 0
        
        for storage_path in [self.hot_storage, self.warm_storage, self.cold_storage]:
            if storage_path.exists():
                for file_path in storage_path.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
        
        self.stats["total_size_mb"] = total_size / (1024 * 1024)
    
    def cleanup_temp_files(self):
        """Remove temporary files"""
        temp_patterns = ['*.tmp', '*.temp', '.DS_Store', 'Thumbs.db']
        
        for pattern in temp_patterns:
            for file_path in self.memory_bundles.rglob(pattern):
                try:
                    file_path.unlink()
                    print(f"[StorageOptimizer] Removed temp file: {file_path.name}")
                except Exception as e:
                    print(f"[StorageOptimizer] Error removing {file_path}: {str(e)}")
    
    def get_storage_report(self) -> Dict[str, Any]:
        """Get storage usage report"""
        self._calculate_storage_size()
        
        return {
            "total_size_mb": self.stats["total_size_mb"],
            "total_files": self.stats["total_files"],
            "by_tier": {
                "hot": self.stats["hot_files"],
                "warm": self.stats["warm_files"],
                "cold": self.stats["cold_files"]
            },
            "optimization": {
                "compressed_files": self.stats["compressed_files"],
                "space_saved_mb": self.stats["space_saved_mb"]
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage optimizer statistics"""
        return self.stats.copy()


def main():
    """Main execution"""
    optimizer = StorageOptimizer()
    
    # Run optimization
    optimizer.optimize_storage()
    
    # Cleanup temp files
    optimizer.cleanup_temp_files()
    
    # Get report
    report = optimizer.get_storage_report()
    
    print(f"\nStorage Report:")
    print(f"  Total Size: {report['total_size_mb']:.2f} MB")
    print(f"  Total Files: {report['total_files']}")
    print(f"  Hot Files: {report['by_tier']['hot']}")
    print(f"  Warm Files: {report['by_tier']['warm']}")
    print(f"  Cold Files: {report['by_tier']['cold']}")
    print(f"  Compressed: {report['optimization']['compressed_files']}")
    print(f"  Space Saved: {report['optimization']['space_saved_mb']:.2f} MB")
    
    return optimizer


if __name__ == "__main__":
    main()
