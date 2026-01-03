#!/usr/bin/env python3
"""
Overlap Resolution System
==========================
Analyzes repository for overlapping directives and collapses
redundant cognition into unified symbolic threads.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLES_PATH = REPO_ROOT / "memory-bundles"

def analyze_document_for_directives(file_path):
    """Extract directives from a markdown or text document"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        directives = []
        
        # Pattern matching for directives
        patterns = [
            r"(?:must|shall|should|will)\s+([^.!?\n]{10,100})",
            r"(?:protocol|directive|requirement|mandate):\s*([^.!?\n]{10,100})",
            r"##?\s+([A-Z][^.\n]{10,100})",
            r"(?:^|\n)\s*[-*]\s*([A-Z][^.\n]{10,100})"
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                directive = match.group(1).strip()
                if len(directive) > 10:  # Filter very short matches
                    directives.append({
                        "text": directive,
                        "source": file_path.name,
                        "pattern": pattern[:20]
                    })
        
        return directives
    except Exception as e:
        print(f"[WARNING] Could not analyze {file_path}: {e}")
        return []

def calculate_similarity(text1, text2):
    """Calculate simple similarity between two text strings"""
    # Convert to lowercase and split into words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    # Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def find_overlapping_directives(all_directives, similarity_threshold=0.4):
    """Find overlapping directives based on similarity"""
    overlaps = []
    
    for i, dir1 in enumerate(all_directives):
        for j, dir2 in enumerate(all_directives[i+1:], start=i+1):
            similarity = calculate_similarity(dir1["text"], dir2["text"])
            
            if similarity >= similarity_threshold:
                overlaps.append({
                    "directive1": dir1,
                    "directive2": dir2,
                    "similarity": similarity,
                    "sources": [dir1["source"], dir2["source"]]
                })
    
    return overlaps

def collapse_overlaps(overlaps):
    """Collapse overlapping directives into unified threads"""
    # Group by similarity clusters
    clusters = defaultdict(list)
    
    for overlap in overlaps:
        # Create cluster key based on directive texts
        key = frozenset([overlap["directive1"]["text"][:30], overlap["directive2"]["text"][:30]])
        clusters[key].append(overlap)
    
    unified_threads = []
    
    for cluster_key, cluster_overlaps in clusters.items():
        # Get all unique directives in this cluster
        directives = []
        sources = set()
        
        for overlap in cluster_overlaps:
            directives.append(overlap["directive1"]["text"])
            directives.append(overlap["directive2"]["text"])
            sources.update(overlap["sources"])
        
        # Create unified directive (use longest as base)
        unique_directives = list(set(directives))
        unified_text = max(unique_directives, key=len)
        
        unified_thread = {
            "unified_directive": unified_text,
            "source_directives": unique_directives,
            "sources": list(sources),
            "cluster_size": len(cluster_overlaps),
            "collapsed_at": datetime.utcnow().isoformat() + "Z"
        }
        
        unified_threads.append(unified_thread)
    
    return unified_threads

def restructure_queries(unified_threads):
    """Restructure overlapping queries into optimized form"""
    restructured = []
    
    for thread in unified_threads:
        # Extract key concepts from unified directive
        words = thread["unified_directive"].split()
        key_concepts = [w for w in words if len(w) > 5][:5]  # Top 5 significant words
        
        restructured_query = {
            "original_directive": thread["unified_directive"],
            "key_concepts": key_concepts,
            "optimized_query": " ".join(key_concepts),
            "sources_unified": len(thread["sources"]),
            "redundancy_eliminated": thread["cluster_size"]
        }
        
        restructured.append(restructured_query)
    
    return restructured

def resolve_overlaps():
    """Execute overlap resolution system"""
    print("[OVERLAP_RESOLVER] Starting query restructuring & overlap resolution...")
    
    # Scan repository for documents
    print("[OVERLAP_RESOLVER] Scanning repository for directives...")
    
    all_directives = []
    
    # Scan markdown files
    md_files = list(REPO_ROOT.glob("*.md"))
    md_files.extend(BUNDLES_PATH.glob("*.md"))
    
    for md_file in md_files[:20]:  # Limit to first 20 to avoid overwhelming
        directives = analyze_document_for_directives(md_file)
        all_directives.extend(directives)
    
    print(f"[OVERLAP_RESOLVER] Found {len(all_directives)} directives across {len(md_files)} documents")
    
    # Find overlaps
    print("[OVERLAP_RESOLVER] Analyzing for overlapping directives...")
    overlaps = find_overlapping_directives(all_directives, similarity_threshold=0.4)
    
    print(f"[OVERLAP_RESOLVER] Detected {len(overlaps)} overlapping directive pairs")
    
    # Collapse overlaps into unified threads
    print("[OVERLAP_RESOLVER] Collapsing overlaps into unified threads...")
    unified_threads = collapse_overlaps(overlaps)
    
    print(f"[OVERLAP_RESOLVER] Created {len(unified_threads)} unified symbolic threads")
    
    # Restructure queries
    print("[OVERLAP_RESOLVER] Restructuring queries for optimization...")
    restructured = restructure_queries(unified_threads)
    
    # Save results
    results_path = BUNDLES_PATH / "overlap_resolution_results.json"
    results = {
        "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
        "total_directives_analyzed": len(all_directives),
        "overlaps_detected": len(overlaps),
        "unified_threads": unified_threads,
        "restructured_queries": restructured
    }
    
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"[OVERLAP_RESOLVER] Results saved to: {results_path}")
    
    # Create human-readable report
    create_overlap_report(results)
    
    print(f"[OVERLAP_RESOLVER] Overlap resolution complete:")
    print(f"  - Directives analyzed: {len(all_directives)}")
    print(f"  - Overlaps detected: {len(overlaps)}")
    print(f"  - Unified threads: {len(unified_threads)}")
    print(f"  - Queries restructured: {len(restructured)}")
    
    return {
        "directives_analyzed": len(all_directives),
        "overlaps_detected": len(overlaps),
        "overlaps_resolved": len(unified_threads),
        "queries_restructured": len(restructured),
        "status": "complete"
    }

