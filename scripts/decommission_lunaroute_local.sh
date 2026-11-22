#!/usr/bin/env bash
# Remove LunaRoute credentials and startup configuration from this user's Termux/Debian home.
# Safe to run with: source scripts/decommission_lunaroute_local.sh
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import re

home = Path.home()
profiles = [home / ".bashrc", home / ".zshrc", home / ".profile"]
patterns = re.compile(r"lunaroute|LUNAROUTE_API_KEY|LUNAROUTE_MODEL", re.IGNORECASE)

for path in profiles:
    if not path.is_file():
        continue
    original = path.read_text(encoding="utf-8")
    kept = [line for line in original.splitlines(keepends=True) if not patterns.search(line)]
    updated = "".join(kept)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        print(f"Cleaned {path}")

key_file = home / ".lunaroute_key"
if key_file.exists() and key_file.is_file():
    key_file.unlink()
    print(f"Deleted {key_file}")

print("LunaRoute shell-profile and local key-file cleanup complete.")
PY

unset LUNAROUTE_API_KEY LUNAROUTE_MODEL
