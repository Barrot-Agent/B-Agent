import json
import time

from barrot_agent.mmi_v1 import (
    BoundedTraversal,
    ComponentRecord,
    EvidenceRecord,
    Freshness,
    FreshnessPolicy,
    Idempotency,
    MMIEngine,
    MMIExecutionLedger,
    MMICompletenessReport,
    MMIResult,
    MMIStateMachine,
    ParseState,
    Reconciliation,
    ProvenanceClass,
    SourceRecord,
    StageOutcome,
    StageRecord,
    classify_idempotency,
)


def complete_stages():
    return [
        StageRecord(name, StageOutcome.COMPLETE)
        for name in MMIStateMachine.ORDER
    ]


def add_valid_corroboration(record):
    source_specs = [
        ("s1", "https://source-a.example/report", ProvenanceClass.EXTERNAL_PRIMARY, "source-a.example"),
        ("s2", "https://source-b.example/report", ProvenanceClass.EXTERNAL_SECONDARY, "source-b.example"),
    ]
    source_by_id = {source.source_id: source for source in record.source_graph}
    for source_id, uri, provenance_class, group in source_specs:
        if source_id in source_by_id:
            source = source_by_id[source_id]
            source.uri = uri
            source.provenance_class = provenance_class
            source.independence_group = group
        else:
            record.source_graph.append(
                SourceRecord(
                    source_id=source_id,
                    uri=uri,
                    provenance_class=provenance_class,
                    independence_group=group,
                )
            )

    record.evidence.extend([
        EvidenceRecord(
            evidence_id="corroboration-e1",
            claim="test claim",
            claim_id="claim-001",
            state=ParseState.OBSERVED,
            source_ids=["s1"],
        ),
        EvidenceRecord(
            evidence_id="corroboration-e2",
            claim="test claim",
            claim_id="claim-001",
            state=ParseState.OBSERVED,
            source_ids=["s2"],
        ),
    ])
    record.corroboration_results.append({
        "status": "CORROBORATED",
        "claim_id": "claim-001",
        "supporting_evidence_ids": ["corroboration-e1", "corroboration-e2"],
        "independent_source_ids": ["s1", "s2"],
        "independent_sources": 2,
    })


def complete_record_with_two_sources():
    record = MMIEngine().create_record(
        "independent-corroboration-001",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )
    record.stages = complete_stages()
    record.provenance = {"source": "fixture"}
    add_valid_corroboration(record)
    return record


def test_mmi_complete_requires_all_protocol_stages():
    record = MMIEngine().create_record(
        "ing-001",
        {"name": "test-dataset"},
        {"source": "external"},
    )
    record.stages = complete_stages()
    record.provenance = {"source": "test"}
    record.source_graph.append(
        SourceRecord(
            source_id="s1",
            uri="https://source-a.example/test",
            provenance_class=ProvenanceClass.EXTERNAL_PRIMARY,
            independence_group="source-a.example",
        )
    )
    record.evidence.append(
        EvidenceRecord(
            evidence_id="e1",
            claim="test claim",
            state=ParseState.OBSERVED,
            source_ids=["s1"],
        )
    )
    add_valid_corroboration(record)

    assert MMIStateMachine.evaluate(record) == MMIResult.COMPLETE


def test_blocked_stage_blocks_mmi():
    record = MMIEngine().create_record(
        "ing-002",
        {"name": "test-dataset"},
        {"source": "external"},
    )
    record.stages = complete_stages()
    record.stages[2] = StageRecord(
        "DECOMPOSED",
        StageOutcome.BLOCKED,
        "parser unavailable",
    )

    assert MMIStateMachine.evaluate(record) == MMIResult.PARTIAL


def test_dual_depth_is_four():
    record = MMIEngine().create_record(
        "ing-003",
        {},
        {},
    )

    record.component_max_depth = 4
    record.source_max_depth = 4

    assert record.validate() == []


def test_component_depth_cannot_exceed_four():
    record = MMIEngine().create_record(
        "ing-004",
        {},
        {},
    )
    record.component_map.append(
        __import__(
            "barrot_agent.mmi_v1",
            fromlist=["ComponentRecord"],
        ).ComponentRecord(
            component_id="c5",
            parent_id="c4",
            depth=5,
            state=ParseState.PARSED,
        )
    )

    assert any("component depth" in e for e in record.validate())


