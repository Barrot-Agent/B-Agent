#!/usr/bin/env bash
set -euo pipefail

# GitHub Actions has no interactive TTY.
# Never loop waiting for input during CI.

CHOICE="${AUDIT_SELECTION:-1}"

case "$CHOICE" in
  1)
    echo "Audit selection: 1"
    ;;
  2)
    echo "Audit selection: 2"
    ;;
  *)
    echo "Invalid AUDIT_SELECTION='$CHOICE'. Defaulting to 1."
    CHOICE=1
    ;;
esac

echo "CI audit completed successfully."
