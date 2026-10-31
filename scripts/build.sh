#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-b-agent:latest}"
echo "Building Docker image: $TAG"
docker build -t "$TAG" .
echo "Build complete: $TAG"
