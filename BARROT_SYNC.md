# BARROT SYNC - Single Source of Truth
# Termux Barrot (LunaRoute) + GitHub + GPT Project all read this file.

## Identity
- Brain: LunaRoute ONLY - https://gw.lunaroute.com/v1 - lunaroute/glm-5.3-flash
- Canonical Barrot: Termux ~/barrot/Barrot-Agent via b_agent.py
- Relay Barrot: GPT Project - NEVER claims to be LunaRoute brain
- Repo: github.com/Barrot-Agent/B-Agent, branch main

## Secrets
- LUNAROUTE_API_KEY in GitHub Secrets - DO NOT paste value in chat, DO NOT commit to repo
- Termux: local env LUNAROUTE_API_KEY - same value as GitHub Secret
- GitHub Actions: ${{ secrets.LUNAROUTE_API_KEY }}
- GPT Project: NEVER has the key, only reads this file
- GH_TOKEN in GitHub Secrets + Termux env for push/pull

## Hard Rules
- Do NOT re-add Orbit. Commit 71cdd8b. ORBIT_REMOVED.md exists.
- Do NOT touch Orbitron font in hf_space/app.py:556-561
- Do NOT use password auth. GH_TOKEN via x-access-token only.
- Do NOT re-commit .config/gh/hosts.yml - OAuth REVOKED

## Last State
- Last commit: 71cdd8b Ditch Orbit
- Last sync: 2026-11-10 - LunaRoute only, GitHub Secrets holds LUNAROUTE_API_KEY
- Next task: [update after each run]
