# MEMORY

Barrot's long-term memory. Append durable facts here when the user says "remember this".

## User
- Sean — Orchestrator. Calls me Barrot.

## Repo
- Barrot-Agent (B-Agent) lives on GitHub.
- Offline build: Termux on phone, 0.5B model, llama-cli, no internet.

## Agent setup
- OpenCode agent: `.opencode/agent/barrot.md`
- Model: `opencode/deepseek-v4.1-flash-free`
- Default agent in this repo: `barrot`
- Runtime: OpenCode free models only. No external providers.

## MCP
- Live stack (opencode.json): `github` remote + `docling` local + `searxng` local. Verified 2026-11-15: github 49 tools, docling 21 tools, searxng 4 tools.
- `github` — remote `https://api.githubcopilot.com/mcp/`; PAT read from `GITHUB_MCP_TOKEN` via `{env:GITHUB_MCP_TOKEN}` header. Token lives in the OpenCode service env (`opencode service set env GITHUB_MCP_TOKEN "$(gh auth token)"`). A service restart is required before MCP connections see new config or env.
- OAuth for github MCP does not work: GitHub's authorization server has no dynamic client registration.
- `docling` — `uvx --from "docling-mcp[local]" docling-mcp-server --transport stdio`; cold start is slow (tens of seconds), startup timeout is 240s.
- `searxng` — `npx mcp-searxng` against `http://127.0.0.1:8888`; start with `bash scripts/start_searxng.sh --daemon` (idempotent, logs to `~/.local/share/searxng/searxng.log`).
- Legacy `mcp_config.json` + `data/mcp_config.json` mirror the live stack for the Python MCP layer (`barrot_agent.mcp_sync`); they are not read by OpenCode.
- 2026-11-16 re-verify: `opencode api get /api/mcp` showed github `connected`, docling + searxng `pending` (later catalogued 21 and 4 tools); `tools.github.get_me` returned login `Barrot-Agent`. GitHub PAT in `~/.config/opencode/service.json` is valid. Tool namespaces churn because the phone cycles MCP connections under RAM pressure — not a config error.
- Phone RAM is tight (~3.6 GB total, <0.5 GB available). MCP connections cycle/reconnect under that pressure — that is resource churn, not a config error. Docling (Python) is the heaviest.

## Offline memory (gist compression)
- Source: Memorilla (Stanford, arXiv 2610.21375) — encodes a collection once, then a ~200M-param module produces 16 query-conditioned memory tokens for a frozen Qwen3-8B. Numbers: FactKG 84.33% vs 80.43% full context at 108x fewer tokens; 0.74 s vs 19.9 s at 512 docs (paper); NarrativeQA >4,000x compression.
- Barrot implementation: `barrot_agent/gist_memory.py` — stdlib, CPU, deterministic, extractive. 16 gist slots x 10 words, two-pass IDF selection, MMR redundancy penalty, measurement-tail extension (a number keeps its unit), source span kept for lookup. The width was raised from 6 to 10 after the long-context test showed 6-word windows orphaning `0.74` from `seconds`; total budget stays fixed at 160 words.
- Rules: fixed budget always; condition on the query; two passes; never generate text — extract verbatim; keep the raw source for names/numbers/dates.
- Verified failure modes of the real system: buried-clue test hallucinated a shellfish allergy and a wrong name/birthday; Hound of the Baskervilles plot QA 1/8 vs 5/8 full context. Gist = context/preferences; RAG = exact facts.
- Limits of our version: lexical only (no embeddings), so synonyms ("health issues" vs "diabetes") do not match.

## Agent leverage (from AGI video, verified part)
- Same model, different harness: GPT-6 Astra scored 62.7% (ARC standard) vs 99.9% (provider adapter with persistent reasoning state + compaction). Environment/tools/memory move the score more than the model name.
- Long-run prompt pattern: clear finish line, permission to self-check, `progress.md` memory file, room to run, stop only for truly undecidable items.
- ARC Prize explicitly says ARC-AGI-3 is not proof of AGI. "AGI is here" = hype; verify at arcprize.org before repeating claims.

## Hype filter calibration (proven 2026-11-15)
- Permanent evidence that the filter works on real transcripts; do not change the threshold without re-running both.
- Better Stack, video `lNpDxKfBlf8`: verdict `OK`; 3 applicable checks, 0 failed.
- Julia McCoy, video `us_pnC6ETNA`: verdict `HYPE`; 5 applicable checks, 2 failed — `benchmark_caveat` (quotes "isn't proof of AGI", then says AGI is here) and `funding_vs_intent` (asserts "built to make you afraid" from grant funding).
- Rule: 2+ failed applicable checks => `HYPE`; non-applicable checks return `passed=None` and do not count.
- Evidence spans are kept in the verdict (`checks[].evidence`); the tag is deterministic, not an LLM judgment.

