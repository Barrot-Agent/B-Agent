from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    REPO_ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T200308Z-sbic-evernorth-capital-askcoin-kamilah-live-market-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def receipt_by_id(artifact: dict) -> dict[str, dict]:
    return {item["source_id"]: item for item in artifact["source_receipts"]}


def test_sbic_statute_and_regional_profiles_resolve_exactly_three_companies() -> None:
    artifact = load_artifact()
    entities = artifact["sbic_identity_resolution"]["entities"]
    assert len(entities) == 3
    assert {item["regional_name"] for item in entities} == {
        "SBIC East Japan",
        "SBIC Central Japan",
        "SBIC West Japan",
    }
    assert {item["legal_name"] for item in entities} == {
        "Tokyo Small and Medium Business Investment & Consultation Co., Ltd.",
        "Nagoya Small and Medium Business Investment & Consultation Co., Ltd.",
        "Osaka Small and Medium Business Investment & Consultation Co., Ltd.",
    }
    assert artifact["sbic_identity_resolution"]["statutory_basis"]["act_number"] == (
        "Act No. 101 of June 10, 1963"
    )
    assert artifact["sbic_identity_resolution"]["identity_status"] == "PRIMARY_SOURCE_RESOLVED"
    distinction = artifact["sbic_identity_resolution"]["distinction_from_sbi_holdings"]
    assert "not SBI Holdings, Inc." in distinction


def test_sbic_chatgpt_activity_is_training_not_an_openai_partnership() -> None:
    research = load_artifact()["chatgpt_sibc_research"]
    assert research["verified_events"][0]["date"] == "2025-02-26"
    assert "Microsoft" in research["verified_events"][0]["speaker"]
    assert research["verified_events"][1]["date"] == "2026-11-16"
    assert "not evidence of an OpenAI partnership" in research["conclusion"]


def test_sbi_holdings_evernorth_voting_and_nonvoting_stakes_are_not_conflated() -> None:
    ownership = load_artifact()["evernorth_capital_reconciliation"][
        "sbi_holdings_evernorth_ownership"
    ]
    assert ownership["class_a_percent"] == 39.9
    assert ownership["class_a_voting_shares"] == 8_885_293
    assert ownership["class_c_percent"] == 9.0
    assert ownership["class_c_non_voting_shares"] == 2_905_659
    assert ownership["class_c_rights"] == (
        "Non-voting; do not add the Class C percentage to the Class A voting percentage."
    )
    assert "not 39.9% of all common shares" in ownership["interpretation"]
    assert "SBI Holdings USA, Inc." in ownership["class_a_holder_entities"]
    assert "does not separately itemize" in ownership["footnote_scope"]


def test_realized_cash_xrp_purchase_and_in_kind_contributions_are_separate() -> None:
    capital = load_artifact()["evernorth_capital_reconciliation"]
    advance = capital["cash_and_xrp_at_advance_funding"]
    closing = capital["business_combination_closing"]
    assert advance["cash_received_usd"] == 214_049_995
    assert advance["cash_used_to_purchase_xrp_usd"] == 214_000_000
    assert advance["xrp_purchased"] == 84_365_876
    assert advance["separately_reported_600000_xrp_in_kind"] is True
    assert closing["gross_cash_proceeds_usd"] == 272_600_000
    assert closing["private_placement_cash_usd"] + closing["spac_trust_cash_released_usd"] == (
        closing["gross_cash_proceeds_usd"]
    )
    assert closing["in_kind_xrp_contributions"] == 388_910_554
    assert "Do not treat gross cash proceeds" in closing["transaction_costs"]


def test_convertible_note_is_realized_financing_but_not_verified_xrp_purchase() -> None:
    note = load_artifact()["evernorth_capital_reconciliation"]["convertible_note"]
    assert note["principal_usd"] == 30_000_000
    assert note["net_cash_proceeds_usd"] == 29_000_000
    assert note["advisor_fee_usd"] == 1_000_000
    assert note["issued"] == "2026-10-12"
    assert note["xrp_purchase_from_note_proceeds_verified"] is False


