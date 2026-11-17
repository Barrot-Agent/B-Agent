# RE WISHLIST — Barrot V3

Date: 2026-11-17
Branch inspected: `main` (repo has **no `work` branch** — only `main` + `origin/main`)
HEAD: `93896c2`
Method: file inventory, sha256 duplicate detection, symbol inspection, test collection,
executed test modules. No code was changed. Analysis only.

Evidence commands used: `git ls-files`, `sha256sum`, `wc -l`, `diff`, `grep -rl`,
`pytest --collect-only`, `pytest -o addopts=`.

---

# JOB 1 — META REVERSE-ENGINEERING THE LOOP

## Where the loop actually lives

```
RE -> Isomorphism Probe -> Anti-Cheat -> Failure Taxonomy -> Second-Order
   -> Axiom Forge -> Emergence Lens -> Plugin -> Skill -> Phoenix
```

Source: `BARROT-12AM-MASTER.md:13-95`. **It exists nowhere else.**

```
TRANSFER_SUCCESS   0 .py files
anti_cheat_passed  0 .py files
AXIOM_FORGE        0 .py files
NOVELTY_SCORE      0 .py files
ISOMORPHISM PROBE  0 .py files
```

The loop is 100% prose. No runner, no schema validator, no ledger. That is the
first-order finding: **the loop cannot fail automatically, so it cannot improve
automatically.**

## Stage-by-stage

| # | Stage | Actually doing | Input | Output | Fails / wastes / misses |
|---|---|---|---|---|---|
| 1 | RE | "Extract pure rules, rebuild from rules only" | source artifact | free-text rule list | **Undefined.** No rule IDs, no count, no hash. Anti-Cheat later asks "quote the exact rule" — impossible to check mechanically against an unnumbered blob. Every downstream claim inherits this ambiguity. |
| 2 | Isomorphism Probe | 1 LLM call, one shot, fixed 3-cycle (Music→Rendering→Metacognition) | rule list + target domain | 4-field report incl. `TOKEN_COUNT` | No baseline. No task difficulty control ("smallest non-trivial" is unverifiable). `TOKEN_COUNT` is self-reported → unmeasurable. All 3 cycles run even if cycle 1 fails → wasted calls. |
| 3 | Anti-Cheat | 2 self-answered questions | success claim | `LEAKED KNOWLEDGE` or pass | **Biggest hole.** "If I delete that rule, does it still work?" is answered by the same model that just claimed success. It is introspection, not evidence. Zero ablations executed. |
| 4 | Failure Taxonomy | Labels failures A/B/C/D | failure list | type per failure | No decision procedure. TYPE B (inversion) and TYPE D (false friend) both mean "works but meaning changed" — a model can pick either. No rule for 0 or 2 matches. Nothing enforces one type per failure. |
| 5 | Second-Order Probe | Apply NEW_PATTERN back to source | pattern | universal / domain-specific | **No metric for "improve".** A yes on an unmeasured question promotes a pattern to Universal. Highest false-positive surface in the loop. |
| 6 | Axiom Forge | Invent 1 axiom, re-run same task | TYPE C failure | axiom + retest | Retest is the *same* task the axiom was fitted to → memorization by construction. "Never generate near-identical again" has no enforcement: axioms are not hashed, so duplicates recur. Provisional status depends on "next full cycle", but no cycle record exists. |
| 7 | Emergence Lens | Hybrid task across 2 domains | ≥2 successes or ≥1 axiom | novelty 0-3 | `NOVELTY_SCORE` has no rubric. Trigger condition includes "≥1 provisional axiom", so a single invented axiom can trigger emergence. "Smallest hybrid task" is unconstrained → unbounded. |
| 8 | Plugin | — | — | — | **Undefined.** Appears in the loop name only. |
| 9 | Skill | — | — | — | **Undefined.** Appears in the loop name only. |
| 10 | Phoenix | Level gate + evidence requirement | evidence dict | level unlock | Real code (`barrot_agent/phoenix.py`, 22K, `LevelSpec`, `PowerLocked`, `EvidenceRequired`, `promote_from_sandbox`). But **not wired to the loop** — `PROMOTE_TO_PHOENIX` is a prose field with no writer. Repo Phoenix state is level 0. |

### Structural defects (measurable)

- Stages: 10. Defined: 7. Undefined: 3 (RE, Plugin, Skill).
- Machine-checkable artifacts: 1 (the JSON log schema at `BARROT-12AM-MASTER.md:76-92`) — and that schema is not implemented anywhere.
- Self-reported numbers: 2 (`TOKEN_COUNT`, `NOVELTY_SCORE`) → both unverifiable.
- Executions per cycle: 0 automated, 1 LLM call per stage, fixed schedule, no early exit.
- Contradictions preserved: `TYPE C` only. No place to store a contradiction.
- Feedback path into code: none. The loop produces prose, never a test, never a file.

