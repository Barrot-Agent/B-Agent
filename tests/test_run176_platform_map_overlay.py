import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "nine_platform_capability_authentication_dataflow_map_run176.json"
)


def load_map():
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def test_run176_map_contains_exact_nine_platforms():
    data = load_map()
    assert data["schema_version"] == "barrot.nine-platform-capability-map.overlay.v1"
    assert data["mission_priority"] == 1
    assert data["foundation"] == "Barrot V3"
    assert {item["name"] for item in data["platforms"]} == {
        "ChatGPT",
        "Claude",
        "Grok",
        "Gemini",
        "Copilot",
        "Codex",
        "Hugging Face",
        "Kaggle",
        "Databricks",
    }


def test_only_the_chatgpt_github_connector_is_claimed_verified():
    data = load_map()
    verified = {
        item["name"]
        for item in data["platforms"]
        if item["authentication"] == "verified"
    }
    assert verified == {"ChatGPT"}


def test_grok_is_not_conflated_with_groq_or_opencode():
    data = load_map()
    grok = next(item for item in data["platforms"] if item["name"] == "Grok")
    assert grok["authentication"] == "unverified"
    assert "Groq" in grok["note"]
    separate = {item["name"]: item for item in data["separate_integrations"]}
    assert separate["OpenCode GitHub MCP"]["authentication"] == "unverified"
    assert separate["Groq API"]["status"] == "not_a_Grok_connection"


def test_no_unverified_external_platform_dispatch_is_claimed():
    data = load_map()
    assert data["coordination"]["independent_external_tasks_dispatched"] == 0
    assert data["coordination"]["structured_cross_platform_evidence_exchange"] is False
    assert data["coordination"]["independent_red_team_quorum"] is False


def test_least_privilege_and_branch_protection_gaps_remain_explicit():
    data = load_map()
    assert data["principles"]["least_privilege"] == "required_not_met"
    assert data["security"]["branch_protection_read"] == "HTTP_403"
    assert data["security"]["visible_fallback_ruleset_enforcement"] == "disabled"
