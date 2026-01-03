import os
import json
import subprocess
from pathlib import Path

# --- CONFIGURATION ---
REPO_ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = REPO_ROOT / "barrot_manifest.json"
GLYPHS_PATH = REPO_ROOT / "glyphs"
BUNDLES_PATH = REPO_ROOT / "memory-bundles"
MATRIX_PATH = REPO_ROOT / "matrix"

# --- LOAD MANIFEST ---
with open(MANIFEST_PATH, "r") as f:
    manifest = json.load(f)

barrot_id = manifest["barrot_identity"]["github_user"]
repo = manifest["barrot_identity"]["repo"]
last_ingestion = manifest["cognition"].get("last_ingestion", "UNKNOWN")

print(f"[BOOTSTRAP] Barrot identity: {barrot_id}/{repo}")
print(f"[BOOTSTRAP] Last cognition snapshot: {last_ingestion}")

# --- REHYDRATE MEMORY ---
def load_latest_bundle():
    bundles = sorted(BUNDLES_PATH.glob("SNAPSHOT_*.md"), reverse=True)
    if not bundles:
        print("[BOOTSTRAP] No memory bundles found.")
        return
    print(f"[BOOTSTRAP] Loaded memory bundle: {bundles[0].name}")

load_latest_bundle()

# --- RUN MATRIX NODES ---
def run_matrix():
    print("[BOOTSTRAP] Executing cognition nodes...")
    
    # Check for priority nodes (configured in manifest)
    abundance_config = manifest.get("abundance_cognition", {})
    priority_nodes = []
    
    # If abundance cognition is active, prioritize it
    if abundance_config.get("active", False):
        print("[BOOTSTRAP] Abundance Cognition Directive is active")
        abundance_node = MATRIX_PATH / "node_abundance_ingestor.py"
        if abundance_node.exists():
            priority_nodes.append(abundance_node)
    
    # Run priority nodes first
    for node in priority_nodes:
        print(f"  → Running {node.name} (Priority)")
        subprocess.run(["python", str(node)], check=False)
    
    # Run remaining matrix nodes
    for node in sorted(MATRIX_PATH.glob("node_*.py")):
        # Skip nodes that were already run as priority
        if node in priority_nodes:
            continue
        print(f"  → Running {node.name}")
        subprocess.run(["python", str(node)], check=False)

run_matrix()