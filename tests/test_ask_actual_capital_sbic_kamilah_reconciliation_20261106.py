from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T022802Z-ask-actual-capital-sbic-kamilah-exact-phrase-reconciliation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_permission_ask_is_distinguished_from_xrp():
    row = load_artifact()["ask_coin"]["strongest_candidate"]
    assert row["project"] == "Permission"
    assert row["token_name"] == "ASK"
    assert row["xrp_relationship_status"] == "NO_DIRECT_XRP_OR_XRPL_RELATIONSHIP_ESTABLISHED"
    assert "XRP" not in row["official_contracts"]


def test_ask_official_contracts_and_fixed_supply_are_preserved():
    row = load_artifact()["ask_coin"]["strongest_candidate"]
    assert row["fixed_supply"] == 100_000_000_000
    assert row["official_contracts"]["Base"] == "0xBB146326778227A8498b105a18f84E0987A684b4"
    assert row["official_contracts"]["Polygon"] == "0xaA3717090CDDc9B227e49d0D84A28aC0a996e6Ff"
    assert row["token_standard"] == "LayerZero Omnichain Fungible Token (OFT)"


def test_future_ask_governance_is_not_misrepresented_as_current():
    row = load_artifact()["ask_coin"]["strongest_candidate"]
    assert any("future capabilities" in x for x in row["official_documentation_utility"])


def test_evernorth_eloc_maximum_is_illustrative_not_cash_received():
    row = load_artifact()["actual_capital"]["evernorth_cantor_equity_line"]
    assert row["maximum_new_shares"] == 5_218_935
    assert row["reference_stock_price_usd"] == 15.46
    assert row["prospectus_rounded_maximum_gross_proceeds_usd"] == 80_700_000
    assert row["cash_received_from_facility_verified"] is False
    assert row["shares_sold_under_facility_verified"] is False
    assert row["xrp_purchases_funded_by_facility_verified"] is False


def test_efficacy_date_and_commitment_fee_are_not_capital_inflow():
    row = load_artifact()["actual_capital"]["evernorth_cantor_equity_line"]
    assert row["registration_effective_date"] == "2026-10-30"
    assert row["upfront_commitment_fee_usd"] == 521_893.5
    assert "Payable by Evernorth" in row["fee_timing"]
    assert "not cash already received" in row["interpretation"][0]


def test_actual_capital_phrase_secondary_usage_is_not_primary_evidence():
    row = load_artifact()["actual_capital"]["exact_phrase_search"]
    assert row["phrase"] == "actual capital"
    assert row["evidentiary_status"] == "SECONDARY_COMMENTARY_NOT_A_PRIMARY_CAPITAL_RECORD"


def test_sbic_exact_phrase_search_does_not_collapse_entity_meanings():
    row = load_artifact()["sbic_chatgpt"]
    assert row["search_status"] == "NO_EXACT_INDEXED_MATCH_RETURNED_IN_THIS_RUN"
    assert len(row["preserved_disambiguations"]) == 3
    assert row["inference_permitted"] is False


def test_kamilah_public_attribution_is_not_claimed_as_legal_identity():
    row = load_artifact()["camilla_kamilah_stevenson"]
    assert row["public_media_corroboration"]["episode_date"] == "2026-06-11"
    assert row["legal_identity_verified"] is False
    assert row["new_youtube_videos_added"] == []
    assert row["inventory_exhaustive"] is False


def test_artifact_is_research_only_and_issues_no_forecast():
    row = load_artifact()
    assert row["model_eligible"] is False
    assert row["forecast_status"] == "NOT_ISSUED"
    assert row["data_cutoff_utc"] is None


def test_permission_coinbase_embedded_wallet_is_a_service_relationship_not_an_xrp_or_token_counterparty():
    data = load_artifact()
    row = data["ask_coin"]["strongest_candidate"]
    relation = row["wallet_infrastructure_relationship"]
    assert relation["provider"] == "Coinbase"
    assert relation["service"] == "Coinbase Embedded Wallet"
    assert relation["announced_date"] == "2026-09-22"
    assert "Permission says it no longer holds wallet keys" in relation["key_control"]
    assert row["xrp_relationship_status"] == "NO_DIRECT_XRP_OR_XRPL_RELATIONSHIP_ESTABLISHED"
    source = next(x for x in data["source_registry"] if x["id"] == relation["source_id"])
    assert source["url"] == "https://www.permission.ai/blog/ask-wallet-update"
    assert hashlib.sha256(source["normalized_evidence"].encode("utf-8")).hexdigest() == source["normalized_evidence_sha256"]
    assert source["exact_quote_word_count"] == 12
