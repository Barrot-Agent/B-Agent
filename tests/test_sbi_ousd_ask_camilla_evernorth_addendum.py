import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_evernorth_sec_holdings_separate_cash_purchase_from_in_kind_contributions():
    snap = load("data/xrp_intelligence/snapshots/20261101T153000Z-evernorth-bitgo-sbi-ousd-ask-camilla-and-market.json")
    e = snap["evernorth"]
    assert e["company_reported_xrp_at_closing"] == 473276430
    assert e["cash_purchase_xrp"] == 84365876.3625
    assert e["cash_used_for_purchase_usd"] == 214100000
    assert e["in_kind_xrp_contributions"] == 388910554
    assert e["sale_status"] == "NO_SALE_INFERRED_FROM_370M_MOVEMENT"


def test_evernorth_370m_movement_is_bitgo_custody_migration_inference_not_sale():
    snap = load("data/xrp_intelligence/snapshots/20261101T153000Z-evernorth-bitgo-sbi-ousd-ask-camilla-and-market.json")
    e = snap["evernorth"]
    d = e["destination_wallet_evidence"]
    assert e["onchain_tracker_page"]["external_outflow_xrp"] == 370346663
    assert d["bitgo_activation_verified_by_bithomp"] == 9
    assert d["destinations_listed"] == 10
    assert d["classification"].startswith("STRONGLY_SUPPORTS_BITGO_CUSTODY_REALLOCATION")


def test_evernorth_custody_and_insurance_are_not_overstated():
    snap = load("data/xrp_intelligence/snapshots/20261101T153000Z-evernorth-bitgo-sbi-ousd-ask-camilla-and-market.json")
    c = snap["evernorth"]["custody"]
    assert c["cold_storage_share_pct"] == 100
    assert c["multisig"] == "2-of-3"
    assert c["insurance_dedicated_to_evernorth"] is False
    assert c["insurance_share_of_evernorth_value_pct_at_2026_10_09"] == 36.9
    assert c["pledge_or_lend_only_if_expressly_directed"] is True


def test_evernorth_financing_capacity_is_not_treated_as_funded_capital():
    snap = load("data/xrp_intelligence/snapshots/20261101T153000Z-evernorth-bitgo-sbi-ousd-ask-camilla-and-market.json")
    f = snap["evernorth"]["financing"]
    assert f["convertible_notes_usd"] == 30000000
    assert f["eloc_potential_gross_usd"] == 76800000
    assert f["eloc_optional_and_conditional"] is True
    assert f["eloc_draw_verified"] is False


def test_jpysc_reserves_and_hyper_deposit_are_separate_capital_categories():
    snap = load("data/xrp_intelligence/snapshots/20261101T153000Z-evernorth-bitgo-sbi-ousd-ask-camilla-and-market.json")
    j = snap["sbi_multirail"]["jpysc"]
    h = snap["sbi_multirail"]["hyper_deposit"]
    assert j["issued_balance_jpy_as_of_2026_09_07"] == 20100000000
    assert j["short_term_jgb_backing_investment_jpy"] == 1000000000
    assert j["lending_applications_jpy"] == 6900000000
    assert h["balance_jpy"] == 1600000000000
    assert h["xrp_capital"] is False


def test_sbi_card_and_jpysc_interop_are_not_misclassified_as_live_xrp_flows():
    snap = load("data/xrp_intelligence/snapshots/20261101T153000Z-evernorth-bitgo-sbi-ousd-ask-camilla-and-market.json")
    s = snap["sbi_multirail"]
    assert "XRP" in s["business_card"]["crypto_choices"]
    assert s["business_card"]["aggregate_xrp_redemptions"] == "UNKNOWN"
    assert s["jpysc"]["public_chain_rollout"] == "PENDING_LEGAL_TAX_AND_REGULATORY_READINESS"
    assert s["ousd_interop"]["status"] == "EXPLORATORY_POC"


def test_coinbase_circle_ripple_is_multi_issuer_not_exclusive_alignment():
    snap = load("data/xrp_intelligence/snapshots/20261101T153000Z-evernorth-bitgo-sbi-ousd-ask-camilla-and-market.json")
    assert snap["coinbase_circle_ripple"]["interpretation"] == "MULTI_ISSUER_AND_MULTI_RAIL_PLATFORM_STRATEGY; NOT_EXCLUSIVE_ALIGNMENT"
    assert "RLUSD listed/distributed" in snap["coinbase_circle_ripple"]["coinbase_position"]
    assert "Circle USDC distribution agreement renewed" in snap["coinbase_circle_ripple"]["coinbase_position"]


def test_permission_coin_ask_has_no_documented_xrpl_integration():
    snap = load("data/xrp_intelligence/snapshots/20261101T153000Z-evernorth-bitgo-sbi-ousd-ask-camilla-and-market.json")
    ask = snap["ask_coin"]
    assert ask["candidate"] == "Permission Coin (ASK)"
    assert ask["chains"] == ["Base", "Polygon"]
    assert ask["xrpl_contract_found"] is False
    assert ask["direct_xrp_integration"] == "NOT_FOUND"


def test_camilla_kamilah_identity_and_video_inventory_remain_carefully_classified():
    snap = load("data/xrp_intelligence/snapshots/20261101T153000Z-evernorth-bitgo-sbi-ousd-ask-camilla-and-market.json")
    c = snap["camilla_stephenson_identity"]
    assert c["identity_status"] == "STRONGLY_SUPPORTED_PERSON_MATCH_CHANNEL_ID_CROSS_LINK_PENDING"
    assert c["known_public_videos"] == 11
    assert c["inventory_complete"] is False
    assert c["actual_capital_exact_phrase_found_in_interview"] is False


def test_japan_law_does_not_claim_xrp_specific_designation():
    snap = load("data/xrp_intelligence/snapshots/20261101T153000Z-evernorth-bitgo-sbi-ousd-ask-camilla-and-market.json")
    law = snap["japan_fiea"]
    assert law["law_number"] == 64
    assert law["promulgated_date"] == "2026-07-23"
    assert law["specific_xrp_designation"] == "NOT_CONFIRMED"


def test_open_interest_provider_disagreement_is_quarantined():
    snap = load("data/xrp_intelligence/snapshots/20261101T153000Z-evernorth-bitgo-sbi-ousd-ask-camilla-and-market.json")
    d = snap["derivatives_provider_observations"]
    assert d["coinglass"]["open_interest_usd"] == 2834000000
    assert d["coingecko"]["open_interest_usd"] == 3529000000
    assert d["liqwall"]["open_interest_usd"] == 1330000000
    assert d["feature_admission"] == "NONE"


def test_current_forecast_status_remains_not_issued():
    handoff = load("data/xrp_intelligence/hand_offs/20261101T153000Z-evernorth-bitgo-sbi-multirail-ask-camilla-handoff.json")
    assert handoff["forecast_status"] == "NOT_ISSUED"
    assert handoff["feature_admission"] == "NONE"
