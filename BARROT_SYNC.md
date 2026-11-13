# BARROT SYNC - Single Source of Truth
# Termux Barrot (LunaRoute) + GitHub + GPT Project may read this file.
# This is a coordination note, not proof of live authentication, data flow, or secret presence.

## Identity
- Intended model provider: LunaRoute - https://gw.lunaroute.com/v1 - lunaroute/glm-5.3-flash. Authentication/data flow NOT VERIFIED.
- Canonical Barrot: Termux ~/barrot/Barrot-Agent via b_agent.py
- Relay Barrot: GPT Project - NEVER claims to be LunaRoute brain
- Repo: github.com/Barrot-Agent/B-Agent, branch main

## Secrets
- LUNAROUTE_API_KEY is referenced by environment-variable name only; presence/validity in GitHub Secrets is NOT VERIFIED. DO NOT paste a value in chat or commit it.
- Termux: local env LUNAROUTE_API_KEY is intended configuration; presence/validity and equality with GitHub Secrets are NOT VERIFIED.
- GitHub Actions: ${{ secrets.LUNAROUTE_API_KEY }}
- GPT Project: NEVER has the key, only reads this file
- GH_TOKEN is a secret-name reference only; presence/validity is NOT VERIFIED. Use only for explicitly approved operations.

## Hard Rules
- Keep the LunaRoute remote MCP server disabled until authentication, permissions, and data flow are verified; the integration OpenCode config defaults it to disabled.
- No automatic external sync or push without explicit approval and an exact approved source SHA.
- Do NOT re-add Orbit. Commit 71cdd8b. ORBIT_REMOVED.md exists.
- Do NOT touch Orbitron font in hf_space/app.py:556-561
- Do NOT use password auth. GH_TOKEN via x-access-token only.
- Do NOT re-commit .config/gh/hosts.yml. Prior audits found the path in affected historical PR branch tips; contents were not read and provider-side OAuth revocation is NOT VERIFIED.

## Last State
- Last commit: 71cdd8b Ditch Orbit
- Last claimed sync: 2026-11-10; this historical note is NOT independently verified. Main Barrot Sync run 43343513347 lacked httpx and logged sync skipped; no sync commit was produced.
- Next task: verify authentication and data flow only with explicit approval; record exact source receipts and commit evidence before claiming a successful sync.