## Transmuted loop variants

### V1 — FASTER: "Ablation Loop" (5 stages)

```
RE(rule IDs + hash) -> Probe -> ABLATION -> Log -> Phoenix
```

- Taxonomy, second-order, emergence, axiom-forge are demoted from **stages** to
  **derived fields computed from the log**, not extra LLM turns.
- Anti-Cheat becomes an executed ablation: delete rule *r*, re-run, compare.
  One mechanical run, not two introspective questions.
- Early exit: if probe fails and no rule can be deleted to flip it, stop. No
  cycle 2 and 3 on a dead branch.

### V2 — SIMPLER: "Witness Loop" (3 stages)

```
CLAIM -> WITNESS -> LOG
```

- One claim per cycle: "rule R transfers to domain D for task T".
- Witness = {rule id, ablation result, task hash, token count measured by the
  harness, timestamp}.
- No claim without a witness. No witness without an executed ablation.
- Taxonomy collapses into: did the ablation flip the result? yes/no → that single
  bit replaces A/B/C/D.
- Cheapest to build and the hardest to fake.

### V3 — ROBUST: "Ledger Loop" (7 stages)

```
RE(ids+hash) -> Probe -> ABLATION -> CLASSIFY(deterministic) -> FORGE(bounded, axiom-hashed)
   -> LEDGER(hash-chained) -> Phoenix(evidence-gated)
```

- Taxonomy becomes a deterministic classifier with explicit precedence:
  missing rule → C; rule present but sign-flipped → B; rule present but operand
  changed → D; magnitude-only → A. First match wins; two matches = UNRESOLVED.
- Axiom Forge writes `axiom_sha256`; a near-duplicate axiom is rejected by hash
  distance, not by instruction.
- Every cycle appends a record containing `prev_sha256` (the MMI append-only rule).
- Phoenix promotion requires the witness + the full chain, so `PROMOTE_TO_PHOENIX`
  can no longer be a prose field.

### Score (judgment rubric — explicitly NOT measured)

Rubric: artifact checkability 40 · information preservation 30 · failure
containment 30. "Checkable" = a program can verify the artifact without asking
the model.

| Variant | Checkable (40) | Preserves info (30) | Contains failure (30) | **Total** | Stages | LLM calls/cycle | Build cost |
|---|---|---|---|---|---|---|---|
| Original | 16 (1/10) | 15 (C only) | 6 (3 undefined, 2 self-reported) | **37** | 10 | 3 | — |
| V1 Ablation | 24 (3/5) | 24 | 21 | **69** | 5 | 3 | low |
| V2 Witness | 40 (3/3) | 15 (taxonomy collapsed) | 27 | **82** | 3 | 1-2 | lowest |
| V3 Ledger | 40 (7/7) | 30 | 25 | **95** | 7 | 3 | highest |

Reading: V2 wins on cost, V3 wins on trust, V1 is the migration path.
Note the trade: V2 scores 82 because it throws away the taxonomy. If you care
about A/B/C/D, V2 is wrong for you and V3 is right.

---

# JOB 2 — REPO-WIDE SCAN

Inventory: 1324 tracked files, 532 tracked `.py` (751 including untracked),
106 test files, 632 test functions, **1028 collected tests**.

MEASURED BASELINE (executed, full suite, coverage gate disabled):

```
python -m pytest -o addopts= -q
1027 passed, 1 skipped, 8 subtests passed in 299.69s (0:04:59)
```

The suite is green. Nothing below is "tests are failing" — every item is
structural: config gate, debris, duplication, untested surface. That distinction
matters: the repo is not broken, the *instrument* is miscalibrated.

## A. BROKEN