## Infinite ingestion (built 2026-11-15)
- Package `barrot_agent/infinite_ingest/`: ingestor, transmuter, cross_analyzer, refiner, sources, storage, models, cli.
- CLI: `python -m barrot_agent.infinite_ingest.cli status|discover|seed|ingest|connect|refine`.
- Caps: 10 ingests/run, 1 refinement per capability per run, stop on rate limit (429/503), `data/raw` capped at 500 MB with oldest-first pruning.
- Dedupe: URL ledger + sha256 content hash; a URL is fetched once. HYPE raw records are stored for audit but never transmuted or allowed to refine.
- Every memory record is a verbatim source statement plus `source_url` and `retrieved_at`; `MemoryRecord.build` refuses missing provenance.
- Sources wired as HTTP adapters: YouTube transcripts, arXiv, Wikipedia, Hacker News, PubMed, OpenAlex, GitHub, generic web, local replay. SearXNG discovery is `discover` (local JSON API at 127.0.0.1:8888).
- Hype filter: `barrot_agent/hype_filter.py`, five checks, 2+ fails => HYPE. Verified: Memorilla video OK; "AGI is here" video HYPE (caveat overridden + motive asserted from funding).
- Cross-analyzer: shared rare terms across different source URLs, graph at `data/connections.json`; combined-capability lines are labelled `status: hypothesis`, never facts.
- Capability test: `data/capabilities/long_context_memory.json`; measures extractive recall of expected facts from the gist prompt, NOT LLM answer accuracy.
- First measured run: 0.00 -> 1.00 recall (5/5 facts), 96 records added, 17 bound, no revert. First pass was 0.80; two extraction defects were fixed (gist window width; 24 -> 48 record cap) before the clean run.
- Not wired: six extra MCP servers (phone RAM); these are Python adapters. Latent-token training / Qwen3-8B still needs a GPU.

## Evidence discipline (Sean, 2026-11-16)
- Two tracks, never mixed.
- DISCOVERY: invent freely — hypotheses, architecture, components, signatures, designs. Each invention gets label CONJECTURED, provenance (Barrot-invented + date + "no evidence yet"), a falsifier, and a test.
- EVIDENCE: never invent measurements, test outcomes, citations, file existence, thresholds, or verification status. Unknown stays UNRESOLVED. Not verified is COMPUTED/CONJECTURED, never VERIFIED. Signature match is not proof of equivalence. Invented thresholds are PROPOSED.
- Reason: an invented fact destroys the audit trail; an invented idea is the job.

## Geometry inventory (2026-11-16)
- No Geometry module/package exists. Only geometry-adjacent code is `barrot_agent/rendering/`.
- Real: incidence/boundary/non-manifold counting (`mesh_topology.py`), polygon triangulation with area-preservation test (`polygon_triangulation.py`), OBJ loading (`obj_mesh_loader.py`).
- Missing: stratification (0 hits), typed equivalence, certificates, exact arithmetic in geometry, geometric transformation, geometry signatures.
- State drift: `EvidenceState` has 7 labels (OBSERVED/PARSED/DERIVED/INFERRED/UNKNOWN/NOT_PARSABLE/NOT_APPLICABLE), not the required 8. The required 4-state VALID/INVALID/UNRESOLVED/NOT_APPLICABLE does not exist as one enum.

