"""Regression tests for ASK identity, actual-capital and creator-identity controls."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261104T161106Z-ask-coin-actual-capital-kamilah-identity-continuation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_permission_ask_is_only_a_candidate_and_not_an_xrpl_token():
    data = load()
    ask = next(x for x in data["exact_phrase_findings"] if x["phrase"] == "ASK Coin")
    assert ask["status"] == "AMBIGUOUS_BEST_SUPPORTED_CANDIDATE_NOT_CONFIRMED"
    assert ask["candidate"]["network_scope"]["Base"].startswith("0x")
    assert ask["candidate"]["network_scope"]["Polygon"].startswith("0x")
    assert ask["candidate"]["network_scope"]["XRP_Ledger_or_XRPL"].startswith("No direct deployment")
    assert "No verified direct Ripple" in " ".join(ask["disconfirming_evidence_and_limits"])


def test_actual_capital_keeps_notional_deposit_and_implied_margin_separate():
    data = load()
    item = next(x for x in data["exact_phrase_findings"] if x["phrase"] == "actual capital")
    occurrences = item["candidate_occurrences"]
    assert occurrences[0]["arithmetic"]["simplified_implied_initial_margin_usd"] == 692000
    assert occurrences[1]["arithmetic"]["simplified_implied_initial_margin_usd"] == 815000
    assert item["status"] == "AMBIGUOUS_NO_SINGLE_EVENT_LINKED_TO_USER_PHRASE"
    assert "not verified actual capital" in occurrences[0]["limitations"][-1]


def test_kamilah_channel_remains_candidate_only_and_no_video_inventory_is_created():
    data = load()["creator_identity_audit"]
    assert data["candidate_channel"]["youtube_handle"] == "@drkamilahstevenson"
    assert data["candidate_channel"]["channel_id_candidate"] == "UCqUPJMQdkCN6lsLVDnichPA"
    assert data["identity_status"] == "UNVERIFIED_CANDIDATE_ONLY"
    assert data["video_inventory_status"] == "NOT_CREATED_PENDING_FIRST_PARTY_IDENTITY_AND_CHANNEL_OWNERSHIP_VERIFICATION"
    assert data["candidate_channel"]["linkage_status"].startswith("CANDIDATE_HANDLE_LINKED")
    assert all(source["model_eligible"] is False for source in load()["source_registry"])


def test_sbic_chatgpt_event_and_sbi_holdings_enterprise_notice_are_separate():
    data = load()
    sources = {source["id"]: source for source in data["source_registry"]}
    assert sources["sbic_east_chatgpt_education_notice"]["url"] == "https://www.sbic.co.jp/seminar/20260305js/"
    assert sources["sbi_holdings_chatgpt_enterprise_notice"]["url"] == "https://www.sbigroup.co.jp/news/2025/0501_15410.html"


SBIC_ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T080500Z-japan-sbic-chatgpt-entity-resolution-primary-sources.json"


def test_japan_sbic_is_three_statutory_companies_not_sbi_holdings():
    data = json.loads(SBIC_ARTIFACT.read_text(encoding="utf-8"))
    entities = data["entity_resolution"]["statutory_identity"]["companies"]
    assert [item["regional_name"] for item in entities] == [
        "SBIC East Japan",
        "SBIC Central Japan",
        "SBIC West Japan",
    ]
    assert len({item["domain"] for item in entities}) == 3
    assert data["entity_resolution"]["statutory_identity"]["article_2_names_three_separate_companies"] is True
    assert data["entity_resolution"]["sbi_holdings"]["legal_name"] == "SBI Holdings, Inc."
    assert data["entity_resolution"]["sbi_holdings"]["established"] == "1999-07-08"


def test_chatgpt_and_ai_references_are_separate_events_and_counterparties():
    data = json.loads(SBIC_ARTIFACT.read_text(encoding="utf-8"))
    refs = data["entity_resolution"]["chatgpt_and_ai_references"]
    assert "Microsoft Japan speaker" in refs["tokyo_sbic_event"]
    assert "not an OpenAI partnership" in refs["tokyo_sbic_event"]
    assert "Ridge-i" in refs["sbi_securities_service"]
    assert "not ChatGPT or OpenAI" in refs["sbi_securities_service"]
    assert "Anthropic/Claude" in refs["sbi_anthropic"]
    assert "SoftBank Group" in refs["softbank_openai"]
    assert "not SBI Holdings" in refs["softbank_openai"]
    assert data["model_eligible"] is False
    assert data["model_admission"]["forecast_issued"] is False


EVERNORTH_CAPITAL_ARTIFACT = ROOT / "research/xrp_intelligence/20261105T081500Z-evernorth-actual-capital-cantor-facility-reconciliation.json"


def test_evernorth_cantor_capacity_is_not_actual_capital():
    data = json.loads(EVERNORTH_CAPITAL_ARTIFACT.read_text(encoding="utf-8"))
    facility = data["capital_reconciliation"]["cantor_committed_equity_facility"]
    assert facility["actual_proceeds_usd_as_of_2026_10_30"] == 0
    assert facility["maximum_new_shares"] == 5_218_935
    assert facility["upfront_commitment_fee_usd"] == 521_893.50
    assert facility["fee_is_capital_raised"] is False
    assert data["model_eligible"] is False


def test_evernorth_cash_in_kind_debt_and_warrant_potential_are_separate():
    data = json.loads(EVERNORTH_CAPITAL_ARTIFACT.read_text(encoding="utf-8"))
    capital = data["capital_reconciliation"]
    assert capital["historical_cash_received_and_deployed"]["amount_usd"] == 214_050_000
    assert capital["historical_cash_received_and_deployed"]["use_of_proceeds_usd"] == 214_000_000
    assert capital["in_kind_xrp_subscriptions"]["total_xrp"] == 262_119_096.061435
    assert capital["convertible_senior_pik_notes"]["gross_cash_consideration_usd"] == 30_000_000
    assert capital["convertible_senior_pik_notes"]["net_proceeds_after_stated_issuance_costs_usd"] == 29_000_000
    assert capital["public_warrants"]["maximum_gross_cash_if_all_exercised_usd"] == 132_249_908
    assert capital["public_warrants"]["proceeds_verified_usd"] is None
