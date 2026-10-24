from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_accuracy_script():
    path = REPO_ROOT / "scripts" / "check_signal_accuracy.py"
    spec = importlib.util.spec_from_file_location("test_signal_accuracy_safety_module", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_accuracy_workflow_does_not_write_to_main():
    workflow = (REPO_ROOT / ".github" / "workflows" / "check-signal-accuracy.yml").read_text(encoding="utf-8")
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "git push" not in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "retention-days: 90" in workflow
    assert "schedule:" in workflow


def test_accuracy_report_marks_legacy_metric_as_uncalibrated(tmp_path: Path, monkeypatch, capsys):
    module = load_accuracy_script()
    now = 1_800_000_000.0
    history_path = tmp_path / "signal_history.jsonl"
    summary_path = tmp_path / "signal_accuracy.json"
    history_path.write_text(
        json.dumps({
            "generated_at_unix": now - (25 * 3600),
            "price_at_emission": 100.0,
            "score": 70,
        }) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "HISTORY_PATH", history_path)
    monkeypatch.setattr(module, "SUMMARY_PATH", summary_path)
    monkeypatch.setattr(module, "_get_xrp_price", lambda: 101.0)
    monkeypatch.setattr(module.time, "time", lambda: now)

    module.main()

    capsys.readouterr()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["checked_count"] == 1
    assert summary["correct_count"] == 1
    assert summary["metric_status"] == "LEGACY_HEURISTIC_NOT_CALIBRATED"
    assert "not a calibrated forecast-performance measure" in summary["methodology_warning"]
    assert "exactly 24 hours" in summary["evaluation_method"]
    assert len(summary["known_limitations"]) >= 3
    updated = json.loads(history_path.read_text(encoding="utf-8").splitlines()[0])
    assert updated["checked"] is True
    assert updated["price_at_check"] == 101.0
