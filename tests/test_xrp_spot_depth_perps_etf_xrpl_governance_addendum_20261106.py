from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T140454Z-xrp-spot-depth-perps-etf-xrpl-governance-addendum.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_rendered_source_excerpt_hashes_are_reproducible_and_scoped():
    data = load_artifact()
    assert len(data["source_registry"]) == 10
    for source in data["source_registry"]:
        receipt = source["receipt"]
        assert receipt["algorithm"] == "SHA-256"
        assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == receipt["digest"]
        assert "not byte-complete" in receipt["scope"]


def test_kraken_quote_arithmetic_and_asynchronous_last_trade_are_preserved():
    data = load_artifact()["spot_market"]
    expected = (data["best_ask_usd"] - data["best_bid_usd"]) / ((data["best_ask_usd"] + data["best_bid_usd"]) / 2) * 10000
    assert math.isclose(data["spread_bps"], expected, rel_tol=0, abs_tol=1e-6)
    assert data["last_trade_below_best_bid"] if "last_trade_below_best_bid" in data else data["quote_consistency"]["last_trade_below_best_bid"]
    assert data["provider_event_timestamp_utc"] is None
    assert data["quote_consistency"]["same_event_time_not_established"] if "same_event_time_not_established" in data["quote_consistency"] else "not proven" in data["quote_consistency"]["interpretation"]


def test_fuelmaps_depth_arithmetic_venue_coverage_and_cancel_risk():
    data = load_artifact()["order_book_depth"]
    assert data["snapshot_time_utc"] == "2026-11-06T13:00:00Z"
    assert "Binance" in data["excluded_venues"] and "Bitget" in data["excluded_venues"]
    for row in data["levels"]:
        calculated = row["bid_depth_usd"] / (row["bid_depth_usd"] + row["ask_depth_usd"]) * 100
        assert abs(calculated - row["bid_share_pct"]) < 0.15
    assert next(x for x in data["levels"] if x["band"] == "±10%")["venues_reporting"] == 5
    assert any("cancelled" in item for item in data["limitations"])


def test_derivatives_rows_reconcile_but_provider_universes_are_not_averaged():
    data = load_artifact()["derivatives"]
    trad = data["tradradar"]
    assert sum(trad["venue_oi_usd"].values()) == trad["venue_oi_row_sum_usd"]
    assert trad["liquidations_24h_lower_bound_usd"] == 19_520_000
    assert math.isclose(trad["long_liquidations_usd"] + trad["short_liquidations_usd"], trad["liquidation_component_sum_usd"], abs_tol=1)
    alpha = data["alpha_finance"]
    assert alpha["open_interest_all_venues_usd"] == 2_760_000_000
    assert data["comparability"]["headline_open_interest_values_comparable"] is False if "comparability" in data else "do not average" in alpha["limitations"][0]


def test_etf_provider_disagreement_is_preserved_not_net_or_averaged():
    data = load_artifact()["etf_flows"]
    alpha = data["alpha_finance_five_fund"]
    insights = data["xrp_insights_seven_instrument"]
    assert alpha["latest_session_net_flow_usd"] == 0
    assert alpha["thirty_session_net_flow_usd"] == 60_800_000
    assert insights["net_holdings_change_xrp"] == -149_487
    assert insights["settled_trading_days"] == 4
    assert data["reconciliation"]["values_comparable"] is False
    assert data["reconciliation"]["direct_cash_creation_redemption_observed"] is False


def test_xrpl_votes_and_fix_cleanup_do_not_imply_lending_activation():
    data = load_artifact()["xrpl_governance"]
    assert data["required_yes_votes"] == 29
    assert data["votes"]["SingleAssetVault"]["yes"] == 23
    assert data["votes"]["LendingProtocol"]["yes"] == 21
    assert data["votes"]["LendingProtocolV1_1"]["yes"] == 21
    assert data["amendment_state"]["active_14_day_countdowns"] == 0
    assert data["fixCleanup3_4_0"]["status"] == "ENABLED"
    assert data["fixCleanup3_4_0"]["enabled_ledger"] == 108112129
    assert "LendingProtocol" in data["fixCleanup3_4_0"]["not_equivalent_to"]
    assert "SingleAssetVault" in data["fixCleanup3_4_0"]["not_equivalent_to"]


def test_lending_collateral_boundary_matches_official_design():
    data = load_artifact()["xrpl_governance"]["collateral_boundary"]
    assert "Uncollateralized" in data["lending_protocol_design"]
    assert "funding capital" in data["vault_deposits"]
    assert "not evidence of XRP posted" in data["first_loss_capital"]
    assert "on-chain custodians" in data["optional_collateralized_extension"]
    assert "No live" in data["current_usage_evidence"]


def test_clarity_act_vote_is_not_mislabeled_as_final_defeat_or_passage():
    data = load_artifact()["regulatory_context"]
    assert data["record_vote_number"] == 234
    assert data["tally"] == {"yea": 49, "nay": 50, "not_voting": 1}
    assert "not a final passage vote" in data["status_limit"]
    assert "motion to reconsider" in data["result"]


def test_hypotheses_retain_counterevidence_and_no_forecast_or_trade_is_created():
    data = load_artifact()
    assert len(data["competing_hypotheses"]) == 6
    assert all(x["supporting"] and x["disconfirming"] for x in data["competing_hypotheses"])
    assert data["forecast_status"]["status"] == "NOT_ISSUED"
    assert data["forecast_status"]["target"] is None
    assert data["forecast_status"]["horizon"] is None
    assert data["safety"]["paper_trade_executed"] is False
    assert data["safety"]["real_money_action"] is False
    assert data["model_eligibility"]["eligible"] is False
