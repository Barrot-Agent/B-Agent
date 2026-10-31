from __future__ import annotations

import json
from pathlib import Path

import pytest

from barrot_agent.ingestion.mmi_execution import (
    EXECUTION_VERSION,
    MMIExecutionEngine,
    MMIExecutionInput,
    execute_bytes,
)
from barrot_agent.sources.mmi_adapter import PlannerMMIAdapter
from barrot_agent.sources.source_acquisition import AcquisitionTarget


def make_request():
    target = AcquisitionTarget(
        target_id="execution-target",
        need_id="execution-need",
        source_type="dataset",
        name="Execution Dataset",
        purpose="MMI execution test",
        discovery_uri="https://example.org/discovery",
        acquisition_uri="https://example.org/data",
        publisher="Example Publisher",
        provenance_requirements=["publisher", "retrieval_timestamp"],
        verification_requirements=["hash"],
        mmi_required=True,
        independent_corroboration_required=True,
    )
    return PlannerMMIAdapter().build_request(target)


def test_execution_captures_exact_source_hash(tmp_path: Path):
    request = make_request()
    content = b"MMI execution evidence"

    result = execute_bytes(
        request,
        content,
        ledger_path=tmp_path / "ledger.jsonl",
        content_type="text/plain",
        source_version="v1",
    )

    assert result.source.content_hash
    assert result.source.version == "v1"
    assert result.source.uri == "https://example.org/data"


def test_execution_does_not_fabricate_components(tmp_path: Path):
    result = execute_bytes(
        make_request(),
        b"plain source content",
        ledger_path=tmp_path / "ledger.jsonl",
    )

    assert result.components == []
    assert len(result.components) == 0


def test_execution_does_not_fabricate_evidence(tmp_path: Path):
    result = execute_bytes(
        make_request(),
        b"plain source content",
        ledger_path=tmp_path / "ledger.jsonl",
    )

    assert result.evidence == []
    assert len(result.evidence) == 0


def test_execution_preserves_protocol_vs_knowledge_separation(
    tmp_path: Path,
):
    result = execute_bytes(
        make_request(),
        b"source",
        ledger_path=tmp_path / "ledger.jsonl",
    )

    assert result.protocol_complete is False
    assert result.knowledge_complete is False


def test_execution_records_two_ledger_events(tmp_path: Path):
    ledger = tmp_path / "ledger.jsonl"

    execute_bytes(
        make_request(),
        b"source",
        ledger_path=ledger,
    )

    records = [
        json.loads(line)
        for line in ledger.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(records) == 2
    assert records[0]["event"] == "MMI_EXECUTION_RECEIVED"
    assert records[1]["event"] == "MMI_EXECUTION_RESULT"
    assert records[0]["record_hash"]
    assert records[1]["record_hash"]
    assert records[1]["previous_hash"] == records[0]["record_hash"]


def test_execution_is_deterministic_for_same_input_except_timestamps(
    tmp_path: Path,
):
    request = make_request()
    first = MMIExecutionInput(
        request=request,
        content=b"same bytes",
        source_version="v1",
        retrieval_timestamp="2026-01-01T00:00:00+00:00",
    )
    second = MMIExecutionInput(
        request=request,
        content=b"same bytes",
        source_version="v1",
        retrieval_timestamp="2026-01-01T00:00:00+00:00",
    )

    assert first.content_hash == second.content_hash
    assert first.source_id == second.source_id


def test_engine_requires_real_request(tmp_path: Path):
    with pytest.raises(AttributeError):
        MMIExecutionEngine(tmp_path / "ledger.jsonl").execute(
            object()  # type: ignore[arg-type]
        )


def test_execution_version_is_declared():
    assert EXECUTION_VERSION == "1.0"
