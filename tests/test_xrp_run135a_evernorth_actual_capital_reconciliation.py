from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261110T160534Z-run135a-evernorth-actual-capital-reconciliation.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_run135a_reconciles_all_inkind_xrp_components_exactly() -> None:
    data = _artifact()
    capital = data["evernorth"]["in_kind_xrp_reconciliation"]
    components = (
        "advance_funding_xrp",
        "series_c_arrington_xrp_capital_fund_xrp",
        "ripple_affiliated_larsen_lam_childrens_remainder_trust_xrp",
        "ripple_direct_contribution_agreement_xrp",
        "delayed_funding_xrp",
    )
    total = sum((Decimal(capital[key]) for key in components), Decimal("0"))
    assert total == Decimal("388910554.061435")
    assert total == Decimal(capital["total_in_kind_xrp"])
    assert capital["exact_component_sum_matches"] is True
    assert capital["prior_200000_xrp_gap_status"] == "RESOLVED"


def test_run135a_separates_pubco_xrp_subtotal_from_total_inkind() -> None:
    capital = _artifact()["evernorth"]["in_kind_xrp_reconciliation"]
    subtotal = (
        Decimal(capital["advance_funding_xrp"])
        + Decimal(capital["series_c_arrington_xrp_capital_fund_xrp"])
        + Decimal(capital["ripple_affiliated_larsen_lam_childrens_remainder_trust_xrp"])
    )
    assert subtotal == Decimal("261919096.061435")
    assert subtotal == Decimal(capital["pubco_xrp_subtotal_xrp"])
    assert subtotal + Decimal(capital["ripple_direct_contribution_agreement_xrp"]) + Decimal(
        capital["delayed_funding_xrp"]
    ) == Decimal(capital["total_in_kind_xrp"])


def test_run135a_cash_subscription_is_not_misreported_as_exact_xrp_purchase_cash() -> None:
    cash = _artifact()["evernorth"]["cash_and_xrp_subscriptions"]
    purchased_xrp = Decimal(cash["xrp_purchased_with_cash"])
    average_price = Decimal(cash["average_purchase_price_usd"])
    arithmetic_purchase = purchased_xrp * average_price
    assert cash["advance_funding_cash_raised_usd"] == "214049995"
    assert abs(arithmetic_purchase - Decimal("214000000")) < Decimal("1")
    assert cash["advance_funding_cash_used_to_purchase_xrp_usd_approx"] == "214000000"
    assert cash["cash_raised_less_detailed_purchase_usd"] == "49995"


def test_run135a_distinguishes_debt_from_confirmed_xrp_purchase_capital() -> None:
    evernorth = _artifact()["evernorth"]
    notes = evernorth["convertible_notes"]
    facility = evernorth["related_party_facility"]
    assert notes["gross_principal_usd"] == "30000000"
    assert notes["net_cash_after_advisor_fee_usd"] == "29000000"
    assert notes["specific_xrp_purchase_proven"] is False
    assert notes["conversion_and_put_risk"]["possible_cash_settlement_usd_approx"] == "120000000"
    assert facility["drawn_as_of_2026_10_07_usd"] == "9700000"
    assert facility["classification"] == "DEBT"


def test_run135a_eloc_is_undrawn_capacity_not_actual_capital() -> None:
    eloc = _artifact()["evernorth"]["committed_equity_facility"]
    assert eloc["proceeds_received_as_of_prospectus_usd"] == "0"
    assert eloc["maximum_shares"] == "5218935"
    assert eloc["fee_payment_verified"] is False
    assert eloc["classification"] == "UNDRAWN CONTINGENT EQUITY CAPACITY, NOT ACTUAL CAPITAL RECEIVED"


def test_run135a_preserves_precision_and_conditional_mark_to_market_caveats() -> None:
    holdings = _artifact()["evernorth"]["derived_holdings_bridge"]
    assert holdings["known_component_subtotal_xrp"] == "473276430.423935"
    assert holdings["third_party_tracker_total_xrp"] == "473276430.061435"
    assert holdings["difference_vs_known_component_subtotal_xrp"] == "0.3625"
    assert holdings["complete_total_xrp"] is None
    assert holdings["residual_cash_purchase_xrp_quantity"] is None
    sensitivity = _artifact()["evernorth"]["current_price_sensitivity"]
    assert sensitivity["conditional_return_pct_approx"] == "-58.9856"
    assert "conditional" in sensitivity["caveat"].lower()


