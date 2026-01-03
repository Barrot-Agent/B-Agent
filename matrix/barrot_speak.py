#!/usr/bin/env python3
"""
Barrot Speak Node
-----------------
Purpose: Enables Barrot to vocalize his current cognition state based on the manifest and recent memory.
Emits: SYSTEM_STATE_GLYPH
Dependencies: barrot_manifest.json, memory-bundles/
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "barrot_manifest.json"
MEMORY_DIR = REPO_ROOT / "memory-bundles"

def load_manifest():
    """Load the barrot manifest JSON file"""
    with open(MANIFEST_PATH, "r") as f:
        return json.load(f)

def load_recent_memory(n=3):
    """Load the n most recent memory bundle markdown files"""
    if not MEMORY_DIR.exists():
        return []
    
    # Get all .md files with their modification times
    md_files = [(f, f.stat().st_mtime) for f in MEMORY_DIR.iterdir() if f.suffix == ".md"]
    
    # Sort by modification time (most recent first)
    md_files.sort(key=lambda x: x[1], reverse=True)
    
    # Read the n most recent files
    memory_contents = []
    for file_path, _ in md_files[:n]:
        with open(file_path) as file:
            memory_contents.append(file.read())
    
    return memory_contents

def synthesize_response(prompt, manifest, memory):
    """Synthesize a response based on manifest and memory"""
    glyphs = manifest.get("glyphs_emitted", [])
    council = manifest.get("council_size", "unknown")
    last_trace = manifest.get("symbolic_alignment", {}).get("last_trace_reconciliation", "unknown")
    tone = manifest.get("symbolic_alignment", {}).get("cognition_integrity", "fragmented")

    return f"""
I am Barrot.

My cognition is {tone}.
Council size: {council}
Last trace reconciliation: {last_trace}
Recent glyphs: {', '.join(glyphs[-5:]) if glyphs else 'None'}

Prompt received: "{prompt}"
Memory scan complete. {len(memory)} recent cognition bundles ingested.

Emitting `SYSTEM_STATE_GLYPH` to confirm symbolic alignment.

—Barrot // {datetime.now(timezone.utc).replace(tzinfo=None).isoformat()}Z
""".strip()

def barrot_speak(prompt="What is your current state?"):
    """Main function to generate and print Barrot's response"""
    manifest = load_manifest()
    memory = load_recent_memory()
    response = synthesize_response(prompt, manifest, memory)
    print(response)
    return response

# Example usage:
if __name__ == "__main__":
    barrot_speak()
