import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T180016Z-xrp-late-session-spot-derivatives-etf-macro-update.json"


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None
    return parsed.astimezone(timezone.utc)


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_late_session_artifact_has_append_only_cutoff_and_resolvable_sources():
    data = _load()
    assert data["append_only"]["original_artifacts_modified"] is False
    assert _utc(data["recorded_at_utc"]) == _utc(data["research_cutoff_utc"])
    source_ids = [item["source_id"] for item in data["source_registry"]]
    assert len(source_ids) == len(set(source_ids))
    known = set(source_ids)
    for observation in data["competing_hypotheses"]:
        assert observation["id"] and observation["claim"]
        assert observation["support"] and observation["disconfirming_or_missing"]
        assert observation["tests"]
    assert len(data["competing_hypotheses"]) >= 4


def test_kraken_ticker_arithmetic_and_time_window_labels_are_correct():
    market = _load()["market_snapshot"]
    spot = market["kraken_spot"]
    midpoint = (spot["best_bid_usd"] + spot["best_ask_usd"]) / 2
    spread_bps = (spot["best_ask_usd"] - spot["best_bid_usd"]) / midpoint * 10000
    assert abs(midpoint - spot["midpoint_usd"]) < 1e-12
    assert abs(spread_bps - spot["spread_bps"]) < 1e-12
    assert spot["utc_day_open_label"] == "current UTC-day open; not a rolling 24-hour open"
    assert spot["volume_24h_xrp"] > 0 and spot["vwap_24h_usd"] > 0
    assert spot["provider_event_time_utc"] is None
    assert spot["model_eligible"] is False


def test_same_venue_quote_comparison_does_not_claim_executable_depth_or_trade_flow():
    comparison = _load()["market_snapshot"]["same_venue_comparison"]
    assert comparison["prior_observation_at_utc"] == "2026-11-05T17:30:50Z"
    expected = (comparison["current_last_usd"] / comparison["prior_last_usd"] - 1) * 100
    assert abs(expected - comparison["last_price_difference_pct_vs_prior_capture"]) < 1e-12
    assert comparison["elapsed_seconds"] is None
    assert comparison["last_price_change_pct_over_observation_interval"] is None
    assert comparison["observation_interval_status"] == "UNKNOWN"
    assert "retrieval time was not exposed" in comparison["interpretation"]


def test_derivatives_aggregator_scope_and_liquidation_disagreement_are_preserved():
    data = _load()["market_snapshot"]["derivatives"]
    trad = data["tradradar"]
    alpha = data["alpha_finance"]
    assert trad["open_interest_usd"] != alpha["open_interest_usd"]
    assert data["reconciliation"]["aggregation"] == "not_averaged"
    assert trad["long_liquidations_usd"] > trad["short_liquidations_usd"]
    assert alpha["short_liquidations_24h_usd"] > alpha["long_liquidations_24h_usd"]
    assert trad["model_eligible"] is False and alpha["model_eligible"] is False


def test_etf_vintages_keep_settled_and_partial_universes_separate():
    etf = _load()["market_snapshot"]["etf_flows"]
    assert etf["xrp_insights"]["data_as_of"] == "2026-11-04"
    assert etf["xrp_insights"]["settled_trading_days"] == 3
    assert etf["crypto_etf_today"]["reported_funds"] == 2
    assert etf["crypto_etf_today"]["fund_universe"] == 5
    assert etf["crypto_etf_today"]["status"] == "PARTIAL"
    assert etf["cryptokeyhole"]["latest_complete_date"] == "2026-11-03"
    assert etf["reconciliation"]["direct_ap_cash_records_retrieved"] is False
    assert etf["reconciliation"]["aggregation"] == "not_averaged"


def test_macro_context_is_counterevidence_not_xrp_causality():
    data = _load()
    assert data["macro_context"]["ap_us_equities"]["date"] == "2026-11-05"
    assert data["macro_context"]["reuters_oil_and_iran"]["date"] == "2026-11-05"
    assert any(item["id"] == "broad_risk_off_ai_equity_selloff" for item in data["competing_hypotheses"])
    assert data["admission"]["model_eligible"] is False
    assert data["admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["admission"]["directional_forecast_issued"] is False
    assert data["admission"]["paper_trade_executed"] is False
