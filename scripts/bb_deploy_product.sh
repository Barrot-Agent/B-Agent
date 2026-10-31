#!/usr/bin/env bash
set -euo pipefail

GUMROAD_TOKEN=$(cat "${HOME}/.config/gumroad/token.enc")
ASSET_DIR="${HOME}/B-Agent/assets/stupid_sindy"

printf "[*] Compiling Stupid Sindy Season 1...\n"
tar -czf /tmp/sindy_s1.tar.gz -C "${ASSET_DIR}" .

printf "[*] Initiating Gumroad API Push...\n"
curl -s -X POST https://api.gumroad.com/v2/products \
  -H "Authorization: Bearer ${GUMROAD_TOKEN}" \
  -d "name=Stupid Sindy S1 Rig Pack" \
  -d "price=1000" \
  -d "description=Full Season 1 asset and rig files."

printf "[+] Deployment strike complete.\n"
