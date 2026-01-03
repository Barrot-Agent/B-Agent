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
    for node in MATRIX_PATH.glob("node_*.py"):
        print(f"  → Running {node.name}")
        subprocess.run(["python", str(node)], check=False)

# --- RUN COGNITION FUSION ---
def run_cognition_fusion():
    print("\n[BOOTSTRAP] Checking cognition fusion status...")
    
    # Check if cognition fusion is enabled
    fusion_enabled = manifest.get("cognition_fusion", {}).get("cognition_fusion_active", False)
    
    if fusion_enabled:
        print("[BOOTSTRAP] Cognition fusion is ACTIVE")
        print("[BOOTSTRAP] Executing cognition fusion protocol...")
        fusion_script = MATRIX_PATH / "cognition_fusion.py"
        if fusion_script.exists():
            subprocess.run(["python", str(fusion_script)], check=False)
        else:
            print("[BOOTSTRAP] Warning: cognition_fusion.py not found")
    else:
        print("[BOOTSTRAP] Cognition fusion is not active")

run_matrix()
run_cognition_fusion()