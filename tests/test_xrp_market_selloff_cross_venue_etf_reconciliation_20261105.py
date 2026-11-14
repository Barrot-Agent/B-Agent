import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T160707Z-xrp-market-selloff-cross-venue-etf-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_spot_arithmetic_and_timestamp_limits_are_explicit():
    data = load()
    spot = data["market_snapshot"]["kraken_spot"]
    expected_mid = (spot["best_bid_usd"] + spot["best_ask_usd"]) / 2
    expected_spread = (spot["best_ask_usd"] - spot["best_bid_usd"]) / expected_mid * 10000
    assert spot["midpoint_usd"] == expected_mid
    assert abs(spot["spread_bps"] - expected_spread) < 1e-12
    assert spot["provider_event_time_utc"] is None
    assert spot["utc_day_open_label"] == "current UTC-day open; not a rolling 24-hour open"
    assert data["source_capture_policy"]["raw_bytes_preserved"] is False


def test_derivatives_provider_disagreement_is_preserved_not_averaged():
    derivatives = load()["market_snapshot"]["derivatives"]
    alpha = derivatives["alpha_finance"]
    trad = derivatives["tradradar"]
    disagreement = derivatives["cross_provider_disagreement"]
    assert alpha["open_interest_usd"] == 2_840_000_000
    assert trad["open_interest_usd"] == 1_950_000_000
    assert disagreement["absolute_difference_usd"] == 890_000_000
    assert disagreement["aggregation"] == "not_averaged"
    assert trad["long_short_account_ratio"] == 3.55
    assert trad["long_account_pct"] == 78.0
    assert trad["liquidations_24h_longs_usd"] > trad["liquidations_24h_shorts_usd"]
    assert "modelled from open interest" in alpha["modelled_liquidation_clusters"]["method"]


def test_etf_flow_universes_and_partial_reporting_are_not_conflated():
    data = load()["market_snapshot"]["etf_flows"]
    insights = data["xrp_insights"]
    keyhole = data["cryptokeyhole"]
    alpha = data["alpha_finance"]
    maketo = data["maketo"]
    assert insights["net_flow_xrp_nov2_to_nov4"] == -259_701
    assert insights["trading_days_in_aggregate"] == 3
    assert keyhole["nov4_reporting_funds"] == "3 of 4"
    assert keyhole["missing_fund"] == "Franklin Templeton XRPZ"
    assert keyhole["nov4_partial_flow_xrp"] == -3_339
    assert alpha["funds_covered"] == 5 and alpha["nov4_reported_flow_usd"] == 0
    assert maketo["funds_covered"] == 5 and maketo["nov4_reported_flow_usd"] == 0
    assert data["reconciliation"]["aggregation"] == "not_averaged"
    assert "No direct AP cash" in data["reconciliation"]["cash_flow_status"]


def test_macro_selloff_is_a_counter_hypothesis_not_causal_attribution():
    data = load()
    macro = data["macro_context"]["reported_observations"]
    assert macro["sp500_change_pct"] == -3.2
    assert macro["nasdaq_change_pct"] == -4.9
    assert "does not prove" in data["macro_context"]["interpretation_limit"]
    assert {x["hypothesis_id"] for x in data["competing_hypotheses"]} == {
        "broad_risk_off",
        "leveraged_long_unwind",
        "xrp_specific_spot_supply_or_etf_pressure",
        "exchange_incident_contagion",
    }


def test_snapshot_is_research_only_and_no_forecast_is_issued():
    data = load()
    assert data["source_capture_policy"]["raw_source_sha256_receipts"] is None
    assert data["source_capture_policy"]["independent_timestamp_anchors"] is False
    assert data["admission"]["model_eligible"] is False
    assert data["admission"]["forecast_status"] == "NOT_ISSUED"
    assert data["admission"]["directional_forecast_issued"] is False
