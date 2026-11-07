#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Preserve an existing workspace environment rather than replacing it.
if [[ -d .venv && ! -x .venv/bin/python ]]; then
  echo "Existing .venv is incomplete; not replacing it automatically." >&2
  exit 1
fi

if [[ ! -d .venv ]]; then
  python -m venv .venv
fi

# Default prebuild installs core/test tooling only; ML and UI extras are opt-in.
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev-codespaces.txt
python -m pre_commit install
python -m pip check
echo "Barrot Codespaces core environment is ready."