def test_ripple_related_party_credit_is_debt_not_xrp_purchase_evidence() -> None:
    credit = load_artifact()["evernorth_capital_reconciliation"][
        "ripple_related_party_credit"
    ]
    assert credit["limit_usd"] == 10_000_000
    assert credit["drawn_usd_as_of_2026_10_07"] == 9_700_000
    assert "not evidence of XRP purchases" in credit["purpose"]


def test_eloc_is_conditional_and_internal_424b3_discrepancy_is_preserved() -> None:
    eloc = load_artifact()["evernorth_capital_reconciliation"]["cantor_eloc"]
    assert eloc["shares_available"] == 5_218_935
    assert eloc["gross_proceeds_cover_case_usd"] == 76_800_000
    assert eloc["net_proceeds_estimate_usd"] == 74_400_000
    assert "$80.7M" in eloc["internal_document_discrepancy"]
    assert "all, some or none" in eloc["issuer_discretion"]
    assert eloc["actual_facility_draw_or_xrp_purchase_verified"] is False
    assert eloc["commitment_fee_usd"] == 521_893.5


def test_ask_coin_exchange_is_not_permission_coin_ask_token() -> None:
    research = load_artifact()["exact_phrase_research"]["ask_coin"]
    assert "Inactive and Untracked" in research["result"]
    assert "separate token" in research["distinct_asset"]
    assert research["xrp_relationship"].startswith("No verified XRP relationship")


def test_actual_capital_phrase_is_secondary_commentary_not_issuer_evidence() -> None:
    research = load_artifact()["exact_phrase_research"]["actual_capital"]
    assert "user-generated" in research["exact_phrase_context"]
    assert "not primary evidence" in research["primary_evidence"]
    assert research["status"] == "PRIMARY_CAPITAL_AMOUNTS_RECONCILED_EXACT_PHRASE_NOT_ISSUER_TERM"


def test_kamilah_candidate_video_is_not_counted_as_verified_attribution() -> None:
    inventory = load_artifact()["kamilah_stevenson_inventory_update"]
    candidate = inventory["candidate_video"]
    assert inventory["verified_public_video_count"] == 1
    assert candidate["video_id"] == "L_5bqd94rWo"
    assert candidate["attribution_status"] == "CANDIDATE_ONLY_NOT_IDENTITY_VERIFIED"
    assert candidate["counted_as_verified"] is False
    assert candidate["first_party_domain_links_specific_youtube_channel"] is False


def test_all_normalized_source_excerpt_hashes_match() -> None:
    artifact = load_artifact()
    receipts = artifact["source_receipts"]
    assert len(receipts) >= 20
    for receipt in receipts:
        if "captured_excerpt_text" in receipt:
            actual = hashlib.sha256(
                receipt["captured_excerpt_text"].encode("utf-8")
            ).hexdigest()
            assert actual == receipt.get("captured_excerpt_sha256_corrected", receipt["captured_excerpt_sha256"]), receipt["source_id"]


def test_direct_market_response_hashes_match_and_are_not_feature_admitted() -> None:
    artifact = load_artifact()
    receipts = receipt_by_id(artifact)
    market_ids = (
        "kraken_xrpusd_ticker",
        "okx_xrpusdt_ticker",
        "binance_xrpusdt_perpetual_premium_index",
    )
    for source_id in market_ids:
        receipt = receipts[source_id]
        actual = hashlib.sha256(
            receipt["raw_response_text"].encode("utf-8")
        ).hexdigest()
        assert actual == receipt["raw_response_sha256"]
        assert receipt["model_eligible"] is False


def test_stale_or_untimestamped_market_data_cannot_trigger_forecast() -> None:
    artifact = load_artifact()
    market = artifact["market_snapshot"]
    observations = {item["source_id"]: item for item in market["observations"]}
    assert observations["kraken_xrpusd_ticker"]["timestamp_status"] == "NOT_SUPPLIED"
    assert observations["okx_xrpusdt_ticker"]["age_seconds_at_reference_clock"] > 300
    assert observations["binance_xrpusdt_perpetual_premium_index"]["age_seconds_at_reference_clock"] > 300
    assert all(item["model_eligible"] is False for item in observations.values())
    assert market["depth_status"].startswith("Depth endpoints")
    assert artifact["model_admission"]["feature_admission"] is False
    assert artifact["model_admission"]["forecast_status"] == "NOT_ISSUED"
