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
