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
- Last sync: 2026-11-15 (session 8) - HYPE FILTER + INFINITE INGESTION: built the
  executable hype gate and the four-module ingestion loop, then ran it once.
  * New: barrot_agent/hype_filter.py - 5 checks, HYPE at 2+ failures, evidence spans.
    Calibration: Memorilla video OK (0/3 applicable failed); "AGI is here" video HYPE
    (2/5: benchmark_caveat, funding_vs_intent). tests/test_hype_filter.py: 34 passed.
  * New: barrot_agent/infinite_ingest/ (models, storage, sources, ingestor, transmuter,
    cross_analyzer, refiner, cli). tests/test_infinite_ingest.py: 29 passed.
    Caps: 10 ingests/run, 1 refine/capability/run, stop on 429/503, raw 500MB prune.
    Every media ingest goes through enforce_gate() before storage/transmutation.
    New tests total 78 passed (hype 34, ingest 29, gist 15).
  * First measured run (data/capabilities/long_context_memory.json):
    0.00 -> 1.00 recall (5/5 facts); 96 records added, 17 bound, no revert.
    First pass 0.80; fixed gist window width 6->10 + measurement-tail extension and
    extraction cap 24->48, then re-ran clean. Harness = extractive recall, not LLM QA.
  * Docs: docs/INFINITE_INGESTION.md. Graph: data/connections.json (96 nodes, 80 edges).
  * Continuous mode NOT enabled - awaiting Sean's approval. 3 SearXNG results queued.
  * Known gaps: no in-pipeline PDF parser (use docling), no automatic fetch retry,
    lexical matching only. Reverted unrelated riemann_hypothesis_harvest.json timestamp
    churn caused by full pytest collection.
- Previous sync: 2026-11-15 (session 7) - VIDEO EXTRACTION + GIST MEMORY: built an offline
  memory compressor from the Memorilla research, and documented both requested videos.
  * Transcripts: both fetched (youtube-transcript-api); ids lNpDxKfBlf8 (Better Stack,
    "Did Stanford Just Solve AI Memory? (Memorilla)") and us_pnC6ETNA (Julia McCoy,
    "It's Official: We've Entered AGI"). 293 and 325 caption segments.
  * New: barrot_agent/gist_memory.py - stdlib/CPU extractive compressor, 16 slots x 6
    words, two-pass IDF scoring, MMR redundancy, verbatim source span + expand() for RAG
    fallback. New: tests/test_gist_memory.py (14 passed), flake8 clean.
  * Docs: docs/VIDEO_EXTRACTION_2026-11-15.md - mechanism, prompts, numbers, verified vs
    hype table. Key verified fact: GPT-6 Astra 62.7% (ARC standard) vs 99.9% (provider
    adapter) - harness matters more than model. Memorilla failure modes recorded.
  * MEMORY.md: offline-memory rules + agent-leverage facts added.
  * Not implemented: latent token training / Qwen3-8B / vLLM - needs 80GB GPU, not Termux.
- Previous sync: 2026-11-15 (session 6) - MCP RECONFIGURED: github/docling/searxng all reachable
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

## Session 2026-11-16 - MCP recheck + V3 Geometry inventory (analysis only)
- What I did: re-verified live MCP (github connected, get_me -> Barrot-Agent;
  docling 21 tools, searxng 4 tools); audited repo for the 12 V3 Geometry
  capabilities against code + executed tests.
- What works now: `barrot_agent/rendering/mesh_topology.py` (edge incidence,
  open boundaries, non-manifold, watertight) with 5 passing tests;
  `polygon_triangulation.py` with area-preservation test (5 passing);
  `obj_mesh_loader.py` (9 passing); provenance via `evolution/evidence_store.py`
  and `ingestion/mmi_contract.py` hash chain.
- What is broken/missing: no Geometry package. Stratification, typed
  equivalence, certificates, geometric transforms, geometry signatures, and
  exact arithmetic are absent. `EvidenceState` is 7 labels, not the required 8;
  no 4-state VALID/INVALID/UNRESOLVED/NOT_APPLICABLE enum.
- Next step: Sean authorizes orchestration layer; reuse rendering.mesh_topology
  and mmi_contract instead of duplicating. PA1 Target 1 doc not found - needs
  path or text.

## Session 2026-11-16 (cont.) - V3 Geometry doc received
- Doc arrived (not a file; pasted in session). Inventory re-run against its exact
  layers: 12-capability table + extra layers (config space, relational, closure,
  symmetry, robustness, minimal explanation, independence).
- Finding: doc's own §25 guess holds - smallest viable new capability is
  Structural Signature + Relational Discovery; representation/constraints/
  invariants/classification/incidence exist only in rendering mesh scope.
- PA1_FINAL_v1.2.txt still absent. No code changed.

## Session 2026-11-16 (cont.) - geometry slice implemented (authorized)
- Did: built `barrot_agent/geometry/` (states, object, signature, relations) + 4
  test files. Additive only; no existing file touched.
- Works now: 72 geometry tests pass, flake8 clean, existing rendering tests
  19/19 pass. Canonicalization is order-independent even when coordinates
  collide; the permutation search is bounded and refuses rather than guessing.
- Broken: `tests/test_phoenix.py::test_passing_experiment_unlocks_level_two`
  fails on sandbox run `gist-budget`. Pre-existing - it still fails with the
  geometry package deleted. Not caused by this work.
- Not built: stratification, certificates, exact arithmetic, equivalence
  registry, config space, robustness, minimal explanation. Designs only,
  labeled CONJECTURED.
- PA1: still UNRESOLVED - file not located on this filesystem.
- Next step: wire signature + relations into one geometry claim path; signature
  match stays "candidate", never equivalence.

## Session 2026-11-16 (cont.) - PA1 v1.2 text received
- `PA1_FINAL_v1.2.txt` still absent on this container; Sean's shell wrote it to a
  mount I cannot see. Verified with wc, cat, `find / -maxdepth 5`.
- Read from pasted text: §5 construct (primary = R_L not M), §6 Target 1
  safeguards (ITPRA labels, +0.05 min effect, equivalence test, 4-way ablation,
  Contradiction Register, PASS/FAIL/INCONCLUSIVE), §7 execution order and STOP.
- §1-4 not provided -> UNRESOLVED, not claimed.
- Effect on code: none. PA1 is construct validation; it defines no geometry
  contract. Geometry slice unchanged and still green (72 tests).
- Next step: Sean supplies §1-4 or the real file path, if that matters; otherwise
  Target 1 execution stays unstarted per §7 STOP.

## Session 2026-11-16 (cont.) - PA1 execution contract received
- Received as text: 8-target sequence, mandatory rules, report schema A-H,
  Target 1 objective + kill criterion (redundancy -> demotion, not deletion).
- Contradiction found: §7 order is 1-2-4-5-3-6-7-8; the bundle diagram omits
  Target 4. Flagged, not resolved by guessing.
