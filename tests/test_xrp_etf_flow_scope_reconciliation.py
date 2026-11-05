import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T023852Z-xrp-etf-flow-scope-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_etf_flow_aggregates_are_not_mislabeled_as_same_universe():
    data = load()["flow_reconciliation"]
    insights = data["xrp_insights"]
    keyhole = data["cryptokeyhole"]
    assert insights["net_flow_xrp"] == -194875
    assert insights["included_funds"] == ["XRPC", "XRP", "XRPR", "XRPZ", "GXRP", "TOXR", "BITW"]
    assert insights["gxrp_flow_status"] == "excluded"
    assert keyhole["net_flow_xrp"] == -6678
    assert keyhole["included_funds"] == ["XRP", "XRPZ", "XRPC", "TOXR"]
    assert keyhole["xrpr_included"] is False
    assert keyhole["bitw_included"] is False
    assert data["arithmetic"]["two_day_flow_difference_xrp"] == -188197
    assert "not attributed" in data["interpretation"][1]


def test_grayscale_sec_holding_is_distinguished_from_undated_aggregator_value():
    data = load()
    sec = data["grayscale_sec_q2_quantity_rollforward"]
    assert sec["closing_xrp_at_2026_06_30"] == 55035728.016985
    assert sec["opening_xrp_at_2025_12_31"] == 122230386.260970
    calculated = (
        sec["opening_xrp_at_2025_12_31"]
        + sec["xrp_contributed"]
        + sec["xrp_redeemed"]
        + sec["xrp_distributed_for_sponsor_fee"]
    )
    assert abs(calculated - sec["closing_xrp_at_2026_06_30"]) < 0.00001
    displayed = data["flow_reconciliation"]["arithmetic"]["gxrp_displayed_vs_sec_2026_06_30_difference_xrp"]
    assert displayed == 10407667.983015
    assert "may be a newer balance" in data["flow_reconciliation"]["interpretation"][3]
    assert data["model_eligible"] is False


def test_xrpr_and_bitw_exposure_types_are_kept_distinct():
    data = load()
    rex = next(x for x in data["source_registry"] if x["id"] == "rexshares_xrpr_issuer_holdings")
    assert rex["direct_xrp_quantity"] == 21260382
    assert rex["coinshares_physical_xrp_shares"] == 386750
    assert rex["direct_xrp_weight_pct"] == 60.05
    assert rex["coinshares_etp_weight_pct"] == 39.90
    insights = data["flow_reconciliation"]["xrp_insights"]
    assert insights["xrpr_included"] is True
    assert insights["bitw_included"] is True


def test_coinbase_custodian_and_prime_broker_roles_are_not_conflated():
    source = next(
        x for x in load()["source_registry"]
        if x["id"] == "grayscale_xrp_trust_etf_sec_s1_coinbase_custody"
    )
    relationships = source["verified_relationships"]
    assert relationships["custodian"] == "Coinbase Custody Trust Company, LLC"
    assert relationships["prime_broker"] == "Coinbase, Inc."
    assert relationships["cold_storage_vault_balance"] is True
    assert relationships["settlement_balance_may_use_omnibus_wallets"] is True


def test_rendered_aggregates_are_not_model_eligible_and_no_forecast_is_issued():
    data = load()
    assert data["model_eligible"] is False
    assert data["data_quality"]["model_eligibility"] == "NONE"
    assert data["data_quality"]["source_byte_hashes_verified"] is False
    assert data["data_quality"]["issuer_file_byte_receipts_verified"] is False
    assert data["predictions"]["issued"] is False


def test_grayscale_sec_cash_order_and_settlement_semantics_are_preserved():
    data = load()
    mechanics = data["grayscale_sec_q2_quantity_rollforward"]["creation_redemption_mechanics"]
    assert mechanics["authorized_participant_order_type_as_of_report_date"] == "cash_orders_only"
    assert mechanics["in_kind_creations_redemptions_permitted"] is False
    assert mechanics["accounting_basis"] == "trade_date"
    assert mechanics["xrp_receivable_payable_settlement_window_max_business_days"] == 2
    assert mechanics["sponsor_fee_accrual"] == "daily_usd"
    assert mechanics["sponsor_fee_payment"] == "xrp"
    assert data["data_quality"]["cash_order_and_settlement_semantics_verified_from_primary_sec_filing"] is True
    assert "not themselves USD cash-flow figures" in mechanics["implications"][0]
