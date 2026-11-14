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
- Last commit: 59599cb SHRM 2.0 hierarchical reasoning refinement
- Last sync: 2026-11-14 - full repo-repair session COMPLETE
- Test suite: 784 passed, 75.33% coverage (Termux python3 -m pytest) - GREEN
- Python: use /data/data/com.termux/files/usr/bin/python3 (has pytest); /usr/bin/python3 has NO pip
- Works now (all fixed + committed this session):
  * mcp_sync engine (barrot_agent/mcp_sync.py + CLI + 17 tests)
  * 13 broken imports fixed (9 bare paths + emit_pingpong restored + AGIEngine alias)
  * emit_pingpong.py recreated (stdlib, never-raises, JSONL to ping-pongings/)
  * pyproject [integrations] extra + requirements-integrations.txt (databricks-sdk,
    flask, huggingface_hub, kaggle, pandas, scikit-learn)
  * a2a/worker.js rate-limiter Map leak fixed (sweep at 1024; verified 429/recovery)
  * README: all 15 dead links repaired; missing-dir refs removed
  * 13 workflows bumped to action majors v7 (checkout/setup-python/artifacts)
  * SHRM 2.0: barrot_agent/reasoning/hrm.py - weighted sources, opt-in 2-level
    H-hierarchy, slope convergence (opt-in), decision traces, v1 label parity
    proven (0 mismatches on 3000 randomized cases), 20 new tests
  * removed dead config: package-hardhat.json, .gitlab-ci.yml
- SHRM 2.0 usage: from barrot_agent.reasoning import hrm2_resolve,
  resolve_with_trace; scripts/emit_signal_with_hrm.py --engine hrm2 [--refined]
- In flight: background pip install of integrations extras (pandas/sklearn build
  slow on device) - verify 4 optional modules import when it completes
- Blocked: gh CLI not installed; SSH push denied (no key) - to push, provide a
  fine-grained GitHub PAT (repo content read/write) as GH_TOKEN env or secret;
  do NOT paste tokens into chat files
- Known flake: tests/test_transmute.py CLI test occasionally fails in full runs
  (timing tie-band), passes in isolation - not a regression
- Next task: verify optional-deps imports after pip finishes; push commits once
  GH_TOKEN available; consider trimming .barrot-backup/ from git history
