#!/usr/bin/env bash
# Start a local SearXNG instance with the JSON API enabled.
#
# The SearXNG MCP server in opencode.json expects http://127.0.0.1:8888.
# First run clones SearXNG, creates a Python virtualenv, installs
# requirements, writes a settings file if missing, and serves in the
# foreground. Stop with Ctrl-C.
set -euo pipefail

SEARXNG_DIR="${SEARXNG_DIR:-$HOME/.local/share/searxng}"
SETTINGS_PATH="${SEARXNG_SETTINGS_PATH:-$HOME/.config/searxng/settings.yml}"
PORT="${SEARXNG_PORT:-8888}"

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
exec .venv/bin/python -m searx.webapp
