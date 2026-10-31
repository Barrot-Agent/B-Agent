#!/bin/bash
while true; do
    if [[ -n $(git status -s) ]]; then
        git add .
        git commit -m "AUTOSYNC: $(date '+%Y-%m-%d %H:%M:%S')"
        git push origin main
    fi
    sleep 300
done
