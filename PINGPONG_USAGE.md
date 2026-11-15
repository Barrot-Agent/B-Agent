# Ping-Pong Request and Refinement System

## External request handoff

The legacy emit_pingpong_request interface declares a handoff to an external 22-agent system. Its authentication, permissions, receipt path and data flow are NOT VERIFIED. Do not treat it as a live integration or commit payloads to trigger an external system without explicit authorization.

## Refinement engine

The Ping-Pong refinement engine provides deterministic normalization and a patch-based pipeline for large JSON documents. It is a data-quality/refactoring component, not the XRP prediction engine and not a source-verification system.

### Data classification and safety

- Offline deterministic refinement is the default.
- data_classification is mandatory. Allowed local classes are derived_summary, public_derived_summary, public_documentation, and public_research_note.
- Immutable classes include raw_source, source_receipt, feature_snapshot, feature_store, event_timeline, forecast_ledger, market_data, credentials, secrets, and user_private.
- Immutable evidence must never pass through this component.
- External LunaRoute calls are disabled unless the caller passes allow_external=True, the environment contains BARROT_ALLOW_EXTERNAL_REFINEMENT=1 and BARROT_LIVE_REFINEMENT_APPROVED=1, the classification is one of public_derived_summary, public_documentation, or public_research_note, the refiner is constructed with the same classification, and the API key is available.
- Secret-like strings and payloads larger than 24,000 characters are rejected before transfer. Large documents are segmented into bounded sections; each section is independently checked.
- A classification is an explicit caller assertion, not an automatic content classifier. Do not label a payload public unless its source and rights have been checked.
- No external call is made by the default CLI, scheduled ingestion or test suite.

### Fixed-point engine

The small-document engine alternates refiners and critiques until model consensus or a deterministic score plateau. It uses a hard round cap, rotates to another refiner on failure, retries transient 429/5xx/timeouts, and records each half-round in a JSONL ledger.

### Large-document pipeline (pp-refine/1.1.0)

The main-branch upgrade adds a resumable 10-stage process:

    SOURCE → AUDIT → SEGMENT → REFINE → GENERATE PATCHES → VALIDATE → APPLY → SEMANTIC EVALUATION → REGRESSION TEST → RECORD RESULTS

- Audit and segmentation: every source leaf must be covered exactly once; slots are bounded to the model output budget and preserve order.
- Patch generation: targeted replace, set, delete, and splice operations use canonical paths and hash preconditions.
- Conflict handling: overlapping or incompatible patches are rejected with a recorded cause.
- Rollback: batches can be rolled back exactly. Verification detects missing content, undeclared deletions, changed paths outside patch scopes, and smuggled changes.
- Semantic evaluation: deterministic checks detect loss and factual drift. An independent judge may claim improvement only after passing three reference calibration cases; deterministic checks can veto regressions.
- Resumability: per-section state and source hashes are persisted. A completed source hash, objective and classification is not repeated. Resume requires the original classification.
- Run safety: run IDs are filename-safe; path traversal and accidental run-ID overwrite are rejected.

### Python API

    from barrot_agent.refinement import HeuristicRefiner, refine_data, refine_document

    small = refine_data(
        data,
        refiners=[HeuristicRefiner()],
        data_classification="derived_summary",
    )

    large = refine_document(
        document,
        objective="normalize formatting without changing facts",
        refiners=[HeuristicRefiner()],
        data_classification="public_documentation",
    )

External use additionally requires caller opt-in, both external authorization environment variables, an eligible public classification, matching LunaRoute adapter and valid key. This is a separate explicit action; no model dispatch is performed by this documentation or by the default runtime.

### CLI

The CLI requires --classification. It defaults to offline mode, prints the result to stdout, and never overwrites the source file.

    python3 scripts/pingpong_refine.py report.json --classification derived_summary
    python3 scripts/pingpong_refine.py report.json --classification public_documentation --out report.refined.json
    python3 scripts/pingpong_refine.py large.json --classification public_research_note --objective "normalize" --offline

External mode additionally requires --live, --allow-external-data, BARROT_ALLOW_EXTERNAL_REFINEMENT=1, BARROT_LIVE_REFINEMENT_APPROVED=1, an eligible public classification and a valid key. Replacing an existing output requires --force-output.

### Live verification

scripts/live_refine_verify.py is a manual verification driver for the public repository capability audit. It requires BARROT_LIVE_REFINEMENT=1 and both external authorization variables; it writes to a unique run-specific artifact and refuses to overwrite evidence. It is not called by a workflow.

The default GitHub Actions test suite is mocked/offline. The pingpong.yml Groq workflow remains quarantined on integration with no permissions and an always-false job. The Cognitive PingPong Engine workflow remains quarantined as well.

### Limitations

The deterministic score measures completeness, consistency, specificity and redundancy; it does not measure factual truth or XRP forecasting accuracy. The semantic judge sees bounded prefixes (20,000 characters per side in the current implementation), and uncalibrated judges cannot claim improvement. This component must never refine canonical XRP receipts, market snapshots, feature stores, event timelines or forecast ledgers.
