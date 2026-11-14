import json
import os
import subprocess
import sys
from pathlib import Path

from barrot_agent.analysis.xrp_telemetry_matrix import CouncilReportNode
from barrot_agent.ingestion.council_ingest_node import CouncilIngestionEngine
from barrot_agent.orchestration.orchestrator_bridge import apply_council_weights


def test_legacy_telemetry_is_status_only_and_writes_no_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = __import__("asyncio").run(CouncilReportNode().generate_report())
    assert result["status"] == "NOT_ISSUED"
    assert result["forecast_issued"] is False
    assert not (tmp_path / "COUNCIL_REVIEW.md").exists()


def test_legacy_council_ingestion_cannot_emit_or_persist_accumulation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    state = tmp_path / "council_weights.json"
    state.write_text('{"council_action":"PRESERVE_ME"}', encoding="utf-8")
    before = state.read_bytes()

    engine = CouncilIngestionEngine()
    assert engine.parse_physical_artifact()["council_action"] == "NOT_ISSUED"
    result = engine.calculate_and_inject({"asset": "XRP", "sentiment": 1.0, "variance": 0.0})

    assert result["status"] == "NOT_ISSUED"
    assert result["orchestrator_weight_multiplier"] is None
    assert state.read_bytes() == before


def test_legacy_orchestrator_bridge_never_applies_weights(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "council_weights.json").write_text(
        '{"council_action":"MAX_ACCUMULATION_TRIGGERED","orchestrator_weight_multiplier":1.15}',
        encoding="utf-8",
    )
    result = apply_council_weights()

    assert result["status"] == "NOT_APPLIED"
    assert result["external_action_performed"] is False


def test_legacy_upgrade_bundle_exits_before_writing_user_files(tmp_path):
    script = Path("barrot_agent/tools/upgrade_bundle.py").resolve()
    env = dict(os.environ)
    env["HOME"] = str(tmp_path)
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "QUARANTINED"
    assert payload["files_written"] is False
    assert not (tmp_path / "barrot").exists()


def test_council_state_files_are_quarantined_and_have_no_active_multiplier():
    root = json.loads(Path("council_weights.json").read_text(encoding="utf-8"))
    data = json.loads(Path("data/council_weights.json").read_text(encoding="utf-8"))
    unified = json.loads(Path("data/mmi_monetization_unified.json").read_text(encoding="utf-8"))

    for state in (root, data, unified["council_weights"]):
        assert state["status"] == "LEGACY_QUARANTINED"
        assert state["council_action"] == "NOT_ISSUED"
        assert state["orchestrator_weight_multiplier"] is None
        assert state["forecast_eligible"] is False


def test_legacy_quarantine_artifact_preserves_original_action_and_source_blobs():
    artifact = json.loads(
        Path("research/xrp_intelligence/20261105T213000Z-legacy-council-heuristic-quarantine.json")
        .read_text(encoding="utf-8")
    )
    assert artifact["finding"]["root_state"]["legacy_values"]["council_action"] == "MAX_ACCUMULATION_TRIGGERED"
    assert artifact["finding"]["root_state"]["legacy_values"]["orchestrator_weight_multiplier"] == 1.15
    assert artifact["admission"]["model_eligible"] is False
    assert artifact["preservation"]["git_history_preserved"] is True
