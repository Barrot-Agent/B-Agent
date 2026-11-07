#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
fi

for command_name in git gh make; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Required command is missing: $command_name" >&2
    exit 1
  fi
done

python - <<'PY'
import importlib.util
import sys

if sys.version_info[:2] != (3, 11):
    raise SystemExit(f"Barrot Codespaces requires Python 3.11; found {sys.version.split()[0]}")
required = ("pytest", "pydantic", "pydantic_settings", "requests", "jwt", "cryptography")
missing = [name for name in required if importlib.util.find_spec(name) is None]
if missing:
    raise SystemExit("Missing core modules: " + ", ".join(missing))
PY

git --version
gh --version
make --version
python -m pip check
echo "Barrot Codespaces health check passed."
