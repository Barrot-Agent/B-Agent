#!/usr/bin/env python3
"""
Quality Filter System
Filters content by relevance, authority, recency, and engagement
"""

from typing import Dict, Any
from datetime import datetime, timezone
import json
from pathlib import Path


class QualityFilter:
    """Filter content based on quality metrics"""
    
    def __init__(self, repo_root: Path = None):
        """Initialize the quality filter"""
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.memory_bundles = self.repo_root / "memory-bundles"
        
        # Default thresholds
        self.thresholds = {
            "min_relevance": 0.7,
            "min_authority": 0.6,
            "min_engagement": 0.5,
            "max_age_days": 365
        }
        
        # Statistics
        self.stats = {
            "total_evaluated": 0,
            "passed": 0,
            "filtered": 0,
            "filter_reasons": {}
        }
    
    def evaluate(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate content quality
        
        Returns:
            Evaluation results with scores and decision
        """
        self.stats["total_evaluated"] += 1
        
        scores = {
            "relevance": self._score_relevance(content),
            "authority": self._score_authority(content),
            "recency": self._score_recency(content),
            "engagement": self._score_engagement(content)
        }
        
        # Compute overall score (weighted average)
        weights = {"relevance": 0.35, "authority": 0.30, "recency": 0.20, "engagement": 0.15}
        overall_score = sum(scores[k] * weights[k] for k in weights)
        
        # Determine pass/fail
        passes = self._check_thresholds(scores)
        
        evaluation = {
            "scores": scores,
            "overall_score": overall_score,
            "passes": passes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if passes:
            self.stats["passed"] += 1
        else:
            self.stats["filtered"] += 1
            reason = self._get_filter_reason(scores)
            self.stats["filter_reasons"][reason] = self.stats["filter_reasons"].get(reason, 0) + 1
        
        return evaluation
    
    def _score_relevance(self, content: Dict[str, Any]) -> float:
        """
        Score content relevance (0-1)
        
        Checks for AI/ML related keywords, topics, and focus areas
        """
        # Placeholder scoring logic
        # In production, would use NLP/embeddings for semantic relevance
        
        ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'nlp', 'computer vision', 'reinforcement learning',
            'transformer', 'gpt', 'llm', 'agi', 'cognitive', 'neural'
        ]
        
        # Check in various fields
        text_to_check = ' '.join([
            str(content.get('title', '')),
            str(content.get('description', '')),
            ' '.join(content.get('topics', [])),
            ' '.join(content.get('tags', [])),
            ' '.join(content.get('focus', []))
        ]).lower()
        
        keyword_matches = sum(1 for keyword in ai_keywords if keyword in text_to_check)
        relevance_score = min(keyword_matches / 5.0, 1.0)
        
        return relevance_score
    
    def _score_authority(self, content: Dict[str, Any]) -> float:
        """
        Score source authority (0-1)
        
        Based on source credibility and reputation
        """
        # Authority scoring based on source
        high_authority_sources = [
            'arxiv', 'nature', 'science', 'ieee', 'acm', 'neurips', 'icml',
            'openai', 'deepmind', 'anthropic', 'google', 'stanford', 'mit'
        ]
        
        medium_authority_sources = [
            'medium', 'github', 'hugging face', 'kaggle', 'youtube',
            'ted', 'coursera', 'reddit'
        ]
        
        source = str(content.get('source', '')).lower()
        
        for high_auth in high_authority_sources:
            if high_auth in source:
                return 0.9
        
        for medium_auth in medium_authority_sources:
            if medium_auth in source:
                return 0.7
        
        return 0.5  # Default authority
    
    def _score_recency(self, content: Dict[str, Any]) -> float:
        """
        Score content recency (0-1)
        
        More recent content scores higher
        """
        # Check for timestamp
        ingested_at = content.get('ingested_at')
        if not ingested_at:
            return 0.5  # Unknown recency
        
        try:
            ingested_time = datetime.fromisoformat(ingested_at.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            age_days = (now - ingested_time).days
            
            # Score based on age (exponential decay)
            if age_days <= 7:
                return 1.0
            elif age_days <= 30:
                return 0.9
            elif age_days <= 90:
                return 0.8
            elif age_days <= 180:
                return 0.7
            elif age_days <= 365:
                return 0.6
            else:
                return max(0.3, 1.0 - (age_days / 1000))
        
        except Exception:
            return 0.5
    
    def _score_engagement(self, content: Dict[str, Any]) -> float:
        """
        Score content engagement (0-1)
        
        Based on citations, views, stars, etc.
        """
        # Placeholder - in production would use actual engagement metrics
        metadata = content.get('metadata', {})
        
        # Check for engagement indicators
        citations = metadata.get('citations', 0)
        stars = metadata.get('stars', 0)
        views = metadata.get('views', 0)
        
        # Simple scoring
        engagement_score = 0.5
        
        if citations > 100:
            engagement_score += 0.2
        elif citations > 10:
            engagement_score += 0.1
        
        if stars > 1000:
            engagement_score += 0.15
        elif stars > 100:
            engagement_score += 0.05
        
        if views > 10000:
            engagement_score += 0.15
        elif views > 1000:
            engagement_score += 0.05
        
        return min(engagement_score, 1.0)
    
    def _check_thresholds(self, scores: Dict[str, float]) -> bool:
        """Check if scores meet minimum thresholds"""
        return (
            scores["relevance"] >= self.thresholds["min_relevance"] and
            scores["authority"] >= self.thresholds["min_authority"] and
            scores["engagement"] >= self.thresholds["min_engagement"]
        )
    
    def _get_filter_reason(self, scores: Dict[str, float]) -> str:
        """Determine primary reason for filtering"""
        if scores["relevance"] < self.thresholds["min_relevance"]:
            return "low_relevance"
        if scores["authority"] < self.thresholds["min_authority"]:
            return "low_authority"
        if scores["engagement"] < self.thresholds["min_engagement"]:
            return "low_engagement"
        return "other"
    
    def set_thresholds(self, thresholds: Dict[str, float]):
        """Update quality thresholds"""
        self.thresholds.update(thresholds)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get quality filter statistics"""
        pass_rate = self.stats["passed"] / self.stats["total_evaluated"] if self.stats["total_evaluated"] > 0 else 0
        return {
            **self.stats,
            "pass_rate": pass_rate
        }


def main():
    """Main execution"""
    filter_system = QualityFilter()
    
    # Test with sample content
    test_content = {
        "title": "Advanced Machine Learning Techniques",
        "source": "arXiv",
        "topics": ["machine learning", "deep learning"],
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {"citations": 150}
    }
    
    evaluation = filter_system.evaluate(test_content)
    
    print("Quality Evaluation:")
    print(f"  Relevance: {evaluation['scores']['relevance']:.2f}")
    print(f"  Authority: {evaluation['scores']['authority']:.2f}")
    print(f"  Recency: {evaluation['scores']['recency']:.2f}")
    print(f"  Engagement: {evaluation['scores']['engagement']:.2f}")
    print(f"  Overall: {evaluation['overall_score']:.2f}")
    print(f"  Passes: {evaluation['passes']}")
    
    stats = filter_system.get_stats()
    print(f"\nFilter Statistics:")
    print(f"  Total Evaluated: {stats['total_evaluated']}")
    print(f"  Passed: {stats['passed']}")
    print(f"  Filtered: {stats['filtered']}")
    print(f"  Pass Rate: {stats['pass_rate']:.1%}")
    
    return filter_system


if __name__ == "__main__":
    main()
