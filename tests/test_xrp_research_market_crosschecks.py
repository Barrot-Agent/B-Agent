"""Regression tests for current XRP cross-venue and ETF-flow reconciliation."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261104T160731Z-cross-venue-market-etf-flow-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_rendered_market_and_etf_sources_are_not_model_eligible():
    data = load()
    assert data["forecast_issued"] is False
    assert data["prediction_status"] == "NOT_ISSUED"
    assert data["model_eligible"] is False
    assert all(source["model_eligible"] is False for source in data["source_registry"])
    assert all(source["raw_content_sha256"] is None for source in data["source_registry"])


def test_cross_venue_quotes_are_not_synchronized_or_mislabeled_as_arbitrage():
    data = load()["market_observations"]
    assert data["synchronization_status"] == "NOT_SYNCHRONIZED"
    assert data["kraken_xrpusd"]["source_event_timestamp"] == "not supplied"
    assert data["okx_xrpusdt"]["source_timestamp_utc"] == "2026-11-04T15:51:31.169Z"
    assert "not a synchronized cross-venue spread" in data["interpretation"]


def test_kraken_open_is_utc_day_open_not_rolling_24_hour_open():
    data = load()["market_observations"]["kraken_xrpusd"]
    assert data["utc_day_open_usd"] == 1.27513
    assert "not a rolling 24-hour open" in data["open_field_semantics"]


def test_etf_flows_are_holdings_changes_not_direct_cash_flows():
    data = load()["etf_flow_reconciliation"]
    assert data["data_as_of_date"] == "2026-11-03"
    assert data["daily_net_holdings_change_xrp"]["2026-11-02"] == -32825
    assert data["daily_net_holdings_change_xrp"]["2026-11-03"] == -162050
    assert data["two_day_net_holdings_change_xrp"] == -194875
    assert sum(data["daily_net_holdings_change_xrp"].values()) == data["two_day_net_holdings_change_xrp"]
    assert "not issuer-reported cash creations/redemptions" in " ".join(data["limitations"])
    assert "BITW" in data["fund_universe"] and "GXRP" in data["fund_universe"]
    assert data["model_eligible"] is False


def test_derivatives_provider_disagreement_is_preserved_without_averaging():
    data = load()["derivatives_reconciliation"]
    assert data["coingecko_open_interest_usd"] == 4188000000
    assert data["tradradar_open_interest_usd"] == 2020000000
    assert data["comparison_status"] == "NON_COMPARABLE_UNTIL_CONTRACT_AND_VENUE_SCOPE_RECONCILED"
    assert "Do not average" in data["rule"]


def test_xrpl_amendment_event_is_not_promoted_to_a_price_signal():
    event = load()["event_timeline"][0]
    assert event["amendment"] == "fixCleanup3_4_0"
    assert event["event_time_utc"] == "2026-11-04T14:52:00Z"
    assert event["ledger_index"] == 108112129
    assert "No XRP supply effect" in event["interpretation"]