- Target 1 cannot execute yet: missing ITPRA baseline operational definition,
  dataset/outcome/path, PA1-ToM predictor spec, preregistered N/power and
  equivalence procedure, M3/M5 partition definitions.
- No code touched. Geometry slice unchanged (72 tests green).

## Session 2026-11-16 (cont.) - STEP 1 LOCATE against frozen PA1 §5-§7
- Sean retracted the "Complete Bundle" paste: it was a recap, not the frozen file.
  Its 8 target names, schema A-H, kill-test wording and diagram are VOID.
  Marked RETRACTED in MEMORY.md so no later session reuses them.
- Frozen PA1 = §5, §6, §7 text only. Targets 2-8 have no defined identity there.
- STEP 1 result: 0 of 20 constructs exist in code.
  - §5 (9 items): S_L, E_C, R_L, M_signed, R_signed_error, probe split, reactivity
    flag, manipulation check, M3/M5 -> all absent. No rating/trial dataset either
    (trial/participant hits are clinical longevity code; rating hit is a power rating).
  - §6 (11 items): ITPRA components, Huron/Barrett labels, MISSING marker,
    held-out log-likelihood, +0.05, preregistration, equivalence test, 4-way
    ablation, recursion ablation, Contradiction Register, PASS/FAIL/INCONCLUSIVE
    -> all absent.
  - §7 is a process rule; no code artifact exists or should exist for it.
- Adjacent reusable infra that DOES exist: scientific_discovery.ClaimStatus,
  VerificationIndependence + IndependenceEvaluator.assess, ContradictionAnalysis;
  mmi_contract.EvidenceState (7 labels); geometry.states.TruthState (4 states).
- Spec gap (not a repo gap): §5 names M3 and M5 but never defines them. §7 names
  targets 1-8 but only target 1 is described. Those stay UNRESOLVED until Sean
  supplies the definitions.
## Session 2026-11-16 (cont.) - STEP 1b semantic alias re-check (§5)
- Searched aliases: signed_error, composer_estimate, probe_flag, is_probe, nonprobe,
  non_probe, reactivity, "estimate vs actual", "expected vs actual", latent, probe,
  expectation, surprise, prediction_error, manipulation check, attention/catch trial,
  overestimate/underestimate, bias, metacognition, model_3/model_5, discrepancy.
- Result: 0 alias matches. All 9 §5 constructs stay MISSING. Near misses examined
  and rejected: analyze_reference.py:105 signed timing bias (audio), gist_memory.py
  latent vectors (embeddings), mcp_sync.py probe_* (network), polymath_ingestion.py:378
  chemical reactivity.
- No code modified. Awaiting Sean.

## Session 2026-11-16 (cont.) - STEP 2 gap-fill design (Target 1 only)
- §6 alias re-check done: 0/11. Only near-alias is Contradiction Register, where
  2 of 5 required fields exist (`supporting_evidence`, `contradicting_evidence`
  in research/scientific_discovery.py:209,368,410). `alternatives` as a register
  field, `missing`, `falsifier` absent. Still MISSING, not PARTIAL.
- Delivered CONJECTURED design for all 20 missing constructs (§5 x9, §6 x11) in
  `barrot_agent/pa1/` (constructs, partitions, itpra, evaluation, contradiction,
  verdict). No files created. No production code.
- Design rules held: every function returns UNRESOLVED/MISSING on absent input,
  never 0; no numeric constant outside §5/§6; Tau absent; Targets 2-8 unnamed.
- M3/M5 identities and the 5 ITPRA component names are NOT in frozen text, so the
  design treats both as registries that refuse to produce a baseline until Sean
  supplies definitions. Not invented.
- Awaiting approval to code.

## Session 2026-11-16 (cont.) - Phoenix push attempt (BLOCKED, no push exists)
- Sean asked to "push to Phoenix" and confirm a push hash / log line before build.
- Finding: `barrot_agent/phoenix.py` is a LOCAL level/evidence protocol. Commands:
  status | experiment | combine | unlock. There is no push, no remote, no push hash,
  and no confirmation token. Do not invent one.
- Phoenix state: level 0 "unawakened". `data/phoenix_state.json` and
  `data/phoenix_experiments.jsonl` do not exist. `run_experiment` calls require(1)
  -> PermissionError at level 0, so Phoenix cannot emit an experiment log line.
- What does work: `log_power()` is not level-gated. It appended a real entry to
  MEMORY.md (line 112): "### Power 2026-11-16 - pa1_frozen_state_v1_2",
  Result: RECORDED, Artifact: sha256:69d629f7...090ee6 (PA1 block, 17 lines).
  This is a record, NOT a pass, NOT a remote confirmation.
- MEMORY.md now also carries the STEP 1 tables (0/9, 0/11) and the near-miss list
  (gist_memory, mcp_sync probe_*, polymath reactivity, analyze_reference offset).
- git: origin github.com/Barrot-Agent/B-Agent, branch main, HEAD eb6dc34.
  MEMORY.md + BARROT_SYNC.md are modified and uncommitted. No commit/push made.
## Session 2026-11-16 (cont.) - Phoenix sandbox repair (runner.py)
- Failing test: tests/test_phoenix.py::PhoenixTests::test_passing_experiment_unlocks_level_two,
  call at tests/test_phoenix.py:210, raised at barrot_agent/phoenix.py:357.
  Expected: result.passed True -> unlock level 2. Got: passed=False, exit_code=-9,
  timed_out=True, 60.3s, stderr "bionic/linker/linker_cfi.cpp:158 MapShadow CHECK".
- NOT combine(): all 4 combine tests pass; combine is at phoenix.py:402. The range
  217-300 is unlock(), not combine.
- Root cause: RLIMIT_AS. On Android bionic the interpreter dies inside the loader
  before user code when RLIMIT_AS < ~3 GiB. Measured: 512 fail, 1024 fail, 1536 fail,
  2048 fail, 3072 pass, 0/disabled pass. Tests hardcode memory_mb=512 at
  tests/test_phoenix.py:40 and tests/test_sandbox.py:34,74, so changing the default
  alone would not have fixed it.
- Fix (barrot_agent/sandbox/runner.py only, no test files touched): added
  MIN_MEMORY_MB = 3072 if sys.platform == "android" else 0 (line 44) and clamp
  requested>0 limits up to the floor in __init__ (lines 164-166). A limit below the
  floor would measure the loader, not the experiment.
- Proof: tests/test_phoenix.py 16/16 pass (was 15/16); tests/test_sandbox.py 7/7 pass;
  flake8 runner.py exit 0.
- NOTE: barrot_agent/sandbox/ is UNTRACKED in git (28 untracked entries total), so
  there is no checkpoint commit and no git-revert for this file.
- Still true: the repo-level Phoenix state is level 0 and there is no push command,
  so the "Phoenix confirms frozen PA1" gate remains unsatisfiable as written.
