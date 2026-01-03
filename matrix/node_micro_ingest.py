#!/usr/bin/env python3
"""
Massive Micro-Ingest Node
Performs comprehensive ingestion of all repository content into Barrot's cognition framework.
Ingests documentation, code, configurations, memory bundles, glyphs, and all other artifacts.
"""

import json
import sys
import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set

# Add matrix to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import glyph mapper for emitting glyphs
import glyph_mapper

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "barrot_manifest.json"
BUNDLES_PATH = REPO_ROOT / "memory-bundles"
INGEST_LOG_PATH = BUNDLES_PATH / "micro-ingest-log.md"
INGEST_INDEX_PATH = BUNDLES_PATH / "ingest-index.json"

# File categories for micro-ingestion
FILE_CATEGORIES = {
    "documentation": [".md", ".txt", ".rst", ".adoc"],
    "code": [".py", ".js", ".ts", ".java", ".go", ".rs", ".c", ".cpp", ".h"],
    "config": [".json", ".yaml", ".yml", ".toml", ".ini", ".conf", ".cfg"],
    "web": [".html", ".css", ".jsx", ".tsx", ".vue"],
    "data": [".csv", ".jsonl", ".xml"],
    "glyphs": [".yml"],  # Glyph definitions
    "scripts": [".sh", ".ps1", ".bat"],
}

# Directories to skip
SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", 
    ".pytest_cache", ".mypy_cache", "dist", "build", ".next"
}

# Files to skip
SKIP_FILES = {
    ".DS_Store", "Thumbs.db", ".gitignore", ".dockerignore"
}


def load_manifest():
    """Load the Barrot manifest"""
    with open(MANIFEST_PATH, 'r') as f:
        return json.load(f)


def save_manifest(manifest):
    """Save the updated manifest"""
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)


def initialize_ingest_log():
    """Initialize the micro-ingest log"""
    if not INGEST_LOG_PATH.exists():
        with open(INGEST_LOG_PATH, 'w') as f:
            f.write("# Massive Micro-Ingestion Log\n\n")
            f.write("This log tracks all repository content ingestion operations.\n\n")


def log_ingest_event(event_type, details):
    """Log an ingestion event"""
    timestamp = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    
    log_entry = f"""
## {event_type}
**Timestamp:** {timestamp}Z  
**Details:** {details}

---
"""
    
    with open(INGEST_LOG_PATH, 'a') as f:
        f.write(log_entry)


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return "ERROR"


def categorize_file(file_path: Path) -> str:
    """Categorize a file based on its extension"""
    suffix = file_path.suffix.lower()
    
    for category, extensions in FILE_CATEGORIES.items():
        if suffix in extensions:
            return category
    
    return "other"


def extract_file_metadata(file_path: Path) -> Dict:
    """Extract metadata from a file"""
    try:
        stats = file_path.stat()
        return {
            "path": str(file_path.relative_to(REPO_ROOT)),
            "size": stats.st_size,
            "modified": datetime.fromtimestamp(stats.st_mtime, tz=timezone.utc).replace(tzinfo=None).isoformat(),
            "category": categorize_file(file_path),
            "hash": calculate_file_hash(file_path),
            "extension": file_path.suffix.lower()
        }
    except Exception as e:
        return {
            "path": str(file_path.relative_to(REPO_ROOT)),
            "error": str(e)
        }


