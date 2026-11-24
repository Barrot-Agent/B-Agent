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


def test_chatgpt_connector_scope_is_verified_without_inflating_admin_access() -> None:
    data = load_map()
    chatgpt = data["platforms"]["ChatGPT"]
    assert chatgpt["authentication_status"] == "VERIFIED_CURRENT_SESSION"
    assert chatgpt["authenticated_principal"] == "Barrot-Agent"
    assert chatgpt["permissions"]["repository_contents_read"] is True
    assert chatgpt["permissions"]["repository_contents_write_on_existing_pr_branches"] is True
    assert chatgpt["permissions"]["administration_read"] is False
    assert chatgpt["permissions"]["branch_protection_details_read"] is False
    assert chatgpt["permissions"]["independent_approval_of_own_pr"] is False
    assert chatgpt["verified_data_flow"]["status"] == "VERIFIED"
    assert chatgpt["verified_data_flow"]["external_model_data_transfer"] is False
    assert data["repository"]["main_branch_protected"] is True
    assert data["repository"]["required_approval_count"] is None
    assert "HTTP_403" in data["repository"]["branch_protection_details_status"]
    protection = data["repository"]["branch_protection_summary"]
    assert protection["branch_protected"] is True
    assert protection["protection_enabled"] is True
    assert protection["required_status_checks_enforcement_level"] == "non_admins"
    assert protection["detailed_endpoint_status"].startswith("HTTP_403")
    assert "required approving review count" in protection["not_verified"]
    assert set(data["repository"]["required_status_checks"]) == {
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