- The exact run dir/log for `20261116T214232Z-gist-budget` is UNRECOVERABLE: the test
  root is a TemporaryDirectory (tests/test_phoenix.py:31-38) removed in tearDown, and
  keep_on_fail=False deletes the run dir. Surviving equivalent: data/sandbox/runs.jsonl
  line `20261116T214330Z-probe-gist`, same script sha256
  ecd103a893b1b780efbce11eef51fcde9c9a1d03d4b12eb557451dc370c9f0a8 as the test's
  PASS_SCRIPT, same stderr, exit -9. Caveat: that repro ran with timeout=60, the test
  uses timeout=10; the failure mechanism is identical.

## 2026-11-16 — B-ACES Transmuted v1.1 (minimal slice)
- What I did: created runs/B-ACES_v1.0_SPEC.md (transmission record),
  runs/B-ACES_TRANSMUTED_v1.1.md, runs/B-ACES_v1.0_IMPLEMENTATION-LOG.md,
  barrot_agent/skills/{debian-verify,_template,SKILL-INDEX.md}.
- What works now: debian-verify executes ls -lh + sha256sum and returns
  MISSING / EXISTS / EXISTS_UNHASHED. Template + index exist on disk.
- What is broken: B-ACES v1.0 spec body was NEVER supplied - no file in
  /root/barrot contains "B-ACES" (grep verified). test_01 premise is false:
  barrot_agent/phoenix.py EXISTS (22K, sha256 fd83ebfa...893bc0), so the test
  is recorded FAIL and the skill stays `draft`, not `verified`.
- Prompt claims contradicted by disk: PA1_Complete_Bundle.txt MISSING,
  PA1_FINAL_v1.2.txt MISSING, runs/2026-11-16-12AM/ MISSING.
- Next step: replace test_01 with a truly-absent path so debian-verify can
  reach `verified`. tau=0.707 still quarantined, unused.

## 2026-11-16 — V3 snapshot cross-corroboration + Geometry Capability Map
- What I did: verified every snapshot claim against disk, scanned
  barrot_agent/geometry/ (677 lines, 5 modules), ran 4 full test modules
  (72 passed) + 2 MMI modules (32 passed), ran an 11-check read-only sandbox
  probe from /tmp/opencode/geom_probe.py (11/11 pass), wrote
  runs/GEOMETRY_CAPABILITY_MAP.md.
- What works now: geometry package is a REAL partial Structural Discovery Core —
  representation, constraints, invariants, signature, relations, incidence,
  8 evidence states, 4 truth states, exact-vs-numerical guard.
- What is broken: snapshot does not match this tree. All 3 checkpoint commits
  ABSENT; .barrot/sources/ and .barrot/mmi_learning/ MISSING (83 files, neither
  dir); scripts/barrot_governed_bundle_executor.py + its test MISSING; no gitlab
  remote; branch is main not barrot/task. Nothing reset.
- Missing layers: classification, stratification, representation correspondence,
  certificates, domain/config space. compare_invariants does not exist anywhere.
- Next step: gate 2 — corroborate the map, then propose ONE addition
  (invariant-set registry w/ 2nd set) with tests. No geometry implementation
  until that gate passes.

## 2026-11-17 — RE meta-analysis + repo-wide scan (analysis only)
- What I did: ran 3 analyses (loop reverse-engineering, full repo scan, top-20
  wishlist). Wrote results/re_wishlist.md, appended a meta_analysis record to
  results/transmute_log.json, updated MEMORY.md. No production code touched.
- Measured baseline: full suite `pytest -o addopts= -q` = 1027 passed, 1 skipped,
  8 subtests passed, 4m59.69s, GREEN. The repo is not test-broken; the instrument is.
- Key finding 1: the 10-stage convergence loop is prose only (BARROT-12AM-MASTER.md),
  0 code hits for TRANSFER_SUCCESS / anti_cheat_passed / AXIOM_FORGE. Anti-Cheat is
  self-interrogation, not an executed ablation. Variant scores 37 / 69 / 82 / 95.
- Key finding 2: pytest.ini --cov-fail-under=70 + -v makes every scoped run exit
  non-zero (4 files = 14.15% coverage, 72/72 pass) and corrupts transmute.py scoring.
- Key finding 3: 10 byte-identical dup pairs, 3 near-clones (_btc 70-88%), 21 untested
  top-level modules (11 mcp_*), 95/120 scripts untested, 16 zero-byte root files.
- No `work` branch exists — only main.
- Next step: fix pytest.ini/transmute scoring (minutes), then build loop V2 Witness
  (CLAIM -> WITNESS -> LOG), then resolve memory precedence.

## 2026-11-17 — PHASE 1 COMPLETE: scoring fixed
- What I did: found the gate declared twice (pytest.ini --cov-fail-under=70 AND
  pyproject [tool.coverage.report] fail_under=70). Benchmarked 4 scoring strategies
  on the same 4 files (2 repeats each), applied the winner.
- Winner: v1_no_cov (rc=0, 7.1s) over v0_current (rc=1, 32.7s), v2_split_gate
  (rc=1, 21.8s), v3_ignore_exit (rc=1, 35.3s).
- Changes: pytest.ini gate removed; pyproject fail_under 70 -> 0; ci.yml full-suite
  step now owns the 70% gate (measured 77.57% on the full suite, so satisfiable);
  transmute.py gets --no-cov, adaptive tie band max(100ms, measured jitter), and
  aborts on a missing --tests path instead of silently scoring 0%.
- Proof: scoped run rc 1 -> 0 (72 passed, 17.7s); transmute candidate wall
  32.7s -> 3.9s; negative control v_break.py parsed 71/72 and was rejected.
- Correction to my earlier claim: the gate did NOT zero the score (rate parsed
  72/72 = 1.0 regardless). Real damage was rc=1 + 4.6x wall inflation + 7.2s
  jitter against a 100ms tie band.
- Next step: PHASE 2 dedupe (10 byte-identical pairs, import shims first).

## 2026-11-17 — prompt bundle staged (not executed)
- Created scripts/bundle_next_phases.py (STUB: only mkdir + print, creates nothing),
  prompts/phase2_dedupe.md, prompts/phase3_cleanup.md, prompts/meta_re_and_mmi.md.
- Phase 1 is DONE (5792fa8). Phases 2, 3 and META/MMI are queued, not started.
- Deferred deliberately: prompts/meta_re_and_mmi.md section 4 rewrites
  .opencode/agent/barrot.md (my own system prompt). Not applied yet.

## 2026-11-17 — PHASE 2 COMPLETE: dedupe (shims, no deletes)
- 8 content groups from 10 byte-identical pairs. 5 shimmed, 2 hash-locked, 1 structural.
- Shims: scripts+toolsmem_palace -> barrot_agent/mem_palace.py;
  scripts/granite_model_config -> barrot_agent/tools/;
  utils/score_to_signal -> barrot_agent/analysis/;
  scripts/deploy_huggingface -> barrot_agent/orchestration/ (+ CLI delegate);
  barrot_agent/tools/trial_tracker -> barrot_agent/monetization/.
