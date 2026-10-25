from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_signal_accuracy.py"
spec = importlib.util.spec_from_file_location("check_signal_accuracy_fail_closed", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(module)


def valid_forecast(**overrides):
    data = {
        "record_type": "forecast",
        "forecast_contract_version": 1,
        "forecast_status": "ISSUED",
        "forecast_id": "xrp-24h-001",
        "target_definition": module.TARGET_DEFINITION,
        "issued_at_utc": "2026-10-25T00:00:00Z",
        "data_cutoff_utc": "2026-10-24T23:59:00Z",
        "horizon_seconds": 86400,
        "probability": 0.7,
        "price_at_issue": 1.25,
        "price_at_issue_timestamp_utc": "2026-10-24T23:58:30Z",
        "price_source_id": "S88-004",
        "price_staleness_tolerance_seconds": 300,
        "assumptions": ["spot and derivatives timestamps are aligned"],
        "alternatives": ["macro shock reverses move"],
        "source_ids": ["S88-004"],
        "model_version": "shadow-v0.1",
        "outcome_tolerance_seconds": 300,
    }
    data.update(overrides)
    return data


def valid_outcome(**overrides):
    data = {
        "record_type": "outcome",
        "forecast_id": "xrp-24h-001",
        "outcome_price": 1.30,
        "observed_at_unix": 1792972800.0,
        "timestamp_quality": "verified_event_time",
        "source_id": "S88-004",
    }
    data.update(overrides)
    return data


def test_legacy_score_only_record_never_becomes_forecast():
    summary, new = module.build_summary(
        [{"score": 88, "confidence": 0.9, "price_at_emission": 1.2, "generated_at_unix": 100}],
        [],
        [],
    )
    assert summary["status"] == "NOT_ISSUED"
    assert summary["checked_count"] == 0
    assert summary["accuracy_pct"] is None
    assert not new


def test_not_issued_null_score_is_skipped_without_type_error():
    summary, new = module.build_summary(
        [{"score": None, "forecast_status": "NOT_ISSUED", "source": "provider unavailable"}],
        [],
        [],
    )
    assert summary["status"] == "NOT_ISSUED"
    assert not new


def test_valid_fixed_horizon_outcome_scores_brier_and_baseline():
    summary, new = module.build_summary([valid_forecast()], [valid_outcome()], [])
    assert len(new) == 1
    assert new[0]["outcome"] == 1
    assert math.isclose(new[0]["brier_score"], 0.09, abs_tol=1e-12)
    assert math.isclose(new[0]["baseline_brier_score"], 0.25, abs_tol=1e-12)
    assert summary["status"] == "EVALUATED"


def test_outcome_outside_horizon_tolerance_is_not_scored():
    summary, new = module.build_summary(
        [valid_forecast()],
        [valid_outcome(observed_at_unix=1792973401.0)],
        [],
    )
    assert not new
    assert summary["status"] == "WAITING_FOR_HORIZON_ALIGNED_OUTCOMES"
    assert summary["outcomes_outside_horizon_tolerance"] == 1


def test_unverified_outcome_timestamp_is_not_scored():
    summary, new = module.build_summary(
        [valid_forecast()],
        [valid_outcome(timestamp_quality="retrieval_time")],
        [],
    )
    assert not new
    assert summary["invalid_outcome_records"] == 1


def test_naive_timestamp_is_rejected():
    ok, reason = module._valid_forecast(valid_forecast(issued_at_utc="2026-10-25T00:00:00"))
    assert not ok and reason == "invalid_or_naive_timestamp"


def test_data_cutoff_after_issue_is_rejected():
    ok, reason = module._valid_forecast(valid_forecast(data_cutoff_utc="2026-10-25T00:00:01Z"))
    assert not ok and reason == "data_cutoff_after_issue"


def test_duplicate_conflicting_outcomes_are_not_arbitrarily_selected():
    summary, new = module.build_summary(
        [valid_forecast()],
        [valid_outcome(), valid_outcome(outcome_price=1.10, source_id="S88-OTHER")],
        [],
    )
    assert not new
    assert summary["ambiguous_outcome_sets"] == 1


def test_evaluation_is_idempotent_by_forecast_id():
    existing = {
        "record_type": "evaluation",
        "forecast_id": "xrp-24h-001",
        "brier_score": 0.09,
        "baseline_brier_score": 0.25,
    }
    summary, new = module.build_summary([valid_forecast()], [valid_outcome()], [existing])
    assert not new
    assert summary["checked_count"] == 1
    assert math.isclose(summary["mean_brier_score"], 0.09)


def test_source_history_loader_does_not_modify_bytes(tmp_path):
    p = tmp_path / "history.jsonl"
    original = b'{"score":44}\nnot-json\n'
    p.write_bytes(original)
    records, malformed = module._load_jsonl(p)
    assert records == [{"score": 44}]
    assert malformed == 1
    assert p.read_bytes() == original


def test_invalid_probability_and_bool_are_rejected():
    for value in [-0.01, 1.01, float("nan"), True, "0.7"]:
        ok, _ = module._valid_forecast(valid_forecast(probability=value))
        assert not ok


def test_missing_assumptions_alternatives_or_sources_are_rejected():
    for field in ["assumptions", "alternatives", "source_ids"]:
        ok, _ = module._valid_forecast(valid_forecast(**{field: []}))
        assert not ok


def test_main_reports_not_issued_and_preserves_legacy_history(tmp_path, monkeypatch, capsys):
    root = tmp_path
    web = root / "web"
    web.mkdir()
    history = web / "signal_history.jsonl"
    original = b'{"score":44,"confidence":0.0,"news_score":88}\n'
    history.write_bytes(original)
    monkeypatch.setattr(module, "ROOT", root)
    monkeypatch.setattr(module, "HISTORY_PATH", history)
    monkeypatch.setattr(module, "OUTCOME_LEDGER_PATH", web / "forecast_evaluation.jsonl")
    monkeypatch.setattr(module, "SUMMARY_PATH", web / "signal_accuracy.json")
    assert module.main() == 0
    assert history.read_bytes() == original
    summary = json.loads((web / "signal_accuracy.json").read_text())
    assert summary["status"] == "NOT_ISSUED"
    assert summary["checked_count"] == 0
    assert summary["accuracy_pct"] is None
    assert not (web / "forecast_evaluation.jsonl").exists()
    assert "NOT_ISSUED" in capsys.readouterr().out


def test_main_writes_idempotent_evaluation_ledger(tmp_path, monkeypatch):
    root = tmp_path
    web = root / "web"
    web.mkdir()
    history = web / "signal_history.jsonl"
    outcomes = web / "forecast_outcome_snapshots.jsonl"
    history.write_text(json.dumps(valid_forecast()) + "\n", encoding="utf-8")
    outcomes.write_text(json.dumps(valid_outcome()) + "\n", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", root)
    monkeypatch.setattr(module, "HISTORY_PATH", history)
    monkeypatch.setattr(module, "OUTCOME_LEDGER_PATH", web / "forecast_evaluation.jsonl")
    monkeypatch.setattr(module, "SUMMARY_PATH", web / "signal_accuracy.json")
    module.main()
    first = (web / "forecast_evaluation.jsonl").read_bytes()
    module.main()
    second = (web / "forecast_evaluation.jsonl").read_bytes()
    assert first == second
    assert len(first.splitlines()) == 1
    summary = json.loads((web / "signal_accuracy.json").read_text())
    assert summary["status"] == "EVALUATED"
    assert summary["checked_count"] == 1
    assert summary["accuracy_pct"] is None


def test_accuracy_workflow_is_read_only_and_manual_only():
    workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "check-signal-accuracy.yml")
    text = workflow.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "schedule:" not in text
    assert "contents: read" in text
    assert "git push" not in text
    assert "git commit" not in text


def test_price_timestamp_after_cutoff_is_rejected():
    ok, reason = module._valid_forecast(valid_forecast(price_at_issue_timestamp_utc="2026-10-25T00:00:01Z"))
    assert not ok and reason == "price_event_after_data_cutoff_or_issue"


def test_stale_price_snapshot_is_rejected():
    ok, reason = module._valid_forecast(valid_forecast(price_at_issue_timestamp_utc="2026-10-24T23:50:00Z"))
    assert not ok and reason == "stale_price_at_issue"


def test_price_source_must_be_in_provenance_lineage():
    ok, reason = module._valid_forecast(valid_forecast(source_ids=["S88-OTHER"]))
    assert not ok and reason == "price_source_not_in_source_lineage"


def test_conflicting_duplicate_forecast_ids_are_excluded():
    first = valid_forecast()
    second = valid_forecast(probability=0.2)
    summary, new = module.build_summary([first, second], [valid_outcome()], [])
    assert not new
    assert summary["issued_forecast_records_seen"] == 0
    assert summary["invalid_forecast_duplicates"] == 1


def test_conflicting_existing_evaluations_are_not_double_counted():
    e1 = {"record_type": "evaluation", "forecast_id": "xrp-24h-001", "brier_score": 0.09, "baseline_brier_score": 0.25}
    e2 = {"record_type": "evaluation", "forecast_id": "xrp-24h-001", "brier_score": 0.64, "baseline_brier_score": 0.25}
    summary, new = module.build_summary([valid_forecast()], [valid_outcome()], [e1, e2])
    assert not new
    assert summary["checked_count"] == 0
    assert summary["conflicting_evaluation_ids"] == 1
