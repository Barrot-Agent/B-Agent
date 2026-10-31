#!/usr/bin/env bash
set -euo pipefail

echo "Running code quality checks..."
black --check barrot_agent tests
isort --check-only barrot_agent tests
flake8 barrot_agent tests
mypy barrot_agent
echo "All checks passed."
