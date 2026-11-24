#!/usr/bin/env bash
# Safely remove LunaRoute shell configuration from this user's Termux/Debian home.
#
# Preview (default):
#   source scripts/decommission_lunaroute_local.sh
#
# Apply profile cleanup (creates timestamped backups first):
#   source scripts/decommission_lunaroute_local.sh --apply
#
# Delete the local key file only as a separate, explicit action:
#   source scripts/decommission_lunaroute_local.sh --apply --delete-key
#
# This does not revoke or rotate credentials stored in GitHub, other services,
# password managers, or other devices.

set -euo pipefail

apply=0
delete_key=0
for arg in "$@"; do
  case "$arg" in
    --apply) apply=1 ;;
    --delete-key) delete_key=1 ;;
    *)
      printf 'Unknown option: %s\n' "$arg" >&2
      return 2 2>/dev/null || exit 2
      ;;
  esac
done

if [[ "$delete_key" == "1" && "$apply" != "1" ]]; then
  echo "Refusing key deletion without --apply." >&2
  return 2 2>/dev/null || exit 2
fi

BARROT_CLEANUP_APPLY="$apply" BARROT_CLEANUP_DELETE_KEY="$delete_key" python3 - <<'PY'
from datetime import datetime
from pathlib import Path
import os
import re
import shutil

home = Path.home()
profiles = [home / ".bashrc", home / ".zshrc", home / ".profile"]
pattern = re.compile(r"lunaroute|LUNAROUTE_API_KEY|LUNAROUTE_MODEL", re.IGNORECASE)
apply = os.environ.get("BARROT_CLEANUP_APPLY") == "1"
delete_key = os.environ.get("BARROT_CLEANUP_DELETE_KEY") == "1"

changes = []
for path in profiles:
    if not path.is_file():
        continue
    original = path.read_text(encoding="utf-8")
    updated = "".join(
        line for line in original.splitlines(keepends=True)
        if not pattern.search(line)
    )
    if updated != original:
        changes.append((path, original, updated))

key_file = home / ".lunaroute_key"
key_exists = key_file.is_file()

if not apply:
    print("PREVIEW ONLY — no files changed.")
    for path, _, _ in changes:
        print(f"Would clean shell profile: {path}")
    if key_exists:
        if delete_key:
            print(f"Would delete local key file: {key_file}")
        else:
            print(f"Local key file exists and will be preserved: {key_file}")
    print("To apply profile cleanup, source this script with --apply.")
    print("To also delete the local key file, add --delete-key explicitly.")
    raise SystemExit(0)

stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
for path, original, updated in changes:
    backup = path.with_name(path.name + f".barrot-backup-{stamp}")
    shutil.copy2(path, backup)
    path.write_text(updated, encoding="utf-8")
    print(f"Cleaned {path}; backup: {backup}")

if key_exists and delete_key:
    key_file.unlink()
    print(f"Deleted local key file: {key_file}")
elif key_exists:
    print(f"Preserved local key file: {key_file}")

print("Shell-profile cleanup applied.")
print("This did not revoke or rotate credentials stored elsewhere.")
PY

if [[ "$apply" == "1" ]]; then
  unset LUNAROUTE_API_KEY LUNAROUTE_MODEL
  echo "Unset LunaRoute variables in the current shell."
else
  echo "Current shell variables were not changed (preview mode)."
fi