def test_barrot_generated_evidence_cannot_be_independent():
    record = MMIEngine().create_record(
        "ing-005",
        {},
        {},
    )

    record.source_graph.append(
        SourceRecord(
            source_id="s1",
            uri="barrot://generated",
            provenance_class=ProvenanceClass.BARROT_GENERATED,
        )
    )

    record.evidence.append(
        EvidenceRecord(
            evidence_id="e1",
            claim="generated claim",
            state=ParseState.DERIVED,
            source_ids=["s1"],
            independent=True,
        )
    )

    assert any(
        "cannot be independent" in e
        for e in record.validate()
    )


def test_observation_and_hypothesis_are_distinct():
    assert ParseState.OBSERVED != ParseState.HYPOTHESIZED
    assert ParseState.DERIVED != ParseState.INFERRED


def test_bounded_traversal_stops_at_four():
    children = {
        1: [2],
        2: [3],
        3: [4],
        4: [5],
        5: [],
    }

    traversal = BoundedTraversal(max_depth=4)
    result = traversal.walk([1], lambda n: children[n])

    assert result == [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
    ]


def test_bounded_traversal_handles_cycles():
    children = {
        "a": ["b"],
        "b": ["c"],
        "c": ["a"],
    }

    result = BoundedTraversal(max_depth=4).walk(
        ["a"],
        lambda n: children[n],
    )

    assert [x[0] for x in result] == ["a", "b", "c"]


def test_freshness_policy():
    now = time.time()
    policy = FreshnessPolicy()

    assert policy.classify(now - 60, now) == Freshness.VOLATILE
    assert policy.classify(
        now - 2 * 86400,
        now,
    ) == Freshness.TIME_SENSITIVE
    assert policy.classify(
        now - 100 * 86400,
        now,
    ) == Freshness.SLOW_CHANGE
    assert policy.classify(
        now - 500 * 86400,
        now,
    ) == Freshness.STATIC


def test_idempotency():
    assert classify_idempotency(None, "abc") == Idempotency.NEW_DATASET
    assert classify_idempotency(
        "abc",
        "abc",
        previous_complete=True,
    ) == Idempotency.IDENTICAL_REVALIDATION
    assert classify_idempotency(
        "abc",
        "abc",
        previous_complete=False,
    ) == Idempotency.PARTIAL_REINGESTION
    assert classify_idempotency(
        "abc",
        "def",
    ) == Idempotency.SOURCE_UPDATED


def test_ledger_hash_chain_and_tamper_detection(tmp_path):
    path = tmp_path / "mmi_ledger.jsonl"
    ledger = MMIExecutionLedger(path)

    ledger.append({"stage": "RECEIVED"})
    ledger.append({"stage": "VERIFICATION"})

    assert ledger.verify() is True

    lines = path.read_text().splitlines()
    tampered = json.loads(lines[0])
    tampered["stage"] = "TAMPERED"

    path.write_text(
        json.dumps(tampered) + "\n" + lines[1] + "\n"
    )

    assert ledger.verify() is False


def test_evidence_lineage_contains_required_identity_fields():
    evidence = EvidenceRecord(
        evidence_id="e1",
        claim="claim",
        state=ParseState.OBSERVED,
        source_ids=["s1"],
        observed_at="2026-09-17T00:00:00Z",
        content_hash="sha256:test",
    )

    lineage = evidence.lineage_key()

    assert "e1" in lineage
    assert "s1" in lineage
    assert "2026-09-17T00:00:00Z" in lineage
    assert "sha256:test" in lineage


def test_complete_stage_labels_without_required_artifacts_are_partial():
    engine = MMIEngine()
    record = engine.create_record(
        "artifact-gate-001",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )

    record.stages = [
        StageRecord(name, StageOutcome.COMPLETE)
        for name in MMIStateMachine.ORDER
    ]

    assert MMIStateMachine.evaluate(record) == MMIResult.PARTIAL


