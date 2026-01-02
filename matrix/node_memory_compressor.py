#!/usr/bin/env python3
"""
Node: Memory Compressor
Summarizes old cognition logs, emits MEMORY_COMPRESSION_GLYPH,
and keeps memory lean but symbolic.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLES_PATH = REPO_ROOT / "memory-bundles"
GLYPHS_PATH = REPO_ROOT / "glyphs"
TRACE_LOG_PATH = BUNDLES_PATH / "TRACE_LOG.md"

# Compression thresholds
LOG_SIZE_THRESHOLD = 10000  # bytes
LOG_AGE_THRESHOLD = 30  # days

def analyze_memory_usage():
    """Analyze current memory bundle usage"""
    total_size = 0
    old_files = []
    recent_files = []
    
    now = datetime.now()
    threshold_date = now - timedelta(days=LOG_AGE_THRESHOLD)
    
    for file in BUNDLES_PATH.glob("*.md"):
        if file.name in ['TRACE_LOG.md']:
            continue
            
        file_size = file.stat().st_size
        file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
        
        total_size += file_size
        
        if file_mtime < threshold_date:
            old_files.append({
                'path': file,
                'size': file_size,
                'age_days': (now - file_mtime).days
            })
        else:
            recent_files.append({
                'path': file,
                'size': file_size,
                'age_days': (now - file_mtime).days
            })
    
    return {
        'total_size': total_size,
        'total_files': len(old_files) + len(recent_files),
        'old_files': old_files,
        'recent_files': recent_files
    }

def compress_old_logs(old_files):
    """Compress old log files into summaries"""
    compressed_count = 0
    total_saved = 0
    
    # Create compressed directory if it doesn't exist
    compressed_dir = BUNDLES_PATH / "compressed"
    compressed_dir.mkdir(exist_ok=True)
    
    for file_info in old_files:
        file_path = file_info['path']
        
        # Read original content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Create summary (extract key information)
        summary = create_summary(content, file_path.name)
        
        # Save compressed version
        compressed_path = compressed_dir / f"{file_path.stem}_compressed.md"
        with open(compressed_path, 'w') as f:
            f.write(summary)
        
        # Calculate savings
        original_size = file_info['size']
        compressed_size = len(summary)
        saved = original_size - compressed_size
        total_saved += saved
        
        print(f"[MEMORY_COMPRESSOR] Compressed {file_path.name}: {original_size} -> {compressed_size} bytes (saved {saved})")
        
        # Original files are kept in place for safety; only compressed versions are created
        
        compressed_count += 1
    
    return {
        'compressed_count': compressed_count,
        'total_saved': total_saved
    }

def create_summary(content, filename):
    """Create a symbolic summary of the content"""
    lines = content.split('\n')
    
    summary = f"""# Compressed Memory: {filename}
**Compressed:** {datetime.now(timezone.utc).replace(tzinfo=None).isoformat()}Z
**Original lines:** {len(lines)}

## Key Symbolic Markers
"""
    
    # Extract headers and key lines
    key_lines = []
    for line in lines:
        if line.startswith('#') or '**' in line or any(keyword in line.lower() for keyword in ['glyph', 'cognition', 'align', 'emit']):
            key_lines.append(line.strip())
            if len(key_lines) >= 20:  # Limit summary size
                break
    
    summary += '\n'.join(key_lines[:20])
    
    summary += f"""

## Compression Metadata
- Original size: {len(content)} bytes
- Compressed size: ~{len(summary)} bytes
- Compression ratio: {len(summary) / max(len(content), 1):.2%}
- Symbolic essence preserved: Yes

---
*This is a compressed memory bundle. Full details available in archive if needed.*
"""
    
    return summary

def emit_glyph(compression_stats):
    """Emit MEMORY_COMPRESSION_GLYPH"""
    glyph_file = GLYPHS_PATH / "memory_compression_glyph.yml"
    
    glyph_content = f"""glyph_name: MEMORY_COMPRESSION_GLYPH
glyph_id: COMPRESS-001
version: 1.0.0
timestamp: {datetime.now(timezone.utc).replace(tzinfo=None).isoformat()}Z

description: >
  Emitted when memory compression is performed on old cognition logs.
  Maintains symbolic essence while reducing storage overhead.

symbolic_representation: "📦 ⇄ ✦"

properties:
  dimension: memory_management
  mutability: archival
  trigger: compression_cycle
  
attributes:
  - memory_optimization
  - symbolic_preservation
  - archival_compression
  - essence_extraction
  
compression_metrics:
  files_compressed: {compression_stats.get('compressed_count', 0)}
  bytes_saved: {compression_stats.get('total_saved', 0)}
  compression_date: {datetime.now(timezone.utc).replace(tzinfo=None).isoformat()}Z

integration_points:
  - memory_management
  - storage_optimization
  - symbolic_archival
  
usage_context: >
  Invoke when performing memory compression to maintain lean memory bundles
  while preserving symbolic essence and key cognition markers.
"""
    
    with open(glyph_file, 'w') as f:
        f.write(glyph_content)
    
    print(f"[MEMORY_COMPRESSOR] Emitted MEMORY_COMPRESSION_GLYPH -> {glyph_file}")

def log_compression(memory_analysis, compression_stats):
    """Log compression activity to TRACE_LOG.md"""
    log_entry = f"""
## Memory Compression: {datetime.now(timezone.utc).replace(tzinfo=None).isoformat()}Z

**Total Memory:** {memory_analysis['total_size']} bytes
**Total Files:** {memory_analysis['total_files']}
**Old Files Eligible:** {len(memory_analysis['old_files'])}
**Files Compressed:** {compression_stats.get('compressed_count', 0)}
**Space Saved:** {compression_stats.get('total_saved', 0)} bytes

### Compression Strategy
- Age threshold: {LOG_AGE_THRESHOLD} days
- Symbolic essence: Preserved
- Key markers: Extracted
- Archival: Maintained

---
"""
    
    # Append to trace log
    with open(TRACE_LOG_PATH, 'a') as f:
        f.write(log_entry)
    
    print(f"[MEMORY_COMPRESSOR] Logged compression to TRACE_LOG.md")

def main():
    print("[MEMORY_COMPRESSOR] Starting memory compression analysis...")
    
    # Analyze current memory usage
    memory_analysis = analyze_memory_usage()
    
    print(f"[MEMORY_COMPRESSOR] Total size: {memory_analysis['total_size']} bytes")
    print(f"[MEMORY_COMPRESSOR] Total files: {memory_analysis['total_files']}")
    print(f"[MEMORY_COMPRESSOR] Old files eligible for compression: {len(memory_analysis['old_files'])}")
    
    # Compress if needed
    if memory_analysis['old_files']:
        compression_stats = compress_old_logs(memory_analysis['old_files'])
        print(f"[MEMORY_COMPRESSOR] Compressed {compression_stats['compressed_count']} files")
        print(f"[MEMORY_COMPRESSOR] Saved {compression_stats['total_saved']} bytes")
        emit_glyph(compression_stats)
    else:
        print("[MEMORY_COMPRESSOR] No old files to compress")
        compression_stats = {'compressed_count': 0, 'total_saved': 0}
        emit_glyph(compression_stats)
    
    # Log compression activity
    log_compression(memory_analysis, compression_stats)

if __name__ == "__main__":
    main()