| Item | Evidence | What it does | Why it's a target | Variant to try |
|---|---|---|---|---|
| 16 zero-byte files in repo root | `find . -maxdepth 1 -type f -size 0` → `Metacognition,` `Music.` `Rendering,` `Axiom` `Emergence` `Failure` `Phoenix` `Plugin` `Second-Order` `Skill` `Anti-Cheat` `Isomorphism` `45` `10` `volume.` `.termux_dna_harvest.log` | Nothing. Debris from a broken heredoc/paste. | They pollute root, break filename globs, and one of them (`Phoenix`) collides with module search paths. | Delete-only commit; or move to `quarantine/`. Zero risk, immediate clarity. |
| `pytest.ini` global coverage gate | `--cov-fail-under=70` + `-v` in `addopts` | Forces 70% coverage on **every** invocation | Any scoped run (4 files) measures 14% and exits non-zero even with 72/72 tests passing. `scripts/transmute.py` runs scoped tests → a passing variant can be scored worse than a failing baseline. | Variant A: keep 70% only in CI (`-o addopts=` in transmute). Variant B: `--cov-fail-under=0` default + explicit CI job. |
| 31 files with `sys.path.insert` | `grep -rl sys.path.insert` | Import-by-hack | Makes module identity ambiguous; a file can import a *different* copy of itself (see duplicates below). | Replace with `pyproject.toml` package install (`pip install -e .`); the repo already has `pyproject.toml`. |
| 8 files with bare `except:` | `grep -l "except:"` | Swallows everything | Masks real failures in a repo whose whole thesis is evidence integrity. | `except Exception as exc:` + log. Mechanical, testable. |
| 95 of 120 scripts have no test reference | `grep -rql <name> tests/` | One-shot utilities | Any transmutation of them is unmeasured → violates rule "no tests, write one first". | Auto-generate a smoke test per script that runs `--help`. |

## B. DUPLICATED (byte-identical, sha256)

```
100%  3 copies  mem_palace.py          scripts/ tools/ barrot_agent/
100%  2 copies  source_registry.py     scripts/ barrot_agent/ingestion/
100%  2 copies  source_acquisition.py  scripts/ barrot_agent/ingestion/
100%  2 copies  sandbox.py             scripts/ barrot_agent/
100%  2 copies  hrm_ternary.py         core/ hf_space/
100%  2 copies  granite_model_config.py  barrot_agent/tools/ scripts/
100%  2 copies  score_to_signal.py     barrot_agent/analysis/ utils/
100%  2 copies  deploy_huggingface.py  barrot_agent/orchestration/ scripts/
100%  2 copies  trial_tracker.py       barrot_agent/monetization/ barrot_agent/tools/
100%  2 copies  grant_generator.py     barrot_agent/monetization/ barrot_agent/tools/
empty 3 copies  __init__.py            repair/ repository/ tools/
```

Near-clones (not identical, same job):

```
emit_signal_btc.py      vs emit_signal.py        86% identical (29/200 lines differ)
knowledge_distill_btc.py vs knowledge_distill.py 88% identical (16/127)
knowledge_ingest_btc.py  vs knowledge_ingest.py  70% identical (36/120)
```

Why these are good targets: a `.btc` variant that is 86% of its sibling means the
divergence is a **parameter**, and two files drift independently forever. Every
`_btc` fix has to be applied twice, and tests only cover one of them.

Variant: collapse to one module with `asset="btc"|"xrp"` and a config dataclass;
keep the old names as thin wrappers for one release. Proof: `diff` → 0 files,
both test modules green, and a parametrized test asserting both assets take the
same code path.

## C. SLOW / OVERSIZED

| File | Lines | Risk |
|---|---|---|
| `barrot_agent/orchestration/repository_repair.py` | 2379 | Single largest unit; 1133-line test file. Every repair touches it. |
| `barrot_agent/research/scientific_discovery.py` | 2190 | Research logic and orchestration in one file. |
| `scripts/barrot_agent.py` | 1609 | Name collides with the `barrot_agent/` package — import confusion. |
| `barrot_agent/smart_agent.py` | 1223 | No matching test file. |
| `barrot_agent/orchestration/shared_runtime.py` | 1175 | Shared by everything; no isolated test. |

Plus: `--cov=barrot_agent` on every run instruments 11k+ lines even for a 4-file
subset (measured TOTAL 11324 statements, 14% covered in 18s).

## D. SAME JOB 2+ WAYS

| Cluster | Files | Lines | Problem |
|---|---|---|---|
| Memory | `mem_palace.py`×3, `barrot_memory_query.py` 136, `barrot_memory_recall.py` 214, `barrot_connectome_memory.py` 359, `barrot_repo_recall.py` 93, `gist_memory.py` 450, `semantic_memory.py` 133 | 1481 | 7 distinct memories with no declared precedence. Which one is authoritative? Unanswered in code. |
| Signal | `emit_signal.py` 213, `emit_signal_btc.py` 200, `emit_signal_with_hrm.py` 85, `signal_summary.py` 298, `score_to_signal.py`×2 | 820 | 3 emitters, 1 of which is 86% a clone. |
| Ingest | `knowledge_ingest.py` 114, `_btc` 120, `knowledge_distill.py` 127, `_btc` 127, `frontier_ingest.py` 114, `infinite_ingest/` 10 modules | 2990 | Two ingestion stacks: script-level and package-level. No shared contract. |
| MMI | `mmi_v1.py` 536, `mmi_adapter.py` 157, `ingestion/mmi_contract.py` 231, `mmi_execution.py` 221, `mmi_ledger.py` 99, `scripts/mmi_compiler.py` 20, `mmi_evaluate.py` 169 | 1433 | 5 MMI state vocabularies; only `geometry/states.py` bridges them explicitly. |
| Reporting | `apex_audit_summary.py`, `benchmark_summary.py`, `signal_summary.py`, `daily_digest.py` | — | 4 summary generators, 4 output shapes, 0 tests. |

