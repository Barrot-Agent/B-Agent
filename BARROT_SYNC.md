# BARROT SYNC - Single Source of Truth
# Termux Barrot (OpenCode) + GitHub + GPT Project all read this file.

## Identity
- Brain: OpenCode ONLY - https://opencode.ai/inference/openai/v1 - opencode/deepseek-v4.1-flash-free
- Canonical Barrot: Termux ~/barrot/Barrot-Agent via b_agent.py
- Relay Barrot: GPT Project - NEVER claims to be the OpenCode brain
- Repo: github.com/Barrot-Agent/B-Agent, branch main

## Secrets
- OPENCODE_API_KEY is public (opencode free models) - not a secret
- GH_TOKEN in GitHub Secrets + Termux env for push/pull
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
- Last sync: 2026-11-15 (session 6) - MCP RECONFIGURED: github/docling/searxng all reachable
  in OpenCode. What changed:
  * Root cause of the github "Authorization header is badly formatted (HTTP 400)"
    failure: `{env:GITHUB_MCP_TOKEN}` was unset in the running server process. Fix =
    token in the OpenCode service env + service restart (verified: 49 github tools,
    live MCP sync probe from scripts/mcp_sync.py).
  * Rewrote mcp_config.json + data/mcp_config.json: removed phantom packages
    (`mcp-server-github`, `mcp-server-memory`, `mcp-server-filesystem`) and
    `/workspace/B-Agent` paths; now mirrors the live stack (github remote, docling,
    searxng, git, memory, filesystem, fetch) with portable relative paths.
  * scripts/start_searxng.sh: added --daemon (idempotent background start; logs to
    ~/.local/share/searxng/searxng.log). SearXNG was NOT running before; now up on
    ~~~~127.0.0.1:8888.
  * README MCP section updated (--daemon, `opencode mcp list`, service restart note).
  * Tests: tests/test_mcp_sync.py 17 passed; tests/test_mcp_integration.py 42 passed.
- Previous sync: 2026-11-15 (session 5) - OFFLINE MODEL DOWNLOAD: created
  ~/download-offline.sh to download Qwen2.5-0.5B-Instruct GGUF Q4_K_M
  (~380MB) to ~/offline-models/ with curl -L -C - resume support.

  Script: ~/download-offline.sh (22 lines, executable)
- Test suite: 848 passed, 76.68% coverage - GREEN (41 new tests; see session
  3 archive below for the pre-upgrade baseline of 807)