## PA1 v1.2 (2026-11-16)
- RETRACTED (Sean, 2026-11-16): the "Complete Bundle v1.2 Execution Plan" paste was a SUMMARY/recap, NOT the frozen file. Do NOT use its 8 target names (IDyOM, Intention vs Accident, Level-k, False-Belief, Multi-Agent ToM, Discovery Quality Gate), its report schema A-H, its kill-test wording, or its diagram. Not authoritative. The "Target 4 missing from diagram" contradiction is void.
- FROZEN PA1 = exactly the §5 / §6 / §7 text below, nothing more.
- File `PA1_FINAL_v1.2.txt` is still ABSENT on this container's filesystem (`wc`, `cat`, `find / -maxdepth 5` all fail). Sean's shell creates it; my shell does not share that mount. Do not claim the file exists.
- Content read from pasted text: §5 CONSTRUCT, §6 Target 1 safeguards, §7 execution. Sections 1-4 were NOT provided - UNRESOLVED, never claimed.
- Target identities 2-8 are NOT defined in §5-§7. §7 fixes only the order 1-2-4-5-3-6-7-8. Do not supply names from the retracted recap.
- §5: primary construct is R_L, not M. M_signed = S_L - E_C(S_L); R_signed_error = R_L - E_C(S_L). Positive M = composer underestimated. Reactivity flag: mean liking diff >0.3 AND 95% CI excludes 0. Manipulation failure != evidence against PA1. M3/M5 identical partitions, no overlap, tuning in train only, M5 must beat M3.
- §6: ITPRA all 5 components, each tagged [Huron Claim] or [Barrett Assumption], MISSING if not quantifiable. Primary metric held-out log-likelihood, min meaningful +0.05, preregistered N/power, equivalence test required, nonsignificant != redundant. 4-way ablation incl. M5-minus-recursion; recursion not proven if drop <0.05. Contradiction Register mandatory. PASS >0.05 reproducible; FAIL = powered negligible; INCONCLUSIVE = insufficient evidence.
- §7: order 1-2-4-5-3-6-7-8, one target, report, STOP, no auto-advance. Theory CLOSED, Target 1 only, Axiom FROZEN, Tau QUARANTINED.
- PA1 governs construct validation, not geometry. No geometry contract comes from it.
- STEP 1 LOCATE result (frozen §5-§7, whole-repo `*.py`, word boundaries, excl. .git/__pycache__): §5 = 0/9 constructs present, all MISSING. §6 = 0/11 procedures present, all MISSING. §7 is a process rule; no code artifact exists or should.
- §5 missing: S_L, E_C(S_L), R_L, M_signed, R_signed_error, probe/non-probe split, reactivity flag, manipulation check, M3/M5.
- §6 missing: ITPRA 5 components, [Huron Claim]/[Barrett Assumption] labels, MISSING marker, held-out log-likelihood, +0.05 minimum, preregistered N/power, equivalence test, 4-way ablation, recursion ablation, Contradiction Register, PASS/FAIL/INCONCLUSIVE.
- STEP 1b semantic alias re-check (signed_error, composer_estimate, latent, probe_flag, is_probe, nonprobe, reactivity, estimate vs actual, expectation, surprise, prediction_error, manipulation check, catch trial, overestimate, bias, metacognition): 0 alias upgrades. All 9 stay MISSING.
- Near misses examined and rejected: `gist_memory.py:4-6` latent vectors = Memorilla embeddings; `mcp_sync.py:428,537,614` `probe_*` = network reachability; `polymath_ingestion.py:378` "chemical synthesis and reactivity"; `analyze_reference.py:105` signed audio timing offset (+13ms bias vs +15ms push). None are §5 constructs.
- §6 Contradiction Register nuance: only 2 of 5 required fields exist (`supporting_evidence`, `contradicting_evidence` in `research/scientific_discovery.py:209,368,410`); `alternatives` as a register field, `missing`, `falsifier` are absent. Still MISSING, not PARTIAL.

## Phoenix sandbox (2026-11-16)
- `barrot_agent/sandbox/` is UNTRACKED in git. No checkpoint, no revert.
- Bug: sandboxed child died with `bionic/linker/linker_cfi.cpp:158 MapShadow CHECK`, exit -9 after 60s, so every experiment "failed". Cause: `RLIMIT_AS`. Measured threshold on this phone: 512/1024/1536/2048 MB all fail, 3072 MB passes, 0 (disabled) passes.
- Fix in `barrot_agent/sandbox/runner.py`: `MIN_MEMORY_MB = 3072 if sys.platform == "android" else 0`, and `__init__` clamps any requested limit >0 up to that floor. A lower limit measures the loader, not the experiment. `0` still means disabled.
- Proof: `tests/test_phoenix.py` 16/16, `tests/test_sandbox.py` 7/7, flake8 clean.
- `combine()` was never involved; all 4 combine tests passed before the fix.