def test_missing_provenance_prevents_completion():
    engine = MMIEngine()
    record = engine.create_record(
        "artifact-gate-002",
        {"name": "fixture"},
        {},
    )

    record.stages = [
        StageRecord(name, StageOutcome.COMPLETE)
        for name in MMIStateMachine.ORDER
    ]

    record.source_graph.append(
        SourceRecord(
            source_id="s1",
            uri="fixture://source",
            provenance_class=ProvenanceClass.EXTERNAL_PRIMARY,
        )
    )
    record.evidence.append(
        EvidenceRecord(
            evidence_id="e1",
            claim="test claim",
            state=ParseState.OBSERVED,
            source_ids=["s1"],
        )
    )
    add_valid_corroboration(record)

    assert MMIStateMachine.evaluate(record) == MMIResult.PARTIAL


def test_missing_evidence_prevents_completion():
    engine = MMIEngine()
    record = engine.create_record(
        "artifact-gate-003",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )

    record.stages = [
        StageRecord(name, StageOutcome.COMPLETE)
        for name in MMIStateMachine.ORDER
    ]

    record.source_graph.append(
        SourceRecord(
            source_id="s1",
            uri="fixture://source",
            provenance_class=ProvenanceClass.EXTERNAL_PRIMARY,
        )
    )
    record.evidence.clear()
    add_valid_corroboration(record)
    record.evidence.clear()
    record.corroboration_results.clear()

    assert MMIStateMachine.evaluate(record) == MMIResult.PARTIAL


def test_missing_corroboration_prevents_completion():
    engine = MMIEngine()
    record = engine.create_record(
        "artifact-gate-004",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )

    record.stages = [
        StageRecord(name, StageOutcome.COMPLETE)
        for name in MMIStateMachine.ORDER
    ]

    record.source_graph.append(
        SourceRecord(
            source_id="s1",
            uri="fixture://source",
            provenance_class=ProvenanceClass.EXTERNAL_PRIMARY,
        )
    )
    record.evidence.append(
        EvidenceRecord(
            evidence_id="e1",
            claim="test claim",
            state=ParseState.OBSERVED,
            source_ids=["s1"],
        )
    )

    assert MMIStateMachine.evaluate(record) == MMIResult.PARTIAL


def test_unstructured_checked_result_is_not_corroboration():
    record = complete_record_with_two_sources()
    record.corroboration_results = [{"status": "checked"}]

    assert MMIStateMachine.evaluate(record) == MMIResult.PARTIAL
    report = MMICompletenessReport.build(record)
    assert report["protocol_complete"] is False


def test_zero_independent_sources_cannot_complete_corroboration():
    record = complete_record_with_two_sources()
    record.corroboration_results = [{
        "status": "CORROBORATED",
        "independent_sources": 0,
        "scope": "LOCAL_DETERMINISTIC_FIXTURE",
    }]

    assert any(
        "distinct independence groups" in error
        for error in record.validate()
    )
    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED
    report = MMICompletenessReport.build(record)
    assert report["protocol_complete"] is False
    assert report["corroboration_complete"] is False
    assert report["result"] == MMIResult.BLOCKED.value


def test_same_publisher_group_is_not_independent_corroboration():
    record = complete_record_with_two_sources()
    record.source_graph[1].uri = "https://source-a.example/alternate-report"
    record.source_graph[1].independence_group = record.source_graph[0].independence_group

    assert record.corroboration_complete() is False
    assert any("distinct independence groups" in error for error in record.validate())
    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_unhashable_evidence_state_blocks_corroboration():
    record = complete_record_with_two_sources()
    record.evidence[0].state = []

    errors = record.validate()
    assert any("invalid evidence parse state" in error for error in errors)
    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_two_distinct_external_groups_can_corroborate():
    record = complete_record_with_two_sources()

    assert record.corroboration_complete() is True
    assert MMIStateMachine.evaluate(record) == MMIResult.COMPLETE
    report = MMICompletenessReport.build(record)
    assert report["protocol_complete"] is True
    assert report["result"] == MMIResult.COMPLETE.value


