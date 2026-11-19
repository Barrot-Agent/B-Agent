import hashlib
import json
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    REPOSITORY_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261109T171649Z-live-spot-exchange-balance-etf-reconciliation.json"
)
EXPECTED_HASHES = {
    "kraken_xrp_usd": "58e8ad61b054062b03e3dcb622d24d997b55e879a8178347d4d6cfa2b195726f",
    "okx_xrp_usdt": "e92072e2840f5431950e60b372351ddd074915866bdf957b4c03b9bf1e474f18",
    "kraken_usdt_usd": "43d646562f95827d347d911f758df2cb893ed2e64bb7ad66fbe83fdae354ddc6",
}


def _artifact():
    return json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))


def test_spot_receipt_text_hashes_are_fixed_and_reproducible():
    artifact = _artifact()
    assert artifact["capture_id"] == "20261109T171649Z"
    receipts = {item["source_id"]: item for item in artifact["spot_receipts"]}
    assert set(receipts) == set(EXPECTED_HASHES)
    for source_id, expected_hash in EXPECTED_HASHES.items():
        receipt = receipts[source_id]
        actual_hash = hashlib.sha256(
            receipt["response_text"].encode("utf-8")
        ).hexdigest()
        assert actual_hash == expected_hash
        assert receipt["response_text_sha256"] == expected_hash
        assert receipt["wire_bytes_preserved"] is False
        assert receipt["response_headers_preserved"] is False


def test_asynchronous_cross_venue_comparison_is_not_model_eligible():
    artifact = _artifact()
    comparison = artifact["normalized_cross_venue_comparison"]
    assert comparison["okx_last_normalized_usd"] == 1.098023856
    assert comparison["mid_gap_bps_okx_vs_kraken"] < 0
    assert comparison["model_eligible"] is False
    okx = next(
        item for item in artifact["spot_receipts"]
        if item["source_id"] == "okx_xrp_usdt"
    )
    assert okx["age_at_capture_reference_seconds"] > 1200
    assert okx["provider_event_time_utc"] == "2026-11-09T16:54:19.463Z"


def test_exchange_wallet_balance_is_not_tradable_float_or_customer_flow():
    observation = _artifact()["exchange_wallet_balance_observation"]
    assert observation["tracked_wallets"] == 701
    assert observation["tracked_exchanges"] == 24
    assert observation["same_wallet_change_7d_xrp"] == -25_800_000
    assert observation["same_wallet_change_30d_xrp"] == -138_100_000
    assert observation["cold_storage_included"] is True
    assert observation["coinbase_cbXRP_base_reserve_xrp"] == 152_000_000
    assert observation["binance_peg_xrp_bnb_chain_reserve_xrp"] == 327_400_000
    assert observation["model_eligible"] is False


def test_etf_flow_aggregate_preserves_exclusions_and_reconstruction_caveats():
    observation = _artifact()["etf_flow_observation"]
    assert observation["computed_net_flow_xrp"] == -812_529
    assert observation["total_xrp_holdings_as_of_2026_11_06"] == 1_195_182_552
    assert observation["settled_trading_sessions"] == 5
    assert observation["flow_excluded_funds_count_as_zero"] is True
    assert "reconstructed" in observation["possible_row_statuses"]
    assert observation["model_eligible"] is False


def test_run94_does_not_issue_a_directional_forecast():
    artifact = _artifact()
    assert artifact["forecast_status"] == "NOT_ISSUED"
    assert artifact["normalized_cross_venue_comparison"]["model_eligible"] is False
