#!/usr/bin/env python3
"""
Query Generator
Generates optimal search queries for each source based on current knowledge gaps
"""

from typing import Dict, List, Any
from datetime import datetime, timezone
import json
from pathlib import Path


class QueryGenerator:
    """Generate optimized search queries for data sources"""
    
    def __init__(self, repo_root: Path = None):
        """Initialize the query generator"""
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.memory_bundles = self.repo_root / "memory-bundles"
        
        # AI/ML research topics
        self.core_topics = [
            "artificial general intelligence",
            "large language models",
            "reinforcement learning",
            "computer vision",
            "natural language processing",
            "transformer architectures",
            "neural networks",
            "deep learning optimization",
            "AI alignment",
            "multimodal learning",
            "few-shot learning",
            "meta-learning",
            "causal inference",
            "explainable AI",
            "AI safety"
        ]
        
        # Advanced topics
        self.advanced_topics = [
            "constitutional AI",
            "chain-of-thought reasoning",
            "retrieval augmented generation",
            "diffusion models",
            "adversarial robustness",
            "continual learning",
            "neural architecture search",
            "quantization",
            "knowledge distillation",
            "federated learning"
        ]
    
    def generate_academic_queries(self, focus_area: str = None) -> List[str]:
        """Generate queries for academic sources (arXiv, papers, etc.)"""
        queries = []
        
        topics = self.core_topics + self.advanced_topics
        
        if focus_area:
            topics = [t for t in topics if focus_area.lower() in t.lower()]
        
        # Generate queries with various formats
        for topic in topics[:10]:  # Limit to avoid overwhelming
            queries.extend([
                f"{topic}",
                f"{topic} AND (neural OR deep learning)",
                f"{topic} recent advances",
                f"{topic} survey",
                f"{topic} benchmark"
            ])
        
        return queries[:20]  # Return top 20
    
    def generate_code_queries(self) -> List[str]:
        """Generate queries for code repositories"""
        return [
            "artificial intelligence",
            "machine learning",
            "deep learning framework",
            "neural network implementation",
            "llm fine-tuning",
            "transformer model",
            "reinforcement learning environment",
            "computer vision toolkit",
            "nlp pipeline",
            "pytorch implementation",
            "tensorflow model",
            "huggingface transformers",
            "stable diffusion",
            "langchain application",
            "llama model"
        ]
    
    def generate_video_queries(self) -> List[str]:
        """Generate queries for video platforms"""
        return [
            "artificial intelligence tutorial",
            "machine learning course",
            "deep learning explained",
            "AI research talk",
            "neural networks from scratch",
            "transformer architecture",
            "LLM development",
            "reinforcement learning tutorial",
            "computer vision project",
            "NLP with transformers",
            "AI conference keynote",
            "ML engineering best practices"
        ]
    
    def generate_forum_queries(self) -> List[str]:
        """Generate queries for forums and discussions"""
        return [
            "AGI development",
            "LLM fine-tuning tips",
            "transformer implementation",
            "AI alignment discussion",
            "neural network optimization",
            "machine learning best practices",
            "deep learning debugging",
            "AI model deployment",
            "ML ops strategies",
            "AI research breakthroughs"
        ]
    
    def generate_news_queries(self) -> List[str]:
        """Generate queries for news sources"""
        return [
            "artificial intelligence news",
            "AI breakthrough",
            "machine learning advancement",
            "AI startup",
            "new AI model released",
            "AI research paper",
            "AI regulation",
            "AI ethics",
            "AI industry trends",
            "OpenAI announcement",
            "Google AI update",
            "AI funding"
        ]
    
    def generate_dataset_queries(self) -> List[str]:
        """Generate queries for dataset sources"""
        return [
            "machine learning dataset",
            "computer vision dataset",
            "NLP corpus",
            "benchmark dataset",
            "text classification dataset",
            "image segmentation dataset",
            "speech recognition dataset",
            "reinforcement learning environment",
            "question answering dataset",
            "multilingual dataset"
        ]
    
    def generate_blog_queries(self) -> List[str]:
        """Generate queries for blog and article sources"""
        return [
            "AI implementation guide",
            "machine learning tutorial",
            "deep learning best practices",
            "transformer architecture explained",
            "LLM fine-tuning",
            "AI model optimization",
            "neural network training tips",
            "production ML",
            "AI research summary",
            "ML engineering patterns"
        ]
    
    def generate_queries_for_source(self, source_type: str, source_config: Dict[str, Any] = None) -> List[str]:
        """
        Generate optimized queries for a specific source type
        
        Args:
            source_type: Type of source (academic, code, video, etc.)
            source_config: Optional source configuration
            
        Returns:
            List of optimized search queries
        """
        query_generators = {
            'academic': self.generate_academic_queries,
            'code': self.generate_code_queries,
            'video': self.generate_video_queries,
            'forum': self.generate_forum_queries,
            'news': self.generate_news_queries,
            'dataset': self.generate_dataset_queries,
            'blog': self.generate_blog_queries
        }
        
        generator = query_generators.get(source_type, self.generate_academic_queries)
        
        # Add source-specific focus if provided
        if source_config and 'focus' in source_config:
            focus = source_config['focus'][0] if isinstance(source_config['focus'], list) else source_config['focus']
            if source_type == 'academic':
                return generator(focus)
        
        return generator()
    
    def generate_gap_based_queries(self, knowledge_gaps: List[str]) -> List[str]:
        """
        Generate queries based on identified knowledge gaps
        
        Args:
            knowledge_gaps: List of identified knowledge gaps
            
        Returns:
            Targeted queries to fill gaps
        """
        queries = []
        
        for gap in knowledge_gaps:
            queries.extend([
                f"{gap}",
                f"{gap} comprehensive guide",
                f"{gap} state of the art",
                f"{gap} recent research",
                f"{gap} implementation"
            ])
        
        return queries
    
    def save_query_plan(self, queries: Dict[str, List[str]]):
        """Save generated query plan to memory bundle"""
        self.memory_bundles.mkdir(parents=True, exist_ok=True)
        
        query_plan = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "queries_by_source": queries,
            "total_queries": sum(len(q) for q in queries.values())
        }
        
        query_plan_path = self.memory_bundles / "query_plan.json"
        with open(query_plan_path, 'w') as f:
            json.dump(query_plan, f, indent=2)
        
        print(f"[QueryGenerator] Query plan saved: {query_plan['total_queries']} queries")


def main():
    """Main execution"""
    generator = QueryGenerator()
    
    # Generate queries for each source type
    query_plan = {}
    
    source_types = ['academic', 'code', 'video', 'forum', 'news', 'dataset', 'blog']
    
    for source_type in source_types:
        queries = generator.generate_queries_for_source(source_type)
        query_plan[source_type] = queries
        print(f"\n{source_type.upper()} Queries ({len(queries)}):")
        for i, query in enumerate(queries[:5], 1):
            print(f"  {i}. {query}")
    
    # Save query plan
    generator.save_query_plan(query_plan)
    
    return generator


if __name__ == "__main__":
    main()
