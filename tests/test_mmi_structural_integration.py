from barrot_agent.mmi_v1 import (
    ComponentRecord,
    EvidenceRecord,
    MMIEngine,
    MMIExecutionLedger,
    MMIRecord,
    ParseState,
    ProvenanceClass,
    SourceRecord,
)


def test_mmi_engine_records_structural_signature_and_ledger_event(tmp_path):
    ledger = MMIExecutionLedger(tmp_path / "mmi.jsonl")
    engine = MMIEngine(ledger=ledger)
    record = MMIRecord("ingest-1", {"dataset": "example"}, {"publisher": "example"})
    record.source_graph.append(
        SourceRecord(
            "source-1",
            "https://example.com/report",
            ProvenanceClass.EXTERNAL_PRIMARY,
            content_hash="sha256:" + "a" * 64,
            independence_group="example.com",
        )
    )
    record.component_map.append(
        ComponentRecord("component-1", None, 1, ParseState.OBSERVED)
    )
    record.evidence.append(
        EvidenceRecord(
            "evidence-1",
            "A source-bound claim",
            ParseState.OBSERVED,
            source_ids=["source-1"],
        )
    )

    signature = engine.analyze_structure(record)

    assert signature.valid_region == "valid"
    assert signature.identity_hash == record.structural_signature["identity_hash"]
    assert record.structural_signature["representation_type"] == "mmi_record"
    assert ledger.verify()
    assert "MMI_STRUCTURAL_SIGNATURE_RECORDED" in ledger.path.read_text()


def test_invalid_mmi_record_produces_invalid_structural_region():
    record = MMIRecord("ingest-invalid", {"dataset": "example"}, {})
    record.component_map.append(
        ComponentRecord("too-deep", None, 5, ParseState.OBSERVED)
    )

    signature = MMIEngine().analyze_structure(record)

    assert signature.valid_region == "invalid"
    assert signature.constraints[0].status == "violated"
    assert "component depth out of range" in signature.constraints[0].detail
