import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261105T084500Z-evernorth-capital-and-wallet-attribution-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_actual_cash_and_in_kind_xrp_are_separated():
    data = load()
    stack = data["actual_capital_stack"]
    placement = stack["private_placement_subscription_agreements"]
    assert placement["cash_raised_usd"] == 214_100_000
    assert placement["xrp_purchased_with_cash"] == 84_365_876
    assert placement["xrp_contributed_in_kind"] == 261_919_096
    assert stack["company_reported_xrp"]["exact_closing_amount_in_prior_sec_filing"] == 473_276_430
    assert data["actual_capital_taxonomy"]["actual_xrp_purchased_with_cash"] == 84_365_876


def test_ripple_credit_facilities_are_distinct_and_not_equity():
    data = load()["actual_capital_stack"]["ripple_credit_facilities"]
    assert data["pathfinder_company_facility"]["amount_borrowed_as_of_2026_10_07_usd"] == 9_700_000
    assert data["separate_evernorth_facility"]["limit_usd"] == 1_000_000
    assert data["separate_evernorth_facility"]["borrowed_as_of_2026_06_30_usd"] == 0
    assert "not equity capital" in data["pathfinder_company_facility"]["classification"]


def test_eloc_effectiveness_is_not_mislabeled_as_cash_draw():
    data = load()["eloc_facility"]
    assert data["registration_effective_at_utc"] == "2026-10-30T16:00:00Z"
    assert data["maximum_new_shares"] == 5_218_935
    assert data["actual_proceeds_verified_usd"] == 0
    assert "NO_FIRST_PURCHASE_NOTICE" in data["status_at_cutoff"]
    assert data["gross_proceeds_scenarios"]["cover_price_gross_usd"] == 76_800_000
    assert data["gross_proceeds_scenarios"]["prospectus_summary_gross_usd"] == 80_700_000


def test_commitment_fee_is_an_outflow_due_november_six():
    data = load()["eloc_commitment_fee"]
    assert data["upfront_fee_usd"] == 521_893.50
    assert data["contractual_due_date"] == "2026-11-06"
    assert data["status_at_cutoff"] == "PAYMENT_NOT_VERIFIED; due date is Nov 6, 2026"
    assert data["classification"].startswith("contractual cash outflow")


def test_onchain_outflow_is_unattributed_not_classified_as_sale():
    data = load()["onchain_attribution"]
    assert data["xrp_in_attributed_wallets"] == 103_129_905
    assert data["xrp_moved_outside_attributed_wallet_set"] == 370_346_663
    assert data["destination_beneficial_ownership"] == "UNRESOLVED"
    assert data["classification"] == "UNATTRIBUTED_OUTFLOW_NOT_CLASSIFIED_AS_SALE"
    assert data["independent_replay_performed"] is False


def test_forecast_and_model_admission_remain_disabled():
    data = load()
    assert data["forecast_issued"] is False
    assert data["model_eligible"] is False
    assert data["data_quality"]["raw_sec_sha256_receipts"] is False
    assert data["data_quality"]["raw_xrpl_transactions_independently_replayed"] is False
