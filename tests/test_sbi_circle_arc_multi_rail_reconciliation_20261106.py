from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261106T231841Z-sbi-circle-arc-multi-rail-reconciliation.json"
ORIGINAL = ROOT / "research" / "xrp_intelligence" / "20261106-institutional-xrp-network-cbxrp-sbi-circle-ripple.json"


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_original_preimage_bound_institutional_network_artifact_remains_unchanged():
    raw = ORIGINAL.read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + bytes([0]) + raw).hexdigest()
    assert git_blob == "303453dd9f5d11bce742dbe61e0f7cb4b18dcdd3"
    assert load_artifact()["related_immutable_artifact"]["git_blob_sha1"] == git_blob


def test_sbi_circle_arc_validator_relationship_is_primary_sourced_and_not_xrpl():
    data = load_artifact()
    edge = {item["id"]: item for item in data["relationship_updates"]}["sbi_circle_arc_validator"]
    assert edge["status"] == "founding_validator_at_public_mainnet_launch"
    assert "operation and governance" in edge["relationship"]
    assert any("not XRPL" in item for item in edge["limits"])
    sources = {item["id"]: item for item in data["sources"]}
    assert sources["circle_arc_mainnet_launch_sbi_validator"]["source_type"] == "primary_company_announcement"


def test_sbi_arc_presale_amount_is_not_misattributed():
    data = load_artifact()
    edge = {item["id"]: item for item in data["relationship_updates"]}["sbi_circle_arc_token_presale"]
    assert edge["announced_total_consortium_raise_usd"] == 222000000
    assert edge["sbi_specific_amount_usd"] is None
    assert edge["cash_settlement_verified"] is False
    capital = data["capital_flow_reconciliation"]
    assert capital["circle_q3_2026_sec_aggregate_gross_proceeds_usd"] == 242200000
    assert capital["arithmetic_difference_usd"] == 20200000
    assert capital["sbi_specific_purchase_identified"] is False
    assert capital["reconciliation_status"] == "UNRESOLVED_DIFFERENT_DISCLOSURE_WINDOWS_OR_COHORTS"


def test_sbi_multi_rail_conclusion_does_not_infer_xrp_demand_or_direction():
    data = load_artifact()
    conclusion = data["network_conclusion"]
    assert "multi-rail strategy" in conclusion["sbi_multi_rail_strategy"]
    assert "No direct SBI-Coinbase agreement" in conclusion["sbi_coinbase"]
    assert "No direct Circle-Ripple partnership" in conclusion["circle_ripple"]
    assert data["quality_and_limits"]["model_eligible"] is False
    assert data["forecast_status"]["directional_forecast_issued"] is False


def test_new_relationship_sources_have_distinct_independence_groups_and_excerpt_hashes():
    sources = {item["id"]: item for item in load_artifact()["sources"]}
    assert sources["circle_arc_mainnet_launch_sbi_validator"]["independence_group"] == "circle_arc_mainnet_launch"
    assert sources["sbi_arc_token_presale_participation"]["independence_group"] == "sbi_group_primary"
    assert sources["circle_q3_2026_arc_presale_sec_disclosure"]["independence_group"] == "circle_q3_2026_sec_filing"
    assert all(len(item["excerpt_sha256"]) == 64 and item["raw_source_bytes_retained"] is False for item in sources.values())
