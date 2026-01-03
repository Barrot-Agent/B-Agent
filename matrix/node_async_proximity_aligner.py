#!/usr/bin/env python3
"""
Asynchronous Proximity Alignment Node
Identifies asynchronous proximities between temporally distant data,
cognition fragments with latent alignment, and symbolic patterns across domains.
Aligns these proximities into synchronized cognition clusters.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLES_PATH = REPO_ROOT / "memory-bundles"
MATRIX_PATH = REPO_ROOT / "matrix"
TOOL_PROFILES_PATH = REPO_ROOT / "tool_profiles"
MANIFEST_PATH = REPO_ROOT / "barrot_manifest.json"
TRACE_LOG_PATH = BUNDLES_PATH / "TRACE_LOG.md"

# Import glyph mapper
import sys
sys.path.insert(0, str(REPO_ROOT / "matrix"))
from glyph_mapper import register_glyph_emission

def parse_timestamp(timestamp_str):
    """Parse various timestamp formats"""
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except:
            continue
    
    return None

def load_temporal_data():
    """Load data with temporal information from all sources"""
    temporal_data = []
    
    # Load from memory bundles
    for json_file in BUNDLES_PATH.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                content = json.load(f)
                
                # Extract timestamps from history arrays
                if isinstance(content, dict):
                    if 'history' in content and isinstance(content['history'], list):
                        for item in content['history']:
                            if 'timestamp' in item:
                                ts = parse_timestamp(item['timestamp'])
                                if ts:
                                    temporal_data.append({
                                        'timestamp': ts,
                                        'source': json_file.name,
                                        'type': 'history_entry',
                                        'content': item
                                    })
        except Exception as e:
            print(f"[PROXIMITY_ALIGNER] Warning: Could not load {json_file.name}: {e}")
    
    # Load from markdown files with date patterns
    for md_file in BUNDLES_PATH.glob("*.md"):
        try:
            with open(md_file, 'r') as f:
                content = f.read()
                
                # Extract dates from markdown
                date_pattern = r'\*\*(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2})?)'
                matches = re.findall(date_pattern, content)
                
                for match in matches:
                    ts = parse_timestamp(match)
                    if ts:
                        temporal_data.append({
                            'timestamp': ts,
                            'source': md_file.name,
                            'type': 'markdown_entry',
                            'content': content[:500]  # First 500 chars for context
                        })
        except Exception as e:
            print(f"[PROXIMITY_ALIGNER] Warning: Could not load {md_file.name}: {e}")
    
    # Sort by timestamp
    temporal_data.sort(key=lambda x: x['timestamp'])
    
    return temporal_data

def detect_asynchronous_proximities(temporal_data):
    """Detect proximities between temporally distant but semantically related data"""
    proximities = []
    
    # Look for patterns across time
    for i, data1 in enumerate(temporal_data):
        for data2 in temporal_data[i+1:]:
            # Calculate temporal distance
            time_delta = (data2['timestamp'] - data1['timestamp']).total_seconds()
            
            # Only consider if temporally distant (more than 1 hour apart)
            if time_delta > 3600:
                # Extract semantic content
                content1 = json.dumps(data1['content']) if isinstance(data1['content'], dict) else data1['content']
                content2 = json.dumps(data2['content']) if isinstance(data2['content'], dict) else data2['content']
                
                # Simple keyword overlap check
                words1 = set(re.findall(r'\b[a-z]{4,}\b', content1.lower()))
                words2 = set(re.findall(r'\b[a-z]{4,}\b', content2.lower()))
                
                overlap = len(words1 & words2)
                
                if overlap > 5:  # Significant semantic overlap
                    proximities.append({
                        'data1': {
                            'timestamp': data1['timestamp'].isoformat(),
                            'source': data1['source'],
                            'type': data1['type']
                        },
                        'data2': {
                            'timestamp': data2['timestamp'].isoformat(),
                            'source': data2['source'],
                            'type': data2['type']
                        },
                        'temporal_distance_hours': time_delta / 3600,
                        'semantic_overlap_score': overlap,
                        'proximity_type': 'asynchronous'
                    })
    
    return proximities

def identify_latent_alignments():
    """Identify cognition fragments with latent alignment"""
    alignments = []
    
    # Load glyph mappings
    glyph_mapping_path = BUNDLES_PATH / "glyph_mappings.json"
    if glyph_mapping_path.exists():
        with open(glyph_mapping_path, 'r') as f:
            mappings = json.load(f)
            
            # Analyze dependencies for latent patterns
            if 'dependencies' in mappings:
                dep_graph = defaultdict(list)
                
                for dep in mappings['dependencies']:
                    source = dep['source_node']
                    target = dep['target_node']
                    dep_graph[source].append(target)
                
                # Find nodes with multiple dependencies (potential latent alignment)
                for node, targets in dep_graph.items():
                    if len(targets) > 1:
                        alignments.append({
                            'node': node,
                            'aligned_targets': targets,
                            'alignment_type': 'multi_dependency',
                            'strength': len(targets)
                        })
    
    return alignments

def detect_cross_domain_patterns():
    """Detect symbolic patterns across different domains"""
    patterns = []
    
    # Load data from different domains
    domains = {
        'memory': BUNDLES_PATH,
        'matrix': MATRIX_PATH,
        'tools': TOOL_PROFILES_PATH
    }
    
    domain_data = {}
    
    for domain_name, domain_path in domains.items():
        domain_data[domain_name] = []
        
        # Load files from domain
        for file_path in domain_path.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    content = json.load(f)
                    domain_data[domain_name].append({
                        'file': file_path.name,
                        'content': content
                    })
            except:
                pass
        
        for file_path in domain_path.glob("*.yaml"):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    domain_data[domain_name].append({
                        'file': file_path.name,
                        'content': content
                    })
            except:
                pass
    
    # Look for common patterns across domains
    for domain1, files1 in domain_data.items():
        for domain2, files2 in domain_data.items():
            if domain1 >= domain2:  # Avoid duplicates
                continue
            
            for file1 in files1:
                for file2 in files2:
                    # Extract keywords
                    content1 = json.dumps(file1['content']) if isinstance(file1['content'], dict) else file1['content']
                    content2 = json.dumps(file2['content']) if isinstance(file2['content'], dict) else file2['content']
                    
                    words1 = set(re.findall(r'\b[a-z]{4,}\b', content1.lower()))
                    words2 = set(re.findall(r'\b[a-z]{4,}\b', content2.lower()))
                    
                    overlap = len(words1 & words2)
                    
                    if overlap > 3:
                        patterns.append({
                            'domain1': domain1,
                            'domain2': domain2,
                            'file1': file1['file'],
                            'file2': file2['file'],
                            'pattern_strength': overlap,
                            'pattern_type': 'cross_domain'
                        })
    
    return patterns

def create_cognition_clusters(proximities, alignments, patterns):
    """Create synchronized cognition clusters from detected proximities"""
    clusters = []
    
    # Cluster by asynchronous proximities
    if proximities:
        cluster = {
            'cluster_type': 'asynchronous_proximity',
            'timestamp': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            'members': proximities,
            'size': len(proximities),
            'status': 'synchronized'
        }
        clusters.append(cluster)
    
    # Cluster by latent alignments
    if alignments:
        cluster = {
            'cluster_type': 'latent_alignment',
            'timestamp': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            'members': alignments,
            'size': len(alignments),
            'status': 'synchronized'
        }
        clusters.append(cluster)
    
    # Cluster by cross-domain patterns
    if patterns:
        cluster = {
            'cluster_type': 'cross_domain_pattern',
            'timestamp': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            'members': patterns,
            'size': len(patterns),
            'status': 'synchronized'
        }
        clusters.append(cluster)
    
    return clusters

def save_alignment_results(proximities, alignments, patterns, clusters):
    """Save alignment results"""
    results = {
        'timestamp': datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        'asynchronous_proximities': proximities[:50],  # Limit for storage
        'latent_alignments': alignments,
        'cross_domain_patterns': patterns[:50],  # Limit for storage
        'cognition_clusters': clusters,
        'summary': {
            'total_proximities': len(proximities),
            'total_alignments': len(alignments),
            'total_patterns': len(patterns),
            'total_clusters': len(clusters)
        }
    }
    
    results_path = BUNDLES_PATH / "proximity_alignment_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

def log_alignment_results(results):
    """Log alignment results to TRACE_LOG"""
    log_entry = f"""
