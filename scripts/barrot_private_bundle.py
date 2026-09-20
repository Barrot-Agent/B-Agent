#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import tarfile

ROOT = Path.cwd()
OUT = ROOT / ".barrot" / "private_bundles"
OUT.mkdir(parents=True, exist_ok=True)

stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
bundle = OUT / f"barrot_private_bundle_{stamp}.tar.gz"
manifest = OUT / f"barrot_private_bundle_{stamp}.json"

EXCLUDE = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}

def excluded(path: Path) -> bool:
    return any(part in EXCLUDE for part in path.parts)

files = []
for p in ROOT.rglob("*"):
    if p.is_file() and not excluded(p):
        rel = p.relative_to(ROOT)
        # Never package credentials/secrets.
        name = str(rel).lower()
        if any(x in name for x in (
            ".env", ".pem", ".key", "credentials", "secret"
        )):
            continue
        files.append(rel)

with tarfile.open(bundle, "w:gz") as tar:
    for rel in sorted(files):
        tar.add(ROOT / rel, arcname=str(rel))

sha256 = hashlib.sha256(bundle.read_bytes()).hexdigest()

data = {
    "bundle": bundle.name,
    "created_utc": stamp,
    "repository": str(ROOT),
    "file_count": len(files),
    "sha256": sha256,
    "purpose": "Barrot private self-drop bundle",
    "secrets_excluded": True,
}

manifest.write_text(json.dumps(data, indent=2) + "\n")

print(f"BUNDLE={bundle}")
print(f"MANIFEST={manifest}")
print(f"FILES={len(files)}")
print(f"SHA256={sha256}")
