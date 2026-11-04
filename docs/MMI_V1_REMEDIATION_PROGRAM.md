# MMI V1 Remediation Program

Status: IN PROGRESS
Baseline branch: main
Baseline commit: 617d48a4980c6f1d0d6bafc168321c8410916e26
Work branch: feat/mmi-v1-single-contract-remediation

## Governing rule

MMI V1 is not accepted because a schema, recommendation, report, or stage label exists. Acceptance requires deterministic artifacts, reproducible tests, and a verifiable execution record. A stage may be COMPLETE only when its required artifacts and predicates are present. Unknown, unavailable, excluded, unsupported, and not-applicable are distinct outcomes.

## Live repository finding

The repository currently contains overlapping MMI implementations:
- `barrot_agent/mmi_v1.py`: broad MMI record, state machine, bounded traversal, freshness, idempotency, completeness report, and `MMIExecutionLedger`.
- `barrot_agent/ingestion/mmi_contract.py`: separate contract, enums, source/component/evidence models.
- `barrot_agent/ingestion/mmi_execution.py`: execution engine using the ingestion contract.
- `barrot_agent/ingestion/mmi_ledger.py`: separate hash-linked ledger.
- `barrot_agent/sources/mmi_adapter.py`: acquisition-target adapter.

This duplication is a current defect. The audit's claim that no MMI state model or ledger exists is stale relative to this baseline.

## V1 architectural decisions

1. Establish one canonical MMI domain contract and one versioned serialization format. Compatibility modules must be adapters; they must not own parallel enums, state machines, or ledgers.
2. Reuse `IntelligencePipeline`, `EvidenceNormalizationEngine`, `EvidenceStore`, `CrossCorroborationEngine`, `SourceIndependenceEngine`, `ClaimLifecycleEngine`, `MCPApprovalGate`, `VerifiedLearningStore`, `BarrotVerifier`, and `OutcomeEvaluator` through explicit adapters.
3. Preserve raw observations separately from derived interpretations and model-generated hypotheses.
4. Every source and evidence item must carry stable lineage: publisher/owner where known, canonical URI, retrieval URI, version, retrieval time, content digest, media type, byte or logical location, license/rights state, and provenance class. Missing fields remain explicitly unknown.
5. Scope is an explicit manifest of included paths/representations and exclusions. Completeness is computed only against that declared scope.
6. Component decomposition and provenance traversal are separate graphs. Each has depth 1..4, cycle detection, node/byte/time budgets, and a recorded termination reason.
7. Parsability is a first-class state: PARSED, PARTIAL, UNSUPPORTED, MALFORMED, EMPTY, UNAVAILABLE, NOT_PRESENT, NOT_APPLICABLE, UNKNOWN. Parser output must include source offsets/locations and dropped-content accounting.
8. Source independence cannot be inferred from different domains. Record publisher/owner, upstream dataset, canonical content fingerprint, syndication/derivation lineage, and independence decision plus rationale. Unknown independence never counts as independent.
9. Contradictions are append-preserved. Reconciliation creates versioned relationships; it never silently overwrites observations.
10. Negative knowledge requires a bounded, recorded search over a declared scope with query, sources, time, and completeness. A failed or empty search is not proof of absence.
11. Freshness policy is explicit and versioned per source class. Missing timestamps classify UNKNOWN, not STATIC.
12. Barrot-generated artifacts remain internal/model-derived and cannot count as external corroboration or independent sources.
13. The canonical MMI event ledger is append-only, hash chained, sequence-numbered, replayable, and fail-closed on malformed or tampered history. No compaction may delete canonical events. External anchoring is a separate optional control.
14. Protocol completeness and knowledge completeness are independent outputs. Neither is inferred from the other.
15. Self-upgrade candidates are downstream proposals. Only executable acceptance evidence can close a capability gap.
16. All state transitions are deterministic and evaluator-versioned. LLMs may propose extraction or targets but cannot decide acceptance or transition state.

## Required execution states

RECEIVED, AUTHORIZATION_CHECKED, ACQUIRED, PROVENANCE_CAPTURED, SCOPE_DECLARED, DECOMPOSED, REPRESENTATIONS_ASSESSED, EVIDENCE_NORMALIZED, CORROBORATED, GAP_ANALYZED, RECONCILED, LEARNING_EXTRACTED, CAPABILITY_ASSESSED, TARGETS_GENERATED, VERIFIED, COMPLETE, PARTIAL, BLOCKED, STALE, CONTRADICTED, UNAVAILABLE, NOT_IN_SCOPE.

Terminal result is computed from required stage predicates and artifacts. A COMPLETE stage label without its required artifacts is rejected.

## Acceptance gates

- Schema and migration compatibility.
- Acquisition/provenance and authorization failure modes.
- Scope and exclusions.
- Four-depth decomposition and provenance traversal, cycles, and budgets.
- Parser-state and dropped-content accounting.
- Idempotency, revalidation, and freshness.
- Observation/interpretation separation and offsets.
- Duplicate/syndication/independence handling.
- Contradiction and reconciliation preservation.
- Bounded negative knowledge.
- Protocol/knowledge completeness independence.
- Deterministic transitions and replay.
- Ledger append-only, tamper detection, crash recovery, and fail-closed behavior.
- Self-generated evidence exclusion.
- Specialized adapter conformance.
- Capability-gap closure requiring executable tests.
- Repository-state corroboration.
- No publication or self-modification before acceptance.
- Clean-checkout reproducibility.

## Implementation sequence

1. Select and document the single canonical contract; add compatibility adapters and remove parallel ownership.
2. Repair the canonical ledger and event schema; add replay and crash/tamper tests.
3. Add source, scope, parsability, and provenance lineage invariants.
4. Add bounded traversal and parser accounting.
5. Integrate existing acquisition, evidence, corroboration, learning, and approval components.
6. Add freshness, negative knowledge, reconciliation, and anti-self-reinforcement.
7. Implement deterministic completeness/state evaluation.
8. Add full acceptance matrix and CI gate.
9. Migrate existing MMI records without deleting source history.
10. Publish a reproducible acceptance report. Do not merge until all required gates pass.

## Evidence discipline

Every remediation item must be marked IMPLEMENTED, TESTED, BLOCKED, or DEFERRED with file/symbol references and CI evidence. No item is marked complete from syntax checks, generated recommendations, filenames, or an LLM assertion alone.