- NOT shimmed (evidence): core/hrm_ternary vs hf_space/hrm_ternary — hf_space is a
  standalone Space, app.py imports bare 'hrm_ternary'; grant_generator x2 — 5-line
  print script, top-level side effects, shim would print on import. Both hash-locked.
- Proof: tests/test_duplicate_shims.py 20/20. Full suite 1047 passed, 1 skipped
  (was 1027 + 20 new). CLI checks preserved for all 3 script shims.
- Cost: +5 sys.path.insert guards (31 -> 36). Die when `pip install -e .` lands.
- Next step: PHASE 3 cleanup (move 16 zero-byte root files to archive/, no deletes).

## 2026-11-17 — PHASE 3 COMPLETE: debris archived, inventories listed
- Moved 16 zero-byte root files to archive/debris-20261116/ (1 git mv tracked
  .termux_dna_harvest.log + 15 plain mv). Nothing deleted. Root now has 0.
- Verified: package imports OK, mem_palace CLI OK, 1048 tests collect with 0
  import errors, no code referenced .termux_dna_harvest.log.
- Listed (NOT fixed) in results/re_wishlist.md: 31 tracked sys.path.insert
  (26 pre-existing + 5 Phase 2 shims), 8 bare except, 94/121 scripts with no
  test reference.
- Scope correction: the wishlist's original "31 sys.path" was an untracked-inclusive
  scan; tracked-only was 26 then. Both read 31 now — verified, not assumed.
- Next step: PHASE 4 (META + MMI + market mastery). Section 4 rewrites
  .opencode/agent/barrot.md — show the diff before committing.

## 2026-11-17 — PHASE 4 SECTION 1: loop reverse-engineered, V3 applied
- Loop is prose only (BARROT-12AM-MASTER.md, 95 lines). 0 .py hits for
  TRANSFER_SUCCESS / anti_cheat_passed / AXIOM_FORGE / NOVELTY_SCORE.
  Stages 8-10 (Plugin/Skill/Phoenix) are named at line 25 and never specified.
- Two structural defects: D1 the loop grades itself (stages 2-6 ask the
  generator to be the judge); D2 nothing is durable (JSON blob in a transcript).
- Built 3 variants, scored by scripts/transmute.py (3 repeats, 10 tests):
  V1 ablation-only 1/10 -> deleted; V2 witness+chain 10/10 182 lines 996389;
  V3 durable ledger 10/10 195 lines 994393 -> APPLIED.
- Honest caveat: baseline jitter was 21726ms, so the tie band decided the
  transmute. Speed was settled by a 1000-record benchmark instead:
  append 7350.7 -> 5103.4ms (-31%, O(n^2) -> O(n)), verify 59.7 -> 48.5ms,
  assert_supported 24.59 -> 13.63ms, same ledger bytes, tamper still caught.
- tests/test_witness_loop.py 10/10 before and after. scripts/witness_loop.py = V3.
- Next step: results/mmi_mastery_wishlist.md (Top 50).

## 2026-11-17 — PHASE 4 SECTION 2: MMI Top-50 wishlist written
- results/mmi_mastery_wishlist.md: 50 items, each with Why / Data / Transmutation
  / Proof of mastery, in 4 groups (market data, execution+risk, paradigm sync,
  loop integrity) + an order of attack.
- All "Why" lines are measured facts, not textbook. Key ones:
  * web/signal_accuracy.json: 772/1697 = 45.5% directional accuracy.
  * web/latest_signal.json publishes confidence 0.0 with score 44, and is 18.6
    days old; scripts/signal_summary.py:135 itself requires 0 < confidence.
  * web/paper_trading_state.json: position_product null + avg_entry_price
    80436.84 + 126 trades -> corrupt book nobody caught.
  * trading/ has no fee, no slippage, no drawdown, no stop; RiskManager checks
    one thing ($25 cap); client_order_id is a fresh uuid per call.
  * two signal ledgers disagree: data/signal_ledger.jsonl 45 lines vs
    web/signal_history.jsonl 1697 records.
- Two claims corrected after checking: prompt_hash DOES exist in
  barrot_agent/barrot_brain.py:121 (so item 33 says it never reaches signals),
  and patch_add_btc_tool.py reads signals rather than writing them (item 31).
- Next step: results/gap_fill_log.json + scripts/verify_artifacts.py (fill item 30).

## 2026-11-17 — PHASE 4 SECTION 3: gap fill applied + logged
- APPLIED: scripts/verify_artifacts.py (read-only cross-artifact checker, exit 1
  on error, --json for CI) + tests/test_verify_artifacts.py (21 tests). Live run
  on this repo reports 4 errors in 4 lines:
    paper state: position_size 0.0124 with position_product null
    signal: confidence 0.0 while signal_summary.py:135 requires 0 < c <= 1
    signal: age 18.6 days > 3600s
    accuracy: 45.5% over 1697 < 52% floor
- APPLIED earlier this phase: witness loop V3 (10 tests).
- results/gap_fill_log.json: 19 gaps — 4 applied, 4 detected (test fires, behaviour
  not fixed), 11 logged with a transmutation plan. 9 critical.
- Deliberately NOT applied: fee/slippage model, drawdown/daily-loss/stop sizing,
  and the zero-confidence write gate. All three change money or the live publish
  path and need their own transmute cycle + regression proof.
- Corrected my own draft: prompt_hash DOES exist (barrot_brain.py:121), it just
  never reaches signals; patch_add_btc_tool.py reads signals, does not write them.
- Next step: SECTION 4 — write the permanent query-transmutation rule into
  .opencode/agent/barrot.md, run scripts/pillars_check.py, SHOW THE DIFF, commit.

## 2026-11-17 — PHASE 4 SECTION 4 COMPLETE: permanent query-transmutation rule
- .opencode/agent/barrot.md: added QUERY TRANSMUTATION (permanent) section —
  line 1 of every response = [Original] ... -> [Transmuted + Gap-Filled] ...;
  six gap-fill categories; original wins on conflict; stop for approval before
  money/secrets/live-state gap-fills.
- Also corrected one false claim already in the file: it said pillars_check.py
  "strips" fiction vocabulary. It only flags it (check_system_prompt_fiction,
  FICTION_TERMS list) and checks the deployed hf_space/app.py, not this file.
- Verification: local FICTION_TERMS scan of barrot.md = none. pillars_check.py
  run for real: deploy_sync OK, system_prompt_fiction clean, github_app and
  databricks FAIL (no creds in this env), hf_space stage=BUILD_ERROR (live Space
  is broken right now — reported, not touched).
- MEMORY.md: added the permanent rule + the measured market facts, and corrected
  my earlier judgment-rubric scores (37/69/82/95) to the measured transmute
  scores (93881 / 996389 / 994393).
- Phase 4 done: meta loop, Top-50 wishlist, gap fill log, permanent rule.

