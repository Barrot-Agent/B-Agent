from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T043946Z-eurgh-gatehub-dinaro-xrpl-sepa-launch.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))


def by_id(artifact: dict, source_id: str) -> dict:
    return next(
        item for item in artifact["source_records"]
        if item["source_id"] == source_id
    )


def test_primary_excerpt_digests_are_stable() -> None:
    artifact = load_artifact()
    for source in artifact["source_records"]:
        excerpt = source["normalized_excerpt"].encode("utf-8")
        assert hashlib.sha256(excerpt).hexdigest() == source["excerpt_sha256"]


def test_gatehub_and_dinaro_roles_are_not_conflated() -> None:
    artifact = load_artifact()
    assert artifact["event_summary"]["issuer"] == "Dinaro d.o.o."
    assert artifact["event_summary"]["distribution_wallet_partner"] == "GateHub Ltd."
    launch = by_id(artifact, "gatehub_eurgh_launch_20261105")
    assert launch["additional_published_fields"]["issuer_address"] == (
        "rDdaSjBbgCGQQsGRSfMidBMyHbPoeE5KQR"
    )
    assert artifact["event_summary"]["networks"] == [
        "XRP Ledger (XRPL)",
        "Xahau",
    ]


def test_banka_slovenije_register_confirms_emi_identity_and_name_change() -> None:
    artifact = load_artifact()
    register = by_id(artifact, "banka_slovenije_dinaro_supervised_entity_register")
    parsed = register["parsed"]
    assert parsed["registration_number"] == "8640084000"
    assert parsed["electronic_money_authorisation_date"] == "2021-11-02"
    assert parsed["former_legal_name"].startswith("PAYWISER")
    assert parsed["name_change_effective_or_recorded"] == "2026-06-08"
    assert parsed["host_member_state_passporting_list_published"] is True


def test_mica_emt_claim_and_whitepaper_approval_are_distinct() -> None:
    artifact = load_artifact()
    legal = by_id(artifact, "banka_slovenije_emti_mica_framework")
    assert legal["parsed"]["emt_interest_permitted"] is False
    assert legal["parsed"]["holder_claim_against_issuer"] is True
    assert legal["parsed"]["issuer_authorisation_required"] == "EMI or bank"
    terms = by_id(artifact, "gatehub_dinaro_eurgh_general_terms")
    assert terms["parsed"]["redemption_at_par"] is True
    assert terms["parsed"]["product_approved_by_competent_authority"] is False
    assert terms["parsed"]["whitepaper_approval_status"] == "NOT_STATED_IN_RETRIEVED_PRIMARY_TEXT"
    assert artifact["whitepaper_access"]["product_approval_status"] == "NOT_APPROVED_PER_OFFICIAL_TERMS"
    assert artifact["whitepaper_access"]["reserve_composition_verified"] is False


def test_free_token_fees_do_not_mean_all_sepa_payments_are_free() -> None:
    artifact = load_artifact()
    launch = artifact["event_summary"]["claimed_issuer_fees"]
    price_list = by_id(artifact, "dinaro_gatehub_programme_price_list")["parsed"]
    assert launch == {
        "issuance": "free",
        "redemption": "free",
        "transfer": "free",
    }
    assert price_list["incoming_sepa_eur"] == 0
    assert price_list["outgoing_sepa_eur"] == 1
    assert price_list["sending_instant_payment_eur"] == 1
    assert price_list["receiving_instant_payment_eur"] == 0


def test_xrpl_deployment_does_not_prove_xrp_bridge_demand() -> None:
    artifact = load_artifact()
    relevance = artifact["network_and_xrp_relevance"]
    assert relevance["explicit_xrp_bridge_asset_requirement_in_gatehub_sepa_flow"] == "not stated"
    assert relevance["xrp_market_purchase_or_reserve_commitment"] == "not disclosed"
    assert relevance["circulation_or_liquidity_data"] == "not disclosed"
    assert artifact["model_admission"]["eligible_as_price_feature"] is False


def test_event_is_not_promoted_to_directional_forecast_or_trade() -> None:
    artifact = load_artifact()
    assert artifact["model_admission"]["candidate_event_timeline_entry"] is True
    assert artifact["forecast"]["status"] == "NOT_ISSUED"
    assert artifact["forecast"]["direction"] is None
    assert artifact["forecast"]["shadow_forecast_issued"] is False
    assert artifact["forecast"]["paper_trade_executed"] is False
    assert artifact["forecast"]["real_money_action"] is False
    assert not any(artifact["external_actions"].values())


def test_xahau_native_fee_and_reserve_asset_is_xah_not_xrp() -> None:
    artifact = load_artifact()
    source = by_id(artifact, "xahau_official_whitepaper_network_token")
    parsed = source["parsed"]
    assert parsed["native_token"] == "XAH"
    assert parsed["transaction_fee_asset"] == "XAH"
    assert parsed["account_reserve_asset"] == "XAH"
    relevance = artifact["network_and_xrp_relevance"]
    assert relevance["xrpl_native_fee_asset"] == "XRP"
    assert relevance["xahau_native_fee_asset"] == "XAH"
    assert relevance["xahau_native_token_is_xah_not_xrp"] is True
    assert "Xahau uses XAH" in relevance["xrp_fee_or_reserve_effect"]