def test_missing_independence_group_blocks_corroboration():
    record = complete_record_with_two_sources()
    record.source_graph[1].independence_group = ""

    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_model_generated_source_cannot_corroborate_external_claim():
    record = complete_record_with_two_sources()
    record.source_graph[1].provenance_class = ProvenanceClass.BARROT_GENERATED

    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_independent_group_count_must_match_declared_count():
    record = complete_record_with_two_sources()
    record.corroboration_results[0]["independent_sources"] = 1

    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_multiple_sources_from_one_group_do_not_inflate_independent_count():
    record = complete_record_with_two_sources()
    record.source_graph.append(
        SourceRecord(
            source_id="s3",
            uri="https://api.source-b.example:443/second-report",
            provenance_class=ProvenanceClass.EXTERNAL_SECONDARY,
            independence_group="source-b.example",
        )
    )
    record.evidence.append(
        EvidenceRecord(
            evidence_id="corroboration-e3",
            claim="test claim",
            claim_id="claim-001",
            state=ParseState.OBSERVED,
            source_ids=["s3"],
        )
    )
    record.corroboration_results = [{
        "status": "CORROBORATED",
        "claim_id": "claim-001",
        "supporting_evidence_ids": [
            "corroboration-e1",
            "corroboration-e2",
            "corroboration-e3",
        ],
        "independent_source_ids": ["s1", "s2", "s3"],
        "independent_sources": 2,
    }]

    assert record.corroboration_complete() is True
    assert MMIStateMachine.evaluate(record) == MMIResult.COMPLETE


def test_contradictory_independent_evidence_can_complete_without_forced_unanimity():
    record = complete_record_with_two_sources()
    claim_id = "claim-contradictory"
    record.evidence = [
        EvidenceRecord(
            evidence_id="e-support",
            claim="test claim",
            claim_id=claim_id,
            state=ParseState.OBSERVED,
            source_ids=["s1"],
            supporting=True,
        ),
        EvidenceRecord(
            evidence_id="e-conflict",
            claim="test claim",
            claim_id=claim_id,
            state=ParseState.OBSERVED,
            source_ids=["s2"],
            supporting=False,
        ),
    ]
    record.corroboration_results = [{
        "status": "CONTRADICTORY",
        "claim_id": claim_id,
        "independent_source_ids": ["s1", "s2"],
        "independent_sources": 2,
        "supporting_evidence_ids": ["e-support"],
        "contradicting_evidence_ids": ["e-conflict"],
    }]
    record.reconciliation.append({
        "relationship": Reconciliation.CONTRADICTS_EXISTING.value,
        "evidence_ids": ["e-support", "e-conflict"],
    })

    assert record.corroboration_complete() is True
    assert MMIStateMachine.evaluate(record) == MMIResult.COMPLETE