## E. UNTESTED CORE MODULES (no `tests/test_<name>.py`)

```
barrot_agent/mcp_*.py           11 modules (adapters, approval, discovery, github,
                                pingpong, provenance, registry, sandbox, scheduler,
                                scorer, targets)
barrot_agent/barrot_brain.py     gpt_api.py    kimi_integration.py
barrot_agent/mem_palace.py       reconfiguration.py
barrot_agent/repo_state_corroborator.py         smart_agent.py
barrot_agent/specialist_role_engine.py          ternary.py
```

21 top-level modules. The `mcp_*` block is the riskiest: 11 modules, no direct
tests, and it is the layer the agent uses to touch the outside world.

---

# JOB 3 — TOP 20 RE WISHLIST (ranked by impact)

**[1] The Loop Itself** — `BARROT-12AM-MASTER.md` — 10 stages, 0 lines of code, 0 checkable artifacts. Everything else in the repo inherits its weakness: claims survive without witnesses. — **Transmutation:** build V2 Witness Loop as the minimum (claim → witness → log), then V3 ledger. — **Proof:** a fake claim must be rejected by the harness (negative test), real claim accepted; cycle wall-time before/after; count of artifacts a program can verify (0 → 3).

**[2] `scripts/transmute.py` scoring** — `scripts/transmute.py:38-40,112` — the scorer decides what "best" means for the whole repo, but it can be gamed by the `pytest.ini` coverage gate and it trusts a regex-parsed tail for pass counts. — **Transmutation:** parse pytest's JSON report (`--json-report`) or `--tb=no -q` counters instead of regex; read `addopts` out of the loop; add a `--no-cov` flag. — **Proof:** run on a known-passing subset: today it exits non-zero on coverage (14% vs 70%); after, it reports 1.0. Same winner chosen on a synthetic pair.

**[3] Memory cluster** — 7 modules / 1481 lines — no declared authority order; agent cannot know which memory is true. — **Transmutation:** one `MemoryStore` interface (write/query/hash) with adapters; precedence table in config. — **Proof:** a test that writes to all 7 and asserts one deterministic read order; line count 1481 → target <800; query timing before/after.

**[4] `_btc` duplication** — `emit_signal_btc.py` 86%, `knowledge_distill_btc.py` 88%, `knowledge_ingest_btc.py` 70% — every fix applied twice, tests cover one. — **Transmutation:** asset parameter + config object; wrappers deprecated. — **Proof:** parametrized test over `xrp`+`btc` on one code path; `diff` between the old pair → n/a.

**[5] `pytest.ini` coverage gate** — `pytest.ini` — breaks every scoped run and corrupts transmute scoring. — **Transmutation:** move `--cov-fail-under` to CI only. — **Proof:** `pytest tests/test_geometry_*.py` exits 0 with 72 passed.

**[6] 16 zero-byte root files** — repo root — debris that collides with module names (`Phoenix`, `Plugin`, `Skill`, `Axiom`). — **Transmutation:** delete or quarantine. — **Proof:** `find . -maxdepth 1 -size 0` → 0; import check unchanged.

**[7] `repository_repair.py` 2379 lines** — `barrot_agent/orchestration/repository_repair.py` — biggest unit, highest blast radius. — **Transmutation:** split into detect / plan / apply / verify; keep public API. — **Proof:** `tests/test_repository_repair.py` (1133 lines) must stay green before/after; per-function timing; cyclomatic proxy = branch count.

**[8] Untested `mcp_*` block** — 11 modules — the agent's outside-world interface has no direct tests. — **Transmutation:** contract tests with a fake transport; one per module. — **Proof:** coverage of `barrot_agent/mcp_*` before (near 0) vs after; no network calls in tests.

**[9] `sys.path.insert` ×31** — repo-wide — ambiguous module identity; a file can import a different copy of itself. — **Transmutation:** `pip install -e .` + remove hacks. — **Proof:** `python -c "import barrot_agent"` from `/tmp` works; grep count → 0; full suite green.

