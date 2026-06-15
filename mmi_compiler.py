#!/usr/bin/env python3
# ==============================================================================
# BARROT-Ω MMI COMPILER [GLOBAL STATE UNIFIER]
# Architect: Sean | Node: Brooklyn Core
# Objective: Recursive Compression of Fragmented Builds into a Global Manifest
# ==============================================================================

import os
import logging

# Configuration
MANIFEST_PATH = "GLOBAL_STATE_MANIFEST.md"
TARGET_DIRS = ["barrot_agent", "apex_lattice", "character-capabilities", "experimental_nodes"]
IGNORE_EXTS = {'.pyc', '.git', '.next', 'node_modules'}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [MMI COMPILER] - %(message)s')
logger = logging.getLogger(__name__)

def compile_manifest():
    logger.info("Initiating MMI Ingestion Protocol...")
    
    with open(MANIFEST_PATH, "w") as manifest:
        manifest.write("# GLOBAL STATE MANIFEST [UNIFIED]\n")
        manifest.write(f"**Date:** 2026-06-15 | **Architect:** Sean\n\n")
        
        for root, dirs, files in os.walk("."):
            # Filter directories
            dirs[:] = [d for d in dirs if not any(ignore in d for ignore in IGNORE_EXTS)]
            
            for file in files:
                if any(file.endswith(ext) for ext in IGNORE_EXTS):
                    continue
                
                file_path = os.path.join(root, file)
                manifest.write(f"## Module: {file_path}\n")
                
                try:
                    with open(file_path, "r", errors='ignore') as f:
                        content = f.read(500) # Extract core logic snippet
                        manifest.write(f"```\n{content}...\n```\n\n")
                except Exception as e:
                    manifest.write(f"Error ingesting: {e}\n\n")
                    
    logger.info(f"=== COMPILATION COMPLETE: {MANIFEST_PATH} ===")

if __name__ == "__main__":
    compile_manifest()
