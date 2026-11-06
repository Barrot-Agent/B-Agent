from __future__ import annotations

import json

from scripts.market_analysis_engine import main


def test_legacy_market_analysis_is_inert_even_when_old_opt_in_is_set(
    monkeypatch, capsys
):
    monkeypatch.setenv("BARROT_ENABLE_LEGACY_MARKET_ANALYSIS", "YES")
    monkeypatch.setenv("GROQ_API_KEY", "must-not-be-used")
    monkeypatch.setenv("DATABRICKS_TOKEN", "must-not-be-used")

    assert main() == 0
    result = json.loads(capsys.readouterr().out)

    assert result["status"] == "NOT_ISSUED"
    assert result["forecast_issued"] is False
    assert result["reason_code"] == "LEGACY_SIGNAL_HISTORY_ANALYSIS_RETIRED"
    assert result["trade_recommendations"] == []
    assert "No Databricks or Groq request" in result["message"]
