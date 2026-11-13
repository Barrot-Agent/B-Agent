import hashlib
import json
from pathlib import Path

ARTIFACT = Path(
    "research/xrp_intelligence/20261113T153500Z-run97-xrp-institutional-collateral-regulatory-paths.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_ripple_prime_advertises_xrp_collateral_but_discloses_no_balance():
    data = load_artifact()["ripple_prime"]
    assert "XRP" in data["collateral_claim"]
    assert data["actual_xrp_collateral_balances_disclosed"] is False
    assert data["xrp_specific_haircuts_disclosed"] is False
    assert data["actual_client_posting_verified"] is False


def test_ripple_prime_cross_margin_is_prime_broker_layer_not_cme_dco_acceptance():
    data = load_artifact()
    prime = data["ripple_prime"]
    cme = data["cme_clearing"]
    assert prime["single_pool_cross_margining"] is True
    assert {"CME", "Nodal Clear"}.issubset(set(prime["clearing_rails_listed"]))
    assert prime["actual_client_posting_verified"] is False
    assert cme["xrp_or_crypto_asset_listed"] is False
    assert "do not establish" in prime["distinction"].lower()


def test_cme_current_public_collateral_list_does_not_include_xrp():
    cme = load_artifact()["cme_clearing"]
    assert cme["xrp_or_crypto_asset_listed"] is False
    assert cme["dco_acceptance_for_xrp_verified"] is False
    assert "request" in cme["interpretation"].lower()


def test_cftc_26_05_initial_three_month_phase_is_restricted():
    cftc = load_artifact()["cftc_letter_26_05"]
    assert cftc["initial_ramp_up"]["duration_months"] == 3
    assert cftc["initial_ramp_up"]["eligible_assets"] == ["payment stablecoins", "Bitcoin", "Ether"]
    assert cftc["legal_character"].startswith("Staff no-action position")


def test_cftc_30_7_underlying_commodity_path_is_conditional():
    cftc = load_artifact()["cftc_letter_26_05"]
    path = cftc["after_initial_phase"]["cftc_30_7_customer_accounts"]
    assert "underlying commodity" in path
    assert cftc["after_initial_phase"]["fcm_notice_required"] is True
    assert cftc["xrp_path"]["potential_30_7_route"]
    assert cftc["xrp_path"]["actual_fcm_notice_or_xrp_customer_collateral_use_verified"] is False


def test_futures_and_cleared_swaps_customer_accounts_require_dco_acceptance():
    cftc = load_artifact()["cftc_letter_26_05"]
    assert "DCO" in cftc["after_initial_phase"]["futures_and_cleared_swaps_customer_accounts"]
    assert cftc["xrp_path"]["dco_acceptance_verified"] is False


def test_xrp_cme_futures_listing_does_not_prove_xrp_is_cme_collateral():
    data = load_artifact()
    xrp = data["cftc_letter_26_05"]["xrp_path"]
    cme = data["cme_clearing"]
    assert xrp["cme_xrp_futures_listed"] is True
    assert xrp["cme_contract_unit_xrp"] == 50000
    assert xrp["cme_contract_cash_settled_usd"] is True
    assert cme["xrp_or_crypto_asset_listed"] is False


def test_coinbase_aggregate_collateral_does_not_disclose_xrp_amount():
    coinbase = load_artifact()["coinbase"]
    assert coinbase["xrp_specific_amount_disclosed"] is False
    assert "no XRP-specific amount" in coinbase["collateral_disclosure"]
    assert coinbase["cftc_letter_requester"] == "Coinbase Financial Markets requested CFTC Staff Letter 26-05."


def test_sec_cftc_interpretation_lists_xrp_but_preserves_howey_analysis():
    data = load_artifact()["sec_cftc_classification"]
    assert data["xrp_listed_as_digital_commodity"] is True
    assert data["issue_date"] == "2026-03-17"
    assert data["effective_date"] == "2026-03-23"
    assert "does not supersede Howey" in data["legal_limit"]


def test_clarity_and_genius_status_are_not_conflated():
    data = load_artifact()["clarity_genius"]
    assert data["clarity_act"]["enacted"] is False
    assert data["clarity_act"]["senate_cloture_failed"] == "2026-08"
    assert data["genius_act"]["implementing_rules_as_of"] == "2026-11-09"
    assert data["genius_act"]["treasury_and_federal_reserve_rules"] == "proposed, not final"


def test_national_trust_bank_charter_does_not_change_stablecoin_issuer_automatically():
    issuers = load_artifact()["clarity_genius"]["issuer_entity_separation"]
    assert "separate from Standard Custody" in issuers["ripple_national_trust_bank"]
    assert "separate from Circle Internet Financial LLC" in issuers["circle_national_trust_bank"]


def test_authored_collateral_evidence_hashes_are_reproducible():
    summaries = load_artifact()["source_summaries"]
    for entry in summaries.values():
        assert hashlib.sha256(entry["text"].encode("utf-8")).hexdigest() == entry["sha256"]


def test_collateral_capability_is_event_timeline_only_not_forecast_feature():
    admission = load_artifact()["model_admission"]
    assert admission["eligible_for_event_timeline"] is True
    assert admission["eligible_as_xrp_collateral_adoption_feature"] is False
    assert admission["eligible_as_xrp_price_feature"] is False
    assert admission["forecast_status"] == "NOT_ISSUED"
