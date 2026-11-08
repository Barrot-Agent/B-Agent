from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261108T093447Z-xrp-spot-etf-derivatives-liquidity-refresh.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_source_receipt_hashes_match_exact_stored_excerpts():
    data = load_artifact()
    receipts = data["source_receipts"]
    ids = [row["source_id"] for row in receipts]
    assert len(ids) == len(set(ids))
    for row in receipts:
        digest = hashlib.sha256(row["excerpt"].encode("utf-8")).hexdigest()
        assert digest == row["excerpt_sha256"]


def test_kraken_and_okx_spot_timestamps_and_quote_units_are_not_normalized():
    data = load_artifact()
    spot = data["market_observations"]["spot"]
    kraken = spot["kraken_xrp_usd"]
    okx = spot["okx_xrp_usdt"]
    assert kraken["provider_event_timestamp_utc"] is None
    assert okx["provider_snapshot_timestamp_utc"] == "2026-11-08T09:21:14.170Z"
    assert okx["age_seconds_at_reference"] == 812.83
    assert kraken["last_usd"] == 1.16
    assert okx["last_usdt"] == 1.1615
    assert data["data_quality"]["usd_usdt_normalized"] is False


def test_opposing_level1_imbalances_are_not_collapsed_into_one_signal():
    data = load_artifact()
    spot = data["market_observations"]["spot"]
    assert spot["derived"]["kraken_bid_ask_size_ratio"] > 4.4
    assert spot["derived"]["okx_bid_ask_size_ratio"] < 0.5
    assert spot["derived"]["raw_okx_vs_kraken_last_pct"] > 0
    assert data["data_quality"]["multi_level_depth"] is False


def test_derivatives_open_interest_and_liquidations_remain_disputed():
    data = load_artifact()
    deriv = data["market_observations"]["derivatives"]
    assert deriv["tradradar"]["open_interest_usd"] == 1_910_000_000
    assert deriv["webeconomia"]["open_interest_usd"] == 1_580_000_000
    assert deriv["disagreement"]["status"] == "UNRESOLVED_DO_NOT_AVERAGE"
    assert deriv["disagreement"]["open_interest_difference_usd"] == 330_000_000
    assert deriv["disagreement"]["liquidation_max_to_min_ratio"] > 4.2


def test_etf_flow_universes_and_partial_publication_are_preserved():
    data = load_artifact()
    etf = data["market_observations"]["etf_flows"]
    assert etf["cryptokeyhole"]["nov6_partial_flow_xrp"] == -752_048
    assert etf["cryptokeyhole"]["nov6_coverage"] == "3 of 4; Franklin XRPZ missing"
    assert etf["xrp_insights"]["nov6_flow_xrp"] == -663_043
    assert etf["xrp_insights"]["nov2_to_nov6_week_flow_xrp"] == -812_500
    assert etf["alpha_finance"]["nov6_flow_usd"] == 0
    assert etf["alpha_finance"]["thirty_session_flow_usd"] == 45_900_000
    assert "do not average" in etf["reconciliation"]


def test_stablecoin_dashboard_internal_contradiction_is_retained_in_receipt():
    data = load_artifact()
    row = next(x for x in data["source_receipts"] if x["source_id"] == "webeconomia_xrp_derivatives_stablecoin_context")
    assert "292,3 mld" in row["excerpt"]
    assert "293,6 mld" in row["excerpt"]
    assert "−15,06 mld" in row["excerpt"]
    assert "−12,73 mld" in row["excerpt"]


def test_counter_hypotheses_and_forecast_abstention_are_present():
    data = load_artifact()
    assert len(data["counter_hypotheses"]) >= 5
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_probability_issued"] is False
    assert data["external_actions"] == {
        "paper_trade": False,
        "real_money": False,
        "funds_transfer": False,
        "external_model_transfer": False,
    }