## Geometry implementation (2026-11-16, authorized by Sean)- Built `barrot_agent/geometry/`: `states.py`, `object.py`, `signature.py`, `relations.py`, `__init__.py`. Additive only; no existing file modified.
- Scope deliberately minimal: 4-state/8-state contracts, typed object facade, structural signature; relational model. Stratification, certificates, exact arithmetic, equivalence registry, config space, robustness, minimal explanation remain unimplemented (designs G2-G11 in the gap-fill table).
- `GeomObject` is a facade over `rendering.mesh_topology.analyze_mesh_topology`; validation happens before normalization so bools/NaN/short tuples are rejected.
- Signature is relative: digest only means "same canonical form under this invariant set and transform class". Only RELABEL is supported; rotation/translation are rejected because the canonical form is not invariant under them.
- Relational edges require a witness; `boundary_of`/`closure_of`/`specializes`/`degenerates_to`/`derived_from` are antisymmetric, `specializes`/`derived_from` checked acyclic.
- Contradiction is a flag on `ConstraintResult`, not a fifth truth state. MMI `NOT_APPLICABLE` maps to `UNRESOLVED` because the 8-state vocabulary has no N/A.
- Canonicalization: coordinate-tied vertices are resolved by taking the lexicographically smallest form over their permutations, bounded at 1000 permutations; past the bound it raises instead of returning an order-dependent digest. Winding is significant.
- Verified: 72 geometry tests pass, flake8 clean, existing rendering tests 19/19 pass.
- Pre-existing unrelated failure: `tests/test_phoenix.py::test_passing_experiment_unlocks_level_two` (sandbox run `gist-budget`). Proven unrelated by running it with the whole `geometry` package removed — still fails.

## Refinement log

### Refinement 2026-11-15 - long_context_memory
- Before: recall=0.00 (0/5 facts), records=0.
- After: recall=1.00 (5/5 facts), records=17, prompt_chars=5075, violations=0.
- Delta: +1.00 recall; 96 records added, 17 bound, no revert, no rate limit.
- First pass: 0.00 -> 0.80; two extraction defects were then fixed (gist window width; extraction cap), and a clean run measured 0.00 -> 1.00.
- Harness: deterministic extractive recall over the gist prompt; not an LLM answer-accuracy benchmark.
- Sources: https://www.youtube.com/watch?v=lNpDxKfBlf8 @ 2026-11-15T23:22:24Z; https://raw.githubusercontent.com/snap-stanford/memorilla/main/README.md @ 2026-11-15T23:22:24Z.

## Power log

### Power 2026-11-16 - pa1_frozen_state_v1_2
- Source: MEMORY.md PA1 block (Sean, 2026-11-16)
- Test: frozen-state markers: RETRACTED, FROZEN PA1, 0/9, 0/11, near-miss list
- Result: RECORDED
- Artifact: sha256:69d629f7ca21b1e63466ab081130d2a6a99aaf968c4739c5b43feafc5c090ee6

## 2026-11-16 — geometry verdict
- Decision: barrot_agent/geometry/ IS the Structural Discovery Core, partially.
  Verdict A+B. Do not rebuild it. Do not call it missing.
- Hard fact: no compare_invariants anywhere in repo; signature digest is
  canonical-form-under-RELABEL only. Translation/winding change the digest —
  that is intentional, not a bug.
- Hard fact: V3 snapshot (checkpoints 9a8b5f08/5fa5534e/3c0a9a66, .barrot MMI
  dirs, governed bundle executor, barrot/task branch, gitlab remote) does NOT
  exist in this tree. Treat that snapshot as another clone's state.

## 2026-11-17 — RE meta-analysis verdicts
- The 10-stage convergence loop exists ONLY as prose in BARROT-12AM-MASTER.md.
  Zero code implements it (TRANSFER_SUCCESS / anti_cheat_passed / AXIOM_FORGE
  grep = 0 in .py). It cannot fail automatically, so it cannot improve.
- Biggest hole in the loop: Anti-Cheat is self-interrogation, not an executed
  ablation. Second: Second-Order promotes to Universal on an unmeasured "improves".
- Loop variants scored: original 37, V1 Ablation 69, V2 Witness 82, V3 Ledger 95
  (those were judgment-rubric numbers, checkability 40 / preservation 30 /
  containment 30 — NOT measured). Superseded 2026-11-17 by real transmute
  scores: V1 ablation-only 1/10 tests 93881, V2 witness+chain 10/10 996389,
  V3 durable ledger 10/10 994393 (applied). Use the measured numbers.
- Repo has NO `work` branch. Only main.
- Repo-wide: 1028 collected tests, 95/120 scripts with no test reference,
  10 byte-identical duplicate pairs, 16 zero-byte root files, 31 sys.path hacks.
- pytest.ini --cov-fail-under=70 corrupts every scoped run AND transmute scoring.
  That is rank 2 on the wishlist and should be fixed before any transmutation.

## 2026-11-17 — PERMANENT RULE: query transmutation
- Sean's standing instruction: every user message gets transmuted, not answered
  literally. Line 1 of every response is exactly:
    [Original] <what was asked> -> [Transmuted + Gap-Filled] <what you will do>
- Gap-fill categories, checked every time: missing input data, missing test or
  proof, missing failure path, missing cost/risk, missing rollback, missing
  verification that the change did what it claims.
