from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_script(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_summary_never_presents_legacy_accuracy_as_predictive_skill():
    module = load_script(REPO_ROOT / "scripts" / "check_signal_accuracy.py", "signal_accuracy_fail_closed")
    summary = module.build_summary({"checked_count": 1659, "correct_count": 772, "accuracy_pct": 46.5})
    assert summary["status"] == "NOT_EVALUATED"
    assert summary["metric_status"] == "NOT_COMPARABLE"
    assert summary["checked_count"] == 0
    assert summary["correct_count"] == 0
    assert summary["accuracy_pct"] is None
    assert summary["legacy_metric"]["status"] == "NOT_COMPARABLE"
    assert summary["legacy_metric"]["accuracy_pct"] == 46.5
    assert summary["evaluation_protocol"]["status"] == "NOT_IMPLEMENTED"


def test_main_preserves_history_and_labels_old_metric(tmp_path, monkeypatch):
    module = load_script(REPO_ROOT / "scripts" / "check_signal_accuracy.py", "signal_accuracy_no_history_mutation")
    history = tmp_path / "signal_history.jsonl"
    original_history = '{"generated_at_unix": 123, "score": 70}\n'
    history.write_text(original_history, encoding="utf-8")
    summary_path = tmp_path / "signal_accuracy.json"
    summary_path.write_text(json.dumps({"checked_count": 1659, "correct_count": 772, "accuracy_pct": 46.5}), encoding="utf-8")
    monkeypatch.setattr(module, "HISTORY_PATH", history)
    monkeypatch.setattr(module, "SUMMARY_PATH", summary_path)
    module.main()
    result = json.loads(summary_path.read_text(encoding="utf-8"))
    assert history.read_text(encoding="utf-8") == original_history
    assert result["status"] == "NOT_EVALUATED"
    assert result["accuracy_pct"] is None
    assert result["legacy_metric"]["status"] == "NOT_COMPARABLE"
    assert result["legacy_metric"]["checked_count"] == 1659


def test_public_accuracy_artifact_fails_closed():
    artifact = json.loads((REPO_ROOT / "web" / "signal_accuracy.json").read_text(encoding="utf-8"))
    assert artifact["status"] == "NOT_EVALUATED"
    assert artifact["metric_status"] == "NOT_COMPARABLE"
    assert artifact["accuracy_pct"] is None
    assert artifact["legacy_metric"]["accuracy_pct"] == 45.9


def test_accuracy_workflow_is_read_only_and_artifact_only():
    workflow = (REPO_ROOT / ".github/workflows/check-signal-accuracy.yml").read_text(encoding="utf-8")
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "git push" not in workflow
    assert "upload-artifact@v4" in workflow


def test_daily_digest_labels_unvalidated_accuracy_as_not_evaluated():
    module = load_script(REPO_ROOT / "scripts" / "daily_digest.py", "daily_digest_accuracy_status")
    line = module._format_accuracy({"status": "NOT_EVALUATED", "metric_status": "NOT_COMPARABLE", "checked_count": 0, "accuracy_pct": None})
    assert "NOT EVALUATED" in line
    assert "not comparable" in line


def test_ask_barrot_script_compiles_and_describes_evaluation_honestly():
    path = REPO_ROOT / "scripts" / "ask_barrot.py"
    source = path.read_text(encoding="utf-8")
    compile(source, str(path), "exec")
    assert "NOT_EVALUATED" in source
    assert "NOT_COMPARABLE" in source
    assert "you have a manually dispatched knowledge-ingestion" in source
    assert "you run hourly knowledge" not in source
