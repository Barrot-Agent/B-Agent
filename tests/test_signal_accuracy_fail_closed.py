from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_legacy_accuracy_is_not_presented_as_predictive_skill():
    module = load_script(ROOT / "scripts" / "check_signal_accuracy.py", "signal_accuracy_fail_closed")
    summary = module.build_summary({"checked_count": 1697, "correct_count": 772, "accuracy_pct": 45.5})
    assert summary["status"] == "NOT_EVALUATED"
    assert summary["metric_status"] == "NOT_COMPARABLE"
    assert summary["checked_count"] == 0
    assert summary["correct_count"] == 0
    assert summary["accuracy_pct"] is None
    assert summary["legacy_metric"]["status"] == "NOT_COMPARABLE"
    assert summary["legacy_metric"]["accuracy_pct"] == 45.5
    assert summary["evaluation_protocol"]["status"] == "NOT_IMPLEMENTED"


def test_accuracy_status_update_preserves_immutable_signal_history(tmp_path, monkeypatch):
    module = load_script(ROOT / "scripts" / "check_signal_accuracy.py", "signal_accuracy_no_history_mutation")
    history = tmp_path / "signal_history.jsonl"
    original = '{"generated_at_unix": 123, "score": 70}\n'
    history.write_text(original, encoding="utf-8")
    summary_path = tmp_path / "signal_accuracy.json"
    summary_path.write_text(json.dumps({"checked_count": 1697, "correct_count": 772, "accuracy_pct": 45.5}), encoding="utf-8")
    monkeypatch.setattr(module, "HISTORY_PATH", history)
    monkeypatch.setattr(module, "SUMMARY_PATH", summary_path)
    module.main()
    result = json.loads(summary_path.read_text(encoding="utf-8"))
    assert history.read_text(encoding="utf-8") == original
    assert result["status"] == "NOT_EVALUATED"
    assert result["accuracy_pct"] is None
    assert result["legacy_metric"]["status"] == "NOT_COMPARABLE"
    assert result["legacy_metric"]["checked_count"] == 1697


def test_public_accuracy_artifact_does_not_claim_legacy_skill():
    artifact = json.loads((ROOT / "web" / "signal_accuracy.json").read_text(encoding="utf-8"))
    assert artifact["status"] == "NOT_EVALUATED"
    assert artifact["metric_status"] == "NOT_COMPARABLE"
    assert artifact["accuracy_pct"] is None
    assert artifact["legacy_metric"]["checked_count"] == 1697
    assert artifact["legacy_metric"]["correct_count"] == 772
    assert artifact["legacy_metric"]["accuracy_pct"] == 45.5


def test_accuracy_workflow_is_read_only_and_artifact_only():
    workflow = (ROOT / ".github" / "workflows" / "check-signal-accuracy.yml").read_text(encoding="utf-8")
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "persist-credentials: false" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "git push" not in workflow
    assert "git commit" not in workflow


def test_daily_digest_labels_unvalidated_accuracy_honestly():
    module = load_script(ROOT / "scripts" / "daily_digest.py", "daily_digest_accuracy_status")
    line = module._format_accuracy({"status": "NOT_EVALUATED", "metric_status": "NOT_COMPARABLE", "checked_count": 0, "accuracy_pct": None})
    assert "NOT EVALUATED" in line
    assert "not comparable" in line.lower()
