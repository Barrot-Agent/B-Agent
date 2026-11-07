import hashlib
import json
import math
from pathlib import Path

ARTIFACT = Path(
    "research/xrp_intelligence/20261107T233253Z-xrp-market-etf-derivatives-macro-vintage-reconciliation.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exchange_receipts_match_exact_preserved_response_text():
    data = load_artifact()
    assert {source["publisher"] for source in data["spot_sources"]} == {"Kraken", "OKX"}
    for source in data["spot_sources"]:
        digest = hashlib.sha256(source["raw_response_text"].encode("utf-8")).hexdigest()
        assert digest == source["raw_response_sha256"]


def test_spot_quotes_preserve_currency_timestamp_and_level_one_limits():
    data = load_artifact()
    kraken, okx = data["spot_sources"]
    assert kraken["instrument"] == "XRP/USD"
    assert kraken["provider_event_timestamp_utc"] is None
    assert kraken["freshness_status"] == "UNVERIFIABLE_NO_PROVIDER_EVENT_TIMESTAMP"
    assert okx["instrument"] == "XRP-USDT"
    assert okx["provider_timestamp_utc"] == "2026-11-07T23:28:53.572Z"
    assert okx["age_seconds_at_run_clock_reference"] == 239.428
    assert okx["freshness_status"] == "NEAR_300S_THRESHOLD_CAPTURE_CLOCK_UNCERTAIN"
    assert all(not source["model_feature_eligible"] for source in data["spot_sources"])
    assert data["derived_reconciliation"]["depth_status"] == "NOT_CAPTURED"


def test_level_one_spreads_recompute_from_native_quotes():
    data = load_artifact()
    kraken, okx = data["spot_sources"]
    for source, quote in (
        (kraken, ("best_bid_usd", "best_ask_usd")),
        (okx, ("best_bid_usdt", "best_ask_usdt")),
    ):
        normalized = source["normalized"]
        bid, ask = normalized[quote[0]], normalized[quote[1]]
        spread = (ask - bid) / ((ask + bid) / 2) * 10000
        assert math.isclose(
            spread,
            normalized["level1_spread_bps"],
            rel_tol=0,
            abs_tol=1e-7,
        )


def test_cross_venue_gap_is_not_an_arbitrage_or_consolidated_price():
    data = load_artifact()
    derived = data["derived_reconciliation"]
    assert derived["cross_venue_comparison_status"] == "NOT_AN_ARBITRAGE_SIGNAL"
    assert math.isclose(
        derived["raw_last_price_difference_pct"],
        (1.1605 / 1.15877 - 1) * 100,
        rel_tol=0,
        abs_tol=1e-7,
    )
    assert any("USD and USDT" in reason for reason in derived["reasons"])
    assert data["model_admission"]["eligible_as_live_price_feature"] is False


def test_derivatives_provider_universes_are_not_averaged():
    data = load_artifact()
    trad = data["derivatives_sources"][0]
    liq = data["derivatives_sources"][1]
    alpha = data["derivatives_sources"][2]
    assert trad["coverage"]["open_interest_exchanges"] == 7
    assert trad["coverage"]["liquidation_exchanges"] == 5
    assert trad["displayed_update_utc"] > liq["as_of_utc"]
    assert trad["model_feature_eligible"] is False
    assert liq["model_feature_eligible"] is False
    assert alpha["as_of_utc"] == "2026-11-07T08:50:00Z"
    assert alpha["model_feature_eligible"] is False


def test_etf_flow_universes_and_accounting_methods_remain_separate():
    data = load_artifact()
    alpha, insights, keyhole = data["etf_flow_sources"]
    assert alpha["universe"]["funds"] == 5
    assert "flow-only" in alpha["methodology"]
    assert insights["universe"]["spot_funds_listed"] == 6
    assert insights["universe"]["index_fund_included"] == "BITW"
    assert insights["universe"]["gxrp_flow_excluded"] is True
    assert insights["reported_weekly_flow_xrp"] == -812500
    assert "3 of 4" in keyhole["excerpt"]
    assert "2026-11-09" in keyhole["excerpt"]
    assert all(not source["model_feature_eligible"] for source in data["etf_flow_sources"])


def test_all_preserved_secondary_excerpts_match_their_hashes():
    data = load_artifact()
    sources = (
        data["derivatives_sources"][:2]
        + data["etf_flow_sources"]
        + data["macro_context"]
    )
    for source in sources:
        if "excerpt_sha256" in source:
            digest = hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest()
            assert digest == source["excerpt_sha256"]


def test_macro_context_is_not_xrp_specific_and_no_forecast_or_trade_exists():
    data = load_artifact()
    assert data["macro_context"][0]["publisher"] == "Reuters"
    assert "not an XRP-specific" in data["macro_context"][0]["interpretation"]
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_forecast"] is None
    assert data["forecast"]["shadow_forecast"] is None
    assert data["forecast"]["paper_trade_executed"] is False
    assert data["forecast"]["real_money_action"] is False