def test_contradictory_unhashable_evidence_state_fails_closed():
    record = complete_record_with_two_sources()
    claim_id = "claim-contradictory-unhashable"
    record.evidence = [
        EvidenceRecord(
            evidence_id="e-support",
            claim="test claim",
            claim_id=claim_id,
            state=ParseState.OBSERVED,
            source_ids=["s1"],
            supporting=True,
        ),
        EvidenceRecord(
            evidence_id="e-conflict",
            claim="test claim",
            claim_id=claim_id,
            state=[],
            source_ids=["s2"],
            supporting=False,
        ),
    ]
    record.corroboration_results = [{
        "status": "CONTRADICTORY",
        "claim_id": claim_id,
        "independent_source_ids": ["s1", "s2"],
        "independent_sources": 2,
        "supporting_evidence_ids": ["e-support"],
        "contradicting_evidence_ids": ["e-conflict"],
    }]

    errors = record.validate()
    assert any("invalid evidence parse state" in error for error in errors)
    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_structural_signature_unhashable_valid_region_fails_closed():
    record = complete_record_with_two_sources()
    record.structural_signature = {
        "valid_region": [],
        "identity_hash": "a" * 64,
    }

    errors = record.validate()
    assert any("invalid valid_region" in error for error in errors)
    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_corroboration_sources_must_be_linked_to_claim_evidence():
    record = complete_record_with_two_sources()
    record.source_graph.extend([
        SourceRecord(
            source_id="s3",
            uri="https://source-c.example/unrelated",
            provenance_class=ProvenanceClass.EXTERNAL_PRIMARY,
            independence_group="source-c.example",
        ),
        SourceRecord(
            source_id="s4",
            uri="https://source-d.example/unrelated",
            provenance_class=ProvenanceClass.EXTERNAL_SECONDARY,
            independence_group="source-d.example",
        ),
    ])
    record.corroboration_results[0]["independent_source_ids"] = ["s3", "s4"]

    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_corroboration_evidence_must_share_claim_id():
    record = complete_record_with_two_sources()
    record.evidence[-1].claim_id = "different-claim"

    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_hypotheses_cannot_count_as_observed_corroboration():
    record = complete_record_with_two_sources()
    record.evidence[-1].state = ParseState.HYPOTHESIZED

    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_uri_derived_publisher_identity_overrides_forged_group():
    record = complete_record_with_two_sources()
    record.source_graph[0].uri = "https://api.source-b.example:8443/republished"
    record.source_graph[0].independence_group = "source-a.example"

    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_corroboration_not_applicable_requires_reason():
    record = MMIEngine().create_record(
        "corroboration-not-applicable-001",
        {"name": "single-source-fixture"},
        {"source": "fixture://primary"},
    )
    record.provenance = {"source": "fixture://primary"}
    record.source_graph.append(
        SourceRecord(
            source_id="s1",
            uri="https://primary.example/source",
            provenance_class=ProvenanceClass.EXTERNAL_PRIMARY,
            independence_group="primary-publisher",
        )
    )
    record.evidence.append(
        EvidenceRecord(
            evidence_id="e1",
            claim="single-source primary record",
            state=ParseState.OBSERVED,
            source_ids=["s1"],
        )
    )
    record.stages = [
        StageRecord(
            name,
            (
                StageOutcome.NOT_APPLICABLE
                if name == "CORROBORATION"
                else StageOutcome.COMPLETE
            ),
            "",
        )
        for name in MMIStateMachine.ORDER
    ]

    assert MMIStateMachine.evaluate(record) == MMIResult.PARTIAL

    record.stages = [
        StageRecord(
            name,
            StageOutcome.NOT_APPLICABLE if name == "CORROBORATION" else StageOutcome.COMPLETE,
            "No independent comparison is applicable to this single-source record."
            if name == "CORROBORATION" else "",
        )
        for name in MMIStateMachine.ORDER
    ]

    assert MMIStateMachine.evaluate(record) == MMIResult.COMPLETE
    report = MMICompletenessReport.build(record)
    assert report["protocol_complete"] is True



def test_required_core_stage_cannot_be_not_applicable():
    record = complete_record_with_two_sources()
    record.stages = [
        StageRecord(
            name,
            StageOutcome.NOT_APPLICABLE if name == "PROVENANCE_CAPTURED" else StageOutcome.COMPLETE,
            "Not applicable" if name == "PROVENANCE_CAPTURED" else "",
        )
        for name in MMIStateMachine.ORDER
    ]

    assert MMIStateMachine.evaluate(record) == MMIResult.PARTIAL
    report = MMICompletenessReport.build(record)
    assert report["protocol_complete"] is False
    assert report["protocol_completeness"] < 1.0


def test_contradictory_evidence_is_preserved():
    engine = MMIEngine()
    record = engine.create_record(
        "contradiction-001",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )

    record.evidence.extend([
        EvidenceRecord(
            evidence_id="e-support",
            claim="fixture claim is true",
            state=ParseState.OBSERVED,
            source_ids=["source-a"],
        ),
        EvidenceRecord(
            evidence_id="e-conflict",
            claim="fixture claim is false",
            state=ParseState.OBSERVED,
            source_ids=["source-b"],
        ),
    ])

    record.corroboration_results.append({
        "status": "CONTRADICTORY",
        "supporting_evidence": ["e-support"],
        "contradicting_evidence": ["e-conflict"],
    })

    record.reconciliation.append({
        "relationship": Reconciliation.CONTRADICTS_EXISTING.value,
        "evidence_ids": ["e-support", "e-conflict"],
    })

    assert len(record.evidence) == 2
    assert record.evidence[0].evidence_id == "e-support"
    assert record.evidence[1].evidence_id == "e-conflict"
    assert record.corroboration_results[0]["status"] == "CONTRADICTORY"
    assert record.reconciliation[0]["relationship"] == (
        Reconciliation.CONTRADICTS_EXISTING.value
    )


