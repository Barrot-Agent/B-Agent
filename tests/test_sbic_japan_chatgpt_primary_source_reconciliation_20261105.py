import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T173711Z-sbic-japan-chatgpt-primary-source-reconciliation.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_sbic_west_chatgpt_seminar_is_primary_source_and_not_a_partnership():
    data = load()
    west = data["source_registry"][0]["content"]
    assert west["explicit_chatgpt_reference"] is True
    assert west["event_title"] == "Generative AI introductory seminar for accounting firms and support organizations"
    assert west["lecturer"] == "Taichi Kakinuma, representative partner attorney, STORIA Law Firm"
    assert west["published_event_date"] == "2024-10-23" if "published_event_date" in west else True
    assert "does not describe an OpenAI partnership" in data["source_registry"][0]["interpretation"]


def test_sbic_east_training_explicitly_covers_chatgpt_and_copilot_for_investees():
    east = load()["source_registry"][1]["content"]
    assert east["explicit_chatgpt_reference"] is True
    assert "ChatGPT usage" in east["day_one"]
    assert "Microsoft Copilot" in east["day_two"]
    assert east["eligibility"] == "investee companies only; general companies not eligible"


def test_sbic_central_non_discovery_is_not_misrepresented_as_absence():
    central = load()["source_registry"][2]
    assert central["finding_status"] == "no explicit ChatGPT-branded event located in this search"
    assert "not proof" in central["interpretation_limit"]


def test_regional_sbic_entities_are_distinct_from_sbi_holdings():
    data = load()
    assert data["entity_resolution"]["sbic_east"] != data["entity_resolution"]["sbic_central"]
    assert data["entity_resolution"]["sbic_central"] != data["entity_resolution"]["sbic_west"]
    assert "not SBI Holdings" in data["entity_resolution"]["distinction"]
    assert data["exact_phrase_resolution"]["not_established"].count("Direct OpenAI partnership") == 1


def test_rendered_research_remains_model_ineligible_without_raw_receipts():
    data = load()
    assert data["source_capture_policy"]["raw_source_sha256_receipts"] is None
    assert data["source_capture_policy"]["model_eligible"] is False
