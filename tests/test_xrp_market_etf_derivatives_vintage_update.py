import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T053921Z-xrp-market-etf-derivatives-vintage-update.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_market_vintage_artifact_has_unique_sources_and_quarantines_unreceipted_data():
    data = load()
    sources = data["source_registry"]
    ids = [source["id"] for source in sources]
    assert len(ids) == len(set(ids))
    assert len(ids) >= 6
    assert all(source["raw_content_sha256"] is None for source in sources)
    assert all(source["model_eligible"] is False for source in sources)
    assert data["data_quality"]["raw_source_bytes_captured"] is False
    assert data["data_quality"]["independent_timestamp_anchor"] is False


def test_kraken_spot_quote_arithmetic_and_yahoo_disagreement_are_preserved():
    data = load()
    spot = data["market_snapshot"]["spot"]
    expected_mid = (spot["best_bid_usd"] + spot["best_ask_usd"]) / 2
    expected_spread = (spot["best_ask_usd"] - spot["best_bid_usd"]) / expected_mid * 10000
    assert math.isclose(spot["mid_usd"], expected_mid, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(spot["displayed_spread_bps"], expected_spread, rel_tol=0, abs_tol=1e-12)
    assert spot["volume_24h_xrp"] > 0
    assert spot["low_24h_usd"] <= spot["last_usd"] <= spot["high_24h_usd"]

    disagreement = data["market_snapshot"]["quarantined_price_disagreement"]
    assert disagreement["yahoo_displayed_price_usd"] < disagreement["kraken_24h_low_usd"]
    assert disagreement["classification"] == "stale_or_non_comparable_quote_quarantined"


def test_derivatives_contracts_reconcile_but_provider_difference_is_not_averaged():
    derivatives = load()["market_snapshot"]["derivatives"]
    kodexius = derivatives["kodexius"]
    total = sum(item["open_interest_usd"] for item in kodexius["contract_breakdown"])
    assert math.isclose(total, kodexius["open_interest_usd"], rel_tol=0, abs_tol=1)
    assert len(kodexius["contract_breakdown"]) == 7
    assert kodexius["weighted_funding_rate_8h_pct"] > 0
    assert derivatives["fibonomy_binance"]["open_interest_usd"] != next(
        item["open_interest_usd"]
        for item in kodexius["contract_breakdown"]
        if item["venue"] == "Binance" and item["instrument"] == "XRPUSDT"
    )
    assert derivatives["binance_oi_provider_difference_usd"] == 990000
    assert "no average" in derivatives["reconciliation"].lower()


def test_etf_flow_vintages_keep_universes_and_partial_rows_distinct():
    etf = load()["market_snapshot"]["etf_flows"]
    insights = etf["xrp_insights"]
    keyhole = etf["cryptokeyhole"]
    assert insights["settled_data_as_of_date"] == "2026-11-03"
    assert insights["latest_row_date"] == "2026-11-04"
    assert insights["latest_row_status"] == "provisional"
    assert insights["net_flow_xrp_nov2_nov3"] == -194875
    assert "BITW" in insights["funds_reporting_universe"]
    assert "XRPR" in insights["funds_reporting_universe"]
    assert insights["gxrp_flow_status"] == "excluded"

    assert keyhole["latest_complete_date"] == "2026-11-03"
    assert keyhole["net_flow_xrp_nov2_nov3"] == -6678
    assert keyhole["nov4_partial_funds_reporting"] == 2
    assert keyhole["nov4_funds_reporting_total"] == 4
    assert "XRPR" not in keyhole["fund_universe"]
    assert "BITW" not in keyhole["fund_universe"]

    arithmetic = etf["arithmetic"]
    assert arithmetic["two_day_flow_difference_xrp"] == -188197
    assert arithmetic["holdings_total_difference_xrp"] == 119592749
    assert arithmetic["remaining_holdings_residual_xrp"] == 18141
    assert "not attributed" in etf["interpretation"][1]


def test_market_vintage_does_not_issue_directional_xrp_forecast():
    data = load()
    assert data["model_eligible"] is False
    assert data["predictions"]["issued"] is False
    assert data["predictions"]["status"] == "NOT_ISSUED"
    assert data["market_snapshot"]["spot"]["model_eligible"] is False
    assert data["market_snapshot"]["derivatives"]["kodexius"]["model_eligible"] is False
    assert data["market_snapshot"]["etf_flows"]["xrp_insights"]["model_eligible"] is False
