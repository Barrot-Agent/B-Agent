import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T040046Z-xrp-spot-derivatives-etf-liquidity-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_direct_exchange_response_receipts_match_embedded_response_text():
    artifact = load_artifact()
    for record in artifact["direct_exchange_observations"]:
        raw = record["raw_response_text"].encode("utf-8")
        assert len(raw) == record["raw_response_bytes"]
        assert hashlib.sha256(raw).hexdigest() == record["raw_response_sha256"]


def test_spot_quotes_preserve_units_and_level_one_scope():
    artifact = load_artifact()
    kraken, okx = artifact["direct_exchange_observations"]
    assert kraken["parsed"]["pair"] == "XRP/USD"
    assert okx["parsed"]["instrument"] == "XRP-USDT"
    assert kraken["provider_event_time_utc"] is None
    assert okx["provider_age_seconds_at_capture"] > okx["freshness_limit_seconds"]
    assert okx["quality_decision"] == "STALE_FOR_LIVE_FEATURES"
    assert "Level-1 quote only; no multi-level depth" in kraken["limitations"]


def test_spread_and_cross_venue_arithmetic_reconcile():
    artifact = load_artifact()
    kraken, okx = artifact["direct_exchange_observations"]
    k = kraken["parsed"]
    o = okx["parsed"]
    expected_k = (k["best_ask_usd"] - k["best_bid_usd"]) / ((k["best_ask_usd"] + k["best_bid_usd"]) / 2) * 10000
    expected_o = (o["best_ask_usdt"] - o["best_bid_usdt"]) / ((o["best_ask_usdt"] + o["best_bid_usdt"]) / 2) * 10000
    expected_diff = (o["last_usdt"] / k["last_usd"] - 1) * 100
    assert abs(expected_k - artifact["derived_checks"]["kraken_level_1_spread_bps"]) < 1e-10
    assert abs(expected_o - artifact["derived_checks"]["okx_level_1_spread_bps"]) < 1e-10
    assert abs(expected_diff - artifact["derived_checks"]["raw_okx_last_premium_vs_kraken_pct"]) < 1e-10


def test_daily_open_and_rolling_open_are_not_conflated():
    artifact = load_artifact()
    derived = artifact["derived_checks"]
    assert "UTC daily open" in artifact["direct_exchange_observations"][0]["limitations"][2]
    assert derived["kraken_last_vs_utc_daily_open_pct"] < 0
    assert derived["okx_last_vs_rolling_24h_open_pct"] < 0


def test_derivatives_provider_disagreement_is_not_averaged():
    artifact = load_artifact()
    alpha = artifact["secondary_market_observations"][0]["reported"]["open_interest_usd"]
    trad = artifact["secondary_market_observations"][1]["reported"]["open_interest_usd"]
    assert alpha - trad == artifact["derived_checks"]["alpha_vs_tradradar_open_interest_difference_usd"]
    assert artifact["derived_checks"]["alpha_vs_tradradar_open_interest_ratio"] > 1.4
    assert len(artifact["competing_hypotheses"]) >= 2


def test_etf_flow_vintages_and_fund_universes_remain_distinct():
    artifact = load_artifact()
    alpha, partial, insights = artifact["etf_flow_reconciliation"]
    assert alpha["reported_funds"] == 5
    assert partial["funds_reported"] == 1
    assert partial["completeness"] == "PARTIAL"
    assert insights["reported_universe"] == "6 US spot funds plus BITW"
    assert insights["nov_6_status"] == "PROVISIONAL"
    assert artifact["competing_hypotheses"][2]["status"] == "DATA_COMPLETENESS_UNRESOLVED"


def test_stale_order_book_snapshot_is_context_only_and_forecast_stays_unissued():
    artifact = load_artifact()
    depth = artifact["liquidity_context"][0]
    assert depth["age_seconds_at_capture"] > 300
    assert depth["quality_decision"] == "HISTORICAL_CONTEXT_ONLY"
    assert artifact["model_eligibility"]["status"] == "NOT_ADMITTED"
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["external_actions"] == {
        "orders_sent": False,
        "paper_trade_created": False,
        "real_money_used": False,
    }
