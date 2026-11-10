from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T022802Z-xrp-market-etf-xrpl-amendment-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_kraken_rendered_hash_and_missing_timestamp_limits_are_preserved():
    row = load_artifact()["spot_market"]["observations"][0]
    assert hashlib.sha256(row["rendered_response_text"].encode("utf-8")).hexdigest() == row["rendered_response_sha256"]
    assert row["rendered_response_sha256"] == "3856053cd1568ea73522e82c035380ee22ed6a6ca6870bd69c46dd1c7f59d0bb"
    assert row["provider_event_timestamp_utc"] is None
    assert row["retrieval_timestamp_utc"] is None
    assert row["raw_http_wire_bytes_captured"] is False


def test_kraken_spread_and_top_level_sizes_reconcile_without_depth_claim():
    row = load_artifact()["spot_market"]["observations"][0]
    bid, ask = row["best_bid_usd"], row["best_ask_usd"]
    expected = (ask - bid) / ((ask + bid) / 2) * 10_000
    assert math.isclose(row["displayed_spread_bps"], expected, rel_tol=0, abs_tol=1e-12)
    assert row["best_bid_size_xrp"] == 7352
    assert row["best_ask_size_xrp"] == 301
    assert row["last_trade_usd"] > row["best_ask_usd"]
    assert any("not full depth" in x for x in row["limitations"])


def test_tradradar_venue_oi_sum_and_liquidation_lower_bound_reconcile():
    row = load_artifact()["derivatives"]
    assert sum(row["venue_scope"]["venue_oi_usd_rounded"].values()) == 1_923_600_000
    assert row["venue_scope"]["open_interest_exchanges"] == 7
    assert math.isclose(row["long_liquidations_usd"] + row["short_liquidations_usd"], 14_911_780, rel_tol=0, abs_tol=1)
    assert row["liquidations_24h_lower_bound_usd"] == 14_910_000
    assert row["long_short_account_ratio"] == 4.05
    assert any("account-count" in x for x in row["limitations"])


def test_etf_partial_days_are_not_promoted_to_zero_total_flow():
    item = load_artifact()["etf_flows"]
    crypto = item["cryptokeyhole"]
    assert crypto["nov5_2026"]["status"] == "PARTIAL"
    assert crypto["nov5_2026"]["reporting_funds"] == 1
    assert crypto["nov5_2026"]["complete_daily_total"] is False
    assert crypto["nov4_2026"]["status"] == "PARTIAL"
    assert crypto["nov4_2026"]["missing_fund"] == "XRPZ"
    assert item["reconciliation"]["direct_netting_permitted"] is False
    assert item["reconciliation"]["averaging_permitted"] is False


def test_xrp_insights_methodology_is_kept_separate_from_cryptokeyhole():
    item = load_artifact()["etf_flows"]
    insights = item["xrp_insights"]
    assert insights["data_as_of_date"] == "2026-11-04"
    assert insights["nov5_row_status"] == "PROVISIONAL"
    assert insights["nov2_to_nov4_settled_window_net_holdings_delta_xrp"] == -259701
    assert "BITW" in insights["fund_scope"]
    assert any("reconstructed" in x for x in insights["methodology"])
    assert item["cryptokeyhole"]["daily_tracked_funds"] != insights["fund_scope"]


def test_xrpl_cleanup_is_enabled_but_lending_and_vault_are_not():
    item = load_artifact()["xrpl_governance"]
    assert item["fixCleanup3_4_0"]["status"] == "ENABLED"
    assert item["fixCleanup3_4_0"]["enabled_ledger"] == 108112129
    for row in item["pending_amendments"]:
        assert row["yes_votes"] < row["required_yes_votes"]
        assert row["status"] == "VOTING_NO_MAJORITY"
    assert "does not itself activate the Lending Protocol" in item["interpretation"]


def test_artifact_is_not_model_eligible_and_issues_no_forecast():
    item = load_artifact()
    assert item["model_eligible"] is False
    assert item["forecast_status"] == "NOT_ISSUED"
    assert item["data_cutoff_utc"] is None
    assert len(item["competing_hypotheses"]) == 6
    assert len(item["model_ineligibility_reasons"]) >= 8
