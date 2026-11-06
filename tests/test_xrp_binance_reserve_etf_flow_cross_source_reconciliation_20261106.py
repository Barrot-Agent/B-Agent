from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T193345Z-xrp-binance-reserve-etf-flow-cross-source-reconciliation.json"
CORRECTION = ROOT / "research" / "xrp_intelligence" / "20261106T194003Z-xrp-binance-reserve-etf-flow-receipt-hash-correction.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def load_corrected_view() -> tuple[dict, dict]:
    original = load_artifact()
    overlay = json.loads(CORRECTION.read_text(encoding="utf-8"))
    derived = copy.deepcopy(original)
    source = next(item for item in derived["source_registry"] if item["id"] == overlay["target_source_id"])
    assert source["sha256"] == overlay["prior_value"]
    source["sha256"] = overlay["corrected_value"]
    return derived, overlay


def test_source_receipt_correction_is_exact_preimage_bound_and_append_only():
    raw = ARTIFACT.read_bytes()
    overlay = json.loads(CORRECTION.read_text(encoding="utf-8"))
    git_blob_sha1 = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    assert git_blob_sha1 == overlay["target_artifact_git_blob_sha1"]
    assert overlay["target_json_pointer"] == "/source_registry/4/sha256"
    assert overlay["preservation"]["source_artifact_modified"] is False
    assert overlay["preservation"]["source_excerpt_modified"] is False
    assert overlay["preservation"]["append_only"] is True
    original = load_artifact()
    source = next(item for item in original["source_registry"] if item["id"] == overlay["target_source_id"])
    assert source["sha256"] == overlay["prior_value"]
    assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == overlay["corrected_value"]
    assert overlay["corrected_value"] == overlay["excerpt_sha256"]


def test_all_normalized_source_receipts_reproduce_after_append_only_correction():
    data, _overlay = load_corrected_view()
    assert len(data["source_registry"]) == 13
    for source in data["source_registry"]:
        assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == source["sha256"]
        assert source["url"].startswith("https://")
        assert source["independence_group"]
    assert data["capture_contract"]["common_point_in_time_cutoff_utc"] is None
    assert data["capture_contract"]["original_http_wire_bytes_captured"] is False


def test_direct_spot_quotes_preserve_pair_and_timestamp_semantics():
    spot = load_artifact()["observations"]["spot"]
    kraken = spot["kraken"]
    okx = spot["okx"]
    assert kraken["pair"] == "XRP/USD"
    assert kraken["last_usd"] == 1.18304
    assert kraken["best_bid_usd"] == 1.18308
    assert kraken["best_ask_usd"] == 1.18309
    assert kraken["provider_timestamp_utc"] is None
    assert kraken["last_below_best_bid"] is True
    assert okx["instrument"] == "XRP-USDT"
    assert okx["provider_snapshot_timestamp_utc"] == "2026-11-06T19:32:37.362Z"
    assert okx["last_usdt"] == 1.183
    assert okx["rolling_24h_open_usdt"] == 1.2362
    assert spot["cross_venue_comparison_eligible"] is False


def test_spread_and_same_venue_returns_are_recomputed():
    spot = load_artifact()["observations"]["spot"]
    kraken = spot["kraken"]
    okx = spot["okx"]
    kraken_bps = (kraken["best_ask_usd"] - kraken["best_bid_usd"]) / ((kraken["best_ask_usd"] + kraken["best_bid_usd"]) / 2) * 10000
    okx_bps = (okx["best_ask_usdt"] - okx["best_bid_usdt"]) / ((okx["best_ask_usdt"] + okx["best_bid_usdt"]) / 2) * 10000
    assert abs(kraken_bps - kraken["spread_bps"]) < 1e-6
    assert abs(okx_bps - okx["spread_bps"]) < 1e-6
    kraken_open_move = (kraken["last_usd"] / kraken["utc_day_open_usd"] - 1) * 100
    okx_open_move = (okx["last_usdt"] / okx["utc_day_open_usdt"] - 1) * 100
    assert abs(kraken_open_move - kraken["last_vs_utc_day_open_pct"]) < 1e-6
    assert abs(okx_open_move - okx["last_vs_utc_day_open_pct"]) < 1e-6
    assert abs(okx["last_vs_rolling_24h_open_pct"] - (okx["last_usdt"] / okx["rolling_24h_open_usdt"] - 1) * 100) < 1e-6


