#!/usr/bin/env bash
set -euo pipefail

echo "Running B-Agent tests..."
pytest "$@"
