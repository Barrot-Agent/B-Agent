#!/bin/bash
# v_sync_relay.sh — periodic auto-commit loop.
# Safety: refuses to auto-commit secret material (.env, keys, credentials)
# and refuses to push to a remote that has diverged (no force pushes).
set -uo pipefail

cd "$(dirname "$0")" || exit 1

SECRET_MATCH='\.(env|pem|key|p12|kaggle\.json|databrickscfg|git-credentials)(\.|$)'

while true; do
    if [[ -n $(git status -s) ]]; then
        git add -A .
        # Never auto-commit secrets that may have landed in the worktree.
        if git diff --cached --name-only | grep -qE "${SECRET_MATCH}"; then
            echo "[relay] SECRET-LIKE FILE STAGED — aborting auto-commit." >&2
            git reset -q
        elif ! git diff --cached --quiet; then
            if ! git commit -m "AUTOSYNC: $(date '+%Y-%m-%d %H:%M:%S')"; then
                echo "[relay] commit failed; leaving changes staged." >&2
            elif ! git pull --rebase --autostash origin main; then
                echo "[relay] remote diverged; rebase failed — NOT pushing." >&2
            else
                git push origin main || echo "[relay] push failed; will retry next tick." >&2
            fi
        fi
    fi
    sleep 300
done
