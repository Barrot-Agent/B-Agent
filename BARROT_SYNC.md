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
- Last sync: 2026-11-14 (session 2) - full repo audit + repair COMPLETE
- Test suite: 784 passed, 75.25% coverage - GREEN; wheel builds clean
- Fixed / Upgraded this session (all committed):
  * 11 broken imports fixed: mcp_orchestrator (7 bare sibling/cross-package
    imports -> _import_flexible), orchestrator_bridge (legacy AGI now loads
    in package mode), dependency_micro_ingestion (longevity dispatch)
  * b_agent.py unrunnable -> fixed (undeclared rich/httpx declared; shebang
    moved to line 1; imports reordered; flake8 clean; --help verified)
  * vader_check.py import-safe without vaderSentiment (lazy analyzer,
    neutral fallback with vader_available=False; real path verified)
  * barrot_task_allocator.py direct-execution ImportError -> sys.path shim
  * WHEEL UNBUILDABLE -> fixed: setuptools discovery scoped to
    barrot_agent* (4 top-level __init__.py dirs broke auto-discovery);
    python -m build verified, wheel contains only barrot_agent/*
  * dependency-audit.yml: requirements.tx typo -> requirements-integrations.txt
    (gate was permanently red); gates test updated to match
  * 2 flaky timing tests hardened (transmute CLI, mcp_sync concurrency:
    bounded retry rounds)
  * opencode.json migrated to native OpenCode V2 shape (providers/package:
    aisdk:/settings/agents/ordered permissions)
  * app.json + GLOBAL_STATE_MANIFEST.md: wrong repo/website URLs corrected
    (were Barrot-Agent/Barrot-Agent -> B-Agent), dead logo URL dropped
  * Dockerfiles: python:3.10-slim -> 3.12-slim (3.10 EOL 2026-10)
  * Dependency floors raised (torch 2.6, transformers 4.48, streamlit 1.41,
    numpy 2.1, cryptography 44, PyJWT 2.10, websockets 14, pillow 11,
    pydantic 2.10, rich 13.7, httpx 0.27); dev toolchain refreshed
    (pytest 9.2, flake8 7.5, mypy 2.4.1, black 26.10.1, pre-commit 4.7 +
    hook revs v6.0.0/26.10.1/9.0.2/7.5.0); cdp-sdk declared in integrations
  * .env.example: +23 env vars derived from actual os.getenv usage
  * v_sync_relay.sh hardened: never auto-commits secret-like files,
    rebase-before-push, no force push
  * .barrot-backup/ untracked (duplicate of git history) + gitignored
  * CHANGELOG.md [Unreleased] section written
  * Security scan clean: no hardcoded secrets, no pull_request_target,
    no eval/exec/pickle on untrusted input, cron schedules all valid
- Still blocked:
  * Docker not installed on this machine -> 3.12 image upgrades are
    compile-checked, not build-tested
  * opencode binary not installed locally -> V2 config migration verified
    against official docs, not runtime-tested
  * 2 TODO-class items left intentionally: smart_agent.py:390 TODO lives
    inside generated code-scaffold text; kaggle/hf Rust-free pins are
    documented platform constraints, not bugs
- Next step: push remaining commits (gh authenticated as Barrot-Agent);
  after push, verify CI green on GitHub; then optional: history-trim of
  removed .barrot-backup/ blobs, Docker build test when docker available
