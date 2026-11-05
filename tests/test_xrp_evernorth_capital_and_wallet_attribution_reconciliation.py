import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T084500Z-evernorth-capital-and-wallet-attribution-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_closing_cash_and_xrp_components_are_separated():
    data = load()
    stack = data["actual_capital_stack"]
    placement = stack["private_placement_subscription_agreements"]
    assert placement["cash_raised_usd"] == 214_049_995
    assert placement["cash_used_to_purchase_xrp_usd"] == 214_000_000
    assert placement["remaining_restricted_cash_as_of_2025_12_31_usd"] == 49_995
    assert math.isclose(placement["xrp_purchased_with_cash"], 84_365_876.3625, abs_tol=1e-6)
    assert math.isclose(stack["in_kind_xrp_at_closing"]["total_xrp"], 388_910_554.061435, abs_tol=1e-6)
    assert stack["closing_gross_cash_proceeds"]["total_gross_cash_usd_approx"] == 272_600_000
    assert stack["pathfinder_contribution"]["xrp_contributed"] == 126_791_458
    assert "delayed" not in stack["pathfinder_contribution"]
    assert math.isclose(
        stack["company_reported_xrp"]["primary_component_reconstruction_xrp"],
        473_276_430.423935,
        abs_tol=1e-6,
    )
    assert stack["company_reported_xrp"]["issuer_approximate_xrp_as_of_2026_10_09"] == 473_000_000
    assert stack["company_reported_xrp"]["proxy_expected_minimum_xrp_at_closing"] == 473_276_430
    assert data["actual_capital_taxonomy"]["actual_cash_used_to_buy_xrp_usd"] == 214_000_000


def test_pik_notes_and_ripple_credit_are_separate_debt_categories():
    data = load()["actual_capital_stack"]
    assert data["convertible_notes"]["principal_usd"] == 30_000_000
    assert data["convertible_notes"]["cash_consideration_usd"] == 30_000_000
    assert data["convertible_notes"]["coupon_pct"] == 4.0
    assert data["ripple_credit_facilities"]["pathfinder_company_facility"]["amount_borrowed_as_of_2026_10_07_usd"] == 9_700_000
    assert data["ripple_credit_facilities"]["separate_evernorth_facility"]["borrowed_as_of_2026_06_30_usd"] == 0


def test_eloc_effectiveness_is_not_mislabeled_as_cash_draw():
    data = load()["eloc_facility"]
    assert data["registration_effective_at_utc"] == "2026-10-30T16:00:00Z"
    assert data["maximum_new_shares"] == 5_218_935
    assert data["actual_proceeds_verified_usd"] == 0
    assert "NO_FIRST_PURCHASE_NOTICE" in data["status_at_cutoff"]
    assert data["gross_proceeds_scenarios"]["cover_price_gross_usd"] == 76_800_000
    assert data["gross_proceeds_scenarios"]["cover_price_estimated_net_usd"] == 74_400_000
    assert data["gross_proceeds_scenarios"]["prospectus_summary_gross_usd"] == 80_700_000


def test_commitment_fee_is_an_outflow_due_november_six():
    data = load()["eloc_commitment_fee"]
    assert data["upfront_fee_usd"] == 521_893.50
    assert data["contractual_due_date"] == "2026-11-06"
    assert data["status_at_cutoff"] == "PAYMENT_NOT_VERIFIED; due date is Nov 6, 2026"
    assert data["classification"].startswith("contractual cash outflow")


def test_public_and_sponsor_warrants_are_contingent_not_actual_capital():
    data = load()["warrants"]
    assert data["public_warrants_shares"] == 11_499_992
    assert data["public_warrant_exercise_price_usd"] == 11.50
    assert data["public_warrant_theoretical_cash_ceiling_usd"] == 132_249_908
    assert data["sponsor_warrants_shares"] == 239_653
    assert data["total_pubco_warrants_reported"] == 11_739_645
    assert data["status"] == "NO_EXERCISE_OR_CASH_RECEIPT_VERIFIED"


def test_onchain_outflow_is_unattributed_and_wallet_total_does_not_reconcile():
    data = load()["onchain_attribution"]
    assert data["xrp_in_attributed_wallets"] == 103_129_905
    assert data["xrp_moved_outside_attributed_wallet_set"] == 370_346_663
    assert data["tracker_total_in_plus_out_xrp"] == 473_476_568
    assert data["difference_rounded_xrp"] == 200_138
    assert data["destination_beneficial_ownership"] == "UNRESOLVED"
    assert data["classification"] == "UNATTRIBUTED_OUTFLOW_NOT_CLASSIFIED_AS_SALE"
    assert data["independent_replay_performed"] is False


def test_forecast_and_model_admission_remain_disabled():
    data = load()
    assert data["forecast_issued"] is False
    assert data["model_eligible"] is False
    assert data["data_quality"]["raw_sec_sha256_receipts"] is False
    assert data["data_quality"]["raw_xrpl_transactions_independently_replayed"] is False