def create_overlap_report(results):
    """Create human-readable overlap resolution report"""
    report_path = BUNDLES_PATH / "OVERLAP_RESOLUTION_REPORT.md"
    
    with open(report_path, "w") as f:
        f.write("# Overlap Resolution Report\n\n")
        f.write(f"**Generated**: {results['analysis_timestamp']}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Directives Analyzed**: {results['total_directives_analyzed']}\n")
        f.write(f"- **Overlaps Detected**: {results['overlaps_detected']}\n")
        f.write(f"- **Unified Threads Created**: {len(results['unified_threads'])}\n")
        f.write(f"- **Queries Restructured**: {len(results['restructured_queries'])}\n\n")
        
        f.write("## Unified Symbolic Threads\n\n")
        for i, thread in enumerate(results['unified_threads'][:10], 1):  # Show top 10
            f.write(f"### Thread {i}\n\n")
            f.write(f"**Unified Directive**: {thread['unified_directive'][:100]}...\n\n")
            f.write(f"**Sources**: {', '.join(thread['sources'])}\n\n")
            f.write(f"**Cluster Size**: {thread['cluster_size']} overlapping directives\n\n")
        
        f.write("## Restructured Queries\n\n")
        for i, query in enumerate(results['restructured_queries'][:10], 1):  # Show top 10
            f.write(f"### Query {i}\n\n")
            f.write(f"**Optimized**: {query['optimized_query']}\n\n")
            f.write(f"**Key Concepts**: {', '.join(query['key_concepts'])}\n\n")
            f.write(f"**Redundancy Eliminated**: {query['redundancy_eliminated']}\n\n")
    
    print(f"[OVERLAP_RESOLVER] Report created: {report_path}")

if __name__ == "__main__":
    result = resolve_overlaps()
    print(f"\n[RESULT] {json.dumps(result, indent=2)}")