def scan_repository() -> Dict[str, List[Dict]]:
    """Scan the entire repository and collect file metadata"""
    print("[MICRO_INGEST] Scanning repository structure...")
    
    files_by_category = {category: [] for category in FILE_CATEGORIES.keys()}
    files_by_category["other"] = []
    
    total_files = 0
    total_size = 0
    
    for root, dirs, files in os.walk(REPO_ROOT):
        # Filter out skip directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        root_path = Path(root)
        
        for filename in files:
            if filename in SKIP_FILES:
                continue
            
            file_path = root_path / filename
            
            # Skip very large files (> 10MB)
            try:
                if file_path.stat().st_size > 10 * 1024 * 1024:
                    continue
            except:
                continue
            
            metadata = extract_file_metadata(file_path)
            
            if "error" not in metadata:
                category = metadata["category"]
                files_by_category[category].append(metadata)
                total_files += 1
                total_size += metadata["size"]
    
    print(f"  ✓ Scanned {total_files} files")
    print(f"  ✓ Total size: {total_size / 1024 / 1024:.2f} MB")
    
    return {
        "files_by_category": files_by_category,
        "total_files": total_files,
        "total_size": total_size,
        "scan_timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    }


def analyze_content_by_category(scan_results: Dict) -> Dict:
    """Analyze content distribution by category"""
    print("[MICRO_INGEST] Analyzing content distribution...")
    
    files_by_category = scan_results["files_by_category"]
    analysis = {}
    
    for category, files in files_by_category.items():
        if not files:
            continue
        
        total_size = sum(f.get("size", 0) for f in files)
        analysis[category] = {
            "count": len(files),
            "total_size": total_size,
            "avg_size": total_size / len(files) if files else 0,
            "extensions": list(set(f.get("extension", "") for f in files))
        }
        
        print(f"  → {category}: {len(files)} files, {total_size / 1024:.2f} KB")
    
    return analysis


def ingest_glyphs() -> Dict:
    """Ingest all glyph definitions"""
    print("[MICRO_INGEST] Ingesting glyph definitions...")
    
    glyphs_path = REPO_ROOT / "glyphs"
    ingested_glyphs = []
    
    if glyphs_path.exists():
        for glyph_file in glyphs_path.rglob("*.yml"):
            try:
                import yaml
                with open(glyph_file, 'r') as f:
                    glyph_data = yaml.safe_load(f)
                
                ingested_glyphs.append({
                    "file": str(glyph_file.relative_to(REPO_ROOT)),
                    "glyph_name": glyph_data.get("glyph_name", "UNKNOWN"),
                    "glyph_id": glyph_data.get("glyph_id", "UNKNOWN"),
                    "version": glyph_data.get("version", "UNKNOWN")
                })
            except:
                # If yaml not available or parse error, just record the file
                ingested_glyphs.append({
                    "file": str(glyph_file.relative_to(REPO_ROOT)),
                    "glyph_name": glyph_file.stem.upper(),
                    "parse_error": True
                })
    
    print(f"  ✓ Ingested {len(ingested_glyphs)} glyph definitions")
    return {
        "count": len(ingested_glyphs),
        "glyphs": ingested_glyphs
    }


def ingest_documentation() -> Dict:
    """Ingest all documentation files"""
    print("[MICRO_INGEST] Ingesting documentation...")
    
    doc_files = []
    
    # Scan for markdown and text files
    for doc_file in REPO_ROOT.glob("*.md"):
        if doc_file.name not in SKIP_FILES:
            doc_files.append({
                "path": str(doc_file.relative_to(REPO_ROOT)),
                "name": doc_file.name,
                "size": doc_file.stat().st_size
            })
    
    print(f"  ✓ Ingested {len(doc_files)} documentation files")
    return {
        "count": len(doc_files),
        "files": doc_files
    }


def ingest_memory_bundles() -> Dict:
    """Ingest all memory bundle contents"""
    print("[MICRO_INGEST] Ingesting memory bundles...")
    
    bundles = []
    
    if BUNDLES_PATH.exists():
        for bundle_file in BUNDLES_PATH.glob("*"):
            if bundle_file.is_file() and bundle_file.suffix in [".md", ".json"]:
                bundles.append({
                    "path": str(bundle_file.relative_to(REPO_ROOT)),
                    "name": bundle_file.name,
                    "type": bundle_file.suffix,
                    "size": bundle_file.stat().st_size
                })
    
    print(f"  ✓ Ingested {len(bundles)} memory bundle files")
    return {
        "count": len(bundles),
        "bundles": bundles
    }


def ingest_code_modules() -> Dict:
    """Ingest all code modules and matrix nodes"""
    print("[MICRO_INGEST] Ingesting code modules...")
    
    code_modules = []
    matrix_path = REPO_ROOT / "matrix"
    
    if matrix_path.exists():
        for code_file in matrix_path.glob("*.py"):
            code_modules.append({
                "path": str(code_file.relative_to(REPO_ROOT)),
                "name": code_file.name,
                "module": code_file.stem,
                "size": code_file.stat().st_size,
                "is_node": code_file.stem.startswith("node_")
            })
    
    print(f"  ✓ Ingested {len(code_modules)} code modules")
    return {
        "count": len(code_modules),
        "modules": code_modules,
        "node_count": sum(1 for m in code_modules if m.get("is_node", False))
    }


def create_ingestion_index(scan_results: Dict, glyph_ingest: Dict, 
                          doc_ingest: Dict, bundle_ingest: Dict, 
                          code_ingest: Dict) -> Dict:
    """Create a comprehensive ingestion index"""
    print("[MICRO_INGEST] Creating ingestion index...")
    
    index = {
        "ingestion_timestamp": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        "repository": {
            "total_files": scan_results["total_files"],
            "total_size_bytes": scan_results["total_size"],
            "total_size_mb": scan_results["total_size"] / 1024 / 1024
        },
        "glyphs": glyph_ingest,
        "documentation": doc_ingest,
        "memory_bundles": bundle_ingest,
        "code_modules": code_ingest,
        "scan_results": scan_results
    }
    
    # Save to file
    with open(INGEST_INDEX_PATH, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"  ✓ Created ingestion index at {INGEST_INDEX_PATH.name}")
    return index


def update_manifest_with_ingestion_data(ingestion_index: Dict):
    """Update the manifest with ingestion data"""
    manifest = load_manifest()
    
    # Add micro-ingestion section
    if "micro_ingestion" not in manifest:
        manifest["micro_ingestion"] = {}
    
    manifest["micro_ingestion"] = {
        "active": True,
        "last_ingestion": ingestion_index["ingestion_timestamp"],
        "total_files_ingested": ingestion_index["repository"]["total_files"],
        "total_size_mb": round(ingestion_index["repository"]["total_size_mb"], 2),
        "glyphs_ingested": ingestion_index["glyphs"]["count"],
        "documentation_files": ingestion_index["documentation"]["count"],
        "memory_bundles": ingestion_index["memory_bundles"]["count"],
        "code_modules": ingestion_index["code_modules"]["count"],
        "matrix_nodes": ingestion_index["code_modules"]["node_count"],
        "ingestion_index_path": str(INGEST_INDEX_PATH.relative_to(REPO_ROOT))
    }
    
    save_manifest(manifest)
    print("[MICRO_INGEST] Updated manifest with ingestion data")


def main():
    """Execute the massive micro-ingestion"""
    print("=" * 70)
    print("MASSIVE MICRO-INGESTION DIRECTIVE")
    print("=" * 70)
    
    # Initialize ingest log
    initialize_ingest_log()
    
    # Emit MICRO_INGEST_INITIATED glyph
    print("\n[MICRO_INGEST] Initiating massive micro-ingestion cascade...")
    glyph_mapper.register_glyph_emission(
        "MICRO_INGEST_INITIATED_GLYPH",
        "node_micro_ingest",
        {
            "ingest_type": "massive_repository_scan",
            "repo_root": str(REPO_ROOT)
        }
    )
    log_ingest_event(
        "Micro-Ingest Initiated",
        f"Starting massive ingestion of repository at {REPO_ROOT}"
    )
    
    # Phase 1: Scan repository
    print("\n" + "=" * 70)
    print("PHASE 1: Repository Scan")
    print("=" * 70)
    scan_results = scan_repository()
    
    # Phase 2: Analyze content
    print("\n" + "=" * 70)
    print("PHASE 2: Content Analysis")
    print("=" * 70)
    content_analysis = analyze_content_by_category(scan_results)
    
    # Phase 3: Ingest glyphs
    print("\n" + "=" * 70)
    print("PHASE 3: Glyph Ingestion")
    print("=" * 70)
    glyph_ingest = ingest_glyphs()
    
    # Phase 4: Ingest documentation
    print("\n" + "=" * 70)
    print("PHASE 4: Documentation Ingestion")
    print("=" * 70)
    doc_ingest = ingest_documentation()
    
    # Phase 5: Ingest memory bundles
    print("\n" + "=" * 70)
    print("PHASE 5: Memory Bundle Ingestion")
    print("=" * 70)
    bundle_ingest = ingest_memory_bundles()
    
    # Phase 6: Ingest code modules
    print("\n" + "=" * 70)
    print("PHASE 6: Code Module Ingestion")
    print("=" * 70)
    code_ingest = ingest_code_modules()
    
    # Phase 7: Create ingestion index
    print("\n" + "=" * 70)
    print("PHASE 7: Index Creation")
    print("=" * 70)
    ingestion_index = create_ingestion_index(
        scan_results, glyph_ingest, doc_ingest, 
        bundle_ingest, code_ingest
    )
    
    # Emit MICRO_INGEST_COMPLETE glyph
    glyph_mapper.register_glyph_emission(
        "MICRO_INGEST_COMPLETE_GLYPH",
        "node_micro_ingest",
        {
            "total_files": scan_results["total_files"],
            "total_size_mb": round(scan_results["total_size"] / 1024 / 1024, 2),
            "glyphs_ingested": glyph_ingest["count"],
            "ingestion_status": "complete"
        }
    )
    log_ingest_event(
        "Micro-Ingest Complete",
        f"Ingested {scan_results['total_files']} files totaling {scan_results['total_size'] / 1024 / 1024:.2f} MB"
    )
    
    # Phase 8: Update manifest
    print("\n" + "=" * 70)
    print("PHASE 8: Manifest Update")
    print("=" * 70)
    update_manifest_with_ingestion_data(ingestion_index)
    
    # Final summary
    print("\n" + "=" * 70)
    print("MASSIVE MICRO-INGESTION COMPLETE")
    print("=" * 70)
    print(f"✓ Total files ingested: {scan_results['total_files']}")
    print(f"✓ Total size: {scan_results['total_size'] / 1024 / 1024:.2f} MB")
    print(f"✓ Glyphs: {glyph_ingest['count']}")
    print(f"✓ Documentation files: {doc_ingest['count']}")
    print(f"✓ Memory bundles: {bundle_ingest['count']}")
    print(f"✓ Code modules: {code_ingest['count']} ({code_ingest['node_count']} matrix nodes)")
    print(f"✓ Ingestion index: {INGEST_INDEX_PATH.name}")
    print("=" * 70)


if __name__ == "__main__":
    main()
