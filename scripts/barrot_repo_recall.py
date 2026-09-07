#!/usr/bin/env python3
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ping-pongings" / "knowledge-base" / "barrot_repo_memory.json"

IGNORE = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".cache",
    ".apex_lattice",
    "coverage",
    ".pytest_cache",
    ".mypy_cache"
}
TEXT_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yaml", ".yml", ".md", ".txt", ".sh", ".toml", ".html", ".css", ".sql"}
MAX_SIZE = 1000000

def git(*args):
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None

def main():
    files = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        rel = path.relative_to(ROOT)

        if any(part in IGNORE for part in rel.parts):
            continue

        try:
            raw = path.read_bytes()
        except Exception:
            continue

        item = {
            "path": str(rel),
            "size": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()
        }

        if path.suffix.lower() in TEXT_EXT and len(raw) <= MAX_SIZE:
            text = raw.decode("utf-8", errors="replace")
            lines = text.splitlines()
            item["lines"] = len(lines)
            item["preview"] = "\n".join(lines[:100])

        files.append(item)

    memory = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": {
            "root": str(ROOT),
            "branch": git("branch", "--show-current"),
            "commit": git("rev-parse", "HEAD"),
            "remote": git("remote", "get-url", "origin")
        },
        "statistics": {
            "files_indexed": len(files)
        },
        "files": sorted(files, key=lambda x: x["path"])
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(memory, indent=2), encoding="utf-8")

    print("BARROT REPOSITORY RECALL COMPLETE")
    print("Indexed files:", len(files))
    print("Memory:", OUT)

if __name__ == "__main__":
    main()