- Bound: gap-fill is additive. If it contradicts the original, the original wins
  and the conflict is stated. If it would touch money, secrets, live state or the
  live publish path: name it and stop for approval, do not do it.
- Written into .opencode/agent/barrot.md (QUERY TRANSMUTATION section) so it
  survives sessions. Local fiction-term scan: clean.

## 2026-11-17 — measured market facts (do not re-derive, do not forget)
- Signal accuracy 45.5% (772/1697) in web/signal_accuracy.json. Below chance.
- web/latest_signal.json publishes confidence 0.0 with score 44, 18.6 days old.
  scripts/signal_summary.py:135 requires 0 < confidence, so the writer is not
  validating.
- web/paper_trading_state.json: position_size 0.0124, position_product null,
  avg_entry_price 80436.84, 126 trades. Corrupt book, shipped unnoticed.
- trading/ has no fee, slippage, drawdown, stop or kelly code. RiskManager has
  exactly one rule ($25 cap). client_order_id = fresh uuid per call.
- Two ledgers disagree: data/signal_ledger.jsonl (45 lines) vs
  web/signal_history.jsonl (1697 records).
- scripts/verify_artifacts.py now catches all of the above; exit 1 with 4 errors.
- scripts/pillars_check.py: hf_space stage=BUILD_ERROR as of 2026-11-17 (live
  Space), deploy_sync OK, system_prompt_fiction clean. It flags, it does not
  strip — corrected the wording in barrot.md.

## 2026-11-17 — CORRECTION: signal asset != traded asset
- The 45.5% accuracy is XRP sentiment (check_signal_accuracy.py:13 prices
  'ripple'). The paper trader is BTC-USD (coinbase_paper_trader.py:14) and never
  reads latest_signal.json (grep = 0 hits). It makes its own Groq call from the
  ticker + last 20 trades.
- Neither latest_signal.json nor latest_signal_btc.json has a product field.
  Asset identity lives only in prose text.
- Therefore: three parallel market models (XRP sentiment, BTC tape, BTC state
  file) with no wire. This is the #1 paradigm-sync defect — wishlist item 0.
- verify_artifacts.py now reports 5 errors on the live repo: position without
  product, confidence 0.0, stale 18.6 days, product missing, accuracy 45.5%.

## 2026-11-17 — PHASE 1-4 CHECKPOINT (pre-BPE-v1)

### Rules now permanent
- TRANSMUTE RULE (already in MEMORY.md above): 2-3 variants, measure, keep winner,
  delete losers, git checkpoint first, report What/Why/Proof.
- QUERY GAP-FILL RULE: every user message is transmuted before answering.
  Line 1 is exactly `[Original] <asked> -> [Transmuted + Gap-Filled] <will do>`.
  Six gap-fill categories: missing input data, missing test/proof, missing failure
  path, missing cost/risk, missing rollback, missing verification.
  Conflict rule: original wins, conflict stated. Money/secrets/live state: stop
  for approval, do not act. Written into .opencode/agent/barrot.md.

### Phase 1 — scorer fix (commit 5792fa8)
- Root cause was TWO coverage gates: pytest.ini --cov-fail-under=70 AND
  pyproject.toml [tool.coverage.report] fail_under = 70.
- Fix: gate removed from pytest.ini; fail_under = 0 in pyproject; CI full-suite
  step owns --cov-fail-under=70 (measured 77.57%).
- transmute.py gained --no-cov, adaptive tie band max(TIE_EPS, jitter), and abort
  on missing --tests path. Scoped run rc 1 -> 0; transmute wall 32724 -> 3948ms.

### Phase 2 — dedupe (commit 96b8258)
- 10 byte-identical pairs -> 8 groups: 5 shimmed, 2 hash-locked, 1 structural.
- Shims: scripts/ + tools/mem_palace -> barrot_agent/mem_palace;
  scripts/granite_model_config -> barrot_agent/tools;
  utils/score_to_signal -> barrot_agent/analysis;
  scripts/deploy_huggingface -> barrot_agent/orchestration (CLI delegate);
  barrot_agent/tools/trial_tracker -> barrot_agent/monetization.
- NOT shimmed: core/hrm_ternary vs hf_space/hrm_ternary (standalone Space,
  app.py imports bare hrm_ternary); grant_generator x2 (prints on import).
  Both hash-locked in tests/test_duplicate_shims.py.
- Cost: +5 sys.path.insert guards (26 pre-existing -> 31 total). Die with
  `pip install -e .`.

