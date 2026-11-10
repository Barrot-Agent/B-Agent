"""Regression checks for XRPL public-node operator relationships and usage limits."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T125743Z-xrpl-public-node-operator-funding-and-usage-terms.json"


def test_honeycluster_ripple_funding_is_first_party_and_not_ownership_evidence():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    edge = next(
        item for item in data["relationship_edges"]
        if item["from"] == "Ripple" and item["to"] == "Honeycluster"
    )
    assert edge["event_date"] == "2024-06"
    assert edge["amount"] is None
    assert edge["ownership_or_control_established"] is False
    assert edge["continuing_support_established"] is False


def test_public_xrpl_nodes_are_not_counted_as_independent_economic_sources():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    independence = data["source_independence"]
    assert independence["operator_count"] == 2
    assert independence["registered_operators"] == ["InFTF", "Honeycluster"]
    assert independence["economic_source_groups_contributed"] == 0
    assert independence["shared_feature_independence_group"] == "xrpl_public_ledger"
    assert "independent XRP demand" in independence["not_evidence_of"]


def test_honeycluster_terms_and_relative_page_vintage_are_not_overstated():
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    terms = data["provider_terms_access"]
    assert terms["press_site_terms_link"]["retrieval_status"] == "404_not_found"
    assert terms["canonical_terms_page"]["retrieval_status"] == "accessible"
    assert terms["canonical_terms_page"]["last_updated"] == "2026-09-24"
    assert terms["explicit_public_endpoint_business_use_authorization_established"] is False
    assert terms["plan_agreement_obtained"] is False
    observations = data["page_last_updated_observations"]
    assert {item["observed_label"] for item in observations} == {
        "Last updated three days ago",
        "Last updated one week ago",
    }
    assert data["model_eligibility"]["eligible"] is False