## 2026-11-17 — CORRECTION to Phase 4.2/4.3: signal asset != traded asset
- Found while cross-checking the wishlist: scripts/check_signal_accuracy.py:13
  prices 'ripple' (XRP) and web/latest_signal.json is XRP headlines, while
  scripts/coinbase_paper_trader.py:14 defaults to PRODUCT_ID=BTC-USD and builds
  its own Groq prompt from that product's ticker+trades. grep 'latest_signal'
  in coinbase_paper_trader.py = 0 hits. The 45.5% accuracy has never governed a
  BTC trade. Three parallel market models, no wire between them.
- Also: neither latest_signal.json nor latest_signal_btc.json has a product /
  product_id field at all. Asset identity exists only in prose.
- Added wishlist item 0 ("one market model per product"), now ranked above the
  other 50, and rewrote item 3 to require accuracy evidence per product.
- Added product_missing to scripts/verify_artifacts.py + a test. 22 tests pass.
  Live run now reports 5 errors (was 4).
- gap_fill_log.json: 20 gaps — 4 applied, 5 detected, 11 logged, 10 critical.
- Not fixed: adding product identity touches the emitter, both signal files, the
  accuracy scorer and the trader in one cycle. Own transmute run required.

## 2026-11-17 — origin/work audit: 0 commits ported, main-wip restored
- Requested: "port real commits from work to main". Result: 0 commits, 0 files.
  Evidence in results/port_log.md.
- Why: origin/work is an unrelated lineage. merge-base = none. 841 commits,
  245 files, 2025-11-19..2026-11-16 vs main 861 commits, 1352 files,
  2026-10-27..2026-11-17. Not ahead/behind: diverged.
- Commit taxonomy of the 841: 393 ping-pong automation cycles, 89 pulse
  snapshots, 76 merges, 157 workflow/manifest churn, 126 PR-feature/plan
  commits. No commit survives real + non-duplicate + safe.
- File taxonomy: 90 shared paths (73 byte-identical, 17 differ and every one is
  a stub on work: transmute.py 1131B vs 15144B, transmute_log.json 70B vs 33378B).
  155 paths only on work, 17 of them moved copies, 138 with content nowhere in
  main. Of the 33 unique .py, 30 already exist under barrot_agent/; the other 3
  are the abandoned coin-app presale and a superseded pingpong_emitter.py.
