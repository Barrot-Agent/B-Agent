#!/bin/bash
# BARROT-Ω CONTINUOUS SYNC ENGINE
# Monitors B-Agent workspace for changes and checkpoints to GitHub

REPO_DIR="$HOME/B-Agent"
cd $REPO_DIR

while true; do
    # Check if there are uncommitted changes
    if [[ -n $(git status -s) ]]; then
        echo "[SYNC] Mutations detected. Initiating checkpoint..."
        git add .
        git commit -m "AUTOSYNC: $(date '+%Y-%m-%d %H:%M:%S') - System State Snapshot"
        git push origin main
        echo "[SYNC] State successfully pushed to GitHub."
    fi
    # Wait 300 seconds before next check to conserve resources
    sleep 300
done
