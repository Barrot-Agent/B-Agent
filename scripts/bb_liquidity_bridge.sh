#!/usr/bin/env bash
set -euo pipefail

# Use a local data path that we control
DATA_DIR="${HOME}/B-Agent/data"
LOG_FILE="${DATA_DIR}/liquidity_depth.log"

printf "[!] TARGETING XRP LIQUIDITY DEPTH...\n"

# Fetch and redirect to your workspace
curl -s "https://api.ripple.com/v2/order_book/XRP/USD" | \
grep -oE '"bid": "[0-9.]+"' | head -n 5 > "${LOG_FILE}"

printf "[+] DEPTH MAPPED TO ${LOG_FILE}\n"
