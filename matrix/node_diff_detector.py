#!/usr/bin/env python3
"""
Node: Diff Detector
Compares the last two cognition snapshots and emits COGNITION_SHIFT_GLYPH
if beliefs or tools have changed.
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLES_PATH = REPO_ROOT / "memory-bundles"
GLYPHS_PATH = REPO_ROOT / "glyphs"
MANIFEST_PATH = REPO_ROOT / "barrot_manifest.json"

def get_latest_snapshots(count=2):
    """Get the last N cognition snapshots"""
    snapshots = sorted(BUNDLES_PATH.glob("SNAPSHOT_*.md"), reverse=True)
    return list(snapshots[:count])

def parse_snapshot(snapshot_path):
    """Parse a snapshot file and extract key information"""
    if not snapshot_path.exists():
        return {}
    
    with open(snapshot_path, 'r') as f:
        content = f.read()
    
    # Extract beliefs and tools (simplified parsing)
    data = {
        'beliefs': [],
        'tools': [],
        'timestamp': snapshot_path.stem.replace('SNAPSHOT_', ''),
        'content_hash': hash(content)
    }
    
    # Parse sections
    if "## Beliefs" in content:
        beliefs_section = content.split("## Beliefs")[1].split("##")[0]
        data['beliefs'] = [line.strip() for line in beliefs_section.split('\n') if line.strip().startswith('-')]
    
    if "## Tools" in content:
        tools_section = content.split("## Tools")[1].split("##")[0]
        data['tools'] = [line.strip() for line in tools_section.split('\n') if line.strip().startswith('-')]
    
    return data

def compare_snapshots(snapshot1, snapshot2):
    """Compare two snapshots and detect changes"""
    changes = {
        'beliefs_added': [],
        'beliefs_removed': [],
        'tools_added': [],
        'tools_removed': [],
        'has_changes': False
    }
    
    if not snapshot1 or not snapshot2:
        return changes
    
    # Compare beliefs
    beliefs1_set = set(snapshot1.get('beliefs', []))
    beliefs2_set = set(snapshot2.get('beliefs', []))
    changes['beliefs_added'] = list(beliefs2_set - beliefs1_set)
    changes['beliefs_removed'] = list(beliefs1_set - beliefs2_set)
    
    # Compare tools
    tools1_set = set(snapshot1.get('tools', []))
    tools2_set = set(snapshot2.get('tools', []))
    changes['tools_added'] = list(tools2_set - tools1_set)
    changes['tools_removed'] = list(tools1_set - tools2_set)
    
    # Determine if there are significant changes
    changes['has_changes'] = (
        len(changes['beliefs_added']) > 0 or
        len(changes['beliefs_removed']) > 0 or
        len(changes['tools_added']) > 0 or
        len(changes['tools_removed']) > 0
    )
    
    return changes

def emit_glyph(changes):
    """Emit COGNITION_SHIFT_GLYPH when changes detected"""
    glyph_file = GLYPHS_PATH / "cognition_shift_glyph.yml"
    
    change_summary = []
    if changes['beliefs_added']:
        change_summary.append(f"Beliefs added: {len(changes['beliefs_added'])}")
    if changes['beliefs_removed']:
        change_summary.append(f"Beliefs removed: {len(changes['beliefs_removed'])}")
    if changes['tools_added']:
        change_summary.append(f"Tools added: {len(changes['tools_added'])}")
    if changes['tools_removed']:
        change_summary.append(f"Tools removed: {len(changes['tools_removed'])}")
    
    glyph_content = f"""glyph_name: COGNITION_SHIFT_GLYPH
glyph_id: SHIFT-001
version: 1.0.0
timestamp: {datetime.utcnow().isoformat()}Z

description: >
  Emitted when cognition snapshots show significant changes in beliefs or tools.
  Indicates evolution or adaptation in the system's understanding and capabilities.

symbolic_representation: "↻ ⚡ △"

properties:
  dimension: cognitive_evolution
  mutability: adaptive
  trigger: snapshot_comparison
  
attributes:
  - belief_tracking
  - tool_evolution
  - capability_adaptation
  - cognitive_plasticity
  
changes_detected:
{chr(10).join([f"  - {change}" for change in change_summary])}

integration_points:
  - cognition_monitoring
  - snapshot_comparison
  - evolution_tracking
  
usage_context: >
  Invoke when comparing cognition snapshots reveals changes in beliefs,
  tools, or capabilities that indicate system evolution or adaptation.
"""
    
    with open(glyph_file, 'w') as f:
        f.write(glyph_content)
    
    print(f"[DIFF_DETECTOR] Emitted COGNITION_SHIFT_GLYPH -> {glyph_file}")

def log_changes(changes):
    """Log detected changes to TRACE_LOG.md"""
    trace_log = BUNDLES_PATH / "TRACE_LOG.md"
    
    log_entry = f"""
## Diff Detection: {datetime.utcnow().isoformat()}Z

**Changes Detected:** {"Yes" if changes['has_changes'] else "No"}

### Beliefs
- Added: {len(changes['beliefs_added'])}
- Removed: {len(changes['beliefs_removed'])}

### Tools
- Added: {len(changes['tools_added'])}
- Removed: {len(changes['tools_removed'])}

---
"""
    
    # Append to trace log
    with open(trace_log, 'a') as f:
        f.write(log_entry)
    
    print(f"[DIFF_DETECTOR] Logged changes to TRACE_LOG.md")

def main():
    print("[DIFF_DETECTOR] Starting snapshot comparison...")
    
    # Get latest snapshots
    snapshots = get_latest_snapshots(2)
    
    if len(snapshots) < 2:
        print("[DIFF_DETECTOR] Insufficient snapshots for comparison")
        return
    
    print(f"[DIFF_DETECTOR] Comparing: {snapshots[1].name} vs {snapshots[0].name}")
    
    # Parse snapshots
    snapshot1_data = parse_snapshot(snapshots[1])
    snapshot2_data = parse_snapshot(snapshots[0])
    
    # Compare
    changes = compare_snapshots(snapshot1_data, snapshot2_data)
    
    # Report findings
    if changes['has_changes']:
        print(f"[DIFF_DETECTOR] Changes detected!")
        print(f"  - Beliefs: +{len(changes['beliefs_added'])} -{len(changes['beliefs_removed'])}")
        print(f"  - Tools: +{len(changes['tools_added'])} -{len(changes['tools_removed'])}")
        emit_glyph(changes)
        log_changes(changes)
    else:
        print("[DIFF_DETECTOR] No significant changes detected")
        log_changes(changes)

if __name__ == "__main__":
    main()
