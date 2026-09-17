import json
import time

from barrot_agent.mmi_v1 import (
    BoundedTraversal,
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
            uri="fixture://test",
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
    record.corroboration_results.append({"status": "checked"})

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
    record.corroboration_results.append({"status": "checked"})

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
    record.corroboration_results.append({"status": "checked"})

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

    record.corroboration_results.append({
        "status": "checked",
    })

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

    record.corroboration_results.append({"status": "checked"})

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
