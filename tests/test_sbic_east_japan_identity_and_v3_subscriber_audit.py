import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = "20261101T214500Z"


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_sbic_east_japan_and_historical_sbi_capital_are_distinct_entities():
    source = load(f"data/xrp_intelligence/source_revisions/{STAMP}-sbic-east-japan-chatgpt-identity.json")
    graph = load(f"data/xrp_intelligence/relationship_graph_addenda/{STAMP}-sbic-east-japan-chatgpt-identity.json")
    ledger = load(f"data/xrp_intelligence/research_ledger_addenda/{STAMP}-sbic-east-japan-chatgpt-identity.json")

    by_id = {item["id"]: item for item in source["sources"]}
    assert "Tokyo Small and Medium Business Investment & Consultation Co., Ltd. (SBIC East Japan)" in by_id[f"SRC-SBIC-EAST-PROFILE-{STAMP}"]["claims"][0]
    historical = by_id[f"SRC-SBI-CAPITAL-2007-{STAMP}"]["claims"]
    assert any("60% SBI Holdings" in claim and "40% Jupiter Investment" in claim for claim in historical)
    assert "SBI_CAPITAL_2007" in {node["id"] for node in graph["nodes"]}
    assert "SBIC_EAST_JAPAN" in {node["id"] for node in graph["nodes"]}
    assert any(edge["from"] == "SBI_CAPITAL_2007" and edge["to"] == "SBI_HOLDINGS" for edge in graph["edges"])
    assert not any(edge["from"] == "SBIC_EAST_JAPAN" and edge["to"] in {"XRP_MARKET", "RIPPLE", "COINBASE", "CIRCLE"} for edge in graph["edges"])
    assert ledger["feature_admission"] == "NONE"
    assert ledger["forecast_status"] == "NOT_ISSUED"


def test_sbic_chatgpt_mentions_are_education_not_partnership():
    source = load(f"data/xrp_intelligence/source_revisions/{STAMP}-sbic-east-japan-chatgpt-identity.json")
    graph = load(f"data/xrp_intelligence/relationship_graph_addenda/{STAMP}-sbic-east-japan-chatgpt-identity.json")
    training = next(item for item in source["sources"] if item["id"] == f"SRC-SBIC-CHATGPT-TRAINING-{STAMP}")
    assert any("restricted to SBIC investee companies" in claim for claim in training["claims"])
    edge = next(edge for edge in graph["edges"] if edge["from"] == "SBIC_EAST_JAPAN" and edge["to"] == "CHATGPT")
    assert edge["status"] == "CONFIRMED_PRIMARY_SOURCE"
    assert "not_partnership" in edge["relation"]


def test_repository_audit_records_subscriber_bypass_and_exact_head_remediation():
    audit = load(f"data/repository_audits/{STAMP}-main-subscriber-access-and-v3-state.json")
    handoff = load(f"data/xrp_intelligence/hand_offs/{STAMP}-xrp-intelligence-and-v3-handoff.json")
    assert audit["observed_main_sha"] == "465ff4b40c43721db25e313df08b44a659f4a360"
    assert any(item["id"] == "FIND-CLIENT-SIDE-PAYWALL-BYPASS" for item in audit["confirmed_security_findings"])
    pr = audit["proposed_remediation"]
    assert pr["pr_number"] == 1476
    assert pr["ci_result"] == "success: 345 tests and 8 subtests passed"
    assert pr["fail_closed_gate_result"] == "success; automatic merging disabled"
    assert pr["state"] == "OPEN_DRAFT_UNMERGED"
    assert handoff["prediction_status"]["status"] == "NOT_ISSUED"
    assert "latest_signal.json remains a public repository file" in audit["proposed_remediation"]["limitation"] or "latest_signal.json" in audit["proposed_remediation"]["limitation"]


def test_kamilah_creator_inventory_remains_partial_and_camilla_match_unverified():
    ledger = load(f"data/xrp_intelligence/research_ledger_addenda/{STAMP}-sbic-east-japan-chatgpt-identity.json")
    assert any(item["classification"] == "UNKNOWN" and "Camilla Stephenson" in item["claim"] for item in ledger["findings"])
    assert any(item["classification"] == "UNKNOWN" and "all-public-video inventory remains incomplete" in item["claim"] for item in ledger["findings"])
