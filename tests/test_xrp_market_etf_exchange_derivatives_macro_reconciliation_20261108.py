from __future__ import annotations

import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research/xrp_intelligence/20261108T070200Z-xrp-market-etf-exchange-derivatives-macro-reconciliation.json"
)


def test_market_etf_exchange_derivatives_reconciliation_is_fail_closed() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert data["artifact_type"] == "xrp_market_microstructure_etf_exchange_derivatives_macro_reconciliation"
    assert data["model_admission"]["eligible"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["data_quality"]["synchronized_market_cutoff"] is False
    assert data["data_quality"]["raw_http_wire_bytes_captured"] is False

    receipts = {row["source_id"]: row for row in data["source_receipts"]}
    assert len(receipts) == 10
    for receipt in receipts.values():
        assert receipt["hash_scope"].startswith("SHA-256 of the exact excerpt string")
        actual = hashlib.sha256(receipt["excerpt"].encode("utf-8")).hexdigest()
        assert actual == receipt["excerpt_sha256"]

    etf = data["etf_flow_reconciliation"]["providers"]
    by_provider = {row["provider"]: row for row in etf}
    assert by_provider["XRP Insights"]["week_net_flow_xrp"] == -813_000
    assert by_provider["XRP Insights"]["nov6_daily_flow_xrp"] == -663_000
    assert by_provider["CryptoKeyhole"]["nov6_partial_flow_xrp"] == -752_048
    assert by_provider["CryptoKeyhole"]["nov6_coverage"] == "3 of 4 funds; Franklin XRPZ missing"
    assert by_provider["Alpha Finance"]["nov6_daily_flow_usd"] == 0
    assert by_provider["Alpha Finance"]["last_7_sessions_flow_usd"] == 8_400_000
    assert "not independent confirmations" in data["etf_flow_reconciliation"]["source_independence"]

    wallets = data["exchange_wallets"]
    assert wallets["attributed_wallet_total_xrp"] == 22_330_000_000
    assert wallets["same_wallet_change_7d_xrp"] == -150_700_000
    assert wallets["same_wallet_change_30d_xrp"] == -161_200_000
    assert wallets["newly_tracked_wallets_xrp"] == 512_000_000
    assert any("not tradable float" in item for item in wallets["caveats"])

    book = data["market_observations"]["visible_orderbook"]
    assert book["bids_within_1pct_usd"] == 9_000_000
    assert book["asks_within_1pct_usd"] == 9_900_000
    assert book["instrument_scope"] == "Binance XRP spot plus OKX XRP-USDT perpetual combined"

    derivatives = data["derivatives"]
    assert derivatives["open_interest_usd"] == 782_970_000
    assert derivatives["funding_weighted_pct_per_8h"] == 0.008
    disagreement = derivatives["hyperliquid_disagreement"]
    assert disagreement["kodexius_oi_usd"] == 98_120_000
    assert disagreement["hyperacademy_oi_usd"] == 196_000_000
    assert disagreement["resolution"] == "UNRESOLVED; do not sum or average"

    assert data["macro_context"]["us_money_market_weekly_inflow_usd"] == 117_970_000_000
    assert len(data["competing_hypotheses"]) >= 5