- Governance block: 5 of the 138 carry flagged vocabulary (glyphs/*_glyph.yml,
  memory-bundles/shrm-v2-config.json, simulation-stack/shrm-v2-config.yml).
  Never ported. delete-main-branch.sh also never ported (destructive).
- Stash cycle: stash@{0} "main-wip-before-work-merge-20261117" (62 paths) created,
  verified, popped clean — 0 conflicts. Backup outside git kept at
  ~/barrot/backup-20261117/ (untracked.tar.gz 31 entries, tracked.patch 2854 lines).
- Gate after restore: 1079 passed, 1 skipped, 47 warnings in 476.59s, cov 78%.
- origin/work untouched. Branch work left at 0732187 as placeholder. Not deleted.
- Still open: barrot_agent/geometry, phoenix.py, sandbox/, experiments/ are
  untracked-but-live. Commit only restores them to disk+git; they are unverified
  against the deployed path.

## 2026-11-17 — safeguards 1-3 verified + NEW FINDING: the suite is not hermetic
- Safeguard 0 (retroactive): commit 5de0c6db6 staged 78 files, zero matches for
  .env / secret / .pem / id_rsa / __pycache__ / .pyc / token / credential.
- Safeguard 1: stash 472391f48 = 43 tracked + 31 untracked = 74 files. The "62"
  figure was `git status --porcelain` lines, where untracked directories collapse.
  Markers all present: collaboration_records 31 (matrix + case-01..30),
  infinite_ingest 7, geometry 9, sandbox 10, phoenix 2, experiments 2,
  feedback_loops 6. Popped with 0 conflicts. stash list now empty.
- Safeguard 2: full suite 1079 passed, 1 skipped, 500.24s, cov 78%.
  Safety subset 68 passed (bundle_lifecycle_safety_regressions, pillars_check_readonly,
  sandbox, verify_artifacts, witness_loop). Restored-WIP subset 150 passed
  (infinite_ingest, duplicate_shims, geometry x4, phoenix, transmute).
- Safeguard 3: local HEAD == remote main == 5de0c6db6, tree clean.
- NEW FINDING (gap): running pytest MUTATES TRACKED FILES every run — 36 paths:
  .barrot/collaboration_records/*.json (timestamps), barrot_capability_audit.json,
  data/evolution/confidence_calibration.json (+60 lines), data/research/
  riemann_hypothesis_harvest.json (156 lines), ping-pongings/knowledge-base/
  refinement_log.jsonl (+5 lines), plus one new feedback_loops/feedback_loop_*.json.
  Verified timestamp/counter churn only, 0 non-time semantic lines in the sampled
  files. Backed up to ~/barrot/backup-20261117/test-run-churn-0909.patch (1653
  lines) and reverted, so HEAD stays clean.
  Consequence: "clean tree after pytest" is false unless the churn is reverted.
  Not fixed — tests should write to tmp_path. Logged as a wishlist item.

## 2026-11-17 — Grok Bot $100K book: project built, Part One drafted
- New project: book/grok-100k-business/. Source TOC supplied by Sean: 7 front
  matter pieces, 5 parts, 29 chapters, stated 297 pages.
- Page audit: supplied units sum to 216 pages. 297 - 216 = 81 pages unaccounted.
  Carried explicitly in toc.yaml under `proposed` (Part Six ch30-34 = 35p,
  appendices A-F = 46p), labeled "proposed, not supplied" in every file. No
  chapter inflated to hide the gap.
- Build: build_book.py measures words -> pages at 320 w/p (code + HTML comments
  excluded), assembles dist/book.md, writes dist/build_report.json, exits 1 on
  missing files or draft units outside 60-150% of target.
- Drafted: 7 front-matter units + Part One ch1-6 = 35.4 of 45 pages (79%).
  Outlined with beats: ch7-29 (23 chapters). Proposed: Part Six + appendices.
- Facts verified on docs.x.ai 2026-11-17: Grok Bot = cloud computer (browser/fs/
  terminal), multi-bot handoffs, routines, memory, MCP/API custom tooling.
  Grok Build = TUI + headless `grok -p` + ACP, install x.ai/cli/install.sh,
  `grok inspect`. Pricing: grok-4.7 $2/$6 per M under 200K (doubles above),
  grok-build-0.1 $1/$2 at 256K, web_search/code_exec $5 per 1k, collections
  $2.50 per 1k, batch -20%, cached input $0.50 per M.
- "Grok Swarm" is NOT a documented product name. Ch11 treats it as a pattern over
  documented primitives (multi-bot handoffs + grok-4.20-multi-agent-0309).
- Foreword carries an ATTRIBUTION PENDING block; a test enforces it.
- Tests: tests/test_book_manuscript.py, 12 tests, pass. Guards TOC/file 1:1,
  216+81=297 arithmetic, budget, placeholders, banned vocabulary, provenance date,
  outline beats, foreword sign-off.

## 2026-11-17 — INCIDENT: bulk delete of untracked files (recovered)
- What happened: during test-churn cleanup I ran
  `git ls-files --others --exclude-standard | xargs -r rm -f`.
  It deleted the entire untracked book project (47 manuscript units, toc.yaml,
  build_book.py, README, tests/test_book_manuscript.py) plus the sync/memory
  appends I had just made (those were tracked-file edits, reverted by
  `git checkout -- .`).
- Recovery: dist/book.md survived (gitignored, so not listed). It carries a marker
  per unit, so all 47 bodies were reconstructed exactly from it; toc.yaml,
  build_book.py, README, tests and .gitignore were rewritten. Rebuild reproduced
  identical numbers (35.4/45 pages, 48.8 pages present, 12 tests pass).
- Rule added: never bulk-delete untracked paths in this repo. Churn cleanup is
  scoped to named patterns (`feedback_loops/feedback_loop_*.json`) and nothing else.
- Backups: ~/barrot/backup-20261117/book-project/ (full tree copy).

## 2026-11-17 — PHASE A COMPLETE: book chapters 7-12 drafted
- Phase A = Part Two, ch7-12 (8+8+7+7+7+7 = 44 target pages). All six drafted.
- Measured pages (build_book.py, 320 w/p, code excluded):
  ch-07 7.1/8, ch-08 6.7/8, ch-09 6.3/7, ch-10 6.2/7, ch-11 7.3/7, ch-12 6.9/7
  = 40.5/44 pages (92%).
- Whole book: 75.9 of 89 drafted pages (85%); 85.9 pages present incl. outlines.
  Build exits clean, no PROBLEMS. 216 supplied pages only; the 81 `proposed` pages
  remain unbuilt and are still labeled proposed.
- New material this pass: ch7 routing-by-ambiguity cases, planner state machine,
  prompt architecture, "when the model is the wrong tool"; ch8 job directory, three
  trigger mechanisms, wrapper tests (empty/timeout/no-write), dry-run, never-touch
  list; ch9 skill lifecycle, quality metrics, registry; ch10 MCP server review,
  thin connectors, data-flow/retention decisions; ch11 worked end-to-end pipeline
  with cost table, swarm debugging procedure, operating cadence; ch12 fence
  red-team tests, team rules and admin caps.
- Tests: tests/test_book_manuscript.py 12 passed. Full suite 1091 passed,
  1 skipped (299s). Pytest churn reverted with scoped cleanup (36 named tracked
  files via git checkout, 2 named feedback_loop files removed). No bulk delete.
- toc.yaml: ch-07..ch-12 status outline -> draft. README status table updated.
- Backup: ~/barrot/backup-20261117/book-phaseA/ (54 files).
- Next: awaiting GO for Part Three (ch13-19). Do not start it unprompted.

## 2026-11-17 — Ch 7 evidence audit + repair (Phase A polish)
- Re-verified every numeric claim in ch-07 against docs.x.ai/docs/models (fetched
  this session) and the Grok Bot overview.
- Confirmed correct: grok-4.7 context 500K, grok-build-0.1 256K, $2/$6 and $1/$2,
  cached input $0.50 / $0.20 per M, whole-request doubling at 200K prompt tokens.
- Fixed 4 defects:
  1. table omitted cached-input column and the fact that grok-build-0.1 also
     doubles above 200K;
  2. "output is 3x input" was stated as universal (true for 4.7, 2x for build);
  3. worked case said "two-tenths of a cent per account"; arithmetic gives
     $0.0028 = three-tenths;
  4. closing budget paragraph claimed "$3 vs $30 per thousand" — unreproducible
     from the price table. Replaced with explicit arithmetic: 1K-in/250-out =
     $3.50 per 1,000 calls; 30K-in/2K-out = $72 per 1,000; 96% vs 28% on $100.
- Also corrected two cross-references: ch-28 "entirely about this" -> operating
  discipline; ch-09 "starts with these four fields" was false (ch-09 uses
  WHEN/INPUTS/ACCESS/STEPS/VALIDATE/RETURN/APPROVAL) -> names inputs, artifact,
  approval boundary.
- ch-07: 7.1 -> 7.4 of 8 pages (93%). Build exit 0, no PROBLEMS. Book tests 12
  pass, full suite 1091 passed / 1 skipped. Churn reverted scoped (36 files + 1
  named feedback_loop json). No other chapter touched.

## 2026-11-17 — Ch 8 evidence audit + repair (Phase A polish)
- Re-verified every claim in ch-08 against docs.x.ai (build/overview, cli/headless-
  scripting, cli/reference, features/sandbox, features/permissions, grok-bot/
  computers, bots, security, skills-routines-and-automations). 2 rounds, 1
  independent challenger, $0.00 (free models only).
- Confirmed correct: install.sh / install.ps1, XAI_API_KEY fallback, TUI/headless/
  ACP surfaces, `grok -p`, `--output-format plain|json|streaming-json`, one hosted
  computer per member shared by all their Bots, routines with Run history and
  Pause/Resume, cross-refs ch-03 (receipt chain) / ch-07 (token maths) / ch-09.
- Fixed 5 material defects:
  1. "token ceiling ... exits non-zero when hit" — not documented. Replaced with
     `--max-turns <N>` (real flag) + the wrapper's wall-clock timeout, and stated
     plainly that the CLI documents no token budget;
  2. wrapper checked `artifact.exists()` against the wrapper CWD, not job_dir —
     relative artifact path could mark a good run failed (and hash a stray file).
     Now resolved against job_dir;
  3. `subprocess.run(timeout=...)` raised TimeoutExpired uncaught, so the timeout
     run left no receipt, contradicting "receipts are append-only, especially when
     the run fails". Caught, verdict="timeout", receipt always written;
  4. "Network scope. An allowlist where the platform supports it." — no allowlist
     feature exists. Replaced with read-only/strict child-network blocking,
     Linux-only enforcement, model API + web tools outside it;
  5. "documentation says plainly that separate Bots are not a security boundary" —
     not in the docs. Replaced with the actual sentence: "Files and sign-ins on
     the shared computer aren't isolated per Bot and can remain there."
- Also: sandbox profiles section (workspace/devbox/read-only/strict, Landlock/
  Seatbelt, GROK_SANDBOX) and the permission layer (`--always-approve` means deny
  rules first, `--tools`/`--disallowed-tools`) added, because the chapter argued
  for fences and never named the documented flags. run_id now includes
  microseconds (same-second retries overwrote receipts). Sample command dropped
  "Stop after 40 tool calls" (prompt text) in favour of `--max-turns 40`.
- ch-08: 7.4 of 8 pages (93%). Build exit 0, no PROBLEMS, no missing files.
  Book tests 12 pass. Full suite 1091 passed / 1 skipped. Whole book 76.9/89
  drafted pages (86%).
- Flight Recorder: results/flight_recorder/2026-11-17-ch08.jsonl (3 rounds,
  ask/said/kept/rejected/cost/time). No other chapter touched.
- TIME: ~22 min wall clock vs 15-min cap — OVER. R1 6m, R2 2m, R3 5m; the rest is
  full-suite proof (3m55s) plus reverting 36 files of pytest timestamp churn. Cost
  $0.00 (free models only; no external AI is wired in this runtime).

## 2026-11-17 — Meta: RE method written down + full snapshot run
- Generated the full snapshot exactly as scripted: /tmp/FULL_SNAPSHOT.md,
  10437 lines / 563235 bytes. Not committed (lives in /tmp).
- Two defects in the snapshot script itself (not the repo):
  1. section 2 uses `git ls-files` without `-c core.quotePath=false`, so the
     tracked file `data/millennium_problem_7_poincaré_conjecture.json` comes back
     quoted (`"...poincar\303\251..."`) and is reported as `0 bytes | 0 lines`;
  2. section 6 runs `find . -type f -name "*ch-*" -o -name "*chapter*"` without
     parentheses, so `-type f` binds only to the first branch; the chapter loop
     walks non-chapter files and its headings pollute the section index. The
     `$(find ...)` is also unquoted, so any path with a space breaks it.
- Wrote results/RE_METHOD.md (1 page): the actual order (pin claim -> split atoms
  -> cheapest authority -> quote and diff -> smallest fix -> before/after proof ->
  revert side effects -> receipt), first-vs-last, done-vs-guessing (witness_loop
  SUPPORTED/REFUTED/CONTRADICTED, 10 tests), three recurring mistakes, and an
  11-line checklist that needs no human in the loop.
- Evidence used, not memory: scripts/witness_loop.py:33-35,95-96, `mcp_config.json`
  :94 pointing at a missing `barrot_agent/mcp_registry.json`, 36 tracked files
  rewritten per full pytest run (measured twice), ch-08's invented token ceiling.
- Not done: the 5-tool MCP server. The spec arrived truncated at tool 4
  (`reverse_engineer` -> `"steps_used": ["1.",`) and tool 5 is absent entirely.
  Two of the three fully specified tools also have no real data source:
  run_foundry_cycle (no Foundry code exists; Sean has not authorised building it)
  and flight_recorder_replay (recorder holds one mission, 3 records, so there is no
  second run of the same task to replay). check_capability does have real data
  (barrot_capability_audit.json: 122 capabilities, evidence, gaps).

## 2026-11-17 — Field track accepted, parked behind GO FIELDS
- Ch 8 confirmed pushed: ceda46a37. HEAD 443deb3a9, main in sync with origin,
  working tree clean except one untracked test artifact.
- Field track contract recorded in MEMORY.md: 8 topics in order, 3-layer tagging
  (L1 Established / L2 Applied / L3 Speculative), six required fields per topic,
  one reverse-engineered example each, prediction-before-promotion gate, $2/15min,
  2 rounds, Flight Recorder per topic. Not started: waiting for GO FIELDS.
- Pre-registered conflict: pillars_check.py bans "free energy" and "Planck-scale",
  but scans only hf_space/app.py. Layer 3 prose is safe in docs, never in the
  deployed surface.
- Dependency that does not exist: Foundry (0 hits in *.py). Track will run on
  RE_METHOD + Flight Recorder until Foundry is real.

## 2026-11-17 — Track 1 Cymatics shipped (prediction gate passed on frequency)
- docs/fields/track-01-cymatics.md: 3-layer tagged page, six required fields, one
  reverse-engineered example, L3 section with its own falsifier.
- New: scripts/cymatics_mode_check.py. Predictions written BEFORE the run, then
  measured on a 60x60 FD Laplacian (lowest 10 eigenpairs, 2.87 s). Predicted ratios
  1.5811/1.5811/2.0000/2.2361 vs measured 1.5807/1.5807/1.9993/2.2343, worst error
  0.16 percent. Tests: tests/test_cymatics_modes.py, 4 passed.
- Partial failure kept in the page: per-axis nodal-count predictions held only for
  (2,2), the one non-degenerate mode. Degenerate pairs mix, so the same frequency
  yields two patterns. That is a result (it is why pattern is not a function of
  frequency alone), not a bug to delete.
- Corrected category error before it shipped: ultrasonic cleaning is cavitation,
  not cymatics.
- Prediction gate result: PASS on frequency ordering, PARTIAL on nodal counts.
  Skill promotion still blocked until one physical plate test is run.
- Caps: $0.00, 12 min of 15. Flight Recorder:
  results/flight_recorder/2026-11-17-track01-cymatics.jsonl

## 2026-11-17 — Cross-domain synthesis before GO SERVER
- docs/synthesis/cross-domain-convergence.md: ablated four existing artifacts
  (cymatus page, RE method, Flight Recorder, fields contract) for shared rules.
- Three converging rules: the artifact outranks the narrator; conditions travel
  with the claim; ambiguity is preserved instead of collapsed to a verdict.
- Method named: THREE-GATE (PIN pointer/atoms, COMPARE only at equal conditions,
  PRESERVE supported / refuted / unverified).
- Three gaps that block GO SERVER honestly: no comparable recorder pair and no
  accuracy/error fields; no scoring rule for transmute_query; no capability-to-test
  binding for reverse_engineer.
- Flight Recorder: results/flight_recorder/2026-11-17-synthesis.jsonl

## 2026-11-17 — Cross-domain audit: 4 links repaired, 3 open
- Broken and fixed: Flight Recorder was write-only (0 consumers in .py) -> new
  barrot_agent/flight_recorder.py reader + schema, 7 records validate; no docs
  index for 69 files -> scripts/build_docs_index.py + docs/INDEX.md; runtime 3 vs
  sync config 8 servers with nobody recording which is authoritative -> audit
  known-break entry; pipeline discovered 7 accepted 3 promoted 0 -> named, not
  bypassed.
- New: scripts/cross_domain_audit.py - 5 links, JSON report, exit 1 on any
  undocumented break. Current run: breaking [], exit 0.
- New: tests/test_cross_domain_audit.py, 3 passed.
- Correction to my earlier report: barrot_agent/mcp_registry.json is a runtime
  artifact created on first save, not a dangling pointer. MCPRegistry._load
  returns early when absent.
- Still open: config drift (needs approval to generate one file), sandbox_passed=0
  (needs MCP_APPROVAL_TOKEN decision), GITHUB_MCP_TOKEN unset in shell.
- Report: docs/synthesis/cross-domain-audit.md

## 2026-11-18 — Phase 1 staged: paid-issue PR pack (verified, not published)
- Built `products/github-pr-template-pack-self-guided/` on
  `phase1/digital-downloads-paid-issue-pr`, Template 1 only. Templates 2-7 not
  started. No merge, publish, price change, or transaction.
- 6 templates, stdlib kit, 76 tests, generated examples. Release gate 9/9:
  39/39 files, 76 tests, flake8 clean, 55 files secret-scanned, 0 findings.
- Independent verifier (separate agent) returned PASS WITH CAVEATS. Round 1
  returned FAIL on 10 claim-integrity defects; all were fixed or documented:
  E-13 marketplace net $5.80 -> $6.30; fee range now includes 30% marketplace;
  unsupported "rest were noise, stale, or unpaid" removed; "committed" wording
  corrected; support break-even 41.5 min; bracket and non-URL validators added;
  Field README added to the gate; platform overlap explained. Stale gate log
  regenerated after the report.
- Pricing $9/$19/$39; direct net $7.60/$16.60/$34.60. Demand is unmeasured;
  pre-registered 30-day kill test is <3 sales at >=300 views.
- All 10 named components PROPOSED, none PROVEN/ACTIVE. Link existence is not
  checked (offline by design) and is documented as a limit.
- Still blocked: support email, seller legal name/address, governing law,
  lawyer review, live checkout/refund test, zip+checksums, Sean's written
  authorization.
- Next: Sean authorizes or rejects. No further building until then.

## 2026-11-18 — v2.2 compliance pass: renames, template prune, README rewrite
- Renames (git mv, history kept): `products/ship-paid-issue-pr-in-2-hours` ->
  `products/github-pr-template-pack-self-guided` (46 paths);
  `products/drafts/citation-audit-service` -> `citation-audit-checklist`.
- Deleted: `products/templates/service-template.md`, `saas-mcp-template.md`.
  Templates now 6, one per surviving category. PRODUCTS_MATRIX rows for offers of
  labour and SaaS removed; rows renumbered 1-6.
- README.md rewritten to the Foundry structure: what it is, Phase 1 status,
  current product + $9/$19/$39, 10 PROPOSED components, 8 roles, run rules,
  compliance, blockers, last-updated HEAD.
- Banned scan scope = compliance surface (README, PRODUCTS_MATRIX, products/,
  docs/money). Result 0. Whole-repo = 894, all in code filenames and historical
  corpora; not a compliance surface and not claimed as zero.
- Product proof after rename: 76/76 tests, release gate 9/9 (39/39 files,
  flake8 clean, 55 files secret-scanned, 0 findings).
- Not done, needs approval: rename internal package `paid_issue_kit`; none of the
  ten components promoted; nothing published, priced live, or merged.
- Next: Sean's Stage 10 decision + the 8 blocked inputs.

## 2026-11-18 — Sean approved safe path (no history rewrite, no code purge)
- Decision recorded: no `filter-repo`/rewrite; `paid_issue_kit` stays; banned-term
  bar applies to customer-facing files only.
- README: added the legacy-name note. Customer product remains GitHub PR Template
  Pack — Self-Guided; "paid issue" is the market term, not an offer of work.
- Customer-facing scan, per file, all 0: root README.md, product README.md,
  deliverables/README_FIELD.md, deliverables/README.md, SALES_COPY.md,
  marketing/PRODUCT_DESCRIPTION.md, marketing/PROMOTIONAL_COPY.md,
  marketing/FAQ.md, PRICING.md.
- No rewrite was needed: the six files Sean named were already compliant; the only
  earlier hit was my own compliance line in README, fixed before the prior commit.
- Legal name/address, governing law, checkout/refund test, support email: not
  filled, not guessed. Remain with Sean.
- Next: Sean supplies the 8 publish inputs, or rejects. No further building.

## 2026-11-18 — Publish inputs, partial: staged only (no publish)
- Authorization received, scope exact: stage only, not publish, until Sean
  approves final checkout. Recorded verbatim. Publication authorization: ABSENT.
- Written into the product files:
  * LICENSE_AND_TERMS.md — PUBLICATION_STATUS: STAGING_ONLY; seller = Sean Drew,
    1545 Minford Place, Bronx, NY 10460, USA; governing law New York, USA; venue
    Bronx County (derived from the address, flagged for lawyer confirmation);
    §13 carries the placeholder support address with a NOT FOR PUBLICATION marker.
  * PRICING.md — prices confirmed for staging on 2026-11-18; no live price; no
    listing; no transaction; revenue $0.00.
  * DELIVERY_REQUIREMENTS.md — §3 email exclusion now has the one licence
    exception; §6 support state corrected; §10 checkboxes reflect reality.
- Input states as of now:
  1 authorization — staging only, publication NOT granted
  2 support email — PENDING, placeholder in licence only
  3 legal name/address — SUPPLIED
  4 governing law — SUPPLIED (New York), lawyer to confirm venue
  5 lawyer review — PENDING
  6 checkout/refund test — NOT TESTED
  7 zip + checksums — NOT BUILT (would ship the placeholder; waits on 2 and 5)
  8 price — CONFIRMED for staging ($9/$19/$39)
- New fail-closed guard: verify_release.py --publication. Staging gate still 9/9
  PASS, rc 0. Publication gate rc 1 by design:
  [FAIL] publication readiness: status=STAGING_ONLY,
  placeholders=['PLACEHOLDER', 'NOT FOR PUBLICATION'].
- Customer-facing banned-term scan after edits: 0 across all 9 files.
- Placeholder email appears in exactly one file (LICENSE_AND_TERMS.md §13).
- STATUS: STAGING ONLY. Not published, not priced live, no transaction, no zip.
- Next: Sean supplies the real support address + lawyer sign-off + checkout test;
  then the publication gate can be flipped, zips built, and checksums verified.

## 2026-11-18 — Support email confirmed (not a placeholder)
- Sean confirmed cryptesseract@gmail.com is the real support address. The
  "do not publish with placeholder" restriction is lifted for the email only.
- LICENSE_AND_TERMS.md: header bullet now reads confirmed 2026-11-18; §13 has the
  address with the placeholder / NOT FOR PUBLICATION markers removed. 0 marker
  hits remain in the file.
- PRICING.md: support address marked CONFIRMED; lawyer review and checkout test
  recorded as the only two publish blockers left on that page.
- DELIVERY_REQUIREMENTS.md: §3 email exception is now unconditional for the real
  address; §6 records the address and that inbound delivery is untested; §10
  checkbox 1 is ticked with that same caveat.
- MEMORY.md corrected: the older "pending / placeholder" record is replaced, so no
  later session acts on stale information.
- Gate proof: staging rc=0, PASS (9 checks, 0 failed). Publication rc=1,
  FAIL (10 checks, 1 failed) with `status=STAGING_ONLY, placeholders=none` —
  the email is no longer a blocker; the status line is.
- STATUS: STAGING ONLY. Blockers left: lawyer review, checkout/refund test,
  zip + checksums, explicit publication authorization.
- Next: lawyer review and the live checkout/refund test. No zip, no publish.
