from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T042823Z-xrp-spot-break-etf-derivatives-context.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))


def test_direct_exchange_receipts_match_exact_rendered_json() -> None:
    artifact = load_artifact()
    assert len(artifact["direct_exchange_observations"]) == 2
    for source in artifact["direct_exchange_observations"]:
        raw = source["raw_response_text"].encode("utf-8")
        assert len(raw) == source["raw_response_bytes"]
        assert hashlib.sha256(raw).hexdigest() == source["raw_response_sha256"]


def test_kraken_timestamp_absence_and_okx_staleness_fail_closed() -> None:
    artifact = load_artifact()
    kraken, okx = artifact["direct_exchange_observations"]
    assert kraken["provider_event_time_utc"] is None
    assert kraken["source_timestamp_status"] == "not supplied by endpoint"
    assert okx["provider_age_seconds_at_capture"] == 507.028
    assert okx["freshness_limit_seconds"] == 300
    assert okx["quality_decision"] == "STALE_FOR_LIVE_FEATURES"


def test_level_one_spread_and_cross_quote_comparison_are_arithmetic_only() -> None:
    artifact = load_artifact()
    derived = artifact["derived_checks"]
    assert math.isclose(
        (1.15428 - 1.15426) / 1.15427 * 10_000,
        derived["kraken_level1_spread_bps"],
        rel_tol=0,
        abs_tol=1e-12,
    )
    assert math.isclose(
        (1.156 - 1.1559) / 1.15595 * 10_000,
        derived["okx_level1_spread_bps"],
        rel_tol=0,
        abs_tol=1e-12,
    )
    assert math.isclose(
        (1.1559 / 1.15461 - 1) * 100,
        derived["raw_okx_last_premium_vs_kraken_pct"],
        rel_tol=0,
        abs_tol=1e-12,
    )
    assert "not an arbitrage" in artifact["derived_checks"]["interpretation"].lower()


def test_etf_zero_flow_is_not_reclassified_as_an_outflow() -> None:
    artifact = load_artifact()
    source = next(
        item for item in artifact["secondary_sources"]
        if item["source_id"] == "tokenpost_sosovalue_xrp_etf_20261105"
    )
    reported = source["reported"]
    assert reported["zero_net_flow_sessions"] == [
        "2026-11-03",
        "2026-11-04",
        "2026-11-05",
    ]
    assert reported["cumulative_net_inflows_usd"] == 1_810_000_000
    assert source["limitations"]
    assert "Zero net flow is not a net outflow." in source["limitations"]


def test_derivatives_account_ratio_and_funding_are_not_misrepresented() -> None:
    artifact = load_artifact()
    source = next(
        item for item in artifact["secondary_sources"]
        if item["source_id"] == "cryptoticker_okx_xrp_derivatives_macro_20261106"
    )
    reported = source["reported"]
    oi = reported["okx_xrp_open_interest_usd"]
    assert oi["2026-10-24"] == 106_600_000
    assert oi["2026-11-04"] == 132_100_000
    assert oi["2026-11-05"] == 122_400_000
    assert math.isclose(
        (oi["2026-11-05"] / oi["2026-10-24"] - 1) * 100,
        reported["open_interest_change_oct24_to_nov5_pct"],
        rel_tol=0,
        abs_tol=1e-12,
    )
    assert reported["long_short_ratio_unit"] == (
        "accounts, not position notional or capital"
    )
    assert reported["funding_rate_pct_per_8h"]["2026-11-06_early_settlement"] == 0.0024


def test_binance_reserve_change_is_not_net_supply_or_the_prior_outflow() -> None:
    artifact = load_artifact()
    source = next(
        item for item in artifact["secondary_sources"]
        if item["source_id"] == "cryptobasic_binance_xrp_reserve_increase_20261105"
    )
    assert source["reported"]["reported_increase_xrp"] == 280_000_000
    context = artifact["cross_source_reconciliation"]["binance_flow_context"]
    assert context["prior_reported_nov4_outflow_xrp"] == 418_500_000
    assert context["comparable"] is False
    assert "Different metrics" in context["reason"]
    assert artifact["model_admission"]["eligible"] is False


def test_no_forecast_or_external_action_is_created_from_this_snapshot() -> None:
    artifact = load_artifact()
    assert artifact["model_admission"]["eligible"] is False
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["direction"] is None
    assert artifact["forecast"]["shadow_forecast_issued"] is False
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False
    assert not any(artifact["external_actions"].values())
