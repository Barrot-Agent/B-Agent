from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research/xrp_intelligence/20261108T203213Z-xrp-sec-cftc-digital-commodity-classification.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_joint_release_excerpt_hash_and_source_independence_are_reproducible():
    data = load_artifact()
    receipt = data["source_receipts"][0]
    excerpt = receipt["normalized_excerpt"]
    digest = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
    assert digest == receipt["normalized_excerpt_sha256"]
    assert digest == "882caeb5fe5085b2c4ba60539298d6a57533ac5321486ec0086ca19494130bf8"
    assert len(excerpt.split()) <= 25
    assert receipt["independence_group"] == "sec_cftc_joint_release_20260317"
    assert "not three independent confirmations" in receipt["independence_assessment"]


def test_sec_release_explicitly_lists_xrp_as_a_digital_commodity():
    data = load_artifact()
    doc = data["regulatory_document"]
    row = data["regulatory_interpretation"]
    assert doc["release_numbers"] == ["33-11412", "34-105020"]
    assert doc["effective_date"] == "2026-03-23"
    assert doc["federal_register_document"] == "2026-05635"
    assert row["sec_asset_level_classification"] == "DIGITAL_COMMODITY"
    assert row["explicitly_includes_xrp"] is True
    assert "characteristics, terms and functions" in row["classification_basis"]


def test_asset_level_classification_is_not_misrepresented_as_transaction_exemption():
    row = load_artifact()["regulatory_interpretation"]
    assert row["not_a_judicial_holding"] is True
    assert row["not_a_universal_transaction_exemption"] is True
    assert "investment contract" in row["non_security_asset_transaction_caveat"]
    assert "Howey" in row["non_security_asset_transaction_caveat"]


def test_cftc_guidance_is_kept_distinct_from_sec_xrp_example():
    row = load_artifact()["regulatory_interpretation"]
    assert "certain non-security crypto assets" in row["cftc_scope"]
    assert "not a separate XRP-specific CEA finding" in row["cftc_scope"]


def test_duplicate_access_points_are_not_counted_as_independent_sources():
    receipt = load_artifact()["source_receipts"][0]
    assert len(receipt["source_urls"]) == 3
    assert receipt["independence_group"] == "sec_cftc_joint_release_20260317"
    assert "same joint SEC/CFTC instrument" in receipt["independence_assessment"]


def test_regulatory_event_is_context_only_not_a_directional_price_signal():
    data = load_artifact()
    relevance = data["scenario_relevance"]
    assert relevance["event_timeline_eligible"] is True
    assert relevance["feature_store_admission"] is False
    assert relevance["directional_price_signal"] is False
    assert "out-of-sample" in relevance["model_eligibility_reason"]


def test_no_forecast_or_external_financial_action_is_issued():
    data = load_artifact()
    assert data["forecast"]["status"] == "NOT_ISSUED"
    assert data["forecast"]["directional_probability_issued"] is False
    assert data["external_actions"]["feature_store_write"] is False
    assert data["external_actions"]["paper_trade"] is False
    assert data["external_actions"]["real_money"] is False
    assert data["model_admission"]["eligible"] is False
