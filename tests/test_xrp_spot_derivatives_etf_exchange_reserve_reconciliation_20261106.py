from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T201059Z-xrp-spot-derivatives-etf-exchange-reserve-reconciliation.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_all_source_excerpt_receipts_reproduce():
    data = load_artifact()
    assert len(data["source_registry"]) == 8
    for source in data["source_registry"]:
        assert source["url"].startswith("https://")
        assert source["independence_group"]
        assert hashlib.sha256(source["excerpt"].encode("utf-8")).hexdigest() == source["sha256"]
    assert data["capture_contract"]["original_http_wire_bytes_captured"] is False
    assert data["capture_contract"]["common_point_in_time_cutoff_utc"] is None


def test_direct_spot_quotes_keep_pair_timestamp_and_spread_semantics():
    spot = load_artifact()["observations"]["spot"]
    kraken, okx = spot["kraken"], spot["okx"]
    assert kraken["pair"] == "XRP/USD"
    assert kraken["last_usd"] == 1.18394
    assert kraken["provider_timestamp_utc"] is None
    assert kraken["last_above_best_ask"] is True
    kraken_spread = (kraken["best_ask_usd"] - kraken["best_bid_usd"]) / ((kraken["best_ask_usd"] + kraken["best_bid_usd"]) / 2) * 10000
    assert abs(kraken_spread - kraken["spread_bps"]) < 1e-9
    assert okx["instrument"] == "XRP-USDT"
    parsed = datetime.fromisoformat(okx["provider_snapshot_timestamp_utc"].replace("Z", "+00:00"))
    assert parsed.astimezone(timezone.utc).isoformat() == "2026-11-06T20:03:34.863000+00:00"
    assert int(parsed.timestamp() * 1000) == okx["provider_timestamp_epoch_ms"] == 1793995414863
    okx_spread = (okx["best_ask_usdt"] - okx["best_bid_usdt"]) / ((okx["best_ask_usdt"] + okx["best_bid_usdt"]) / 2) * 10000
    assert abs(okx_spread - okx["spread_bps"]) < 1e-9
    assert spot["cross_venue_comparison_eligible"] is False


def test_depth_is_explicitly_stale_not_carried_forward():
    depth = load_artifact()["observations"]["depth"]
    assert depth["status"] == "NO_NEW_SYNCHRONIZED_SPOT_DEPTH_OBSERVATION"
    assert depth["age_at_current_capture_minutes"] > 120
    assert "Do not carry" in depth["note"]


def test_derivatives_provider_disagreement_is_not_averaged():
    derivatives = load_artifact()["observations"]["derivatives"]
    tr, alpha, disagreement = derivatives["tradradar"], derivatives["alpha_finance"], derivatives["oi_scope_disagreement"]
    assert tr["oi_usd"] == 1_920_000_000
    assert tr["long_liquidations_usd"] == 12_270_000
    assert tr["short_liquidations_usd"] == 598_040
    assert alpha["oi_usd"] == 2_770_000_000
    assert alpha["modelled_short_liquidation_levels_usd"] == 129_500_000
    assert disagreement["absolute_difference_usd"] == 850_000_000
    assert disagreement["comparison_eligible"] is False
    assert "Do not average" in disagreement["reason"]


def test_etf_holdings_universes_and_partial_rows_are_not_cash_flows():
    etf = load_artifact()["observations"]["etf"]
    assert etf["xrp_insights"]["nov5_holdings_delta_xrp"] == 110_214
    assert etf["xrp_insights"]["nov2_to_nov5_holdings_delta_xrp"] == -149_487
    assert etf["cryptokeyhole"]["nov5_partial_fund_count"] == 2
    assert etf["comparison_eligible"] is False
    assert "not equivalent to AP cash" in etf["reason"]


def test_exchange_balances_exclude_new_wallet_and_wrapped_reserve_inference():
    balances = load_artifact()["observations"]["exchange_balances"]["xrp_insights"]
    assert balances["tracked_wallet_count"] == 701
    assert balances["same_wallet_change_7d_xrp"] == -34_700_000
    assert balances["naive_total_change_xrp"] == 359_400_000
    assert balances["newly_tracked_wallet_xrp"] == 512_000_000
    assert balances["wrapped_and_other_reserves_xrp"]["total"] == 487_700_000
    assert balances["wrapped_and_other_reserves_xrp"]["Binance_XRP_BF2"] == 325_800_000
    assert balances["wrapped_and_other_reserves_xrp"]["Coinbase_cbXRP_Base"] == 150_700_000


def test_escrow_is_provider_derived_and_not_admitted_as_tradable_supply():
    escrow = load_artifact()["observations"]["escrow"]
    assert escrow["provider_reported_live_escrow_xrp"] == 31_100_000_000
    assert escrow["direct_ledger_receipts_captured"] is False
    assert "not circulating" in escrow["interpretation"]


def test_no_directional_forecast_or_financial_action_is_created():
    data = load_artifact()
    assert data["status"] == "RESEARCH_ONLY_MODEL_INELIGIBLE"
    assert data["model_eligibility"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_forecast"] is False
    assert all(value is False for value in data["safety"].values())
