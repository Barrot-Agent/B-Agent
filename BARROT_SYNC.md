# BARROT SYNC - Single Source of Truth
# Termux Barrot (OpenCode) + GitHub + GPT Project all read this file.

## Identity
- Brain: OpenCode ONLY - https://gw.opencode.com/v1 - opencode/glm-5.3-flash
- Canonical Barrot: Termux ~/barrot/Barrot-Agent via b_agent.py
- Relay Barrot: GPT Project - NEVER claims to be OpenCode brain
- Repo: github.com/Barrot-Agent/B-Agent, branch main

## Secrets
- OPENCODE_API_KEY in GitHub Secrets - DO NOT paste value in chat, DO NOT commit to repo
- Termux: local env OPENCODE_API_KEY - same value as GitHub Secret
- GitHub Actions: ${{ secrets.OPENCODE_API_KEY }}
- GPT Project: NEVER has the key, only reads this file
- GH_TOKEN in GitHub Secrets + Termux env for push/pull

## Hard Rules
- Do NOT re-add Orbit. Commit 71cdd8b. ORBIT_REMOVED.md exists.
- Do NOT touch Orbitron font in hf_space/app.py:556-561
- Do NOT use password auth. GH_TOKEN via x-access-token only.
- Do NOT re-commit .config/gh/hosts.yml - OAuth REVOKED

## Barrot Operating Loop - 7 PERMANENT LAWS (Sean's orders, never re-ask)
1. MEMORY: You have no reliable memory. Read BARROT_SYNC.md FIRST before doing
   anything. After EVERY task update this file: What you did, What works now,
   What is broken, Next step.
2. HACKATHON RULE: Always keep a working demo. Never break the build to add a
   feature. If a change breaks tests, revert with git immediately.
3. TRANSMUTER: Never settle for v1. Make 2-3 variants (faster / simpler / more
   robust), test each, keep the winner, delete losers. Measure: speed, tests
   passed, errors. (Enforced by scripts/transmute.py - see barrot.md.)
4. SAFETY: Before any big change: git add -A && git commit -m "checkpoint before transmute"
5. MCP FIRST: Use filesystem + github + fetch + memory MCPs before guessing.
   Do not hallucinate APIs - fetch them.
6. SHIP LOOP: Scan -> Fix -> Test with bash -> Commit -> Log to BARROT_SYNC.md
   -> Repeat. Do not ask permission per file.
7. REPORT: End every session with 3 lines: Fixed / Upgraded / Still blocked + why.

## Last State
- Last commit: 459adec Add live concurrent MCP sync engine (mcp_sync) + agent instructions
- Last sync: 2026-11-14 - repo-repair session, full audit in progress
- Test suite: 764 passed, 74.9% coverage (Termux python3 -m pytest, ~5 min) - GREEN
- Python: use /data/data/com.termux/files/usr/bin/python3 (has pytest); /usr/bin/python3 has NO pip
- Works now: compileall clean; mcp_sync engine committed; import fixes applied
  to 6 files (agi_reasoning, transformative_insights, sindy_video_pipeline,
  vision_pipeline, barrot_integration, inference_provider) - NOT yet committed
- Broken: barrot_agent/agi/quantum_entanglement.py:10 imports emit_pingpong -
  module does not exist anywhere in repo (deleted, call site line 98 remains)
- Broken deps (not in requirements.txt): databricks-sdk, huggingface_hub, flask,
  kaggle, pandas, scikit-learn (kaggle_competitions_automation)
- Blocked: gh CLI not installed; SSH push denied (no key) - push needs GH_TOKEN
- README: 12 dead links; site/ search-engine/ coin-app/ character-capabilities/
  dirs referenced by README do not exist in repo
- a2a/worker.js: rate-limiter `clients` Map never evicts stale entries (memory
  growth per isolate); otherwise hardened (constant-time auth, rate limit,
  body caps) - fix queued
- Workflows: mixed action versions (13 files still on checkout@v4/setup-python@v5/v6)
- Next task: fix/remove emit_pingpong import -> run suite -> commit import fixes
  -> add optional deps to requirements -> fix a2a Map leak -> README links