def test_run135a_is_not_a_forecast_or_model_eligible_dataset() -> None:
    data = _artifact()
    assert data["source_capture"]["raw_bytes_captured"] is False
    assert data["source_capture"]["raw_sha256_receipts_available"] is False
    assert data["model_eligible"] is False
    assert data["forecast_status"] == "NOT_ISSUED"


def test_run135a_kraken_rest_open_is_utc_day_not_rolling_24h() -> None:
    market = _artifact()["market_context"]["kraken_xrp_usd"]
    assert market["utc_day_open_usd"] == "1.09748"
    assert market["open_24h_usd"] is None
    assert market["vwap_24h_usd"] == "1.07906869"
    assert market["high_24h_usd"] == "1.11511"
    assert market["low_24h_usd"] == "1.03011"
    assert "midnight UTC" in market["open_field_semantics"]


def test_run135a_separates_the_two_ripple_credit_facilities_from_nh_kyobo_notes() -> None:
    evernorth = _artifact()["evernorth"]
    small = evernorth["evernorth_facility"]
    company = evernorth["related_party_facility"]
    notes = evernorth["convertible_notes"]
    assert small["lender"] == "Ripple Labs Inc."
    assert small["facility_limit_usd"] == "1000000"
    assert small["drawn_as_of_2026_06_30_usd"] == "0"
    assert company["lender"] == "Ripple"
    assert company["facility_limit_usd"] == "10000000"
    assert company["drawn_as_of_2026_10_07_usd"] == "9700000"
    assert notes["counterparty"].startswith("NH Investment & Securities")


def test_run135a_records_review_corrections_without_overwriting_historical_artifacts() -> None:
    data = _artifact()
    corrections = data["evernorth"]["corrections"]
    assert len(corrections) == 2
    assert corrections[0]["prior_field"] == "open_24h_usd"
    assert corrections[0]["disposition"].startswith("Historical artifacts are preserved")
    assert corrections[1]["source_artifact"].endswith(
        "20261104T134706Z-evernorth-close-actual-capital-sbi-ownership-reconciliation.json"
    )


def test_run135a_residual_cash_was_used_for_xrp_at_close_but_quantity_is_unknown() -> None:
    cash = _artifact()["evernorth"]["cash_and_xrp_subscriptions"]
    assert cash["advance_funding_cash_received_usd"] == "214049995"
    assert cash["cash_used_to_purchase_xrp_usd_approx"] == "214000000"
    assert cash["residual_cash_purchase_at_close_usd"] == "49995"
    assert cash["residual_cash_purchase_xrp_quantity"] is None
    assert cash["total_cash_deployed_to_xrp_usd"] == "214049995"


def test_run135a_does_not_claim_complete_evernorth_closing_holdings() -> None:
    bridge = _artifact()["evernorth"]["derived_holdings_bridge"]
    assert bridge["known_component_subtotal_xrp"] == "473276430.423935"
    assert bridge["complete_total_xrp"] is None
    assert bridge["residual_cash_purchase_at_close_usd"] == "49995"
    assert bridge["residual_cash_purchase_xrp_quantity"] is None
    assert "not the exact closing total" in bridge["status"]


def test_run135a_preserves_evernorth_issuer_reported_liquidity_risk() -> None:
    liquidity = _artifact()["evernorth"]["liquidity_snapshot"]
    assert liquidity["as_of"] == "2026-06-30"
    assert liquidity["evernorth"]["unrestricted_cash_usd_approx"] == "100000"
    assert liquidity["evernorth"]["net_working_capital_deficit_usd_approx"] == "696100000"
    assert liquidity["evernorth"]["accumulated_deficit_usd_approx"] == "340900000"
    assert liquidity["evernorth"]["net_loss_usd"] == "188134733"
    assert liquidity["pathfinder_company"]["unrestricted_cash_usd_approx"] == "800000"
