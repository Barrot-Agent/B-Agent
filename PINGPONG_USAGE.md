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

report = refine_data(data)                       # live LunaRoute pool (needs LUNAROUTE_API_KEY)
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

## Standing rule

This engine is the **baseline of all data processing**: new data pipelines
should route their datasets through `refine_data` (or the CLI) instead of
ad-hoc one-pass cleanups, so every dataset converges to a measured fixed
point with a full provenance ledger.
