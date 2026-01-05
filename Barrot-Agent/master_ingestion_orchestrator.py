#!/usr/bin/env python3
"""
Master Ingestion Orchestrator
Coordinates all ingestors with priority scheduling, rate limiting, and resource allocation
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone
import json

# Import all ingestors
from ingestors.academic_ingestor import AcademicIngestor
from ingestors.video_ingestor import VideoIngestor
from ingestors.code_ingestor import CodeIngestor
from ingestors.blog_ingestor import BlogIngestor
from ingestors.podcast_ingestor import PodcastIngestor
from ingestors.forum_ingestor import ForumIngestor
from ingestors.conference_ingestor import ConferenceIngestor
from ingestors.documentation_ingestor import DocumentationIngestor
from ingestors.book_ingestor import BookIngestor
from ingestors.patent_ingestor import PatentIngestor
from ingestors.news_ingestor import NewsIngestor
from ingestors.dataset_ingestor import DatasetIngestor
from ingestors.social_ingestor import SocialIngestor


class MasterIngestionOrchestrator:
    """Orchestrates all data ingestion across 15 categories and 100+ sources"""
    
    def __init__(self, config_path: Path = None):
        """Initialize the master orchestrator"""
        self.repo_root = Path(__file__).resolve().parent
        self.config_path = config_path or self.repo_root / "Barrot-Agent" / "ingestion_config.yaml"
        self.config = self._load_config()
        self.memory_bundles = self.repo_root / "memory-bundles"
        
        # Initialize all ingestors
        self.ingestors = {
            'academic': AcademicIngestor(self.config_path),
            'video': VideoIngestor(self.config_path),
            'code': CodeIngestor(self.config_path),
            'blog': BlogIngestor(self.config_path),
            'podcast': PodcastIngestor(self.config_path),
            'forum': ForumIngestor(self.config_path),
            'conference': ConferenceIngestor(self.config_path),
            'documentation': DocumentationIngestor(self.config_path),
            'book': BookIngestor(self.config_path),
            'patent': PatentIngestor(self.config_path),
            'news': NewsIngestor(self.config_path),
            'dataset': DatasetIngestor(self.config_path),
            'social': SocialIngestor(self.config_path)
        }
        
        # Priority mapping
        self.priority_levels = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
        
        # Orchestration stats
        self.stats = {
            "total_sources": 0,
            "sources_processed": 0,
            "items_ingested": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load ingestion configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _get_all_sources(self) -> List[Dict[str, Any]]:
        """Extract all sources from config with metadata"""
        sources = []
        
        # Map config categories to ingestor types
        category_mapping = {
            'academic_research': 'academic',
            'video_platforms': 'video',
            'code_repositories': 'code',
            'blogs_articles': 'blog',
            'podcasts_audio': 'podcast',
            'forums_communities': 'forum',
            'conference_proceedings': 'conference',
            'documentation_sites': 'documentation',
            'books_textbooks': 'book',
            'patents_technical': 'patent',
            'news_media': 'news',
            'datasets': 'dataset',
            'social_media': 'social'
        }
        
        for category, ingestor_type in category_mapping.items():
            if category in self.config:
                category_sources = self.config[category].get('sources', [])
                for source in category_sources:
                    source['ingestor_type'] = ingestor_type
                    source['category'] = category
                    sources.append(source)
        
        return sources
    
    def _sort_by_priority(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort sources by priority (critical > high > medium > low)"""
        return sorted(
            sources,
            key=lambda s: (
                self.priority_levels.get(s.get('priority', 'medium'), 3),
                s.get('name', '')
            )
        )
    
    def ingest_all(self, max_sources: int = None) -> Dict[str, Any]:
        """
        Orchestrate ingestion from all configured sources
        
        Args:
            max_sources: Optional limit on number of sources to process
            
        Returns:
            Orchestration results and statistics
        """
        print("[MasterOrchestrator] ═══════════════════════════════════════════")
        print("[MasterOrchestrator] Starting Universal Data Ingestion")
        print("[MasterOrchestrator] ═══════════════════════════════════════════")
        
        self.stats["start_time"] = datetime.now(timezone.utc).isoformat()
        
        # Get all sources
        all_sources = self._get_all_sources()
        self.stats["total_sources"] = len(all_sources)
        
        print(f"[MasterOrchestrator] Total sources configured: {len(all_sources)}")
        
        # Sort by priority
        prioritized_sources = self._sort_by_priority(all_sources)
        
        # Limit if specified
        if max_sources:
            prioritized_sources = prioritized_sources[:max_sources]
            print(f"[MasterOrchestrator] Processing top {max_sources} priority sources")
        
        # Process each source
        results = []
        for source in prioritized_sources:
            if not source.get('enabled', True):
                print(f"[MasterOrchestrator] Skipping disabled source: {source.get('name')}")
                continue
            
            try:
                ingestor_type = source.get('ingestor_type')
                ingestor = self.ingestors.get(ingestor_type)
                
                if not ingestor:
                    print(f"[MasterOrchestrator] No ingestor found for type: {ingestor_type}")
                    continue
                
                print(f"\n[MasterOrchestrator] Processing: {source.get('name')} ({source.get('priority', 'medium')} priority)")
                
                # Ingest from source
                items = ingestor.ingest(source)
                
                result = {
                    "source": source.get('name'),
                    "category": source.get('category'),
                    "priority": source.get('priority'),
                    "items_count": len(items),
                    "status": "success",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                results.append(result)
                
                self.stats["sources_processed"] += 1
                self.stats["items_ingested"] += len(items)
                
            except Exception as e:
                print(f"[MasterOrchestrator] Error processing {source.get('name')}: {str(e)}")
                results.append({
                    "source": source.get('name'),
                    "category": source.get('category'),
                    "priority": source.get('priority'),
                    "items_count": 0,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                self.stats["errors"] += 1
        
        self.stats["end_time"] = datetime.now(timezone.utc).isoformat()
        
        # Generate orchestration summary
        summary = {
            "orchestration": self.stats,
            "results": results,
            "ingestor_stats": {
                ingestor_type: ingestor.get_stats()
                for ingestor_type, ingestor in self.ingestors.items()
            }
        }
        
        # Save summary
        self._save_orchestration_summary(summary)
        
        print("\n[MasterOrchestrator] ═══════════════════════════════════════════")
        print("[MasterOrchestrator] Ingestion Complete!")
        print(f"[MasterOrchestrator] Sources Processed: {self.stats['sources_processed']}")
        print(f"[MasterOrchestrator] Items Ingested: {self.stats['items_ingested']}")
        print(f"[MasterOrchestrator] Errors: {self.stats['errors']}")
        print("[MasterOrchestrator] ═══════════════════════════════════════════")
        
        return summary
    
    def ingest_by_category(self, category: str) -> Dict[str, Any]:
        """Ingest from all sources in a specific category"""
        print(f"[MasterOrchestrator] Ingesting from category: {category}")
        
        all_sources = self._get_all_sources()
        category_sources = [s for s in all_sources if s.get('category') == category]
        
        results = []
        for source in category_sources:
            if not source.get('enabled', True):
                continue
            
            try:
                ingestor_type = source.get('ingestor_type')
                ingestor = self.ingestors.get(ingestor_type)
                if ingestor:
                    items = ingestor.ingest(source)
                    results.extend(items)
            except Exception as e:
                print(f"[MasterOrchestrator] Error: {str(e)}")
        
        return {"category": category, "items_count": len(results), "items": results}
    
    def ingest_by_priority(self, priority: str) -> Dict[str, Any]:
        """Ingest from all sources with a specific priority"""
        print(f"[MasterOrchestrator] Ingesting from {priority} priority sources")
        
        all_sources = self._get_all_sources()
        priority_sources = [s for s in all_sources if s.get('priority') == priority]
        
        results = []
        for source in priority_sources:
            if not source.get('enabled', True):
                continue
            
            try:
                ingestor_type = source.get('ingestor_type')
                ingestor = self.ingestors.get(ingestor_type)
                if ingestor:
                    items = ingestor.ingest(source)
                    results.extend(items)
            except Exception as e:
                print(f"[MasterOrchestrator] Error: {str(e)}")
        
        return {"priority": priority, "items_count": len(results), "items": results}
    
    def _save_orchestration_summary(self, summary: Dict[str, Any]):
        """Save orchestration summary to memory bundle"""
        self.memory_bundles.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        summary_path = self.memory_bundles / f"ingestion_orchestration_{timestamp}.json"
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"[MasterOrchestrator] Summary saved to: {summary_path}")
    
    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get current orchestration statistics"""
        return self.stats.copy()


def main():
    """Main execution function"""
    orchestrator = MasterIngestionOrchestrator()
    
    # Run full ingestion (limited to 10 sources for demo)
    results = orchestrator.ingest_all(max_sources=10)
    
    return results


if __name__ == "__main__":
    main()