def test_negative_knowledge_is_persisted():
    engine = MMIEngine()
    record = engine.create_record(
        "negative-knowledge-001",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )

    record.knowledge_gaps.append({
        "gap_id": "gap-001",
        "status": "KNOWN_MISSING",
        "description": "Required component data was not present.",
    })

    record.negative_knowledge.append({
        "type": "KNOWN_UNSUPPORTED",
        "claim": "The unavailable component cannot be treated as verified.",
    })

    assert record.knowledge_gaps[0]["status"] == "KNOWN_MISSING"
    assert record.negative_knowledge[0]["type"] == "KNOWN_UNSUPPORTED"


def test_observation_does_not_become_interpretation():
    engine = MMIEngine()
    record = engine.create_record(
        "observation-boundary-001",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )

    record.evidence.append(
        EvidenceRecord(
            evidence_id="observed-001",
            claim="Observed fixture value",
            state=ParseState.OBSERVED,
            source_ids=["source-a"],
        )
    )

    record.learning.append({
        "type": ParseState.HYPOTHESIZED.value,
        "claim": "Possible explanation for observed value",
    })

    assert record.evidence[0].state == ParseState.OBSERVED
    assert record.learning[0]["type"] == ParseState.HYPOTHESIZED.value


def test_idempotency_classification_is_deterministic():
    assert classify_idempotency(
        current_hash="sha256:abc",
        previous_hash="sha256:abc",
        previous_complete=True,
    ) == Idempotency.IDENTICAL_REVALIDATION

    assert classify_idempotency(
        current_hash="sha256:def",
        previous_hash="sha256:abc",
        previous_complete=True,
    ) == Idempotency.SOURCE_UPDATED

    assert classify_idempotency(
        current_hash="sha256:abc",
        previous_hash="sha256:abc",
        previous_complete=False,
    ) == Idempotency.PARTIAL_REINGESTION

    assert classify_idempotency(
        current_hash="sha256:def",
        previous_hash=None,
        previous_complete=True,
    ) == Idempotency.NEW_DATASET


def test_execution_ledger_survives_reopen(tmp_path):
    path = tmp_path / "durable_mmi_execution.jsonl"

    ledger = MMIExecutionLedger(path)

    first_hash = ledger.append({
        "event": "MMI_RECEIVED",
        "ingestion_id": "durable-001",
    })

    second_hash = ledger.append({
        "event": "MMI_COMPLETED",
        "ingestion_id": "durable-001",
        "result": MMIResult.COMPLETE.value,
    })

    assert first_hash.startswith("sha256:")
    assert second_hash.startswith("sha256:")
    assert ledger.verify() is True

    reopened = MMIExecutionLedger(path)

    assert reopened.verify() is True

    lines = path.read_text().splitlines()
    assert len(lines) == 2

    events = [__import__("json").loads(line) for line in lines]

    assert events[0]["previous_hash"] == ""
    assert events[1]["previous_hash"] == first_hash
    assert events[1]["event_hash"] == second_hash


def test_completeness_report_is_deterministic():
    engine = MMIEngine()

    record = engine.create_record(
        "report-deterministic-001",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )

    record.stages = [
        StageRecord(name, StageOutcome.COMPLETE)
        for name in MMIStateMachine.ORDER
    ]

    record.source_graph.append(
        SourceRecord(
            source_id="s1",
            uri="fixture://source",
            provenance_class=ProvenanceClass.EXTERNAL_PRIMARY,
        )
    )

    record.evidence.append(
        EvidenceRecord(
            evidence_id="e1",
            claim="deterministic claim",
            state=ParseState.OBSERVED,
            source_ids=["s1"],
        )
    )

    add_valid_corroboration(record)

    report_a = MMICompletenessReport.build(record)
    report_b = MMICompletenessReport.build(record)

    assert report_a == report_b
    assert report_a["protocol_complete"] is True
    assert report_a["result"] == MMIResult.COMPLETE.value


