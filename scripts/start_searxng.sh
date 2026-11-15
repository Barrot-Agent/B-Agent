#!/usr/bin/env bash
# Start a local SearXNG instance with the JSON API enabled.
#
# The SearXNG MCP server in opencode.json expects http://127.0.0.1:8888.
# First run clones SearXNG, creates a Python virtualenv, installs
# requirements, writes a settings file if missing, and serves in the
# foreground. Stop with Ctrl-C.
#
# Usage:
#   bash scripts/start_searxng.sh            # foreground
#   bash scripts/start_searxng.sh --daemon   # background, idempotent
set -euo pipefail

DAEMON=0
for arg in "$@"; do
  case "$arg" in
    --daemon|-d) DAEMON=1 ;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "unknown argument: $arg (use --daemon)" >&2
      exit 2
      ;;
  esac
done

SEARXNG_DIR="${SEARXNG_DIR:-$HOME/.local/share/searxng}"
SETTINGS_PATH="${SEARXNG_SETTINGS_PATH:-$HOME/.config/searxng/settings.yml}"
PORT="${SEARXNG_PORT:-8888}"
LOG_PATH="${SEARXNG_LOG_PATH:-$HOME/.local/share/searxng/searxng.log}"
PID_PATH="${SEARXNG_PID_PATH:-$HOME/.local/share/searxng/searxng.pid}"
BASE_URL="http://127.0.0.1:${PORT}"

healthy() {
  curl -fsS -m 3 -o /dev/null "${BASE_URL}/config" 2>/dev/null
}

if [ "$DAEMON" = "1" ] && healthy; then
  echo "SearXNG already running at ${BASE_URL}"
  exit 0
fi

command -v uv >/dev/null 2>&1 || {
  echo "uv is required: https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
}

if [ ! -d "$SEARXNG_DIR/.git" ]; then
  mkdir -p "$(dirname "$SEARXNG_DIR")"
  git clone --depth 1 https://github.com/searxng/searxng.git "$SEARXNG_DIR"
fi

if [ ! -x "$SEARXNG_DIR/.venv/bin/python" ]; then
  uv venv "$SEARXNG_DIR/.venv" --python 3.13
  uv pip install --python "$SEARXNG_DIR/.venv/bin/python" \
    -r "$SEARXNG_DIR/requirements.txt"
fi

if [ ! -f "$SETTINGS_PATH" ]; then
  mkdir -p "$(dirname "$SETTINGS_PATH")"
  secret="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
  cat >"$SETTINGS_PATH" <<EOF
use_default_settings: true

general:
  instance_name: "Barrot SearXNG"
  contact_url: "http://127.0.0.1:${PORT}"

server:
  secret_key: "${secret}"
  bind_address: "127.0.0.1"
  port: ${PORT}
  limiter: false
  public_instance: false
  image_proxy: false

search:
  safe_search: 0
  autocomplete: ""
  formats:
    - html
    - json
EOF
fi

cd "$SEARXNG_DIR"
export SEARXNG_SETTINGS_PATH="$SETTINGS_PATH"

if [ "$DAEMON" = "0" ]; then
  exec .venv/bin/python -m searx.webapp
fi

nohup .venv/bin/python -m searx.webapp >"$LOG_PATH" 2>&1 &
pid=$!
echo "$pid" >"$PID_PATH"
echo "SearXNG starting (pid ${pid}) -> ${BASE_URL}  log: ${LOG_PATH}"

for _ in $(seq 1 30); do
  if healthy; then
    echo "SearXNG ready at ${BASE_URL}"
    exit 0
  fi
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "SearXNG exited during startup; last log lines:" >&2
    tail -20 "$LOG_PATH" >&2 || true
    exit 1
  fi
  sleep 1
done

echo "SearXNG did not become healthy within 30s; see ${LOG_PATH}" >&2
exit 1