- What was built (all reuse session 3's refiners/engine/scorer - nothing replaced):
  * paths.py - canonical dot-path pointers with escaping for keys containing
    dots/backslashes (real KB keys like "a2a_server.py" exposed TWO escaping
    bugs pre-ship: ptr_join escaping the prefix's structural dots, and the
    ESC constant being the 2-char "\." instead of the 1-char "\"; both fixed
    + locked with roundtrip regression tests), value hashes, walk_leaves
  * segmentation.py - document audit + coverage-exact slot plan
    (dict_keys / list_slice / string_range slots, <=9000 chars each incl.
    key-name overhead, bounded sibling context, natural-boundary string
    splitting). COVERAGE CONTRACT: raises if any leaf would be uncovered -
    the pipeline can never silently skip source content. list slots map
    local->absolute leaf paths via Slot.absolute_leaf_path (start offset)
  * patches.py - targeted patches (replace/set/delete/splice) with hash
    preconditions validated against the LIVE document; conflict detection
    (same-path duplicate/conflict, ancestor-supersedes, DELETE-vs-SET
    incompatible); batch apply returns the mutated document + undo stack;
    exact rollback; verify_against_original proves nothing missing, nothing
    smuggled outside declared scopes, untouched containers keep shape,
    deletions declared
  * semantics.py - FOUR separate results: A mechanical (scoring.py
    unchanged) / B semantic / C regression / D overall status. The
    deterministic core is offline+repeatable and can ONLY certify
    non-regression or flag loss (meaning coverage with hedge vocabulary
    excluded, >40% loss line, numeric drift, key loss) - it never claims
    improvement. "improved" requires an INDEPENDENT judge
    (LLMSemanticJudge wraps a DIFFERENT model than the refiner) that passed
    calibration on 3 reference cases (CALIBRATION_CASES); uncalibrated
    judges cannot vote improved; the deterministic core can veto any judge.
    Judge context capped at 20,000 chars/side (documented limitation)
  * pipeline.py - the 10-step workflow SOURCE->AUDIT->SEGMENT->REFINE->
    GENERATE PATCHES->VALIDATE->APPLY->SEMANTIC EVALUATION->REGRESSION
    TEST->RECORD RESULTS. Per-section atomic run state = resume point
    (interrupted runs resume with --resume, refined sections never
    repeated); persistent learning history refinement_history.jsonl records
    source identity/hashes/objective/patches/evals/failures/disposition/
    timestamp/implementation version (pp-refine/1.1.0); (source, objective)
    pairs already complete are skipped unless --force; semantic regression
    veto -> rollback to original + one corrected attempt with judge
    regressions as critique; disposition "complete" ONLY if no section
    failed/skipped AND verification passed
  * scoring.py - completeness rewritten dedupe-aware: list elements count
    per UNIQUE value (raw counting made legitimate dedup LOWER the score -
    real bug, found by the resume test, fixed)
  * scripts/pingpong_refine.py - CLI keeps all old flags/exit codes; adds
    --objective / --resume RUN_ID / --force; small docs -> classic loop,
    >24K docs -> patch pipeline; prints mechanical/semantic/verification +
    incomplete sections explicitly
  * scripts/live_refine_verify.py - live-runtime verification driver
  * tests/test_refinement_upgrade.py - 39 tests, all MOCKED/offline by
    default; REAL-runtime tier gated behind BARROT_LIVE_REFINEMENT=1 env
    (live section refine + independent judge, never runs in default suite)
- Verified live (REAL OpenCode runtime, NOT mocked):
  * source: barrot_capability_audit.json - 28,582 chars, 642 leaves, 782
    nodes -> 5 dict_keys slots (max 8,856 chars), coverage contract held
  * pool: OpenCode free models; judge = independent model
  * result: disposition=complete in 322s, 5/5 sections refined, 8 attempts,
    1 patch applied (doc already near-clean), mechanical 0.9989 -> 0.9989,
    semantic=unchanged regression=1.0, verification ok=True 0 missing
    0 smuggled 0 deletions
  * TRUST GATE PROVEN LIVE: the judge scored all 9 dimensions 1.0 but
    FAILED calibration on the 3 reference cases -> downgraded, could NOT
    vote "improved" (calibrated=False) - no manufactured improvements
  * refined output persisted: refinement_runs/live_refined_capability_audit.json
    (29,904 chars); learning history run_id ref-5698ae8b7657-1794692948
- Still open / limitations:
  * judge sees max 20,000 chars per side (prefix) for very large docs
  * keys containing dots are addressable but awkward (escaped as \.)
  * classic engine still truncates at 24K by design - it is the SMALL-doc
    path; the pipeline is the large-doc path
- Next step: wire refine_document into data_registry write paths; optional
  nightly GitHub Action re-refining knowledge-base JSON via the pipeline
- Producer track (session 4, same day): user judged the 5 tracks
  grid-correct but NOT vocal-ready; v2 data acquired and banked:
  * producers/reference_acquisition.md - 5 sources via web search + webfetch
    (Roland/Darkchild harp signature, Timbaland per-layer timing, Missy
    tumbi+go-go chant, Black Coffee kick+tom-loop split foundation,
    dembow 3-2 clave) cross-referenced vs v1 cheat sheets -> v2 patch list
  * tracks/kits/pd/ - 24 one-shots: 15 public-domain TR-808/808-mini
    (smpldsnds, license-verified; unlicensed candidates REJECTED) + 9
    synthesized signatures (log drum modal, steelpan bowl partials, tumbi
    Karplus-Strong, squelch glide bass, rhythmic harp) + README manifest
  * commits adc8843 + d00f158; next: rebuild v2 tracks against the patch
    list, then user feedback loop (kill/keep/change + rating anchors)
- v2 rebuild EXECUTED (session 4 cont., user authorized + gave baseline
  anchor: ALL 5 v1 tracks = 3/10; prediction gap 4 pts logged in ledger):
  * make_beats.py patched (not rewritten): kit-sample render path
    (KIT_DRUMS velocity ladder + KIT_MELODIC pitch-shifted one-shots),
    per-layer offsets (Timbo: kick rigid / percussion +28-35ms), strange
    accent every 4 bars, kick-dropout hook bars, explicit 3-2 clave,
    and-of-2 snare accent, static root-only sub, tom-loop (80Hz HP + ducked
    vs kick), bar-end shaker, noise-build, ambient bed, Darkchild rhythmic
    harp + squelch bass, Missy tumbi + call-and-response
  * FIX: v1 Missy "pluck" hook layer was missing from render/MIDI mapping
    lists - never sounded in v1; now renders (tumbi) - likely part of the 3
  * evidence: MIDI offsets measured +27.3ms vs 28 spec; clave steps exactly
    [0,6,12,20,24]; dropout bars verified; sample-vs-synth correlation in
    rendered WAVs (kick 0.408 vs 0.106, conga 0.342 vs 0.129); all 5
    spectral centroids shifted (nothing skipped); pattern duration bug fixed
  * commit 0186c88; ledger tracks/feedback/ledger.jsonl live (2 entries);
    v2 predictions logged (4-5/10, NOT claiming vocal-ready)
  * next: user re-scores v2 + kill/keep/change -> gap shrinks or patches; a
    10-anchor still missing

## Session 3 Archive - PING-PONG REFINEMENT ENGINE (2026-11-14)
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
  * barrot_agent/refinement/refiners.py - OpenCodeRefiner (live, strict-JSON
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
  mmi_recommendations.json) through the live OpenCode pool:
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
  * tracks/cover.png (image gen + PIL type), tracks/README.md
- Verification: MIDI reload 268-1045 notes, exact tempo events; WAV stereo
  RMS 0.11-0.18; librosa beat-track lock 95.7/123.0/112.3 vs 95/122/110 spec.
- Deps added: pretty_midi, mido, music21, librosa (user site).
- Next step (music): pick a favorite, humanize further, add ghost notes +
  fills, try stems/render per-section, or ship pack to Gumroad pipeline.
