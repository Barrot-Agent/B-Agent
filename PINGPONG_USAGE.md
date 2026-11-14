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

# Ping-Pong Refinement Engine — derived data only

The engine from main commit `f1708870` is preserved, but external-provider
behavior is default-deny. Deterministic heuristics are the default. This is
an optional helper for explicitly classified derived summaries, not the
baseline of all data processing.

- The API and CLI require an explicit data classification.
- Raw sources, source receipts, feature snapshots/stores, event timelines,
  forecast ledgers, market data, credentials, secrets and private records
  are rejected.
- LunaRoute requires an explicit live refiner, `allow_external=True`,
  `BARROT_ALLOW_EXTERNAL_REFINEMENT=1`, a public-derived classification,
  and an available key.
- CLI external mode requires both `--live` and `--allow-external-data`.
- Secret-like payloads are blocked. Payloads over 24,000 characters are
  rejected rather than truncated.
- Never send XRP raw evidence, exchange receipts, feature records, event
  timelines, forecasts, credentials or private material to this engine.
