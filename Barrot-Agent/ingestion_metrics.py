#!/usr/bin/env python3
"""
Ingestion Metrics System
Tracks comprehensive metrics for ingestion operations
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta


class IngestionMetrics:
    """Track and report ingestion metrics"""
    
    def __init__(self, repo_root: Path = None):
        """Initialize the ingestion metrics system"""
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.memory_bundles = self.repo_root / "memory-bundles"
        self.metrics_path = self.memory_bundles / "ingestion_metrics.json"
        
        # Load or initialize metrics
        self.metrics = self._load_metrics()
        
        # Current session metrics
        self.session = {
            "start_time": None,
            "end_time": None,
            "content_ingested_count": 0,
            "content_ingested_volume_mb": 0,
            "processing_time_seconds": 0,
            "success_count": 0,
            "failure_count": 0,
            "sources_processed": []
        }
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load existing metrics or create new"""
        if self.metrics_path.exists():
            with open(self.metrics_path, 'r') as f:
                return json.load(f)
        
        return {
            "total_content_ingested": 0,
            "total_volume_mb": 0,
            "total_processing_time_seconds": 0,
            "total_sessions": 0,
            "success_rate": 0.0,
            "average_processing_time": 0.0,
            "ingestion_by_source": {},
            "ingestion_by_type": {},
            "daily_stats": [],
            "knowledge_graph_growth": [],
            "metadata": {
                "created": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0"
            }
        }
    
    def _save_metrics(self):
        """Save metrics to disk"""
        self.memory_bundles.mkdir(parents=True, exist_ok=True)
        self.metrics["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        with open(self.metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def start_session(self):
        """Start a new ingestion session"""
        self.session["start_time"] = datetime.now(timezone.utc).isoformat()
        print(f"[IngestionMetrics] Session started: {self.session['start_time']}")
    
    def end_session(self):
        """End the current ingestion session"""
        self.session["end_time"] = datetime.now(timezone.utc).isoformat()
        
        # Calculate session duration
        start = datetime.fromisoformat(self.session["start_time"])
        end = datetime.fromisoformat(self.session["end_time"])
        self.session["processing_time_seconds"] = (end - start).total_seconds()
        
        # Update global metrics
        self._update_global_metrics()
        
        # Save metrics
        self._save_metrics()
        
        print(f"[IngestionMetrics] Session ended: {self.session['end_time']}")
        print(f"[IngestionMetrics] Duration: {self.session['processing_time_seconds']:.2f}s")
    
    def record_ingestion(self, source: str, content_type: str, volume_kb: float, success: bool = True):
        """
        Record a content ingestion event
        
        Args:
            source: Source name
            content_type: Type of content
            volume_kb: Size in kilobytes
            success: Whether ingestion succeeded
        """
        self.session["content_ingested_count"] += 1
        self.session["content_ingested_volume_mb"] += volume_kb / 1024
        
        if success:
            self.session["success_count"] += 1
        else:
            self.session["failure_count"] += 1
        
        # Track by source
        if source not in self.session["sources_processed"]:
            self.session["sources_processed"].append(source)
        
        # Update source-specific metrics
        if source not in self.metrics["ingestion_by_source"]:
            self.metrics["ingestion_by_source"][source] = {
                "count": 0,
                "volume_mb": 0,
                "success_count": 0,
                "failure_count": 0
            }
        
        self.metrics["ingestion_by_source"][source]["count"] += 1
        self.metrics["ingestion_by_source"][source]["volume_mb"] += volume_kb / 1024
        
        if success:
            self.metrics["ingestion_by_source"][source]["success_count"] += 1
        else:
            self.metrics["ingestion_by_source"][source]["failure_count"] += 1
        
        # Update type-specific metrics
        if content_type not in self.metrics["ingestion_by_type"]:
            self.metrics["ingestion_by_type"][content_type] = {
                "count": 0,
                "volume_mb": 0
            }
        
        self.metrics["ingestion_by_type"][content_type]["count"] += 1
        self.metrics["ingestion_by_type"][content_type]["volume_mb"] += volume_kb / 1024
    
    def _update_global_metrics(self):
        """Update global metrics from session"""
        self.metrics["total_sessions"] += 1
        self.metrics["total_content_ingested"] += self.session["content_ingested_count"]
        self.metrics["total_volume_mb"] += self.session["content_ingested_volume_mb"]
        self.metrics["total_processing_time_seconds"] += self.session["processing_time_seconds"]
        
        # Calculate success rate
        total_attempts = self.session["success_count"] + self.session["failure_count"]
        if total_attempts > 0:
            session_success_rate = self.session["success_count"] / total_attempts
            # Update rolling average
            prev_total = (self.metrics["total_sessions"] - 1)
            if prev_total > 0:
                self.metrics["success_rate"] = (
                    (self.metrics["success_rate"] * prev_total + session_success_rate) /
                    self.metrics["total_sessions"]
                )
            else:
                self.metrics["success_rate"] = session_success_rate
        
        # Calculate average processing time
        if self.metrics["total_sessions"] > 0:
            self.metrics["average_processing_time"] = (
                self.metrics["total_processing_time_seconds"] /
                self.metrics["total_sessions"]
            )
        
        # Record daily stats
        today = datetime.now(timezone.utc).date().isoformat()
        daily_entry = {
            "date": today,
            "content_count": self.session["content_ingested_count"],
            "volume_mb": self.session["content_ingested_volume_mb"],
            "sources": len(self.session["sources_processed"])
        }
        
        # Update or append daily stats
        if self.metrics["daily_stats"] and self.metrics["daily_stats"][-1]["date"] == today:
            # Update existing entry
            self.metrics["daily_stats"][-1]["content_count"] += daily_entry["content_count"]
            self.metrics["daily_stats"][-1]["volume_mb"] += daily_entry["volume_mb"]
            self.metrics["daily_stats"][-1]["sources"] = max(
                self.metrics["daily_stats"][-1]["sources"],
                daily_entry["sources"]
            )
        else:
            # Append new entry
            self.metrics["daily_stats"].append(daily_entry)
    
    def record_knowledge_graph_growth(self, nodes: int, edges: int):
        """Record knowledge graph size"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nodes": nodes,
            "edges": edges
        }
        
        self.metrics["knowledge_graph_growth"].append(entry)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        return {
            "overall": {
                "total_content": self.metrics["total_content_ingested"],
                "total_volume_mb": self.metrics["total_volume_mb"],
                "total_sessions": self.metrics["total_sessions"],
                "success_rate": f"{self.metrics['success_rate']:.1%}",
                "avg_processing_time": f"{self.metrics['average_processing_time']:.2f}s"
            },
            "by_source": self.metrics["ingestion_by_source"],
            "by_type": self.metrics["ingestion_by_type"],
            "recent_daily": self.metrics["daily_stats"][-7:],  # Last 7 days
            "knowledge_graph": self.metrics["knowledge_graph_growth"][-1] if self.metrics["knowledge_graph_growth"] else None
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data formatted for dashboard visualization"""
        # Prepare time series data
        daily_data = self.metrics["daily_stats"][-30:]  # Last 30 days
        
        # Source breakdown
        source_data = [
            {"source": source, **data}
            for source, data in self.metrics["ingestion_by_source"].items()
        ]
        source_data.sort(key=lambda x: x["count"], reverse=True)
        
        # Type distribution
        type_data = [
            {"type": content_type, **data}
            for content_type, data in self.metrics["ingestion_by_type"].items()
        ]
        
        return {
            "daily_ingestion": daily_data,
            "sources": source_data[:10],  # Top 10 sources
            "content_types": type_data,
            "knowledge_graph_timeline": self.metrics["knowledge_graph_growth"][-30:],  # Last 30 entries
            "summary": {
                "total_content": self.metrics["total_content_ingested"],
                "total_sources": len(self.metrics["ingestion_by_source"]),
                "success_rate": self.metrics["success_rate"],
                "total_volume_gb": self.metrics["total_volume_mb"] / 1024
            }
        }


def main():
    """Main execution"""
    metrics = IngestionMetrics()
    
    # Simulate session
    metrics.start_session()
    
    # Simulate ingestions
    metrics.record_ingestion("arXiv", "academic_paper", 250, True)
    metrics.record_ingestion("GitHub", "code_repository", 500, True)
    metrics.record_ingestion("YouTube", "video_content", 2000, True)
    metrics.record_ingestion("Medium", "blog_article", 100, False)
    
    # Record knowledge graph
    metrics.record_knowledge_graph_growth(1500, 3000)
    
    # End session
    metrics.end_session()
    
    # Get summary
    summary = metrics.get_summary()
    
    print("\nIngestion Metrics Summary:")
    print(f"  Total Content: {summary['overall']['total_content']}")
    print(f"  Total Volume: {summary['overall']['total_volume_mb']:.2f} MB")
    print(f"  Success Rate: {summary['overall']['success_rate']}")
    print(f"  Avg Processing Time: {summary['overall']['avg_processing_time']}")
    
    return metrics


if __name__ == "__main__":
    main()
