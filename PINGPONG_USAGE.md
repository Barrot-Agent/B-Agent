# Ping-Pong Request System

## Overview

The `emit_pingpong_request` function allows Barrot-Agent to defer complex processing tasks to Sean's 22-agent entanglement system.

## Usage

```python
from emit_pingpong import emit_pingpong_request

# Create your payload
payload = {
    "task": "process_quantum_data",
    "priority": "high",
    "data": {"items": [1, 2, 3]}
}

# Emit the request
emit_pingpong_request(payload)
```

## Output

The function creates a `pingpong_request.json` file with the following structure:

```json
{
  "timestamp": "2025-12-30T11:39:52.503571+00:00",
  "payload": { ... },
  "origin": "barrot",
  "directive": "offload_pingpong",
  "notes": "Barrot defers to Sean's 22-agent entanglement system."
}
```

## Workflow

1. Call `emit_pingpong_request(payload)` with your data
2. The function generates `pingpong_request.json`
3. Commit the JSON file to GitHub
4. The external system (Sean's 22-agent entanglement system) picks up the request
5. Processing is offloaded to the external system

## Notes

- The generated `pingpong_request.json` file is excluded from version control by default (see `.gitignore`)
- To trigger the external system, you must manually commit and push the JSON file
- Timestamps are in ISO 8601 format with UTC timezone

---

# Ping-Pong Refinement Engine — the baseline of all data processing

`barrot_agent.refinement` refines any JSON-able data by ping-ponging between
models until the data **cannot be refined further** — a measured fixed point,
not a model's mood.

## How it decides to stop

Two independent signals, either one ends the run with `converged=True`:

| signal | meaning |
|---|---|
| `model_consensus` | the refining model returned `CONVERGED`, the critic returned `CONVERGED`, and no data change was accepted for `patience` half-rounds |
| `score_plateau` | the deterministic quality score (`scoring.py`: completeness/consistency/specificity/redundancy) has been flat for `patience` consecutive ping halves — cosmetic byte-churn is not refinement, so the loop stops regardless of model enthusiasm |

Non-converged exits: `max_rounds` (hard cap) and `pool_exhausted` (every
model in the pool failed a pass, after in-pool rotation and per-call retry
with backoff).

## Safety semantics

- **No silent data loss**: a rewrite is accepted only if the score does not
  regress. Non-improving rewrites are applied (they may still carry real
  semantic fixes the mechanical score cannot see) but count as unstable and
  feed the plateau counter.
- **Dynamic pool**: round r starts at `refiner[r % n]`; a failed actor hands
  the paddle to the next model within the same pass; the critic is always a
  different model than the one that just refined. Roles swap every round.
- **Transient errors** (timeouts, HTTP 429/5xx) are retried with exponential
  backoff (3 attempts); responses truncated by the token budget
  (`finish_reason=length`) are retried once with a doubled budget.
- **Ledger**: every half-round is appended to
  `ping-pongings/knowledge-base/refinement_log.jsonl`.

## Python API

```python
from barrot_agent import refine_data, refine_json_file, HeuristicRefiner

report = refine_data(data)                       # live OpenCode pool
report = refine_data(data, refiners=[HeuristicRefiner()], ledger=None)  # offline
report.converged, report.stop_reason, report.score_start, report.score_end
report.data        # the refined data (fixed point)
report.history     # per-half-round records

refine_json_file("doc.json")                     # in place
refine_json_file("doc.json", out_path="out.json")
```

## CLI

```bash
python3 scripts/pingpong_refine.py data.json             # in place, live pool
python3 scripts/pingpong_refine.py in.json -o out.json   # to file
echo '{"a": "x  x"}' | python3 scripts/pingpong_refine.py -
python3 scripts/pingpong_refine.py data.json --offline   # deterministic, no API
python3 scripts/pingpong_refine.py data.json --max-rounds 8 --no-ledger
```

Exit codes: `0` converged, `1` capped (`max_rounds`/`pool_exhausted`), `2` input error.

## Large documents: the patch pipeline (pp-refine/1.1.0)

The classic loop truncates its prompt echo at 24,000 chars. Documents above
that threshold are automatically routed through the **patch pipeline**
(`RefinementPipeline`, `refine_document`), which implements the full
10-step workflow:

```
SOURCE → AUDIT → SEGMENT → REFINE → GENERATE PATCHES → VALIDATE → APPLY
       → SEMANTIC EVALUATION → REGRESSION TEST → RECORD RESULTS
```

- **AUDIT** (`segmentation.audit_document`): size/depth/leaf profile, and
  whether segmentation is needed (threshold: 24,000 chars).
- **SEGMENT** (`segmentation.segment_document`): coverage-exact slot plan.
  Every leaf of the source is covered exactly once — `dict_keys` slots
  (key groups), `list_slice` slots (contiguous, ordered), and
  `string_range` slots (paragraph/sentence-bounded ranges of oversized
  string leaves). Each slot carries bounded sibling context. The coverage
  contract raises if the plan would skip anything, so no content can be
  silently dropped.
- **REFINE** (`RefinementPipeline._refine_slot`): each slot ping-pongs
  through the existing refiner pool (same `OpenCodeRefiner`/`HeuristicRefiner`
  engine); a candidate is rejected up front on mechanical or deterministic
  semantic regression, with the critique fed back for the retry.
- **GENERATE PATCHES / VALIDATE / APPLY** (`patches.py`): section diffs
  become targeted patches (`replace`/`set`/`delete`/`splice`) on canonical
  dot-paths. Every patch is hash-preconditioned against the live document;
  overlapping, conflicting (same path, different new value) and
  incompatible (DELETE vs SET) patches are rejected with an explicit cause;
  splices on one leaf apply in offset-safe order. Failed patches never
  abort the batch — they are rejected individually and reported.
- **SEMANTIC EVALUATION** (`semantics.py`): four separate results —
  **A.** mechanical score (unchanged `scoring.py`), **B.** semantic score,
  **C.** regression score, **D.** overall status (`improved`/`unchanged`/
  `regressed`). The deterministic core is offline, repeatable, and can
  only certify non-regression or flag loss (meaning coverage, numeric
  drift, key loss) — it never claims improvement. Claiming `improved`
  requires an **independent judge** (`LLMSemanticJudge` wired to a
  different model than the refiner) that has passed **calibration**: three
  reference cases (`CALIBRATION_CASES`) with known expected verdicts. An
  uncalibrated judge is downgraded and cannot vote `improved`; the
  deterministic core can veto any judge verdict.
- **REGRESSION TEST** (`patches.verify_against_original`): proves the
  final document against the original — every original leaf still present
  (unless a declared DELETE removed it), nothing changed outside declared
  patch scopes (smuggle detection), untouched containers keep their exact
  child structure, ordering preserved.
- **RECORD RESULTS** (`pipeline.py`): atomic per-section run state
  (`refinement_runs/<run_id>.json`) is the resume point; the persistent
  learning history (`refinement_history.jsonl`) records source
  identity/hashes, objective, patches, mechanical + semantic + regression
  results, failures and corrections, disposition, timestamp and
  implementation version (`pp-refine/1.1.0`).

Failure handling: if semantic quality regresses, the refinement is NOT
accepted merely because the mechanical score improved — the batch is
rolled back to the original and one corrected attempt is made with the
judge's regressions as critique; if that also regresses, the run is
recorded as `rolled_back`. A run is only `complete` when **no** section
failed or was skipped AND verification passed; otherwise it reports
`incomplete` with the exact section IDs. Interrupted runs resume with
`--resume <run_id>` (sections already `refined` are never repeated), and
a `(source, objective)` pair already converged in the learning history is
skipped unless `--force` is given.

```python
from barrot_agent import RefinementPipeline, refine_document, LLMSemanticJudge

out = refine_document(big_doc, objective="tighten and verify")
out["disposition"], out["mechanical"], out["semantic"], out["verification"]
out["run_id"]                          # resume/audit handle

pipe = RefinementPipeline(refiners, judge=LLMSemanticJudge(other_refiner))
out = pipe.run(big_doc, objective="...")
out = pipe.resume(out["run_id"])       # after interruption
```

CLI:

```bash
python3 scripts/pingpong_refine.py big.json --objective "tighten and verify"
python3 scripts/pingpong_refine.py big.json --resume ref-<id>
python3 scripts/pingpong_refine.py big.json --force    # ignore history
```

Exit codes: `0` complete/already_converged, `1` incomplete/rolled_back,
`2` input error. Small documents (<24K chars) keep using the classic loop.

Known limitations: judge context is capped at 20,000 chars per side
(`LLMSemanticJudge.max_chars`) — for very large documents the judge sees
a prefix; canonical dot-paths escape literal dots in keys, so keys
containing dots are not addressable.

## Standing rule

This engine is the **baseline of all data processing**: new data pipelines
should route their datasets through `refine_data` (or the CLI) instead of
ad-hoc one-pass cleanups, so every dataset converges to a measured fixed
point with a full provenance ledger.
