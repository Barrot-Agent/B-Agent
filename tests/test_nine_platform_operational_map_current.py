from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "research" / "operations" / "nine_platform_operational_map_current.json"
EXPECTED_PLATFORMS = {
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


def load_map() -> dict:
    return json.loads(MAP.read_text(encoding="utf-8"))


def test_current_operational_map_has_exact_nine_platform_scope_and_main_sha_format() -> None:
    data = load_map()
    assert data["schema_version"] == "barrot.nine-platform-operational-map.v1"
    assert data["repository"]["full_name"] == "Barrot-Agent/B-Agent"
    assert re.fullmatch(r"[0-9a-f]{40}", data["repository"]["main_sha"])
    assert set(data["platforms"]) == EXPECTED_PLATFORMS


def test_chatgpt_connector_scope_is_verified_without_overstating_permissions() -> None:
    data = load_map()
    chatgpt = data["platforms"]["ChatGPT"]

    assert chatgpt["authentication"]["status"] == "VERIFIED_FOR_GITHUB_CONNECTOR"
    evidence = chatgpt["authentication"]["evidence"]
    assert all(
        fragment in evidence
        for fragment in (
            "main metadata/tree",
            "open PRs",
            "workflow runs/jobs/logs",
            "file reads",
        )
    )
    observed_actions = chatgpt["permissions"]["observed_actions"]
    assert any(
        "Write existing" in action
        and "integration/mission-handoff-refresh-20261125" in action
        for action in observed_actions
    )
    assert "Merge to main" in chatgpt["permissions"]["not_used"]
    assert "Deploy" in chatgpt["permissions"]["not_used"]
    assert chatgpt["data_flow"]["verified"] is True
    assert chatgpt["data_flow"]["status"] == "LIVE_TESTED"
    assert chatgpt["data_flow"]["external_transfer_occurred"] is False

    repository = data["repository"]
    assert repository["main_branch_protected"] is True
    assert repository["required_approval_count"] is None
    assert "HTTP_403" in repository["branch_protection_details_status"]
    protection = repository["branch_protection_summary"]
    assert protection["branch_protected"] is True
    assert protection["protection_enabled"] is True
    assert protection["required_status_checks_enforcement_level"] == "non_admins"
    assert protection["detailed_endpoint_status"].startswith("HTTP_403")
    assert "required approving review count" in protection["not_verified"]
    assert set(repository["required_status_checks"]) == {
        "Full repository test suite",
        "audit",
        "pip-audit",
        "Verify PR merge tree against current base",
    }


def test_unverified_platforms_remain_unknown_and_no_cross_platform_transfer_is_claimed() -> None:
    data = load_map()
    for name, platform in data["platforms"].items():
        if name == "ChatGPT":
            continue
        assert platform["authentication_status"] == "NOT_TESTED_THIS_SESSION"
        assert platform["permission_scope"] == "UNKNOWN"
        assert platform["data_flow"]["verified"] is False
        assert platform["data_flow"]["external_transfer_occurred"] is False
        assert platform["task_assignment_status"] == "DESIGNED_NOT_EXECUTED"
        assert platform["capabilities"]["status"] == "NOT_TESTED"
        assert platform["authentication"]["status"] == "NOT_TESTED"
        assert platform["permissions"]["status"] == "UNKNOWN_NOT_TESTED"

    coordination = data["coordination"]
    assert coordination["status"] == "DESIGNED_NOT_EXECUTED"
    assert coordination["structured_evidence_exchange_across_nine_platforms"] is False
    assert coordination["external_model_data_transfer_occurred"] is False


def test_three_missions_remain_coequal_active_and_round_robin() -> None:
    portfolio = load_map()["mission_portfolio"]
    assert portfolio["scheduling_policy"] == "durable_round_robin_v1"
    assert {item["mission_id"] for item in portfolio["missions"]} == {
        "xrp_intelligence_prediction_engine",
        "professional_audio_production",
        "long_horizon_continuity_capability_development",
    }
    assert all(item["priority"] == 1 and item["status"] == "active" for item in portfolio["missions"])


def test_current_pr_inventory_includes_integration_and_dependency_workstreams():
    data = load_map()
    repository = data["repository"]
    expected = set(range(1702, 1712))

    assert repository["current_main_state"]["open_pull_request_count"] == len(expected)
    assert set(repository["current_main_state"]["open_pull_request_numbers"]) == expected
    assert {item["number"] for item in repository["current_open_pull_requests"]} == expected
    assert {item["number"] for item in data["current_prs"]} == {1702, 1703, 1704, 1705}
    assert {item["number"] for item in data["dependency_prs"]} == {1706, 1707, 1708, 1709, 1710, 1711}
    assert next(item for item in data["dependency_prs"] if item["number"] == 1708)["classification"] == "superseded_pending_successor_merge"
    assert next(item for item in data["dependency_prs"] if item["number"] == 1711)["classification"] == "blocked_dependency_compatibility"
    assert repository["security_posture"]["alert_counts"] == "UNKNOWN_NOT_ZERO"
    latest_observation = data["latest_xrp_ingestion_observation"]
    latest_ingestion = repository["current_main_state"]["latest_xrp_ingestion_run"]
    assert latest_observation["run_number"] == latest_ingestion["run_number"]
    assert latest_observation["run_id"] == latest_ingestion["run_id"]
    assert latest_observation["evaluation"]["forecast_status"] == "NOT_ISSUED"
