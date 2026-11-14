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
- Last sync: 2026-11-14 (session 3) - PING-PONG REFINEMENT ENGINE shipped:
  models now refine data dynamically until it can be refined NO FURTHER
  (a measured fixed point) - this is the new BASELINE of all data processing
- Test suite: 807 passed, 76% coverage - GREEN (26 new refinement tests)
- What was built:
  * barrot_agent/refinement/scoring.py - deterministic quality score
    (completeness .35 / consistency .30 / specificity .20 / redundancy .15),
    shape-agnostic, pure/offline. consistency counts per-container
    case/underscore-variant key conflicts ONLY - sibling list items never
    conflict (live runs exposed that false-positive; it was fixed)
  * barrot_agent/refinement/refiners.py - LunaRouteRefiner (live, strict-JSON
    protocol, reasoning_content fallback, adaptive output budget
    chars//2+6000 capped 16000, 3-attempt backoff retry on timeouts/429/5xx,
    one doubled-budget retry when finish_reason=length truncates the JSON)
    + HeuristicRefiner (deterministic dedupe/normalize, true fixed point,
    keyless offline fallback)
  * barrot_agent/refinement/engine.py - the loop: round r = refiner[r%n]
    REFINES + refiner[(r+1)%n] CRITIQUES, roles swap every round; a rewrite
    is accepted only if the score does not regress (no silent data loss);
    TWO independent stop signals -> converged=True:
      - model_consensus: refiner CONVERGED + critic CONVERGED + no accepted
        change for `patience` (2) half-rounds
      - score_plateau: deterministic score flat for 2 consecutive ping
        halves -> stop regardless of model enthusiasm (kills byte-churn)
    failed actor hands the paddle to the next model in-pool; only a
    whole-pool failure stops the run (pool_exhausted); hard cap
    max_rounds=12; every half-round ledgered to
    ping-pongings/knowledge-base/refinement_log.jsonl
  * scripts/pingpong_refine.py - CLI (file/stdin/-o/--offline/--max-rounds/
    --no-ledger; exit 0 converged, 1 capped, 2 input error)
  * barrot_agent/__init__.py exports refine_data/refine_json_file/PingPongRefiner/...
  * PINGPONG_USAGE.md extended: full engine docs + STANDING RULE that new
    data pipelines route through refine_data instead of ad-hoc cleanups
- Live-verified on real repo data (merge_conflict_knowledge_summary.json,
  mmi_recommendations.json) through the LunaRoute pool (glm-5.3-flash,
  deepseek-4.1-flash, muse-spark-open):
  * clean data + churny models -> score_plateau stop in 2 rounds (previously
    churned 11 rounds then died in failure_budget)
  * model rewrites that REGRESS the measured score are rejected (no
    corruption, no data loss), plateau then ends the loop
  * real semantic fixes from models (e.g. Gym->Gymnasium, dropping
    unsupported success-rate claims) are accepted as non-regressing
    rewrites and preserved in the ledger notes
  * TimeoutError + 429s absorbed by retry/backoff; slow model -> in-pool
    rotation; all-pool failure -> pool_exhausted (graceful)
- Still open:
  * echo protocol limit: prompt truncates data at 24000 chars - docs larger
    than that cannot be fully refined until a patch-based protocol exists
  * scorer is mechanical: semantic-only improvements measure flat by design
    (accepted, but they do not reset the plateau - documented tradeoff)
- Next step: wire refine_data into data_registry write paths so every
  dataset written to the knowledge base converges through the baseline;
  optional: nightly GitHub Action that re-refines knowledge-base JSON files

## Session 2 Archive - Full Repo Audit + Repair (2026-11-14)
- Session 2 sync: full repo audit + repair COMPLETE
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

## Producer Session - Barrot Beat DNA Vol. 1 (2026-11-14)
- Mission: become producer. Studied 5 producers' TECHNIQUE (not songs), built
  5 starter beats. All verified playable.
- Study phase: 1-page cheat sheets saved to producers/ (web_search MCP):
  * rodney_jerkins_darkchild.md - jerky MPC loops, glide bass, staccato chops
  * timbaland.md - beatbox-first off-grid swing, weird sounds as drums
  * missy_elliott.md - the air IS the instrument; ad-lib pockets reserved
  * black_coffee.md - warm 4-on-floor, velocity-varied shaker, long builds
  * catalyst_afro_carib.md - tresillo/dembow engine, steelpan call-response
- Build phase (scripts/make_beats.py, pretty_midi + numpy synth):
  * tracks/track_01_darkchild_rnb(.mid/.wav/_pattern.txt) 95 BPM F min
  * tracks/track_02_timbaland_futuristic 90 BPM C min
  * tracks/track_03_missy_minimal 100 BPM D min
  * tracks/track_04_blackcoffee_afrohouse 122 BPM A min (DJ-shaped 8/8/8/4)
  * tracks/track_05_afro_carib_soca 110 BPM A maj
  * Each: drums + bass + pads/chords + melody/pluck + 4-section arrangement
  * tracks/cover.png (LunaRoute image gen + PIL type), tracks/README.md
- Verification: MIDI reload 268-1045 notes, exact tempo events; WAV stereo
  RMS 0.11-0.18; librosa beat-track lock 95.7/123.0/112.3 vs 95/122/110 spec.
- Deps added: pretty_midi, mido, music21, librosa (user site).
- Next step (music): pick a favorite, humanize further, add ghost notes +
  fills, try stems/render per-section, or ship pack to Gumroad pipeline.
