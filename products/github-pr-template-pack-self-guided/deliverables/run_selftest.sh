#!/usr/bin/env bash
# Run the kit's own test suite. No network, no third-party packages.
set -euo pipefail
cd "$(dirname "$0")"
exec python3 -m unittest discover -s tests "$@"
