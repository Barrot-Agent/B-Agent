#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${BRAIN_SHARED_SECRET:-}" ]]; then
    echo "FATAL: BRAIN_SHARED_SECRET must be configured; refusing to start without API authentication." >&2
    exit 1
fi

MODEL_PATH="/app/model.gguf"
MODEL_URL="https://huggingface.co/${MODEL_REPO}/resolve/main/${MODEL_FILE}"

if [ ! -f "$MODEL_PATH" ]; then
    echo "Downloading model (~8GB, first boot only)..."
    curl -L --progress-bar -o "$MODEL_PATH" "$MODEL_URL"
fi

echo "Starting llama-server on port ${PORT}..."
exec /app/llama-server \
    -m "$MODEL_PATH" \
    --port "$PORT" \
    --host 0.0.0.0 \
    -c 8192 \
    --n-cpu-moe 99 \
    -ngl 0 \
    --api-key "$BRAIN_SHARED_SECRET"