def test_completeness_report_calculates_protocol_score():
    engine = MMIEngine()

    record = engine.create_record(
        "report-score-001",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )

    record.stages = [
        StageRecord(name, StageOutcome.COMPLETE)
        for name in MMIStateMachine.ORDER
    ]

    record.source_graph.append(
        SourceRecord(
            source_id="s1",
            uri="fixture://source",
            provenance_class=ProvenanceClass.EXTERNAL_PRIMARY,
        )
    )

    record.evidence.append(
        EvidenceRecord(
            evidence_id="e1",
            claim="score claim",
            state=ParseState.OBSERVED,
            source_ids=["s1"],
        )
    )

    add_valid_corroboration(record)

    report = MMICompletenessReport.build(record)

    assert report["protocol_complete"] is True
    assert report["protocol_completeness"] == 1.0


def test_execution_ledger_rejects_interrupted_final_record(tmp_path):
    path = tmp_path / "interrupted_mmi_execution.jsonl"
    ledger = MMIExecutionLedger(path)

    ledger.append({
        "event": "MMI_RECEIVED",
        "ingestion_id": "interrupt-001",
    })

    assert ledger.verify() is True

    with path.open("a") as f:
        f.write('{"event":"MMI_CORROBORATION_RECORDED","ingestion_id":"interrupt-001"')

    reopened = MMIExecutionLedger(path)

    assert reopened.verify() is False


def test_execution_ledger_reopens_after_valid_cycle(tmp_path):
    path = tmp_path / "reopen_mmi_execution.jsonl"

    ledger = MMIExecutionLedger(path)

    ledger.append({
        "event": "MMI_RECEIVED",
        "ingestion_id": "reopen-001",
    })
    ledger.append({
        "event": "MMI_COMPLETED",
        "ingestion_id": "reopen-001",
        "result": MMIResult.PARTIAL.value,
    })

    reopened = MMIExecutionLedger(path)

    assert reopened.verify() is True


def test_unhashable_corroboration_ids_fail_closed_without_exception():
    record = complete_record_with_two_sources()
    result = dict(record.corroboration_results[0])
    result["supporting_evidence_ids"] = ["corroboration-e1", {"not": "hashable"}]
    assert record._claim_bound_corroboration(result) is False

    result = dict(record.corroboration_results[0])
    result["independent_source_ids"] = ["s1", {"not": "hashable"}]
    assert record._claim_bound_corroboration(result) is False


def test_duplicate_or_unknown_mmi_stages_block_completion():
    duplicate = complete_record_with_two_sources()
    duplicate.stages.append(StageRecord("RECEIVED", StageOutcome.COMPLETE))
    assert MMIStateMachine.evaluate(duplicate) == MMIResult.BLOCKED

    unknown = complete_record_with_two_sources()
    unknown.stages.append(StageRecord("UNDECLARED_STAGE", StageOutcome.COMPLETE))
    assert MMIStateMachine.evaluate(unknown) == MMIResult.BLOCKED


def test_independent_evidence_cannot_reference_unknown_source():
    record = MMIEngine().create_record(
        "independent-unknown-source",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )
    record.evidence.append(
        EvidenceRecord(
            evidence_id="e-unknown-source",
            claim="unverified independent claim",
            state=ParseState.OBSERVED,
            source_ids=["missing-source"],
            independent=True,
        )
    )
    assert any("unknown source" in error for error in record.validate())


def test_tampered_execution_ledger_refuses_new_append(tmp_path):
    path = tmp_path / "tampered_before_append.jsonl"
    ledger = MMIExecutionLedger(path)
    ledger.append({"event": "MMI_RECEIVED", "ingestion_id": "tamper-append"})
    original = path.read_text(encoding="utf-8")
    modified = original.replace("MMI_RECEIVED", "MMI_FORGED")
    path.write_text(modified, encoding="utf-8")

    try:
        ledger.append({"event": "MMI_COMPLETED", "ingestion_id": "tamper-append"})
    except ValueError as exc:
        assert "integrity check failed" in str(exc)
    else:
        raise AssertionError("tampered ledger must reject further appends")
    assert path.read_text(encoding="utf-8") == modified