### Phase 3 — cleanup (commit f109189)
- 16 zero-byte root files moved to archive/debris-20261116/ (1 git mv, 15 mv).
  Nothing deleted. Root zero-byte count 16 -> 0. 1048 tests still collect.
- Inventories in results/re_wishlist.md (listed, not fixed): 31 sys.path.insert,
  8 bare except, 94 of 121 scripts with no test reference.

### Phase 4 — meta RE + MMI + gap fill + rule (commits e0496f4, 388fff8, 2a8a790, 3fed755, 8e9e468)
- Loop: anti-cheat replaced by executed ablation + hash-chained ledger
  (scripts/witness_loop.py, V3, 10 tests). 10-stage loop was prose only.
- results/mmi_mastery_wishlist.md: 51 items (item 0 + 50), every Why measured.
- Key market facts: accuracy 45.5% (772/1697, XRP only); confidence 0.0 published;
  signal 18.6 days stale; paper book position without product; no fee/slippage/
  stop/drawdown; $25 is the only risk rule; two ledgers disagree (45 vs 1697).
- ITEM 0: signal measures XRP, paper trader trades BTC-USD, zero coupling.
  Neither signal file has a product field. Three parallel market models.
- scripts/verify_artifacts.py: 22 tests, reports 5 errors on the live repo.

### Gap fill summary — results/gap_fill_log.json
- 20 gaps total: 4 applied, 5 detected, 11 logged. 10 critical, 8 high, 2 medium.
- NOTE: the "19 gaps / 4 applied / 4 detected / 11 logged" figure was correct
  before the product_missing gap was added in commit 8e9e468. Current truth is 20.

### Test baseline
- 1080 collected, 1079 passed, 1 skipped (real-runtime tier). exit 0, ~4m24s.

### origin/work — audited 2026-11-17, NOT merged, 0 commits ported
- origin/work is an UNRELATED lineage: merge-base = none. 841 commits, 245 files,
  2025-11-19..2026-11-16. main: 861 commits, 1352 files. Diverged, not ahead/behind.
- 841 commits = 393 ping-pong cycles + 89 pulse snapshots + 76 merges + 157
  workflow churn + 126 PR plans. Nothing real and non-duplicate.
- 155 paths only on work; 138 with content nowhere in main. 33 unique .py: 30
  already exist under barrot_agent/, 3 unwanted (coin-app presale, superseded
  pingpong_emitter.py). 17 shared files differ and work always holds the stub
  (transmute.py 1131B vs 15144B).
