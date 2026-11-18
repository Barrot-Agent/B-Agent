"""Validate the latest nine-platform capability/authentication map."""
import json
from pathlib import Path

MAP_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "nine_platform_capability_authentication_dataflow_map_latest.json"
)


def load_map():
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def test_latest_map_covers_nine_platforms_without_fabricated_connections():
    data = load_map()
    expected = {
        "ChatGPT", "Claude", "Grok", "Gemini", "Copilot",
        "Codex", "Hugging Face", "Kaggle", "Databricks",
    }
    assert set(data["platforms"]) == expected
    chatgpt = data["platforms"]["ChatGPT"]
    assert chatgpt["authentication_status"] == "verified"
    assert chatgpt["data_flow"]["status"] == "verified"
    assert chatgpt["data_flow"]["path"] == (
        "ChatGPT session -> GitHub connector -> Barrot-Agent/B-Agent"
    )
    assert set(chatgpt["permissions"]) == {
        "admin", "maintain", "push", "pull", "triage"
    }
    for name in expected - {"ChatGPT"}:
        platform = data["platforms"][name]
        assert platform["authentication_status"] == "unverified"
        assert platform["data_flow"] == "not_verified"
        assert platform["permissions"] == []
    assert data["coordination"]["external_dispatch_performed"] is False
    assert data["coordination"]["external_data_transfer_performed"] is False


def test_latest_map_matches_repository_and_forecast_admission_state():
    data = load_map()
    repo = data["repository_state"]
    assert repo["main_sha"] == "e204c21100f3d059e2ba633d041fe8927b61ccaf"
    integration = repo["integration"]
    assert integration["pr_number"] == 1663
    assert integration["draft"] is True
    assert integration["ahead_by"] == 274
    assert integration["behind_by"] == 0
    registry = data["prediction_engine"]["source_registry"]
    assert registry == {
        "public_endpoint_records": 53,
        "hourly_sources": 48,
        "weekly_sources": 3,
        "noncommercial_nodes_excluded": 2,
        "scheduled_sources": 51,
    }
    ingestion = data["prediction_engine"]["latest_ingestion"]
    assert ingestion["run_id"] == 44267762749
    assert ingestion["receipt_count"] == 34
    assert ingestion["source_failures"] == 21
    assert ingestion["walk_forward_forecasts"] == 0
    assert ingestion["forecast_issuance"] == "disabled"
    assert ingestion["external_anchor"] == "NOT_ANCHORED"


def test_latest_map_preserves_security_gates_and_open_pr_classifications():
    data = load_map()
    security = data["security_and_governance"]
    assert security["main_branch_protected"] is True
    assert security["fallback_ruleset"]["enforcement"] == "disabled"
    assert security["pr_1663"]["draft"] is True
    assert security["pr_1663"]["formal_reviews"] == 0
    assert security["transitive_script_security_review"] == "incomplete"
    assert security["sensitive_branch_path"]["content_read"] is False
    assert len(data["open_pr_backlog"]) == 10
    pr = next(item for item in data["open_pr_backlog"] if item["number"] == 1663)
    assert pr["classification"] == "blocked"
    assert data["merge_decision"] == "NO_MERGE"
