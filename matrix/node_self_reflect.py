#!/usr/bin/env python3
"""
Node: Self-Reflection
Reads the last 3 cognition runs, detects drift, and emits SELF_ALIGNMENT_GLYPH.
Suggests MANIFEST_PATCH.md if misalignment is found.
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
TRACE_LOG_PATH = REPO_ROOT / "memory-bundles" / "TRACE_LOG.md"
GLYPHS_PATH = REPO_ROOT / "glyphs"
MANIFEST_PATH = REPO_ROOT / "barrot_manifest.json"

def read_last_cognition_runs(count=3):
    """Read the last N cognition runs from TRACE_LOG.md"""
    if not TRACE_LOG_PATH.exists():
        return []
    
    with open(TRACE_LOG_PATH, 'r') as f:
        content = f.read()
    
    # Parse log entries (simple parsing)
    runs = []
    entries = content.split("## Run:")
    for entry in entries[-count:]:
        if entry.strip():
            runs.append(entry.strip())
    
    return runs

def detect_drift(runs):
    """Analyze cognition runs for drift patterns"""
    if len(runs) < 2:
        return False, "Insufficient data for drift analysis"
    
    # Simple drift detection: check for inconsistencies in node execution
    nodes_per_run = []
    for run in runs:
        # Extract nodes from run (simplified)
        if "Nodes Executed:" in run:
            nodes_line = [line for line in run.split('\n') if "Nodes Executed:" in line]
            if nodes_line:
                nodes_per_run.append(nodes_line[0])
    
    # Check for variations
    if len(set(nodes_per_run)) > 1:
        return True, "Node execution pattern drift detected"
    
    return False, "No drift detected"

def emit_glyph(glyph_name, reason):
    """Emit a glyph to the glyphs directory"""
    glyph_file = GLYPHS_PATH / f"{glyph_name.lower()}.yml"
    
    glyph_content = f"""glyph_name: {glyph_name}
glyph_id: SELF-001
version: 1.0.0
timestamp: {datetime.utcnow().isoformat()}Z

description: >
  Emitted when self-reflection detects drift or misalignment in cognition patterns.
  Indicates need for system recalibration or manifest adjustment.

symbolic_representation: "◎ ⟲ ✓"

properties:
  dimension: meta_cognitive
  mutability: corrective
  trigger: drift_detection
  
attributes:
  - self_awareness
  - pattern_recognition
  - alignment_verification
  - corrective_action
  
emission_context: >
  {reason}

integration_points:
  - cognition_monitoring
  - manifest_integrity
  - trace_reconciliation
  
usage_context: >
  Invoke when self-reflection analysis detects drift in cognition patterns
  or misalignment with symbolic intent.
"""
    
    with open(glyph_file, 'w') as f:
        f.write(glyph_content)
    
    print(f"[SELF_REFLECT] Emitted glyph: {glyph_name} -> {glyph_file}")

def suggest_manifest_patch():
    """Create a MANIFEST_PATCH.md if misalignment is detected"""
    patch_path = REPO_ROOT / "MANIFEST_PATCH.md"
    
    patch_content = f"""# Manifest Patch Suggestion
**Generated:** {datetime.utcnow().isoformat()}Z
**Reason:** Self-reflection detected misalignment

## Suggested Changes

1. **Update cognition integrity check frequency**
   - Current: Daily
   - Suggested: Hourly

2. **Add drift tolerance threshold**
   ```json
   "symbolic_alignment": {{
     "drift_tolerance": 0.05,
     "auto_correct": true
   }}
   ```

3. **Enable continuous trace reconciliation**
   - Monitor node execution patterns in real-time
   - Auto-emit alignment glyphs when needed

## Implementation Priority
- High: Drift tolerance threshold
- Medium: Integrity check frequency
- Low: Continuous trace reconciliation

## Review Required
Please review and integrate these suggestions into barrot_manifest.json
"""
    
    with open(patch_path, 'w') as f:
        f.write(patch_content)
    
    print(f"[SELF_REFLECT] Created MANIFEST_PATCH.md at {patch_path}")

def main():
    print("[SELF_REFLECT] Starting self-reflection analysis...")
    
    # Read last cognition runs
    runs = read_last_cognition_runs(3)
    print(f"[SELF_REFLECT] Analyzed {len(runs)} cognition runs")
    
    # Detect drift
    has_drift, reason = detect_drift(runs)
    
    if has_drift:
        print(f"[SELF_REFLECT] Drift detected: {reason}")
        emit_glyph("SELF_ALIGNMENT_GLYPH", reason)
        suggest_manifest_patch()
    else:
        print(f"[SELF_REFLECT] System aligned: {reason}")
    
    # Update manifest with last reflection timestamp
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest = json.load(f)
        
        if "symbolic_alignment" not in manifest:
            manifest["symbolic_alignment"] = {}
        
        manifest["symbolic_alignment"]["last_self_reflection"] = datetime.utcnow().isoformat()
        manifest["symbolic_alignment"]["drift_detected"] = has_drift
        
        with open(MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"[SELF_REFLECT] Updated manifest with reflection results")

if __name__ == "__main__":
    main()
