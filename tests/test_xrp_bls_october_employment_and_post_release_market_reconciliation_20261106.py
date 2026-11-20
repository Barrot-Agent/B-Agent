from __future__ import annotations

import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T134313Z-bls-october-employment-and-xrp-post-release-market-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_bls_primary_release_is_point_in_time_and_actuals_are_correct() -> None:
    data = load_artifact()
    macro = data["macro"]
    actual = macro["actual"]

    assert data["cutoff"]["event_time_utc"] == "2026-11-06T13:30:00Z"
    assert macro["release"] == "US Employment Situation — October 2026"
    assert actual["nonfarm_payroll_change"] == 165000
    assert actual["unemployment_rate_pct"] == 4.1
    assert actual["average_hourly_earnings_change_mom_pct"] == 0.4
    assert actual["average_hourly_earnings_change_yoy_pct"] == 3.1
    assert actual["average_hourly_earnings_usd"] == 38.00
    assert actual["revisions"]["august"]["change"] == 53000
    assert actual["revisions"]["september"]["change"] == 31000
    assert actual["revisions"]["combined_change"] == 84000


def test_survey_disagreement_is_preserved_without_averaging() -> None:
    macro = load_artifact()["macro"]
    assert macro["expectations"]["reuters_survey"]["nonfarm_payroll_change"] == 65000
    assert macro["expectations"]["wsj_reported_survey"]["nonfarm_payroll_change"] == 59000
    assert macro["surprise_vs_reuters"]["nonfarm_payroll_change"] == 100000
    assert "disagreement" in macro["market_reaction_reporting"]
    assert "average" in macro["expectations"]["wsj_reported_survey"]["note"]


def test_kraken_post_release_quote_receipt_and_top_of_book_metrics() -> None:
    data = load_artifact()
    market = data["market"]["kraken_xrp_usd"]
    receipt = next(
        source["receipt"]
        for source in data["source_registry"]
        if source["id"] == "kraken_xrp_usd_post_release_ticker"
    )

    assert market["last_trade_usd"] == 1.18134
    assert market["best_bid_usd"] == 1.18333
    assert market["best_ask_usd"] == 1.18334
    assert round(market["spread_bps"], 4) == 0.0845
    assert market["volume_24h_xrp"] == 44440274.07079497
    assert market["vwap_24h_usd"] == 1.22731060
    assert market["exact_provider_timestamp_utc"] is None
    assert market["depth_status"].startswith("Top-of-book only")
    assert len(receipt["digest"]) == 64
    assert receipt["scope"].startswith("Exact 317-character JSON text")


def test_derivatives_aggregator_universes_are_not_combined() -> None:
    market = load_artifact()["market"]
    trad = market["tradradar_derivatives"]
    alpha = market["alpha_finance_derivatives"]

    assert trad["open_interest_usd"] == 1920000000
    assert trad["venue_row_sum_usd"] == 1916890000
    assert trad["open_interest_change_24h_pct"] == -6.12
    assert trad["long_liquidations_usd"] == 18680000
    assert trad["short_liquidations_usd"] == 648780
    assert trad["long_short_account_ratio"] == 3.97
    assert alpha["open_interest_usd"] == 2780000000
    assert alpha["long_liquidations_24h_usd"] == 21400000
    assert alpha["short_liquidations_24h_usd"] == 765800
    assert "do not average" in alpha["note"]
    assert "combined_open_interest_usd" not in market


def test_etf_holdings_delta_is_not_mislabelled_as_cash_flow() -> None:
    etf = load_artifact()["market"]["etf_holdings_delta"]

    assert etf["net_holdings_change_xrp"] == -149487
    assert etf["settled_trading_days"] == 4
    assert etf["total_holdings_xrp"] == 1196450700
    assert round(etf["net_flow_as_pct_of_total_holdings"], 6) == -0.012494
    assert "not direct AP cash" in etf["interpretation_limit"]


def test_competing_hypotheses_include_disconfirming_evidence() -> None:
    hypotheses = load_artifact()["competing_hypotheses"]

    assert len(hypotheses) == 5
    assert all(item["supporting_evidence"] for item in hypotheses)
    assert all(item["disconfirming_evidence"] for item in hypotheses)


def test_forecast_remains_unissued_and_no_trade_action_occurred() -> None:
    data = load_artifact()

    assert data["status"] == "research_only_model_ineligible"
    assert data["model_admission"]["eligible_for_feature_store"] is False
    assert data["forecast_status"]["status"] == "NOT_ISSUED"
    assert data["action_policy"]["paper_trading_performed"] is False
    assert data["action_policy"]["real_money_actions_performed"] is False
    assert data["action_policy"]["external_actions_performed"] is False
