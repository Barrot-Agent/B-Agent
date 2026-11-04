import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "market_analysis_engine.py"
WORKFLOW = ROOT / ".github" / "workflows" / "capability-1-market-analysis.yml"


def _load_engine():
    spec = importlib.util.spec_from_file_location("market_analysis_engine", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_legacy_market_analysis_is_disabled_without_explicit_local_opt_in(monkeypatch):
    engine = _load_engine()
    monkeypatch.delenv("BARROT_ENABLE_LEGACY_MARKET_ANALYSIS", raising=False)
    assert engine.legacy_market_analysis_enabled() is False
    with pytest.raises(SystemExit, match="Legacy market analysis is disabled"):
        engine.main()


def test_legacy_analysis_schema_forbids_forecasts_and_trade_recommendations():
    engine = _load_engine()
    valid = {
        "summary": "Descriptive only.",
        "observations": ["Observed score dispersion."],
        "data_quality": ["Historical labels are not independently verified."],
        "competing_hypotheses": ["The apparent pattern may be sampling noise."],
        "validation_gaps": ["No chronological out-of-sample test exists."],
        "forecast_status": "NOT_ISSUED",
        "trade_recommendations": [],
    }
    assert engine.validate_analysis_response(json.dumps(valid)) == valid

    invalid_recommendation = dict(valid, trade_recommendations=["Buy XRP"])
    with pytest.raises(ValueError, match="trade recommendations"):
        engine.validate_analysis_response(json.dumps(invalid_recommendation))

    invalid_forecast = dict(valid, forecast_status="ISSUED")
    with pytest.raises(ValueError, match="cannot issue a forecast"):
        engine.validate_analysis_response(json.dumps(invalid_forecast))


def test_databricks_query_is_bounded_read_only_and_receipted(monkeypatch):
    engine = _load_engine()
    monkeypatch.setenv("DATABRICKS_HOST", "dbc.example.com")
    monkeypatch.setenv("DATABRICKS_TOKEN", "test-token")
    monkeypatch.setenv("DATABRICKS_WAREHOUSE_ID", "warehouse-123")
    captured = {}

    payload = {
        "status": {"state": "SUCCEEDED"},
        "manifest": {
            "truncated": False,
            "schema": {
                "columns": [
                    {"name": "date"},
                    {"name": "direction"},
                    {"name": "confidence"},
                    {"name": "accuracy"},
                ]
            },
        },
        "result": {"data_array": [["2026-11-03", "neutral", "0.5", "0.4"]]},
    }

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps(payload).encode("utf-8")

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["body"] = json.loads(request.data)
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(engine, "urlopen", fake_urlopen)
    result = engine.query_databricks(
        "SELECT date, direction, confidence, accuracy FROM workspace.barrot.signals LIMIT 30"
    )

    assert captured["url"] == "https://dbc.example.com/api/2.0/sql/statements"
    assert captured["body"]["warehouse_id"] == "warehouse-123"
    assert captured["body"]["statement"].startswith("SELECT ")
    assert captured["body"]["wait_timeout"] == "50s"
    assert captured["body"]["on_wait_timeout"] == "CANCEL"
    assert captured["body"]["row_limit"] == 100
    assert captured["timeout"] == 60
    assert result["record_count"] == 1
    assert result["data_cutoff_utc"] == "2026-11-03"
    assert len(result["raw_response_sha256"]) == 64


def test_databricks_query_rejects_non_select_and_incomplete_execution(monkeypatch):
    engine = _load_engine()
    with pytest.raises(ValueError, match="read-only SELECT"):
        engine.query_databricks("DELETE FROM workspace.barrot.signals")

    monkeypatch.setenv("DATABRICKS_HOST", "dbc.example.com")
    monkeypatch.setenv("DATABRICKS_TOKEN", "test-token")
    monkeypatch.setenv("DATABRICKS_WAREHOUSE_ID", "warehouse-123")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps({"status": {"state": "PENDING"}}).encode("utf-8")

    monkeypatch.setattr(engine, "urlopen", lambda *_args, **_kwargs: Response())
    with pytest.raises(RuntimeError, match="did not succeed"):
        engine.query_databricks("SELECT 1")


def test_legacy_market_analysis_workflow_is_disabled_and_has_no_external_access():
    content = WORKFLOW.read_text(encoding="utf-8")
    assert "if: false" in content
    assert "permissions: {}" in content
    assert "secrets." not in content
    assert "git push" not in content
    assert "contents: write" not in content
    assert "schedule:" not in content
    assert "Disabled: legacy market-analysis output is not a validated XRP forecast." in content