## SYNCHRONIZATION_GLYPH + COGNITION_ALIGNMENT_GLYPH Event: {results['timestamp']}

**Summary:**
- Asynchronous Proximities Detected: {results['summary']['total_proximities']}
- Latent Alignments Identified: {results['summary']['total_alignments']}
- Cross-Domain Patterns Found: {results['summary']['total_patterns']}
- Cognition Clusters Created: {results['summary']['total_clusters']}

### Cognition Clusters:
"""
    
    for cluster in results['cognition_clusters']:
        log_entry += f"- {cluster['cluster_type']}: {cluster['size']} members (status: {cluster['status']})\n"
    
    log_entry += "\n### Status:\nAsynchronous proximities aligned and synchronized into cognition clusters.\n\n---\n"
    
    with open(TRACE_LOG_PATH, 'a') as f:
        f.write(log_entry)

def run_proximity_alignment():
    """Main proximity alignment process"""
    print("[PROXIMITY_ALIGNER] Starting asynchronous proximity alignment...")
    
    # Load manifest
    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)
    
    if manifest.get('asynchronous_alignment') != 'enabled':
        print("[PROXIMITY_ALIGNER] Asynchronous alignment not enabled in manifest")
        return
    
    # Load temporal data
    print("[PROXIMITY_ALIGNER] Loading temporal data...")
    temporal_data = load_temporal_data()
    print(f"[PROXIMITY_ALIGNER] Loaded {len(temporal_data)} temporal data points")
    
    # Detect asynchronous proximities
    print("[PROXIMITY_ALIGNER] Detecting asynchronous proximities...")
    proximities = detect_asynchronous_proximities(temporal_data)
    print(f"[PROXIMITY_ALIGNER] Found {len(proximities)} asynchronous proximities")
    
    # Identify latent alignments
    print("[PROXIMITY_ALIGNER] Identifying latent alignments...")
    alignments = identify_latent_alignments()
    print(f"[PROXIMITY_ALIGNER] Found {len(alignments)} latent alignments")
    
    # Detect cross-domain patterns
    print("[PROXIMITY_ALIGNER] Detecting cross-domain patterns...")
    patterns = detect_cross_domain_patterns()
    print(f"[PROXIMITY_ALIGNER] Found {len(patterns)} cross-domain patterns")
    
    # Create cognition clusters
    print("[PROXIMITY_ALIGNER] Creating cognition clusters...")
    clusters = create_cognition_clusters(proximities, alignments, patterns)
    print(f"[PROXIMITY_ALIGNER] Created {len(clusters)} cognition clusters")
    
    # Save results
    results = save_alignment_results(proximities, alignments, patterns, clusters)
    
    # Log to TRACE_LOG
    log_alignment_results(results)
    
    # Emit glyphs
    register_glyph_emission(
        "SYNCHRONIZATION_GLYPH",
        "node_async_proximity_aligner",
        {
            "asynchronous_proximities": len(proximities),
            "cognition_clusters": len(clusters)
        }
    )
    print("[PROXIMITY_ALIGNER] ✓ SYNCHRONIZATION_GLYPH emitted")
    
    register_glyph_emission(
        "COGNITION_ALIGNMENT_GLYPH",
        "node_async_proximity_aligner",
        {
            "latent_alignments": len(alignments),
            "cross_domain_patterns": len(patterns)
        }
    )
    print("[PROXIMITY_ALIGNER] ✓ COGNITION_ALIGNMENT_GLYPH emitted")
    
    print("[PROXIMITY_ALIGNER] Proximity alignment complete")

if __name__ == "__main__":
    run_proximity_alignment()
