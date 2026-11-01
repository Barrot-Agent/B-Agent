import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


SNAPSHOT = "data/xrp_intelligence/snapshots/20261101T160541Z-evernorth-bitgo-custody-reorganization-and-unattributed-inflows.json"


def test_bitgo_out_of_set_movement_is_not_classified_as_sale():
    snap = load(SNAPSHOT)
    custody = snap["custody_reorganization"]
    assert round(custody["tracker_movement_sum_xrp"], 2) == 370346663.23
    assert custody["classification"] == "STRONGLY_SUPPORTED_INTERNAL_BITGO_CUSTODY_REALLOCATION"
    assert custody["market_sale_verified"] if "market_sale_verified" in custody else False


def test_destination_account_ownership_remains_unproven():
    snap = load(SNAPSHOT)
    custody = snap["custody_reorganization"]
    assert custody["explorer_corroboration"]["bithomp_pages_opened"] == 9
    assert custody["beneficial_ownership"] == "NOT_DIRECTLY_DISCLOSED"
    assert custody["exchange_deposit_verified"] is False


def test_unmapped_600k_tranche_and_200137_difference_are_preserved():
    snap = load(SNAPSHOT)
    custody = snap["custody_reorganization"]
    assert custody["unmapped_advance_funding_subscriber_tranche_xrp"] == 600000
    assert round(custody["reconciliation_gap_after_known_buckets_vs_sec_total_xrp"]) == 599982
    assert round(custody["tracker_balance_plus_outflow_difference_vs_sec_xrp"], 2) == 200137.78
    assert custody["reconciliation_status"] == "UNRESOLVED"


def test_tagged_inflows_are_not_admitted_as_new_evernorth_purchases():
    snap = load(SNAPSHOT)
    inflows = snap["candidate_additional_inflows"]
    assert round(inflows["combined_reported_inflow_xrp"], 3) == 9069762.136
    assert inflows["beneficial_owner"] == "UNKNOWN"
    assert inflows["purchase_status"] == "NOT_VERIFIED"
    assert inflows["market_feature_admission"] == "NONE"


def test_eloc_stale_price_explanation_is_inference_and_no_draw_is_verified():
    snap = load(SNAPSHOT)
    eloc = snap["cantors_equity_facility_reconciliation"]
    assert eloc["cover_gross_proceeds_usd"] == 76800000
    assert eloc["detailed_net_proceeds_estimate_usd"] == 74400000
    assert eloc["conflicting_summary_gross_proceeds_usd"] == 80700000
    assert eloc["likely_stale_reference_price_usd"] == 15.46
    assert eloc["draw_verified"] is False
    assert eloc["stale_price_explanation_classification"] == "INFERENCE_NOT_ISSUER_CONFIRMED"


def test_yield_commencement_does_not_prove_xrp_collateral_deployment():
    snap = load(SNAPSHOT)
    strategy = snap["company_reported"]["strategy_disclosure"]
    assert strategy["yield_strategies"] == "The prospectus states yield strategies commenced following Closing."
    assert strategy["actual_protocols_wallets_amounts_counterparties"] == "NOT_DISCLOSED"
    assert strategy["actual_xrp_collateral_loan"] == "NOT_VERIFIED"
    assert snap["model_controls"]["feature_admission"] == "NONE"
    assert snap["model_controls"]["forecast_status"] == "NOT_ISSUED"