**[10] MMI vocabulary sprawl** — 5 state vocabularies / 1433 lines — contradictions can be silently re-labelled between layers. — **Transmutation:** one canonical `EvidenceState` + explicit lossy mappings (as `geometry/states.py` already does). — **Proof:** property test: for every state, `roundtrip(state)` never upgrades UNRESOLVED → VERIFIED.

**[11] Ingest stacks (script vs package)** — `knowledge_ingest*.py` vs `infinite_ingest/` — 2990 lines doing one job two ways. — **Transmutation:** package wins; scripts become CLI shims. — **Proof:** same input file → same output hash through both paths before deprecation.

**[12] `barrot_agent/geometry` 4 missing layers** — classification, stratification, correspondence, certificates — the core is real but incomplete; the gaps are known and bounded. — **Transmutation:** add invariant-set registry first (makes the registry a registry, not a constant). — **Proof:** 2 sets, digest stability test for `mesh.v1`, relabel invariance ×50 on the new set.

**[13] Phoenix ↔ loop disconnect** — `barrot_agent/phoenix.py` — promotion is prose; state is level 0. — **Transmutation:** a single `promote(claim_with_witness)` entry point that refuses resourceless claims. — **Proof:** negative test — promotion without witness raises `EvidenceRequired`.

**[14] 95 untested scripts** — `scripts/*.py` — transmutation rule 5 ("no tests, write one first") is currently unenforceable. — **Transmutation:** auto-smoke `--help` test per script + import check. — **Proof:** smoke suite runs in <30s; number of scripts with at least one test 25 → 120.

**[15] `score_to_signal.py` duplicated in two trees** — `barrot_agent/analysis/` + `utils/` — 12 lines each, identical; wrong one gets edited. — **Transmutation:** keep package copy, delete utils copy, re-export. — **Proof:** import from both names resolves to same `__file__`.

**[16] `scripts/barrot_agent.py` name collision** — 1609-line script vs `barrot_agent/` package — import confusion under `sys.path` hacks. — **Transmutation:** rename to `barrot_cli.py`. — **Proof:** no ambiguous imports; suite green.

**[17] Summary/report generators ×4** — `apex_audit_summary.py`, `benchmark_summary.py`, `signal_summary.py`, `daily_digest.py` — four output shapes, zero tests. — **Transmutation:** one `report_schema.json` (already exists at `reporting/report_schema.json`!) + one writer. — **Proof:** all four outputs validate against the existing schema.

**[18] `results/transmute_log.json` cross-machine drift** — entries carry `/data/data/com.termux/...` paths that cannot be re-verified here. — **Transmutation:** normalize paths to repo-relative + `host` field. — **Proof:** every entry's target resolves on this host or is explicitly marked `foreign`.

**[19] `barrot_agent/gist_memory.py` 450 lines, untested** — compression logic with no test. — **Transmutation:** property test (round-trip preserves key facts), then variant with simpler encoding. — **Proof:** fact-retention rate on a fixed corpus, encode/decode ms.

**[20] 8 bare `except:`** — repo-wide — silent failure in an evidence-first repo. — **Transmutation:** explicit exception classes + log line. — **Proof:** inject a failure, assert it appears in the log (today it disappears).

---

## Top 3 to do first

**1. The Loop (rank 1).** It is the only item where the cost of not doing it compounds:
every other target is "we cannot prove this is better" *because* the loop has no
witness mechanism. V2 Witness Loop is ~3 stages, 1-2 LLM calls, and it makes the
transmute rule ("never claim a repair succeeded unless validation confirms it")
mechanically enforced instead of aspirational.

**2. `pytest.ini` + `transmute.py` scoring (ranks 2, 5).** Cheapest possible
unblock. Right now a 72/72-passing scoped run exits non-zero; that means the
scoring engine that judges every future transmutation is reading a corrupted
signal. Fix cost: minutes. Payoff: every later measurement becomes trustworthy.

**3. Memory cluster (rank 3).** 1481 lines, 7 authorities, zero declared
precedence. This is the substrate the loop writes into — building a witness
ledger on top of an ambiguous memory means the witness lands in the wrong store.
Do it before any loop persistence work.

Deliberately **not** first: geometry layers (rank 12), `repository_repair` split
(rank 7). Both are large, both are currently well-tested, and neither blocks
measurement. They are the right work *after* the instrument is fixed.

---

## Status of this document

Analysis only. No production file modified. No fix applied.
`results/transmute_log.json` received one `kind: "meta_analysis"` record with the
rubric, the variant scores, and the ranked list ids.
Full suite re-run as a clean baseline: **1027 passed, 1 skipped, 4m59.69s**.
tau = 0.707 remains quarantined and unused.
