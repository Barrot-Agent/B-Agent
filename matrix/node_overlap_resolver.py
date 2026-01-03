#!/usr/bin/env python3
"""
Overlap Resolution Node
Continuously scans memory bundles, directives, and manifest entries for semantic overlap.
Detects when directives have been restated or reissued.
Collapses redundant cognition into unified symbolic threads.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLES_PATH = REPO_ROOT / "memory-bundles"
MANIFEST_PATH = REPO_ROOT / "barrot_manifest.json"
TRACE_LOG_PATH = BUNDLES_PATH / "TRACE_LOG.md"

# Import glyph mapper
import sys
sys.path.insert(0, str(REPO_ROOT / "matrix"))
from glyph_mapper import register_glyph_emission

def load_manifest():
    """Load the Barrot manifest"""
    with open(MANIFEST_PATH, 'r') as f:
        return json.load(f)

def load_memory_bundles():
    """Load all memory bundle files for analysis"""
    bundles = {}
    
    # Load JSON bundles
    for json_file in BUNDLES_PATH.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                bundles[json_file.name] = {
                    'type': 'json',
                    'content': json.load(f),
                    'path': str(json_file)
                }
        except Exception as e:
            print(f"[OVERLAP_RESOLVER] Warning: Could not load {json_file.name}: {e}")
    
    # Load markdown bundles
    for md_file in BUNDLES_PATH.glob("*.md"):
        try:
            with open(md_file, 'r') as f:
                bundles[md_file.name] = {
                    'type': 'markdown',
                    'content': f.read(),
                    'path': str(md_file)
                }
        except Exception as e:
            print(f"[OVERLAP_RESOLVER] Warning: Could not load {md_file.name}: {e}")
    
    return bundles

def extract_semantic_tokens(text):
    """Extract semantic tokens from text for overlap detection"""
    if isinstance(text, dict):
        text = json.dumps(text)
    elif not isinstance(text, str):
        text = str(text)
    
    # Convert to lowercase and extract meaningful words
    text = text.lower()
    
    # Remove common words and extract significant tokens
    words = re.findall(r'\b[a-z]{4,}\b', text)
    
    # Filter out very common words
    common_words = {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'what', 'when', 'where'}
    words = [w for w in words if w not in common_words]
    
    return words

def calculate_semantic_similarity(tokens1, tokens2):
    """Calculate semantic similarity between two token sets"""
    if not tokens1 or not tokens2:
        return 0.0
    
    set1 = set(tokens1)
    set2 = set(tokens2)
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    if union == 0:
        return 0.0
    
    return intersection / union

def detect_semantic_overlaps(bundles, threshold=0.5):
    """Detect semantic overlaps between memory bundles"""
    overlaps = []
    bundle_items = list(bundles.items())
    
    for i, (name1, bundle1) in enumerate(bundle_items):
        tokens1 = extract_semantic_tokens(bundle1['content'])
        
        for name2, bundle2 in bundle_items[i+1:]:
            tokens2 = extract_semantic_tokens(bundle2['content'])
            
            similarity = calculate_semantic_similarity(tokens1, tokens2)
            
            if similarity >= threshold:
                overlaps.append({
                    'bundle1': name1,
                    'bundle2': name2,
                    'similarity': similarity,
                    'type': 'semantic_overlap'
                })
    
    return overlaps

def detect_restated_directives(bundles):
    """Detect when directives have been restated or reissued"""
    directive_patterns = [
        r'directive',
        r'protocol',
        r'must',
        r'shall',
        r'requirement',
        r'specification'
    ]
    
    restated = []
    directive_contents = defaultdict(list)
    
    for name, bundle in bundles.items():
        content = bundle['content']
        if isinstance(content, dict):
            content = json.dumps(content)
        
        # Check if content contains directive-like patterns
        is_directive = any(re.search(pattern, content, re.IGNORECASE) for pattern in directive_patterns)
        
        if is_directive:
            tokens = extract_semantic_tokens(content)
            key = tuple(sorted(set(tokens[:20])))  # Use first 20 unique tokens as key
            directive_contents[key].append(name)
    
    # Find restated directives (same semantic content in multiple files)
    for key, files in directive_contents.items():
        if len(files) > 1:
            restated.append({
                'files': files,
                'type': 'restated_directive',
                'semantic_key': str(key[:5])  # First 5 tokens for readability
            })
    
    return restated

def collapse_redundant_cognition(overlaps, restated):
    """Collapse redundant cognition into unified symbolic threads"""
    unified_threads = []
    
    # Create unified threads from overlaps
    for overlap in overlaps:
        thread = {
            'type': 'semantic_overlap_thread',
            'bundles': [overlap['bundle1'], overlap['bundle2']],
            'similarity': overlap['similarity'],
            'timestamp': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            'status': 'unified'
        }
        unified_threads.append(thread)
    
    # Create unified threads from restated directives
    for restatement in restated:
        thread = {
            'type': 'restated_directive_thread',
            'bundles': restatement['files'],
            'semantic_key': restatement['semantic_key'],
            'timestamp': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            'status': 'unified'
        }
        unified_threads.append(thread)
    
    return unified_threads

def save_overlap_results(overlaps, restated, unified_threads):
    """Save overlap resolution results"""
    results = {
        'timestamp': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        'semantic_overlaps': overlaps,
        'restated_directives': restated,
        'unified_threads': unified_threads,
        'summary': {
            'total_overlaps': len(overlaps),
            'total_restatements': len(restated),
            'total_unified_threads': len(unified_threads)
        }
    }
    
    results_path = BUNDLES_PATH / "overlap_resolution_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

def log_overlap_resolution(results):
    """Log overlap resolution to TRACE_LOG"""
    log_entry = f"""
