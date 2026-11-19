from barrot_agent.mmi_v1 import (
    MMIExecutionLedger,
    EvidenceRecord,
    MMIEngine,
    MMIResult,
    MMIStateMachine,
    ParseState,
    ProvenanceClass,
    SourceRecord,
    StageOutcome,
    StageRecord,
)


class FakeExistingPipeline:
    name = "IntelligencePipeline"


class FakeExistingNormalizer:
    name = "EvidenceNormalizationEngine"


class FakeExistingCorroborator:
    name = "CrossCorroborationEngine"


class FakeExistingIndependence:
    name = "SourceIndependenceEngine"


def test_mmi_accepts_existing_barrot_components_without_reimplementing_them():
    components = {
        "acquisition": FakeExistingPipeline(),
        "normalization": FakeExistingNormalizer(),
        "corroboration": FakeExistingCorroborator(),
        "independence": FakeExistingIndependence(),
    }

    engine = MMIEngine(components=components)

    assert engine.components["acquisition"].name == "IntelligencePipeline"
    assert engine.components["normalization"].name == "EvidenceNormalizationEngine"
    assert engine.components["corroboration"].name == "CrossCorroborationEngine"
    assert engine.components["independence"].name == "SourceIndependenceEngine"


def test_external_evidence_can_be_independent():
    engine = MMIEngine()

    record = engine.create_record(
        "integration-001",
        {"name": "external-dataset"},
        {"source": "external-primary"},
    )

    record.source_graph.append(
        SourceRecord(
            source_id="source-1",
            uri="https://example.org/source",
            provenance_class=ProvenanceClass.EXTERNAL_PRIMARY,
            depth=1,
            content_hash="sha256:abc",
            observed_at="2026-09-17T00:00:00Z",
        )
    )

    record.evidence.append(
        EvidenceRecord(
            evidence_id="evidence-1",
            claim="Observed external claim",
            state=ParseState.OBSERVED,
            source_ids=["source-1"],
            independent=True,
            content_hash="sha256:def",
            observed_at="2026-09-17T00:00:00Z",
        )
    )

    assert record.validate() == []


def test_generated_agreement_is_not_external_corroboration():
    engine = MMIEngine()

    record = engine.create_record(
        "integration-002",
        {},
        {},
    )

    record.source_graph.extend([
        SourceRecord(
            source_id="barrot-1",
            uri="barrot://generated/a",
            provenance_class=ProvenanceClass.BARROT_GENERATED,
        ),
        SourceRecord(
            source_id="barrot-2",
            uri="barrot://generated/b",
            provenance_class=ProvenanceClass.BARROT_GENERATED,
        ),
    ])

    record.evidence.extend([
        EvidenceRecord(
            evidence_id="e1",
            claim="same generated conclusion",
            state=ParseState.DERIVED,
            source_ids=["barrot-1"],
            independent=True,
        ),
        EvidenceRecord(
            evidence_id="e2",
            claim="same generated conclusion",
            state=ParseState.DERIVED,
            source_ids=["barrot-2"],
            independent=True,
        ),
    ])

    assert record.validate()


def test_protocol_and_knowledge_completeness_are_separate():
    engine = MMIEngine()

    record = engine.create_record(
        "integration-003",
        {},
        {},
    )

    record.stages = [
        StageRecord(name, StageOutcome.COMPLETE)
        for name in MMIStateMachine.ORDER
    ]

    record.protocol_completeness = 1.0
    record.knowledge_completeness = 0.25

    record.provenance = {"source": "integration-test"}
    record.source_graph.append(
        SourceRecord(
            source_id="s1",
            uri="fixture://integration",
            provenance_class=ProvenanceClass.EXTERNAL_PRIMARY,
        )
    )
    record.evidence.append(
        EvidenceRecord(
            evidence_id="e1",
            claim="integration test claim",
            state=ParseState.OBSERVED,
            source_ids=["s1"],
        )
    )
    record.corroboration_results.append({"status": "checked"})

    assert MMIStateMachine.evaluate(record) == MMIResult.COMPLETE
    assert record.protocol_completeness == 1.0
    assert record.knowledge_completeness == 0.25


def test_mmi_cycle_persists_corroboration_and_ledger(tmp_path):
    ledger = MMIExecutionLedger(tmp_path / "mmi_execution.jsonl")
    engine = MMIEngine(ledger=ledger)

    record = engine.create_record(
        "ledger-cycle-001",
        {"name": "fixture"},
        {"source": "fixture://source"},
    )

    record.stages = [
        StageRecord(name, StageOutcome.COMPLETE)
        for name in MMIStateMachine.ORDER
    ]

    record.provenance = {"source": "fixture://source"}
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
            claim="ledger test claim",
            state=ParseState.OBSERVED,
            source_ids=["s1"],
        )
    )

    engine.record_corroboration(
        record,
        {"status": "confirmed", "source_ids": ["s1"]},
    )

    completed = engine.complete(record)
    report = engine.completeness_report(completed)

    assert completed.result == MMIResult.COMPLETE
    assert completed.corroboration_results == [
        {"status": "confirmed", "source_ids": ["s1"]}
    ]
    assert report["protocol_complete"] is True
    assert report["result"] == MMIResult.COMPLETE.value
    assert ledger.verify() is True

    events = [
        __import__("json").loads(line)
        for line in ledger.path.read_text().splitlines()
        if line.strip()
    ]

    assert [event["event"] for event in events] == [
        "MMI_RECEIVED",
        "MMI_CORROBORATION_RECORDED",
        "MMI_COMPLETED",
        "MMI_COMPLETENESS_REPORTED",
    ]


def test_mmi_ledger_tampering_is_detected(tmp_path):
    ledger = MMIExecutionLedger(tmp_path / "mmi_execution.jsonl")

    ledger.append({
        "event": "MMI_RECEIVED",
        "ingestion_id": "tamper-001",
    })
    ledger.append({
        "event": "MMI_COMPLETED",
        "ingestion_id": "tamper-001",
        "result": MMIResult.COMPLETE.value,
    })

    assert ledger.verify() is True

    lines = ledger.path.read_text().splitlines()
    lines[0] = lines[0].replace(
        '"MMI_RECEIVED"',
        '"MMI_TAMPERED"',
        1,
    )
    ledger.path.write_text("\n".join(lines) + "\n")

    assert ledger.verify() is False
