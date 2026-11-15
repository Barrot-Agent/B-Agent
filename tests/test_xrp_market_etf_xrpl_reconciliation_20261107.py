import hashlib
import json
from pathlib import Path

import pytest


ARTIFACT = Path(__file__).parents[1] / "research" / "xrp_intelligence" / "20261107T102024Z-xrp-market-etf-xrpl-reconciliation.json"


@pytest.fixture(scope="module")
def artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exchange_receipts_match_exact_json_hashes_and_byte_lengths(artifact):
    for source in artifact["sources"][:2]:
        raw = source["raw_response_exact_json"].encode("utf-8")
        assert len(raw) == source["raw_response_bytes"]
        assert hashlib.sha256(raw).hexdigest() == source["raw_response_sha256"]


def test_level_one_spreads_recompute_from_bid_and_ask(artifact):
    kraken, okx = artifact["sources"][:2]
    k = kraken["normalized_metrics"]
    o = okx["normalized_metrics"]
    assert k["level1_spread_bps"] == pytest.approx(
        (k["best_ask_usd"] - k["best_bid_usd"]) / ((k["best_ask_usd"] + k["best_bid_usd"]) / 2) * 10_000
    )
    assert o["level1_spread_bps"] == pytest.approx(
        (o["best_ask_usdt"] - o["best_bid_usdt"]) / ((o["best_ask_usdt"] + o["best_bid_usdt"]) / 2) * 10_000
    )


def test_kraken_last_trade_anomaly_is_preserved_and_excluded(artifact):
    source = artifact["sources"][0]
    m = source["normalized_metrics"]
    assert m["last_usd"] < m["best_bid_usd"]
    assert m["last_below_best_bid_bps"] == pytest.approx(
        (m["best_bid_usd"] / m["last_usd"] - 1) * 10_000
    )
    assert source["provider_event_timestamp_utc"] is None


def test_okx_provider_timestamp_fails_live_freshness_limit(artifact):
    source = artifact["sources"][1]
    assert source["provider_event_age_seconds_at_capture"] > source["freshness_limit_seconds"]
    assert source["freshness_status"] == "STALE_EXCEEDS_300_SECOND_LIMIT"


def test_cross_currency_gap_is_not_admitted_as_arbitrage_or_price_feature(artifact):
    assert artifact["derived_reconciliation"]["raw_cross_venue_last_price_gap_pct"] > 0
    assert artifact["model_admission"]["eligible"] is False
    assert any("USD and USDT" in reason for reason in artifact["model_admission"]["reasons"])


def test_derivatives_venue_sum_and_aggregator_coverage_disagreement_are_explicit(artifact):
    trad = next(s for s in artifact["sources"] if s["id"].startswith("tradradar_"))
    venue_sum = sum(trad["normalized_metrics"]["venue_open_interest_usd"].values())
    assert venue_sum == pytest.approx(artifact["derived_reconciliation"]["tradradar_seven_venue_oi_sum_usd"])
    assert abs(venue_sum - trad["normalized_metrics"]["open_interest_usd"]) < 5_000_000
    assert artifact["derived_reconciliation"]["oi_aggregator_spread_usd"] == 310_000_000


def test_etf_flow_fund_universes_and_completeness_are_not_collapsed(artifact):
    alpha, insights, keyhole = [s for s in artifact["sources"] if "etf" in s["id"] or "flows" in s["id"]]
    assert alpha["normalized_metrics"]["fund_count"] == 5
    assert insights["universe"] == "Six spot funds plus BITW index sleeve"
    assert keyhole["normalized_metrics"]["nov6_funds_published"] == 2
    assert keyhole["normalized_metrics"]["nov6_funds_expected"] == 4
    assert artifact["model_admission"]["eligible"] is False


def test_fixcleanup_activation_is_separate_from_lending_and_vault_votes(artifact):
    dashboard = next(s for s in artifact["sources"] if s["id"].startswith("xrpldashboard_"))
    fix = next(s for s in artifact["sources"] if s["id"].startswith("xrplwin_"))
    assert fix["enabled_ledger"] == 108112129
    assert dashboard["normalized_metrics"]["single_asset_vault_yes_including_24h_carry"] < dashboard["normalized_metrics"]["validators_required"]
    assert dashboard["normalized_metrics"]["lending_protocol_yes_including_24h_carry"] < dashboard["normalized_metrics"]["validators_required"]


def test_no_directional_forecast_or_external_action_is_recorded(artifact):
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["directional_forecast"] is None
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["external_actions"]["orders_sent"] is False
    assert artifact["external_actions"]["funds_transferred"] is False
    assert artifact["external_actions"]["deployment_triggered"] is False