## OVERLAP_RESOLUTION_GLYPH Event: {results['timestamp']}

**Summary:**
- Semantic Overlaps Detected: {results['summary']['total_overlaps']}
- Restated Directives Detected: {results['summary']['total_restatements']}
- Unified Threads Created: {results['summary']['total_unified_threads']}

### Semantic Overlaps:
"""
    
    for overlap in results['semantic_overlaps'][:10]:  # Limit to first 10 for readability
        log_entry += f"- {overlap['bundle1']} ↔ {overlap['bundle2']} (similarity: {overlap['similarity']:.2f})\n"
    
    if len(results['semantic_overlaps']) > 10:
        log_entry += f"- ... and {len(results['semantic_overlaps']) - 10} more\n"
    
    log_entry += "\n### Restated Directives:\n"
    
    for restatement in results['restated_directives'][:10]:
        log_entry += f"- Files: {', '.join(restatement['files'])}\n"
    
    if len(results['restated_directives']) > 10:
        log_entry += f"- ... and {len(results['restated_directives']) - 10} more\n"
    
    log_entry += "\n### Status:\nOverlap resolution complete. Redundant cognition collapsed into unified threads.\n\n---\n"
    
    with open(TRACE_LOG_PATH, 'a') as f:
        f.write(log_entry)

def run_overlap_resolution():
    """Main overlap resolution process"""
    print("[OVERLAP_RESOLVER] Starting overlap resolution...")
    
    # Load manifest
    manifest = load_manifest()
    
    if manifest.get('overlap_resolution') != 'enabled':
        print("[OVERLAP_RESOLVER] Overlap resolution not enabled in manifest")
        return
    
    # Load memory bundles
    print("[OVERLAP_RESOLVER] Loading memory bundles...")
    bundles = load_memory_bundles()
    print(f"[OVERLAP_RESOLVER] Loaded {len(bundles)} memory bundles")
    
    # Detect semantic overlaps
    print("[OVERLAP_RESOLVER] Detecting semantic overlaps...")
    overlaps = detect_semantic_overlaps(bundles)
    print(f"[OVERLAP_RESOLVER] Found {len(overlaps)} semantic overlaps")
    
    # Detect restated directives
    print("[OVERLAP_RESOLVER] Detecting restated directives...")
    restated = detect_restated_directives(bundles)
    print(f"[OVERLAP_RESOLVER] Found {len(restated)} restated directives")
    
    # Collapse redundant cognition
    print("[OVERLAP_RESOLVER] Collapsing redundant cognition...")
    unified_threads = collapse_redundant_cognition(overlaps, restated)
    print(f"[OVERLAP_RESOLVER] Created {len(unified_threads)} unified threads")
    
    # Save results
    results = save_overlap_results(overlaps, restated, unified_threads)
    
    # Log to TRACE_LOG
    log_overlap_resolution(results)
    
    # Emit glyph
    register_glyph_emission(
        "OVERLAP_RESOLUTION_GLYPH",
        "node_overlap_resolver",
        {
            "semantic_overlaps": len(overlaps),
            "restated_directives": len(restated),
            "unified_threads": len(unified_threads)
        }
    )
    
    print("[OVERLAP_RESOLVER] ✓ OVERLAP_RESOLUTION_GLYPH emitted")
    print("[OVERLAP_RESOLVER] Overlap resolution complete")

if __name__ == "__main__":
    run_overlap_resolution()
