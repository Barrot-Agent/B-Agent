import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "xrp_intelligence" / "snapshots" / "20261031T160137Z-xrp-exchange-wallets-binance-recovery-and-v3-audit.json"


def load_snapshot():
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def test_exchange_wallet_snapshot_is_not_tradable_float():
    data = load_snapshot()["exchange_balances"]
    assert data["total_xrp"] == 22_480_000_000
    assert data["tracked_wallets"] == 701
    assert data["tracked_exchanges"] == 24
    assert data["methodology"]["cold_storage_included"] is True
    assert data["methodology"]["tradable_float"] is False
    assert data["methodology"]["official_proof_of_reserves"] is False
    assert data["known_non_customer_reserves_xrp"]["total"] == 487_200_000


def test_binance_and_coinbase_same_wallet_changes_are_provider_specific():
    data = load_snapshot()["exchange_balances"]["exchanges"]
    assert data["binance"]["balance_xrp"] == 2_780_000_000
    assert data["binance"]["same_wallet_change_7d_xrp"] == 17_600_000
    assert data["binance"]["same_wallet_change_30d_xrp"] == 30_300_000
    assert data["coinbase"]["balance_xrp"] == 5_850_000_000
    assert data["coinbase"]["same_wallet_change_7d_xrp"] == 17_700_000
    assert data["coinbase"]["same_wallet_change_30d_xrp"] == 18_400_000


def test_october_30_decline_is_not_treated_as_persistent_binance_outflow():
    data = load_snapshot()
    changes = data["exchange_balances"]["daily_same_wallet_change_xrp"]
    assert changes["2026-10-30"] == -207_300_000
    assert changes["2026-10-31"] == 105_900_000
    assert data["incident_causality_reassessment"]["status"] == "PRIOR_CAUSAL_HYPOTHESIS_WEAKENED_NOT_ESTABLISHED"
    assert data["incident_causality_reassessment"]["source_wallet_membership_in_153_binance_wallet_set"] == "UNKNOWN"


def test_binance_recovery_coverage_is_a_company_claim_not_purchase_evidence():
    data = load_snapshot()["binance_recovery_update3"]
    assert "XRP" in data["top_ten_assets_minimum_1_to_1_claim"]
    assert data["xrp_minimum_coverage_claim"] == "AT_LEAST_1_TO_1_BY_BINANCE_STATEMENT"
    assert data["full_zk_proof_status"].startswith("PENDING")
    assert data["xrp_units_replenished"] == "UNKNOWN"
    assert data["xrp_spot_purchase_usd"] == "UNKNOWN"
    assert data["xrp_otc_purchase_usd"] == "UNKNOWN"


def test_no_directional_feature_or_forecast_is_admitted():
    data = load_snapshot()
    assert data["feature_admission"]["exchange_balance_directional_feature"] == "NOT_ADMITTED"
    assert data["feature_admission"]["forecast"] == "NOT_ISSUED"
    assert data["forecast_status"] == "NOT_ISSUED"
