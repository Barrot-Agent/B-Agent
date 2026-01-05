#!/usr/bin/env python3
"""
Content Alignment Scorer
Scores incoming content for alignment with puzzle pieces and system goals.
Prevents noise ingestion by filtering low-quality or irrelevant content.
"""

from typing import Dict, List, Any
from datetime import datetime, timezone


class AlignmentScorer:
    """
    Scores content for alignment with Barrot's current state and goals.
    
    Evaluates content based on:
    - Relevance to current puzzle pieces
    - Alignment with active modules
    - Contribution to knowledge gaps
    - Quality and credibility
    """
    
    def __init__(self, puzzle_pieces: List[Dict[str, Any]], active_modules: List[Dict[str, Any]]):
        """
        Initialize alignment scorer.
        
        Args:
            puzzle_pieces: Current AGI puzzle pieces
            active_modules: Active processing modules
        """
        self.puzzle_pieces = puzzle_pieces
        self.active_modules = active_modules
        self.knowledge_gaps = self._identify_knowledge_gaps()
        
    def _identify_knowledge_gaps(self) -> List[str]:
        """Identify current knowledge gaps from puzzle pieces."""
        gaps = []
        
        for piece in self.puzzle_pieces:
            # Pieces with lower integration level indicate gaps
            if piece.get("integration_level") in ["low", "initiated"]:
                gaps.append(piece.get("name", ""))
        
        return gaps
    
    def score_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score content for alignment.
        
        Args:
            content: Content to score
            
        Returns:
            Scoring results with overall score and breakdown
        """
        # Calculate component scores
        puzzle_relevance = self._score_puzzle_relevance(content)
        module_alignment = self._score_module_alignment(content)
        gap_contribution = self._score_gap_contribution(content)
        quality_score = self._score_quality(content)
        
        # Calculate weighted overall score
        overall_score = (
            puzzle_relevance * 0.3 +
            module_alignment * 0.2 +
            gap_contribution * 0.3 +
            quality_score * 0.2
        )
        
        # Determine acceptance
        accepted = overall_score >= 0.6
        
        return {
            "overall_score": overall_score,
            "accepted": accepted,
            "breakdown": {
                "puzzle_relevance": puzzle_relevance,
                "module_alignment": module_alignment,
                "gap_contribution": gap_contribution,
                "quality_score": quality_score
            },
            "reasoning": self._generate_reasoning(overall_score, puzzle_relevance, gap_contribution),
            "scored_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _score_puzzle_relevance(self, content: Dict[str, Any]) -> float:
        """
        Score content relevance to current puzzle pieces.
        
        Args:
            content: Content to score
            
        Returns:
            Score between 0 and 1
        """
        # Check if content mentions puzzle piece concepts
        content_text = self._extract_text(content)
        
        relevance_count = 0
        for piece in self.puzzle_pieces:
            piece_name = piece.get("name", "").lower()
            piece_desc = piece.get("description", "").lower()
            
            if piece_name in content_text.lower() or any(word in content_text.lower() for word in piece_desc.split()[:5]):
                relevance_count += 1
        
        # Normalize by number of puzzle pieces
        score = min(relevance_count / max(len(self.puzzle_pieces), 1), 1.0)
        return score
    
    def _score_module_alignment(self, content: Dict[str, Any]) -> float:
        """
        Score alignment with active modules.
        
        Args:
            content: Content to score
            
        Returns:
            Score between 0 and 1
        """
        # Check if content is suitable for current modules
        content_type = content.get("source", "")
        
        # Different content types align better with different modules
        alignment_map = {
            "youtube": 0.8,
            "arxiv": 0.9,
            "github": 0.85,
            "web": 0.7
        }
        
        return alignment_map.get(content_type, 0.5)
    
    def _score_gap_contribution(self, content: Dict[str, Any]) -> float:
        """
        Score contribution to filling knowledge gaps.
        
        Args:
            content: Content to score
            
        Returns:
            Score between 0 and 1
        """
        content_text = self._extract_text(content)
        
        # Check if content addresses knowledge gaps
        gap_count = 0
        for gap in self.knowledge_gaps:
            if gap.lower() in content_text.lower():
                gap_count += 1
        
        # Higher score if addresses gaps
        if len(self.knowledge_gaps) == 0:
            return 0.5  # Neutral if no gaps
        
        score = min(gap_count / len(self.knowledge_gaps) * 2, 1.0)
        return score
    
    def _score_quality(self, content: Dict[str, Any]) -> float:
        """
        Score content quality and credibility.
        
        Args:
            content: Content to score
            
        Returns:
            Score between 0 and 1
        """
        score = 0.5  # Base score
        
        # Check relevance score if available
        if "relevance_score" in content:
            score = content["relevance_score"]
        
        # Adjust based on source credibility
        source = content.get("source", "")
        credibility_boost = {
            "arxiv": 0.2,
            "github": 0.1,
            "youtube": 0.05,
            "web": 0.0
        }
        
        score = min(score + credibility_boost.get(source, 0.0), 1.0)
        
        return score
    
    def _extract_text(self, content: Dict[str, Any]) -> str:
        """Extract text from content for analysis."""
        # Combine various text fields
        text_parts = []
        
        if "title" in content:
            text_parts.append(content["title"])
        if "description" in content:
            text_parts.append(content["description"])
        if "abstract" in content:
            text_parts.append(content["abstract"])
        
        return " ".join(text_parts)
    
    def _generate_reasoning(self, overall_score: float, puzzle_relevance: float, gap_contribution: float) -> str:
        """Generate human-readable reasoning for score."""
        if overall_score >= 0.8:
            return "Highly aligned content with strong relevance to puzzle pieces and knowledge gaps."
        elif overall_score >= 0.6:
            return "Moderately aligned content that contributes to system goals."
        elif puzzle_relevance > 0.5 and gap_contribution < 0.3:
            return "Relevant to puzzle pieces but doesn't address knowledge gaps."
        elif gap_contribution > 0.5:
            return "Addresses knowledge gaps but may have lower overall relevance."
        else:
            return "Low alignment with current system state and goals."
    
    def batch_score(self, contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score multiple content items.
        
        Args:
            contents: List of content items to score
            
        Returns:
            List of scoring results
        """
        return [self.score_content(content) for content in contents]
    
    def filter_by_threshold(self, contents: List[Dict[str, Any]], threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Filter content by alignment threshold.
        
        Args:
            contents: Content items to filter
            threshold: Minimum alignment score
            
        Returns:
            Filtered content list
        """
        scored = self.batch_score(contents)
        filtered = []
        
        for content, score_result in zip(contents, scored):
            if score_result["overall_score"] >= threshold:
                content["alignment_score"] = score_result
                filtered.append(content)
        
        return filtered