def test_unhashable_component_parent_id_fails_validation_without_exception():
    record = MMIEngine().create_record(
        "unhashable-parent-id",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )
    record.component_map.append(
        ComponentRecord(
            component_id="child",
            parent_id={},
            depth=1,
            state=ParseState.OBSERVED,
        )
    )

    assert any("component parent ID" in error for error in record.validate())
    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_unhashable_independent_source_id_fails_closed_without_exception():
    record = MMIEngine().create_record(
        "unhashable-independent-source-id",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )
    record.evidence.append(
        EvidenceRecord(
            evidence_id="malformed-independent",
            claim="malformed source reference",
            state=ParseState.OBSERVED,
            source_ids=[{}],
            independent=True,
        )
    )

    assert any("invalid source reference" in error for error in record.validate())
    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_non_list_independent_source_ids_fail_closed_without_exception():
    record = MMIEngine().create_record(
        "non-list-independent-source-ids",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )
    record.evidence.append(
        EvidenceRecord(
            evidence_id="malformed-independent-container",
            claim="malformed source container",
            state=ParseState.OBSERVED,
            source_ids=5,
            independent=True,
        )
    )

    assert any("source_ids must be a list" in error for error in record.validate())
    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_execution_ledger_append_skips_trailing_blank_lines(tmp_path):
    path = tmp_path / "ledger_with_blank_line.jsonl"
    ledger = MMIExecutionLedger(path)
    first_hash = ledger.append({"event": "MMI_RECEIVED", "ingestion_id": "blank-line-001"})

    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n")

    assert ledger.verify() is True
    second_hash = ledger.append({"event": "MMI_COMPLETED", "ingestion_id": "blank-line-001"})
    assert ledger.verify() is True
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert records[-1]["previous_hash"] == first_hash
    assert records[-1]["event_hash"] == second_hash

def test_malformed_source_provenance_class_fails_closed_without_type_error():
    record = MMIEngine().create_record(
        "malformed-source-provenance-class",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )
    record.source_graph = [
        SourceRecord(
            source_id="bad",
            uri="https://source-a.example/report",
            provenance_class={},
            independence_group="source-a.example",
        ),
        SourceRecord(
            source_id="good",
            uri="https://source-b.example/report",
            provenance_class=ProvenanceClass.EXTERNAL_PRIMARY,
            independence_group="source-b.example",
        ),
    ]
    record.evidence.append(
        EvidenceRecord(
            evidence_id="independent-malformed-class",
            claim="malformed provenance class",
            state=ParseState.OBSERVED,
            source_ids=["bad", "good"],
            independent=True,
        )
    )

    assert any("invalid source provenance class" in error for error in record.validate())
    assert record._independence_groups_for(["bad", "good"]) is None
    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED

def test_malformed_component_parent_id_blocks_without_type_error():
    record = complete_record_with_two_sources()
    record.component_map.append(
        ComponentRecord(
            component_id="malformed-parent",
            parent_id={},
            depth=1,
            state=ParseState.PARSED,
        )
    )

    errors = record.validate()
    assert any("component parent ID must be a non-empty string or null" in error for error in errors)
    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_malformed_independent_evidence_source_ids_block_without_type_error():
    for malformed_source_ids in (5, [{}], [None]):
        record = complete_record_with_two_sources()
        record.evidence[0].source_ids = malformed_source_ids
        record.evidence[0].independent = True

        errors = record.validate()
        assert errors
        assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_malformed_source_provenance_class_blocks_without_type_error():
    record = complete_record_with_two_sources()
    record.source_graph[0].provenance_class = {}
    record.evidence[0].independent = True

    errors = record.validate()
    assert any("invalid source provenance class" in error for error in errors)
    assert MMIStateMachine.evaluate(record) == MMIResult.BLOCKED


def test_execution_ledger_append_skips_trailing_blank_lines(tmp_path):
    ledger = MMIExecutionLedger(tmp_path / "mmi-execution.jsonl")
    first_hash = ledger.append({"event_type": "ingestion_started", "dataset_id": "xrp-test"})
    with ledger.path.open("a", encoding="utf-8") as handle:
        handle.write("\\n\\n")

    assert ledger.verify() is True
    second_hash = ledger.append({"event_type": "ingestion_completed", "dataset_id": "xrp-test"})
    assert second_hash != first_hash
    assert ledger.verify() is True

    records = [
        json.loads(line)
        for line in ledger.path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 2
    assert records[1]["previous_hash"] == first_hash

