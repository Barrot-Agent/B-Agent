#!/usr/bin/env bash
set -euo pipefail

MANIFEST_PATH="${HOME}/B-Agent/GLOBAL_STATE_MANIFEST.md"

if [[ ! -f "$MANIFEST_PATH" ]]; then
  echo "GLOBAL_STATE_MANIFEST.md not found at $MANIFEST_PATH" >&2
  exit 1
fi

if command -v pbcopy >/dev/null 2>&1; then
  cat "$MANIFEST_PATH" | pbcopy
elif command -v xclip >/dev/null 2>&1; then
  cat "$MANIFEST_PATH" | xclip -selection clipboard
elif command -v wl-copy >/dev/null 2>&1; then
  cat "$MANIFEST_PATH" | wl-copy
else
  echo "No supported clipboard tool found. Install pbcopy, xclip, or wl-copy." >&2
  exit 1
fi

echo "Copied $MANIFEST_PATH to clipboard."
