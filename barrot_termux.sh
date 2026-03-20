#!/bin/bash
# BARROT-Ω TERMUX ROLE: SYNC ONLY
# All inference runs on Hugging Face Space
# This script is the only thing Termux should run

echo "========================================"
echo "BARROT-Ω TERMUX SYNC AGENT"
echo "Role: Git sync only. No API calls."
echo "========================================"

cd /data/data/com.termux/files/home/barrot

# Count current entries
ENTRIES=$(python3 -c "import json; d=json.load(open('barrot_brain_unified.json')); print(len(d.get('knowledge',[])))" 2>/dev/null)
echo "[SYNC] Brain entries: $ENTRIES"

# Sync to GitHub and GitLab
bash brain_sync.sh
git add -A
git commit -m "Termux sync: $(date '+%Y-%m-%d %H:%M') — $ENTRIES entries"
git push origin main
git push gitlab main

echo "[SYNC] Done. Hugging Face Space handles all inference."
echo "========================================"
