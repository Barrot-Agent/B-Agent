#!/usr/bin/env python3
"""
Paradox Resolution Matrix
==========================
Detects and resolves contradictions, paradoxes, capsized logic,
and symbolic drift in the cognition system.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLES_PATH = REPO_ROOT / "memory-bundles"
MANIFEST_PATH = REPO_ROOT / "barrot_manifest.json"

# Contradiction indicators
CONTRADICTION_PATTERNS = [
    (r"(must|shall)\s+not", r"(must|shall)\s+(?!not)"),
    (r"always\s+", r"never\s+"),
    (r"enabled", r"disabled"),
    (r"active", r"inactive"),
    (r"true", r"false")
]

# Paradox patterns (self-referential or logically inconsistent)
PARADOX_INDICATORS = [
    r"this\s+statement\s+is\s+false",
    r"(?:never|always)\s+(?:always|never)",
    r"(?:all|none)\s+(?:none|all)",
    r"impossible\s+(?:to|that).{0,20}possible"
]

def load_manifest():
    """Load Barrot manifest"""
    with open(MANIFEST_PATH, "r") as f:
        return json.load(f)

def scan_for_contradictions(content, source_name):
    """Scan content for logical contradictions"""
    contradictions = []
    
    # Look for direct contradictions in patterns
    for positive_pattern, negative_pattern in CONTRADICTION_PATTERNS:
        positive_matches = list(re.finditer(positive_pattern, content, re.IGNORECASE))
        negative_matches = list(re.finditer(negative_pattern, content, re.IGNORECASE))
        
        if positive_matches and negative_matches:
            for pos_match in positive_matches[:3]:  # Limit matches
                for neg_match in negative_matches[:3]:
                    context_pos = content[max(0, pos_match.start()-50):min(len(content), pos_match.end()+50)]
                    context_neg = content[max(0, neg_match.start()-50):min(len(content), neg_match.end()+50)]
                    
                    contradictions.append({
                        "type": "contradiction",
                        "source": source_name,
                        "statement1": context_pos.strip(),
                        "statement2": context_neg.strip(),
                        "severity": "medium"
                    })
    
    return contradictions

def scan_for_paradoxes(content, source_name):
    """Scan content for paradoxes"""
    paradoxes = []
    
    for pattern in PARADOX_INDICATORS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            context = content[max(0, match.start()-50):min(len(content), match.end()+50)]
            
            paradoxes.append({
                "type": "paradox",
                "source": source_name,
                "statement": context.strip(),
                "pattern": pattern[:30],
                "severity": "high"
            })
    
    return paradoxes

def detect_symbolic_drift(manifest):
    """Detect symbolic drift in manifest"""
    drift_indicators = []
    
    # Check symbolic alignment
    alignment = manifest.get("symbolic_alignment", {})
    
    if alignment.get("drift_detected", False):
        drift_indicators.append({
            "type": "symbolic_drift",
            "source": "barrot_manifest.json",
            "description": "Drift explicitly detected in manifest",
            "severity": "high"
        })
    
    # Check cognition integrity
    if alignment.get("cognition_integrity") != "aligned":
        drift_indicators.append({
            "type": "cognition_misalignment",
            "source": "barrot_manifest.json",
            "description": f"Cognition integrity is {alignment.get('cognition_integrity')}",
            "severity": "medium"
        })
    
    return drift_indicators

def detect_capsized_logic(contradictions):
    """Detect capsized logic from contradiction patterns"""
    capsized = []
    
    # Group contradictions by source
    by_source = defaultdict(list)
    for contradiction in contradictions:
        by_source[contradiction["source"]].append(contradiction)
    
    # If multiple contradictions in same source, logic may be capsized
    for source, source_contradictions in by_source.items():
        if len(source_contradictions) >= 3:
            capsized.append({
                "type": "capsized_logic",
                "source": source,
                "description": f"Multiple contradictions ({len(source_contradictions)}) detected",
                "contradictions_count": len(source_contradictions),
                "severity": "high"
            })
    
    return capsized

def resolve_contradiction(contradiction):
    """Resolve a contradiction using priority rules"""
    # Resolution strategy: prefer newer, more specific statements
    resolution = {
        "original_contradiction": contradiction,
        "resolution_strategy": "prioritize_specificity",
        "resolved_statement": contradiction["statement1"],  # Default to first
        "confidence": 0.7,
        "resolved_at": datetime.utcnow().isoformat() + "Z"
    }
    
    # If one statement is longer (more specific), prefer it
    if len(contradiction["statement1"]) > len(contradiction["statement2"]) * 1.5:
        resolution["resolved_statement"] = contradiction["statement1"]
        resolution["confidence"] = 0.8
    elif len(contradiction["statement2"]) > len(contradiction["statement1"]) * 1.5:
        resolution["resolved_statement"] = contradiction["statement2"]
        resolution["confidence"] = 0.8
    
    return resolution

def resolve_paradox(paradox):
    """Resolve a paradox through logical transformation"""
    resolution = {
        "original_paradox": paradox,
        "resolution_strategy": "logical_transformation",
        "transformed_statement": f"Context-dependent: {paradox['statement'][:50]}",
        "explanation": "Paradox resolved by recognizing context-dependent truth values",
        "confidence": 0.6,
        "resolved_at": datetime.utcnow().isoformat() + "Z"
    }
    
    return resolution

def reunify_cognition(resolutions):
    """Reunify resolved cognition into cohesive structure"""
    unified_cognition = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "resolutions_applied": len(resolutions),
        "unified_principles": [],
        "confidence_score": 0.0
    }
    
    # Extract unified principles from resolutions
    for resolution in resolutions:
        if resolution.get("resolved_statement"):
            unified_cognition["unified_principles"].append(resolution["resolved_statement"][:100])
    
    # Calculate average confidence
    if resolutions:
        avg_confidence = sum(r.get("confidence", 0.5) for r in resolutions) / len(resolutions)
        unified_cognition["confidence_score"] = round(avg_confidence, 2)
    
    return unified_cognition

def resolve_paradoxes():
    """Execute paradox resolution protocol"""
    print("[PARADOX_RESOLVER] Starting contradiction & paradox resolution...")
    
    # Load manifest
    manifest = load_manifest()
    
    # Scan repository for contradictions and paradoxes
    print("[PARADOX_RESOLVER] Scanning repository for contradictions...")
    
    all_contradictions = []
    all_paradoxes = []
    
    # Scan markdown files
    md_files = list(REPO_ROOT.glob("*.md"))[:15]  # Limit scan
    md_files.extend(list(BUNDLES_PATH.glob("*.md"))[:15])
    
    for md_file in md_files:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            contradictions = scan_for_contradictions(content, md_file.name)
            paradoxes = scan_for_paradoxes(content, md_file.name)
            
            all_contradictions.extend(contradictions)
            all_paradoxes.extend(paradoxes)
        except Exception as e:
            print(f"[WARNING] Could not scan {md_file}: {e}")
    
    print(f"[PARADOX_RESOLVER] Found {len(all_contradictions)} contradictions and {len(all_paradoxes)} paradoxes")
    
    # Detect symbolic drift
    print("[PARADOX_RESOLVER] Detecting symbolic drift...")
    drift_indicators = detect_symbolic_drift(manifest)
    
    print(f"[PARADOX_RESOLVER] Detected {len(drift_indicators)} drift indicators")
    
    # Detect capsized logic
    print("[PARADOX_RESOLVER] Detecting capsized logic...")
    capsized = detect_capsized_logic(all_contradictions)
    
    print(f"[PARADOX_RESOLVER] Detected {len(capsized)} instances of capsized logic")
    
    # Resolve contradictions
    print("[PARADOX_RESOLVER] Resolving contradictions...")
    contradiction_resolutions = [resolve_contradiction(c) for c in all_contradictions]
    
    # Resolve paradoxes
    print("[PARADOX_RESOLVER] Resolving paradoxes...")
    paradox_resolutions = [resolve_paradox(p) for p in all_paradoxes]
    
    # Combine all resolutions
    all_resolutions = contradiction_resolutions + paradox_resolutions
    
    # Reunify cognition
    print("[PARADOX_RESOLVER] Reunifying resolved cognition...")
    unified = reunify_cognition(all_resolutions)
    
    # Save results
    results = {
        "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
        "contradictions_found": len(all_contradictions),
        "paradoxes_found": len(all_paradoxes),
        "drift_indicators": len(drift_indicators),
        "capsized_logic_instances": len(capsized),
        "contradiction_resolutions": contradiction_resolutions,
        "paradox_resolutions": paradox_resolutions,
        "unified_cognition": unified
    }
    
    results_path = BUNDLES_PATH / "paradox_resolution_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"[PARADOX_RESOLVER] Results saved to: {results_path}")
    
    # Create resolution report
    create_resolution_report(results)
    
    print(f"[PARADOX_RESOLVER] Paradox resolution complete:")
    print(f"  - Contradictions resolved: {len(all_contradictions)}")
    print(f"  - Paradoxes resolved: {len(all_paradoxes)}")
    print(f"  - Drift indicators: {len(drift_indicators)}")
    print(f"  - Cognition reunified: {unified['resolutions_applied']} resolutions applied")
    print(f"  - Confidence score: {unified['confidence_score']}")
    
    return {
        "contradictions_found": len(all_contradictions),
        "paradoxes_resolved": len(all_paradoxes),
        "drift_indicators": len(drift_indicators),
        "capsized_logic": len(capsized),
        "total_resolutions": len(all_resolutions),
        "reunification_confidence": unified["confidence_score"],
        "status": "complete"
    }

def create_resolution_report(results):
    """Create human-readable resolution report"""
    report_path = BUNDLES_PATH / "PARADOX_RESOLUTION_REPORT.md"
    
    with open(report_path, "w") as f:
        f.write("# Paradox Resolution Report\n\n")
        f.write(f"**Generated**: {results['analysis_timestamp']}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Contradictions Found**: {results['contradictions_found']}\n")
        f.write(f"- **Paradoxes Found**: {results['paradoxes_found']}\n")
        f.write(f"- **Drift Indicators**: {results['drift_indicators']}\n")
        f.write(f"- **Capsized Logic Instances**: {results['capsized_logic_instances']}\n")
        f.write(f"- **Confidence Score**: {results['unified_cognition']['confidence_score']}\n\n")
        
        f.write("## Contradiction Resolutions\n\n")
        for i, resolution in enumerate(results['contradiction_resolutions'][:5], 1):
            f.write(f"### Resolution {i}\n\n")
            f.write(f"**Strategy**: {resolution['resolution_strategy']}\n\n")
            f.write(f"**Confidence**: {resolution['confidence']}\n\n")
            f.write(f"**Resolved Statement**: {resolution['resolved_statement'][:100]}...\n\n")
        
        f.write("## Unified Cognition\n\n")
        unified = results['unified_cognition']
        f.write(f"**Resolutions Applied**: {unified['resolutions_applied']}\n\n")
        f.write(f"**Confidence Score**: {unified['confidence_score']}\n\n")
        f.write("**Unified Principles**:\n\n")
        for principle in unified['unified_principles'][:10]:
            f.write(f"- {principle}\n")
    
    print(f"[PARADOX_RESOLVER] Report created: {report_path}")

if __name__ == "__main__":
    result = resolve_paradoxes()
    print(f"\n[RESULT] {json.dumps(result, indent=2)}")
