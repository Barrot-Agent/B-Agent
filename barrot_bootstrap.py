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
    
    # Priority nodes to run first (in order)
    priority_nodes = [
        "node_micro_ingest.py",      # Ingest repository content first
        "node_global_crawler.py",     # Then crawl external sources
        "node_self_reflect.py",       # Self-reflection
        "node_session_ingestor.py",   # Ingest session data
        "node_memory_compressor.py",  # Compress old memory
        "node_diff_detector.py"       # Detect changes
    ]
    
    # Run priority nodes first
    for node_name in priority_nodes:
        node_path = MATRIX_PATH / node_name
        if node_path.exists():
            print(f"  → Running {node_name}")
            subprocess.run(["python", str(node_path)], check=False)
    
    # Run any remaining nodes not in priority list
    for node in MATRIX_PATH.glob("node_*.py"):
        if node.name not in priority_nodes:
            print(f"  → Running {node.name}")
            subprocess.run(["python", str(node)], check=False)

run_matrix()