def test_spot_depth_is_not_combined_across_incompatible_sources():
    depth = load_artifact()["observations"]["depth"]
    fuel = depth["fuelmaps"]
    edge = depth["edgeornot"]
    assert fuel["snapshot_time_utc"] == "2026-11-06T18:00:00Z"
    assert fuel["age_at_capture_minutes"] == 93.75
    assert fuel["bands_usd"]["0.5"]["bids"] == 9_000_000
    assert fuel["bands_usd"]["0.5"]["asks"] == 5_100_000
    assert fuel["bands_usd"]["1"]["bid_share_pct"] == 60.09
    assert fuel["excluded_venues"] == ["Binance", "Bitget"]
    assert "Binance spot plus OKX perpetual" in edge["scope"]
    assert depth["aggregation_rule"].startswith("Do not add or average")


def test_derivatives_keep_venue_universes_and_liquidation_units_separate():
    derivatives = load_artifact()["observations"]["derivatives"]
    tr = derivatives["tradradar"]
    okx = derivatives["okx_secondary_analysis"]
    assert tr["oi_usd"] == 1_900_000_000
    assert tr["oi_change_24h_pct"] == -2.47
    assert tr["funding_pct_per_8h"] == 0.001
    assert tr["liquidations_lower_bound_usd"] == 11_960_000
    assert tr["long_liquidations_usd"] == 11_360_000
    assert tr["short_liquidations_usd"] == 600_340
    assert tr["long_short_account_ratio"] == 3.90
    assert okx["oi_thursday_midday_usd"] == 128_900_000
    assert okx["oi_friday_morning_usd"] == 117_400_000
    assert okx["long_short_account_ratio_friday_morning"] == 3.91
    assert "not notional exposure" in derivatives["interpretation"]


def test_etf_flow_sources_are_disagreements_not_comparable_cash_flows():
    etf = load_artifact()["observations"]["etf"]
    ss = etf["sosovalue_via_tokenpost"]
    xi = etf["xrp_insights_holdings_delta"]
    assert ss["zero_net_flow_days"] == 3
    assert ss["cumulative_net_inflows_usd"] == 1_810_000_000
    assert xi["holdings_delta_xrp_nov2_to_nov5"] == -149_487
    assert xi["settled_days"] == 4
    assert xi["total_holdings_xrp"] == 1_196_450_700
    assert etf["comparison_eligible"] is False
    assert "AP cash" in etf["reason"]


def test_binance_reserve_and_large_transfer_series_retain_conflicting_scopes():
    flows = load_artifact()["observations"]["exchange_reserves"]
    cb = flows["cryptobasic_cryptoquant_report"]
    xi = flows["xrp_insights_wallet_labels"]
    tw = flows["trackwhale_large_transfer_index"]
    assert cb["change_xrp"] == 280_000_000
    assert abs((cb["binance_xrp_reserves_nov5"] / cb["binance_xrp_reserves_nov3"] - 1) * 100 - cb["change_pct"]) < 1e-6
    assert cb["origin_confirmed"] is False
    assert cb["deposit_transaction_share_nov5_pct"] == 56.2
    assert xi["binance_xrp"] == 2_740_000_000
    assert xi["newly_tracked_wallets_xrp"] == 512_000_000
    assert tw["net_flow_xrp"] == -20_020_000
    assert tw["internal_and_exchange_to_exchange_excluded"] is True
    reconciliation = flows["reconciliation"]
    assert reconciliation["reserve_estimates_conflict"] is True
    assert reconciliation["difference_xrp"] == 110_000_000
    assert reconciliation["no_averaging"] is True


def test_macro_vintages_and_competing_hypotheses_preserve_counterevidence():
    data = load_artifact()
    macro = data["observations"]["macro"]
    assert macro["bls_october_employment"]["nonfarm_payroll_change"] == 165_000
    assert macro["bls_october_employment"]["unemployment_rate_pct"] == 4.1
    assert macro["reuters_post_release"]["nasdaq_change_pct"] == 1.7
    assert macro["reuters_post_release"]["sp500_change_pct"] == 0.6
    assert len(data["hypotheses"]) == 6
    assert all(item["support"] and item["counter"] for item in data["hypotheses"])


def test_no_forecast_or_financial_action_is_created():
    data = load_artifact()
    assert data["status"] == "RESEARCH_ONLY_MODEL_INELIGIBLE"
    assert data["model_eligibility"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_forecast"] is False
    assert all(value is False for value in data["safety"].values())
