from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from barrot_agent.ingestion.mmi_contract import (
    MMI_MAX_DEPTH,
    MMIEvidence,
    MMIComponent,
    MMIOutcome,
    MMISource,
    EvidenceState,
    clamp_depth,
)
from barrot_agent.ingestion.mmi_ledger import MMILedger


def make_source() -> MMISource:
    return MMISource(
        source_id="source-1",
        source_type="file",
        uri="file:///tmp/source",
        version="1",
        content_hash="a" * 64,
        acquired_at="2026-09-18T00:00:00+00:00",
    )


def test_depth_is_clamped():
    assert clamp_depth(-4) == 0
    assert clamp_depth(2) == 2
    assert clamp_depth(99) == MMI_MAX_DEPTH


def test_component_depth_and_provenance_depth_are_separate():
    component = MMIComponent(
        component_id="c1",
        parent_id=None,
        name="root",
        component_depth=4,
        provenance_depth=2,
        state=EvidenceState.PARSED,
        source_id="source-1",
    )
    assert component.validate() == []


def test_scope_boundary_and_representation_absence():
    from barrot_agent.ingestion.mmi_contract import assess_representation

    assert assess_representation(None) == EvidenceState.NOT_APPLICABLE


def test_evidence_rejects_self_corroboration():
    evidence = MMIEvidence(
        evidence_id="e1",
        source_id="source-1",
        component_id=None,
        state=EvidenceState.DERIVED,
        statement="derived statement",
        independent_sources=["e1"],
        generated_by_barrot=True,
    )
    assert evidence.validate()


def test_ledger_hash_chain_and_tamper_detection(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    ledger = MMILedger(path)

    ledger.append(
        "STAGE",
        {"name": "RECEIVED"},
        source_id="source-1",
    )
    ledger.append(
        "STAGE",
        {"name": "DECOMPOSED"},
        source_id="source-1",
    )

    assert ledger.verify()

    records = path.read_text(encoding="utf-8").splitlines()
    records[0] = records[0].replace("RECEIVED", "TAMPERED")
    path.write_text("\n".join(records) + "\n", encoding="utf-8")

    assert not ledger.verify()

    with pytest.raises(RuntimeError):
        ledger.append("AFTER_TAMPER", {}, source_id="source-1")


def test_evaluator_distinguishes_protocol_and_knowledge_completeness(
    tmp_path: Path,
):
    payload = {
        "protocol_version": "1.0",
        "source": {
            "source_id": "source-1",
            "source_type": "file",
            "uri": "file:///source",
            "version": "1",
            "content_hash": "a" * 64,
            "acquired_at": "2026-09-18T00:00:00+00:00",
        },
        "stages": [
            {"name": name, "status": "COMPLETE"}
            for name in (
                "RECEIVED",
                "PROVENANCE_CAPTURED",
                "DECOMPOSED",
                "REPRESENTATIONS_ASSESSED",
                "EVIDENCE_NORMALIZED",
                "CORROBORATION",
                "GAP_ANALYSIS",
                "RECONCILIATION",
                "LEARNING_EXTRACTED",
                "CAPABILITY_ANALYZED",
                "ACQUISITION_TARGETS_GENERATED",
                "VERIFICATION",
            )
        ],
        "scope_boundary": {"defined": True},
        "termination": {"bounded": True},
        "knowledge_complete": False,
        "outcome": MMIOutcome.NEW_DATASET.value,
    }

    source = tmp_path / "mmi.json"
    source.write_text(json.dumps(payload), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/mmi_evaluate.py",
            str(source),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["protocol_complete"] is True
    assert report["knowledge_complete"] is False
    assert any(
        "does not imply knowledge completeness" in warning
        for warning in report["warnings"]
    )


def test_evaluator_fails_when_required_stage_is_missing(tmp_path: Path):
    payload = {
        "protocol_version": "1.0",
        "source": {
            "source_id": "source-1",
            "source_type": "file",
            "uri": "file:///source",
            "version": "1",
            "content_hash": "a" * 64,
            "acquired_at": "2026-09-18T00:00:00+00:00",
        },
        "stages": [],
        "scope_boundary": {"defined": True},
        "termination": {"bounded": True},
    }

    source = tmp_path / "mmi.json"
    source.write_text(json.dumps(payload), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/mmi_evaluate.py",
            str(source),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["protocol_complete"] is False
    assert report["error_count"] > 0