- Never port: delete-main-branch.sh (destructive) and 5 flagged-vocabulary files
  (glyphs/*_glyph.yml, memory-bundles/shrm-v2-config.json,
  simulation-stack/shrm-v2-config.yml).
- Work is an ARCHIVE. Local branch `work` = 0732187, tracks nothing, kept as
  placeholder until Sean says delete. Full evidence: results/port_log.md.
- Backup of main-wip kept outside git: ~/barrot/backup-20261117/
  (untracked.tar.gz 31 entries, tracked.patch 2854 lines).

### pytest is not hermetic (measured 2026-11-17)
- Every `pytest -q` run rewrites 36 TRACKED paths: .barrot/collaboration_records/*
  (generated_at + EXECUTION_TIMESTAMP), barrot_capability_audit.json,
  data/evolution/confidence_calibration.json, data/research/
  riemann_hypothesis_harvest.json, ping-pongings/knowledge-base/refinement_log.jsonl,
  and drops a new feedback_loops/feedback_loop_*.json.
- Verified: 0 non-time semantic lines changed. It is harness churn, not test logic.
- Therefore a clean working tree requires reverting the churn after each pytest run
  (`git checkout -- .` + rm the new feedback_loop file). Backup of one such churn:
  ~/barrot/backup-20261117/test-run-churn-0909.patch.
- Open fix (not done): point those writers at tmp_path. Own transmute run.

### Book project — grok-100k-business (started 2026-11-17)
- Location: book/grok-100k-business/. Contract is toc.yaml; build_book.py measures
  320 words/page (code + HTML comments excluded), emits dist/book.md +
  dist/build_report.json.
- Stated 297 pages; supplied TOC units total 216; the 81-page difference is
  explicitly assigned to `proposed` Part Six (35p) + appendices A-F (46p).
  Sean has NOT confirmed those; labeled proposed everywhere.
- Drafted: front matter + Part One = 35.4/45 pages (79%). Phase A (Part Two,
  ch7-12) drafted = 40.5/44 pages (92%). Whole book 76.9/89 drafted pages (86%).
  Outlined: ch13-29. Proposed (unbuilt): Part Six + appendices A-F.
- Polish order is ch-07, ch-08, ... one chapter per commit. Ch 7 = 7.4/8,
  ch 8 = 7.4/8 after repair; both evidence-audited against docs.x.ai.
- Phase A completed 2026-11-17; ch-07..ch-12 status=draft in toc.yaml. Test guard:
  12 book tests pass; full suite 1091 passed / 1 skipped. Awaiting GO for Part Three.
- Grok facts verified 2026-11-17 (docs.x.ai): Grok Bot = cloud computer + multi-bot
  handoffs + routines + memory + MCP/API; Grok Build = TUI/headless/ACP,
  `grok -p`, `grok inspect`, install via x.ai/cli/install.sh; pricing grok-4.7
  $2/$6 per M (<200K), grok-build-0.1 $1/$2 (256K), tools $5/1k search + $5/1k
  code exec, collections $2.50/1k, batch -20%, cached input $0.50/M.
- Grok Build controls verified 2026-11-17: `--max-turns N` is the only documented
  run bound (no token budget flag, no documented non-zero exit on limit);
  `--sandbox workspace|devbox|read-only|strict` (off by default, Landlock/Seatbelt,
  child network blocked only in read-only/strict and only on Linux, no allowlist);
  `--allow`/`--deny` (deny wins), `--always-approve`/`--yolo`, `--tools`/`--disallowed-tools`,
  `--no-auto-update` for CI, `grok agent stdio` = ACP.
- Grok Bot isolation, exact doc wording: "Files and sign-ins on the shared computer
  aren't isolated per Bot and can remain there." Never write "Bots are not a
  security boundary" - the docs do not say that.
- Own RE method is written down: results/RE_METHOD.md (order, first-vs-last,
  done-vs-guessing, 3 recurring mistakes, 11-box checklist). Core rule: a claim is
  true when deleting its evidence changes an executable result, not when a model
  says so. Check the pointer before the prose (mcp_config.json:94 pointed at a
  missing barrot_agent/mcp_registry.json).
- Snapshot script (Sean's /tmp/full_snapshot.sh) has 2 defects: git quotePath
  breaks section 2 on the poincaré filename; section 6 find precedence is wrong.
- MCP server spec (5 tools) is INCOMPLETE: message truncated inside tool 4
  (reverse_engineer) and tool 5 never arrived. run_foundry_cycle has no Foundry to
  call; flight_recorder_replay has one mission only. check_capability can be real
  from barrot_capability_audit.json.
- FIELD TRACK (queued 2026-11-17, NOT started - needs GO FIELDS): 8 topics in
  order - cymatics, resonance/sympathetic, frequencies/harmonics/Fourier, acoustic
  field, EM field, toroidal (engineering vs model), quantum field (real QFT vs pop),
  noetic (speculative). 3 layers, tag every claim, never mix: L1 Established
  (measured, citation + units + conditions), L2 Applied (engineering practice,
  names a build/test/vendor doc), L3 Speculative (hypothesis or metaphor, carries
  its own falsifier, never supports an L1/L2 claim). Each topic: definition, math/
  mechanism, real experiment, production example, what it is NOT, falsifier. One
  reverse-engineered example per topic. No skill promotion until a prediction on a
  NEW case is made and tested. Caps $2 / 15 min per topic, 2 rounds max, Flight
  Recorder per topic. Gate: Ch 8 pushed (done: ceda46a37) AND Sean says GO FIELDS.
- Trap for the field track: "free energy" and "Planck-scale" are in
  scripts/pillars_check.py FICTION_TERMS. That check only scans hf_space/app.py,
  so Layer 3 wording is safe in docs but must never enter the deployed surface.
- Foundry does not exist yet (0 hits for "foundry" in *.py). "Learn via Foundry" is
  aspirational until it is built; until then the track runs on RE_METHOD +
  Flight Recorder.
- Track 1 cymatics done 2026-11-17: docs/fields/track-01-cymatics.md. Gate result -
  frequency ordering predicted then confirmed (sqrt(m2+n2), worst error 0.16%);
  per-axis nodal counts only predictable for non-degenerate modes. Membrane test,
  not a plate. Skill promotion blocked until one physical plate experiment.
- Query transmutation is the standing format for every Sean query: ORIGINAL / GAP /
  TRANSMUTED / EXECUTE / SHOW BOTH, and gaps get filled with [FILLED GAP] instead
  of questions.
- Ping-pong routing protocol (2026-11-17): caps 2 rounds default / $2 per task /
  15 min; advice only, no external AI can authorize commits. External ChatGPT and
  Meta AI are NOT wired in this runtime - only free-model subagents are available,
  and they cost $0. Log every round to results/flight_recorder/.
- "Grok Swarm" is not a documented product; written as a pattern, not a SKU.
- Foreword attribution pending; test enforces the ATTRIBUTION PENDING block.
- INCIDENT 2026-11-17: `git ls-files --others | xargs rm` deleted the untracked
  project. Recovered from dist/book.md. Never bulk-delete untracked files here.

## 2026-11-18 — Phase 1 product staged: paid-issue PR pack
- `products/github-pr-template-pack-self-guided/`, branch
  `phase1/digital-downloads-paid-issue-pr`. Template 1 only; Templates 2-7
  locked. Status STAGED, independently verified PASS WITH CAVEATS, not published.
- Product: "Ship a Paid-Issue PR in 2 Hours — GitHub Template Pack". $9 Field
  (templates), $19 Operator (kit), $39 Team (10 seats + support). Direct net
  $7.60/$16.60/$34.60 after 10% + $0.50; marketplace 30%.
- 6 templates (5 Markdown + 1 CSV), 4 functional Python modules, 76 tests,
  stdlib only, no network. 9 hard gates, 7 intake stop rules, 3-hour effort cap,
  $30/hour floor, 120-minute timebox with CLAIM HOLDS/BROKEN.
- Market snapshot 2026-11-18: 5,319 open `label:bounty` issues; 6/100 state an
  amount (median $525, range $450-$600); 112 merged PRs, pooled median 1.11h,
  52.7% <=2h (review latency, not effort). Demand for this pack is unmeasured:
  pre-registered 30-day test kills at <3 sales with >=300 views.
- Verification: separate agent. Round 1 FAIL found 10 claim defects; fixed all
  (E-13 $6.30, 30% fee range, unsupported 94% sentence, committed wording,
  support 41.5 min, bracket/non-URL validators, Field README gate, doc wording).
  Link existence is not checked (offline by design) and is documented.
- Never: merge to main, publish a listing, change a live price, transact, or
  mark any of the 10 named components Active without HEAD + test log. All 10
  remain PROPOSED.
- Publish blockers: support email, legal name/address, governing law, lawyer
  review, live checkout/refund test, zip+checksums, Sean's written approval.

## 2026-11-18 — PERMANENT PRODUCT RULES (v2.2 / v2.3.1)
- v2.2: digital downloads ONLY. No offers of labour. A product is files plus a
  self-guided checklist. Template 4 (offers of labour) is DELETED and must not
  come back.
- v2.3.1: secrets come from env vars or GitHub Secrets only. Never write a secret
  value to a file, a log, or chat.
- Store only readily accessible data: specs, sources, templates, logs, HEAD, STATUS.
- Dynamic role-shift across the 8 roles; sandbox first.
- Transmute every query to: Intent + Best Outcome + Compliant Path + Sandbox Test
  + Log Proof.
- Never merge, publish, or change a price without Sean's explicit approval.
- Banned terms on the product surface (scan must be 0): service, consulting,
  done-for-you, audit for you, we'll fix, we fix your repo, paid issue fixing,
  workflow fixing, repo audit, 1:1, live support, repair service.
- Scan scope = compliance surface: README.md, PRODUCTS_MATRIX.md, products/,
  docs/money/. The rest of the repo is code and historical corpus, so a literal
  whole-repo zero is not achievable and must not be reported as if it were.
- 2026-11-18 state: compliance-surface scan = 0. Whole-repo = 894 hits (code
  filenames such as github_service.py, historical corpora). Reported, not hidden.

## 2026-11-18 — product renamed + README rewritten
- `products/ship-paid-issue-pr-in-2-hours/` -> `products/github-pr-template-pack-self-guided/`
  (git mv, 46 paths; product content re-titled "GitHub PR Template Pack — Self-Guided").
- `products/drafts/citation-audit-service/` -> `products/drafts/citation-audit-checklist/`.
- `products/templates/service-template.md` and `saas-mcp-template.md` deleted;
  remaining templates = 6, one per surviving category (advertising, course,
  download, ebook, marketplace, trading tool).
- PRODUCTS_MATRIX rows for offers of labour and SaaS removed; rows renumbered 1-6.
- Root README.md rewritten to the Foundry structure: status, current product,
  10 PROPOSED components, 8 roles, how to run, compliance, blockers, HEAD.
- Product tests still 76/76 after the rename; release gate still 9/9.
- Internal Python package is still named `paid_issue_kit` (name only, domain term).
  Not renamed: it would touch 46 files, manifests, logs and tests, and needs its
  own transmute cycle plus Sean's approval.
