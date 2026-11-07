import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T132200Z-xrp-exchange-wallet-balance-same-wallet-flow.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_normalized_evidence_hash_is_reproducible():
    data = load_artifact()
    canonical = json.dumps(
        data["normalized_evidence_record"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == data["source_lineage"]["normalized_evidence_record_sha256"]


def test_exchange_wallet_snapshot_is_dated_and_not_live():
    data = load_artifact()
    assert data["source_snapshot_time_utc"] == "2026-11-07T08:01:00Z"
    assert data["headline"]["wallet_count"] == 701
    assert data["headline"]["exchange_count"] == 24
    assert data["source_lineage"]["raw_source_bytes_retained"] is False


def test_same_wallet_changes_are_not_customer_flows():
    data = load_artifact()["headline"]
    assert data["same_wallet_net_change_7d_display"] == "-150.7M XRP"
    assert data["same_wallet_net_change_30d_display"] == "-161.2M XRP"
    assert "Neither measure proves customer withdrawals" in data["interpretation"]


def test_naive_total_increase_is_coverage_change_sensitive():
    data = load_artifact()["headline"]
    assert data["naive_total_change_display"] == "+350.8M XRP"
    assert data["newly_tracked_wallets"] == 2
    assert data["newly_tracked_wallets_balance_display"] == "512.0M XRP"


def test_total_is_not_tradable_float_and_includes_cold_reserves():
    data = load_artifact()
    assert data["storage_and_wrapped_reserves"]["storage_split_pct"]["cold_labeled"] == 48
    assert data["storage_and_wrapped_reserves"]["storage_split_pct"]["unclassified"] == 39.9
    assert "not tradable float" in data["storage_and_wrapped_reserves"]["interpretation"].lower()


def test_binance_reserve_disagreement_is_preserved_not_averaged():
    data = load_artifact()["storage_and_wrapped_reserves"]["internal_source_disagreement"]
    assert data["exchange_table_binance_peg_reserve"] == "327.4M XRP"
    assert data["reserve_summary_binance_peg_reserve"] == "325.8M XRP"
    assert data["difference"] == "1.6M XRP"
    assert "do not average" in data["treatment"].lower()


def test_sbi_vc_trade_balance_is_attributed_wallet_context_only():
    data = load_artifact()
    sbi = next(x for x in data["exchange_breakdown"] if x["exchange"] == "SBI VC Trade")
    assert sbi["xrp_held_display"] == "56.6M"
    assert sbi["change_7d_display"] == "-2.9M"
    assert sbi["change_30d_display"] == "-4.2M"
    assert "not customer withdrawal evidence" in sbi["notes"]


def test_coverage_gaps_are_explicit():
    data = load_artifact()
    assert any("OKX and Korbit main wallets" in x for x in data["methodology_and_limitations"])
    assert any("323M XRP" in x for x in data["methodology_and_limitations"])


def test_no_market_feature_or_forecast_is_admitted():
    data = load_artifact()
    assert data["model_admission"]["admitted_to_price_features"] is False
    assert data["model_admission"]["admitted_to_exchange_flow_features"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"


def test_seven_day_and_thirty_day_windows_are_not_conflated():
    data = load_artifact()
    assert data["source_snapshot_time_utc"] == "2026-11-07T08:01Z"
    assert data["headline"]["same_wallet_window_utc"] == "2026-10-31 through 2026-11-07"
    assert data["headline"]["same_wallet_window_30d_utc"] == "2026-10-08 through 2026-11-07"
    assert "not the sum of all eight displayed rows" in data["daily_same_wallet_changes_note"]
