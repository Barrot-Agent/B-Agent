#!/usr/bin/env python3
"""
Auto-Glyph Emergence Detector
Monitors for pattern convergence in ingested data and detects new glyph emergence.
Automatically creates new glyph definitions when thresholds are met.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone


class AutoGlyphEmergenceDetector:
    """
    Detects emergent patterns in ingested data and triggers glyph creation.
    
    Monitors for:
    - Pattern convergence across multiple data sources
    - Cross-domain synthesis opportunities
    - Recurring themes and concepts
    - Novel insight combinations
    """
    
    def __init__(self, base_path: Path = None):
        """
        Initialize glyph emergence detector.
        
        Args:
            base_path: Base path for file operations
        """
        self.base_path = base_path or Path(__file__).parent.parent
        self.existing_glyphs = self._load_existing_glyphs()
        self.pattern_buffer = []
        self.convergence_threshold = 0.85
        self.min_occurrence_count = 5
        
    def _load_existing_glyphs(self) -> List[str]:
        """Load list of existing glyphs."""
        manifest_path = self.base_path / "barrot_manifest.json"
        
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                return manifest.get("glyphs_emitted", [])
        
        return []
    
    def detect_emergence(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect glyph emergence from processed data.
        
        Args:
            processed_data: List of processed content items
            
        Returns:
            Detection results with new glyph candidates
        """
        # Extract patterns from processed data
        patterns = self._extract_patterns(processed_data)
        
        # Add to pattern buffer
        self.pattern_buffer.extend(patterns)
        
        # Analyze convergence
        convergence_analysis = self._analyze_convergence(self.pattern_buffer)
        
        # Identify new glyph candidates
        candidates = self._identify_glyph_candidates(convergence_analysis)
        
        # Filter out existing glyphs
        new_candidates = [c for c in candidates if not self._is_duplicate_glyph(c)]
        
        return {
            "patterns_detected": len(patterns),
            "convergence_points": len(convergence_analysis),
            "new_glyph_candidates": new_candidates,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _extract_patterns(self, processed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract patterns from processed data.
        
        Args:
            processed_data: Processed content items
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        for item in processed_data:
            # Extract concepts and relationships
            concepts = item.get("processed_content", {}).get("concepts", [])
            
            # Create pattern entries
            for concept in concepts:
                patterns.append({
                    "concept": concept,
                    "source": item.get("source"),
                    "content_id": item.get("id"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        return patterns
    
    def _analyze_convergence(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze pattern convergence across sources.
        
        Args:
            patterns: Pattern buffer
            
        Returns:
            List of convergence points
        """
        # Group patterns by concept
        concept_groups = {}
        
        for pattern in patterns:
            concept = pattern["concept"]
            if concept not in concept_groups:
                concept_groups[concept] = []
            concept_groups[concept].append(pattern)
        
        # Identify convergence points
        convergence_points = []
        
        for concept, group in concept_groups.items():
            if len(group) >= self.min_occurrence_count:
                # Check if from multiple sources
                sources = set(p["source"] for p in group)
                
                if len(sources) >= 2:
                    convergence_points.append({
                        "concept": concept,
                        "occurrence_count": len(group),
                        "source_diversity": len(sources),
                        "sources": list(sources),
                        "strength": len(group) / self.min_occurrence_count
                    })
        
        return convergence_points
    
    def _identify_glyph_candidates(self, convergence_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify potential new glyphs from convergence points.
        
        Args:
            convergence_points: Points of pattern convergence
            
        Returns:
            List of glyph candidates
        """
        candidates = []
        
        for point in convergence_points:
            # Check if meets threshold
            if point["strength"] >= self.convergence_threshold:
                glyph_name = self._generate_glyph_name(point["concept"])
                
                candidates.append({
                    "glyph_name": glyph_name,
                    "concept": point["concept"],
                    "emergence_strength": point["strength"],
                    "source_diversity": point["source_diversity"],
                    "supporting_sources": point["sources"],
                    "occurrence_count": point["occurrence_count"]
                })
        
        return candidates
    
    def _generate_glyph_name(self, concept: str) -> str:
        """
        Generate a glyph name from concept.
        
        Args:
            concept: Concept name
            
        Returns:
            Glyph name in standard format
        """
        # Convert to glyph naming convention
        name = concept.upper().replace(" ", "_").replace("-", "_")
        
        # Add GLYPH suffix if not present
        if not name.endswith("_GLYPH"):
            name += "_GLYPH"
        
        return name
    
    def _is_duplicate_glyph(self, candidate: Dict[str, Any]) -> bool:
        """
        Check if glyph already exists.
        
        Args:
            candidate: Glyph candidate
            
        Returns:
            True if duplicate
        """
        glyph_name = candidate["glyph_name"]
        
        # Check exact match
        if glyph_name in self.existing_glyphs:
            return True
        
        # Check for similar glyphs
        concept = candidate["concept"].lower()
        for existing in self.existing_glyphs:
            if concept in existing.lower():
                return True
        
        return False
    
    def create_glyph_definition(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new glyph definition file.
        
        Args:
            candidate: Glyph candidate to create
            
        Returns:
            Creation result
        """
        glyph_name = candidate["glyph_name"]
        glyph_path = self.base_path / "glyphs" / f"{glyph_name.lower()}.yml"
        
        # Create glyph definition
        definition = {
            "glyph_name": glyph_name,
            "concept": candidate["concept"],
            "status": "emergent",
            "emission_date": datetime.now(timezone.utc).isoformat(),
            "emergence_strength": candidate["emergence_strength"],
            "source_diversity": candidate["source_diversity"],
            "supporting_sources": candidate["supporting_sources"],
            "occurrence_count": candidate["occurrence_count"],
            "description": f"Auto-generated glyph for {candidate['concept']} pattern convergence",
            "triggers": [
                "Pattern convergence across multiple sources",
                f"Concept appeared {candidate['occurrence_count']} times"
            ],
            "implications": [
                "Represents emerging pattern in AGI knowledge space",
                "Requires validation and refinement"
            ],
            "next_steps": [
                "Manual review of glyph definition",
                "Integration with existing glyphs",
                "Expansion of related concepts"
            ]
        }
        
        # Save to user-defined glyphs directory
        user_glyph_path = self.base_path / "glyphs" / "user_defined" / f"{glyph_name.lower()}.yml"
        user_glyph_path.parent.mkdir(parents=True, exist_ok=True)
        
        import yaml
        with open(user_glyph_path, 'w') as f:
            yaml.dump(definition, f, default_flow_style=False)
        
        # Update manifest
        self._update_manifest(glyph_name)
        
        return {
            "created": True,
            "glyph_name": glyph_name,
            "path": str(user_glyph_path),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _update_manifest(self, glyph_name: str):
        """
        Update barrot_manifest.json with new glyph.
        
        Args:
            glyph_name: Name of new glyph
        """
        manifest_path = self.base_path / "barrot_manifest.json"
        
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            if glyph_name not in manifest.get("glyphs_emitted", []):
                manifest.setdefault("glyphs_emitted", []).append(glyph_name)
                manifest["last_glyph_emission"] = datetime.now(timezone.utc).date().isoformat()
                manifest["last_update"] = datetime.now(timezone.utc).date().isoformat()
                
                with open(manifest_path, 'w') as f:
                    json.dump(manifest, f, indent=2)
    
    def monitor_and_emit(self, processed_data: List[Dict[str, Any]], auto_create: bool = True) -> Dict[str, Any]:
        """
        Monitor data and automatically emit new glyphs.
        
        Args:
            processed_data: Processed content data
            auto_create: Whether to automatically create glyphs
            
        Returns:
            Monitoring results
        """
        # Detect emergence
        detection = self.detect_emergence(processed_data)
        
        created_glyphs = []
        
        # Auto-create if enabled
        if auto_create and detection["new_glyph_candidates"]:
            for candidate in detection["new_glyph_candidates"]:
                try:
                    result = self.create_glyph_definition(candidate)
                    created_glyphs.append(result)
                except Exception as e:
                    print(f"Error creating glyph {candidate['glyph_name']}: {e}")
        
        return {
            "detection": detection,
            "glyphs_created": created_glyphs,
            "auto_create_enabled": auto_create,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
