import ast
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "market_analysis_engine.py"
WORKFLOW = ROOT / ".github" / "workflows" / "capability-1-market-analysis.yml"


def _load_engine():
    spec = importlib.util.spec_from_file_location("market_analysis_engine", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_retired_market_analysis_emits_only_not_issued_status(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GROQ_API_KEY", "must-not-be-used")
    monkeypatch.setenv("DATABRICKS_HOST", "must-not-be-used.example")
    monkeypatch.setenv("DATABRICKS_TOKEN", "must-not-be-used")
    monkeypatch.setenv("DATABRICKS_WAREHOUSE_ID", "must-not-be-used")

    engine = _load_engine()
    assert engine.main() == 0

    output = json.loads(capsys.readouterr().out)
    assert output == engine.STATUS
    assert output["status"] == "NOT_ISSUED"
    assert output["forecast_issued"] is False
    assert output["trade_recommendations"] == []
    assert "no databricks or" in output["message"].lower()
    assert list(tmp_path.iterdir()) == []


def test_retired_market_analysis_has_no_network_or_provider_entrypoints():
    engine = _load_engine()
    for name in ("query_databricks", "call_groq", "analyze_market", "urlopen"):
        assert not hasattr(engine, name)

    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported_modules = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_modules.update(
        node.module.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    assert imported_modules == {"__future__", "json"}


def test_retired_status_cannot_be_misread_as_accuracy_or_a_forecast():
    engine = _load_engine()
    status = engine.STATUS
    assert status["status"] == "NOT_ISSUED"
    assert status["forecast_issued"] is False
    assert status["reason_code"] == "LEGACY_SIGNAL_HISTORY_ANALYSIS_RETIRED"
    assert status["trade_recommendations"] == []
    assert "accuracy" not in status
    assert "probability" not in status


def test_legacy_market_analysis_workflow_is_disabled_and_has_no_external_access():
    content = WORKFLOW.read_text(encoding="utf-8")
    assert "if: false" in content
    assert "permissions: {}" in content
    assert "secrets." not in content
    assert "git push" not in content
    assert "contents: write" not in content
    assert "schedule:" not in content
    assert "Disabled: legacy market-analysis output is not a validated XRP forecast." in content
