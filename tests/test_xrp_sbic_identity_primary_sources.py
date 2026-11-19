"""Primary-source regression tests for Japanese SBIC identity and ChatGPT references."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research/xrp_intelligence/20261110T151935Z-sbic-east-central-west-primary-identity-reconciliation.json"


def _load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_statute_names_three_distinct_sbic_companies():
    data = _load()
    entities = {item["id"]: item for item in data["entities"]}
    assert set(("SBIC_EAST", "SBIC_CENTRAL", "SBIC_WEST")).issubset(entities)
    assert entities["SBIC_EAST"]["legal_name"].startswith("Tokyo ")
    assert entities["SBIC_CENTRAL"]["legal_name"].startswith("Nagoya ")
    assert entities["SBIC_WEST"]["legal_name"].startswith("Osaka ")
    assert data["legal_identity"]["act_number"] == "Act No. 101 of 1963"


def test_sbi_holdings_is_not_an_sbic_regional_alias():
    data = _load()
    entities = {item["id"]: item for item in data["entities"]}
    assert entities["SBI_HOLDINGS"]["established"] == "1999-07-08"
    assert entities["SBI_HOLDINGS"]["legal_name"] == "SBI Holdings, Inc."
    assert entities["SBIC_EAST"]["legal_name"] != entities["SBI_HOLDINGS"]["legal_name"]
    assert entities["SBIC_CENTRAL"]["legal_name"] != entities["SBI_HOLDINGS"]["legal_name"]
    assert entities["SBIC_WEST"]["legal_name"] != entities["SBI_HOLDINGS"]["legal_name"]


def test_chatgpt_reference_is_training_not_partnership():
    data = _load()
    phrase = data["exact_phrase_research"]["SBIC, ChatGPT SBIC"]
    assert phrase["exact_entity_or_partnership_found"] is False
    assert phrase["model_eligible"] is False
    assert data["relationship_edges"][-2]["status"] == "CONFIRMED_EDUCATIONAL_USE_ONLY"
    assert data["claims"][2]["classification"] == "CONFIRMED"
    assert data["claims"][4]["classification"] == "NOT_ESTABLISHED"


def test_nagoya_ai_salon_is_limited_to_investee_companies():
    receipt = next(x for x in _load()["source_receipts"] if x["source_id"] == "sbic_nagoya_salon")
    assert "investee-company-only" in receipt["normalized_excerpt"].casefold()
    assert "no named chatgpt or openai partnership" in receipt["normalized_excerpt"].casefold()


def test_raw_capture_and_normalized_hash_scope_are_not_conflated():
    for receipt in _load()["source_receipts"]:
        assert receipt["raw_bytes_captured"] is False
        assert receipt["raw_byte_sha256"] is None
        assert receipt["hash_scope"] == "normalized excerpt only; not the raw HTTP response"
        digest = hashlib.sha256(receipt["normalized_excerpt"].encode("utf-8")).hexdigest()
        assert digest == receipt["normalized_excerpt_sha256"]


def test_sbic_research_is_excluded_from_xrp_prediction_features():
    data = _load()
    assert data["xrp_admission"]["status"] == "EXCLUDED_NO_DIRECT_XRP_RELATIONSHIP_ESTABLISHED"
    assert data["xrp_admission"]["forecast_eligible"] is False
