from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T151019Z-xrp-spot-derivatives-etf-secondary-context-reconciliation.json"
)


def _load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_direct_exchange_payloads_and_normalized_article_excerpt_match_hashes():
    artifact = _load()
    for source in artifact["sources"][:2]:
        assert hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest() == source["raw_response_sha256"]
        assert source["hash_scope"].startswith("SHA-256 of exact JSON text")
    article = artifact["sources"][2]
    assert hashlib.sha256(article["normalized_excerpt"].encode("utf-8")).hexdigest() == article["normalized_excerpt_sha256"]


def test_kraken_unknown_event_time_is_not_replaced_and_last_is_not_midpoint():
    artifact = _load()
    source = artifact["sources"][0]
    normalized = source["normalized"]
    assert source["provider_event_timestamp_utc"] is None
    assert source["freshness"] == "UNKNOWN_PROVIDER_EVENT_TIME"
    assert normalized["last_usd"] < normalized["best_bid_usd"]
    assert normalized["midpoint_usd"] == 1.165675
    assert source["model_eligible"] is False


def test_okx_provider_timestamp_is_fresh_using_conservative_clock_reference():
    artifact = _load()
    source = artifact["sources"][1]
    captured = datetime.fromisoformat(artifact["captured_at_utc"].replace("Z", "+00:00"))
    event = datetime.fromisoformat(source["provider_event_timestamp_utc"].replace("Z", "+00:00"))
    age = (captured - event).total_seconds()
    assert age == source["age_at_reference_seconds"] == 8.435
    assert source["age_is_upper_bound"] is True
    assert 0 <= age <= 300
    assert source["freshness"] == "FRESH_WITHIN_300_SECONDS"


def test_level_one_spreads_and_cross_venue_difference_are_reproducible():
    artifact = _load()
    kraken, okx = artifact["sources"][:2]
    k = kraken["normalized"]
    o = okx["normalized"]
    k_spread = (k["best_ask_usd"] - k["best_bid_usd"]) / k["midpoint_usd"] * 10000
    o_spread = (o["best_ask_usdt"] - o["best_bid_usdt"]) / o["midpoint_usdt"] * 10000
    assert abs(k_spread - k["level1_spread_bps"]) < 1e-8
    assert abs(o_spread - o["level1_spread_bps"]) < 1e-8
    raw_diff = abs(k["last_usd"] - o["last_usdt"]) / ((k["last_usd"] + o["last_usdt"]) / 2) * 100
    assert abs(raw_diff - artifact["reconciliation"]["raw_last_price_difference_pct"]) < 1e-8
    assert "not normalized" in artifact["reconciliation"]["currency_basis"].lower()
    assert artifact["reconciliation"]["depth"] == "NOT_CAPTURED"


def test_secondary_lineage_is_not_counted_as_independent_confirmation():
    article = _load()["sources"][2]
    lineage = article["source_lineage"]
    assert "CoinGlass -> U.Today" in lineage["liquidation_data"]
    assert "SoSoValue -> CoinGape" in lineage["etf_data"]
    assert "not three independent confirmations" in lineage["liquidation_data"]
    assert "not an issuer-primary" in lineage["etf_data"]
    assert article["model_eligible"] is False


def test_account_ratio_open_interest_and_liquidations_keep_distinct_semantics():
    article = _load()["sources"][2]
    observations = article["observations"]
    assert observations["okx_long_short_account_ratio"]["2026-11-07T06:00:00Z"] == 4.3
    assert observations["okx_open_interest_usd"]["2026-11-04"] == 132100000
    assert observations["okx_open_interest_usd"]["2026-11-06"] == 117100000
    assert observations["liquidation_total_usd"] == 16750000
    assert "accounts, not notional" in " ".join(article["limitations"])


def test_counter_hypotheses_retain_both_bearish_and_stabilization_evidence():
    artifact = _load()
    hypotheses = {item["id"]: item for item in artifact["competing_hypotheses"]}
    assert set(hypotheses) == {"H1_LEVERAGED_LONG_OVERHANG", "H2_POSITION_RESET_AND_MEAN_REVERSION", "H3_BROADER_RISK_OFF"}
    assert hypotheses["H1_LEVERAGED_LONG_OVERHANG"]["disconfirming_evidence"]
    assert hypotheses["H2_POSITION_RESET_AND_MEAN_REVERSION"]["disconfirming_evidence"]
    assert hypotheses["H3_BROADER_RISK_OFF"]["disconfirming_evidence"]


def test_editorial_scenario_levels_are_not_promoted_to_forecasts():
    artifact = _load()
    assert artifact["scenario_levels"]["source"].startswith("CryptoTicker editorial")
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is None
    assert artifact["forecast"]["probabilities"] is None
    assert artifact["model_admission"]["admitted_to_live_price_features"] is False
    assert artifact["model_admission"]["admitted_to_historical_price_features"] is False
    assert artifact["forecast"]["shadow_or_paper_trade"] is False
    assert artifact["forecast"]["real_money_action"] is False
