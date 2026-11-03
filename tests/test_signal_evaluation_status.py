import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_signal_accuracy.py"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "check-signal-accuracy.yml"


def test_legacy_scorer_emits_blocked_status_without_network_or_writes(tmp_path):
    web = tmp_path / "web"
    web.mkdir()
    history = web / "signal_history.jsonl"
    summary = web / "signal_accuracy.json"
    history.write_text('{"legacy":"preserve"}\n', encoding="utf-8")
    summary.write_text('{"accuracy_pct":45.5}\n', encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["status"] == "BLOCKED_NO_VALIDATED_FIXED_HORIZON_DATA"
    assert payload["forecast_issuance"] == "BLOCKED"
    assert payload["evaluation_executed"] is False
    assert payload["paper_trading"] == "NOT_STARTED"
    assert payload["legacy_summary_validity"] == "UNVALIDATED_VARIABLE_HORIZON"
    assert history.read_text(encoding="utf-8") == '{"legacy":"preserve"}\n'
    assert summary.read_text(encoding="utf-8") == '{"accuracy_pct":45.5}\n'


def test_legacy_scorer_does_not_create_or_modify_legacy_files(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["legacy_files_modified"] is False
    assert not (tmp_path / "web" / "signal_history.jsonl").exists()
    assert not (tmp_path / "web" / "signal_accuracy.json").exists()


def test_status_contract_requires_fixed_horizon_and_independent_evaluation():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    required = set(payload["required_forecast_fields"])
    assert {
        "data_cutoff_utc",
        "target",
        "horizon_seconds",
        "assumptions",
        "probability_or_confidence",
        "alternative_hypotheses",
        "source_snapshot_ids",
        "outcome_measurement_utc",
    }.issubset(required)
    controls = set(payload["required_evaluation_controls"])
    assert "fixed-horizon walk-forward evaluation" in controls
    assert "independent evaluation attestation" in controls


def test_accuracy_workflow_is_read_only_and_does_not_push():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "contents: read" in workflow
    assert "persist-credentials: false" in workflow
    assert "signal_evaluation_status.json" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "contents: write" not in workflow
    assert "git push" not in workflow
    assert "git add" not in workflow
    assert "pip install requests" not in workflow



def test_public_signal_accuracy_api_does_not_serve_legacy_score():
    html = (REPO_ROOT / "web" / "landing.html").read_text(encoding="utf-8")
    start = html.index('name: "getSignalAccuracy"')
    end = html.index("\n  });", start)
    tool = html[start:end]

    assert 'title: "Signal Evaluation Status"' in tool
    assert "BLOCKED_NO_VALIDATED_FIXED_HORIZON_DATA" in tool
    assert "UNVALIDATED_VARIABLE_HORIZON" in tool
    assert 'fetch("signal_accuracy.json")' not in tool
    assert "accuracy_unavailable" not in tool
