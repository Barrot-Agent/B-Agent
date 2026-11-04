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
    assert sources["sbi_holdings_chatgpt_enterprise_notice"]["url"] == "https://www.sbigroup.co.jp/news/2025/0609_15491.html"
