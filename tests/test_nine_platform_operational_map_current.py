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
            "current main metadata and complete recursive tree",
            "all ten current open PRs and shared diffs",
            "exact-head CI/security/gate checks",
            "workflow logs and artifact manifests",
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
    detailed_status = protection["detailed_endpoint_status"]
    assert detailed_status.startswith("HTTP 403 ")
    assert "RESOURCE_NOT_ACCESSIBLE_BY_INTEGRATION" in detailed_status
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
    expected = {1702, 1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711}

    assert repository["current_main_state"]["open_pull_request_count"] == len(expected)
    assert set(repository["current_main_state"]["open_pull_request_numbers"]) == expected
    assert {item["number"] for item in repository["current_open_pull_requests"]} == expected
    assert {item["number"] for item in data["current_prs"]} == {1702, 1703, 1704, 1705}
    dependency_expected = {1706, 1707, 1708, 1709, 1710, 1711}
    assert {item["number"] for item in data["dependency_prs"]} == dependency_expected
    assert next(item for item in data["dependency_prs"] if item["number"] == 1711)["classification"] == "blocked_dependency_compatibility"
    assert next(item for item in data["dependency_prs"] if item["number"] == 1708)["classification"] == "duplicate_subset_of_1706"
    assert {item["number"] for item in data["supporting_prs"]} == set()
    assert any(item["number"] == 1712 for item in repository["merged_pull_requests"])
    assert {item["number"] for item in data["repair_prs"]} == {1713, 1714}
    source = next(item for item in data["repair_prs"] if item["number"] == 1713)
    successor = next(item for item in data["repair_prs"] if item["number"] == 1714)
    assert source["draft"] is True
    assert source["successor_pr"] == 1714
    assert source["state"] == "closed" and source["merged"] is False
    assert source["classification"].startswith("superseded_source_preserved_as_draft")
    assert "Telegram additions intentionally excluded from #1714" in source["classification"]
    assert successor["draft"] is False
    assert successor["state"] == "closed" and successor["merged"] is True
    assert successor["merge_commit_sha"] == repository["main_sha"]
    assert successor["classification"].startswith("active_clean_v3_governance_successor")
    assert successor["checks"]["full_suite"]["conclusion"] == "success"
    assert successor["checks"]["gated_merge"]["conclusion"] == "success"
    assert next(item for item in repository["merged_pull_requests"] if item["number"] == 1712)["classification"] == "merged"

    assert repository["security_posture"]["alert_counts"] == "UNKNOWN_NOT_ZERO"
    latest_observation = data["latest_xrp_ingestion_observation"]
    latest_ingestion = repository["latest_xrp_ingestion"]
    assert latest_observation["run_number"] == latest_ingestion["run_number"]
    assert latest_observation["run_id"] == latest_ingestion["run_id"]
    assert latest_observation["run_number"] > 0
    assert latest_observation["event_timeline"]["verified_receipt_links"] == 0
    assert latest_observation["evaluation"]["forecast_status"] == "NOT_ISSUED"
    validation = data["latest_integration_validation"]
    assert validation["pr_number"] == 1702
    assert re.fullmatch(r"[0-9a-f]{40}", validation["tested_head_sha"])
    suite = validation["full_suite"]
    assert suite["conclusion"] in {"success", "failure"}
    assert suite["passed"] > 0 and suite["failed"] >= 0
    if suite["conclusion"] == "success":
        assert suite["failed"] == 0
    else:
        assert suite["failed"] > 0

    assert latest_observation["evaluation"]["forecast_status"] == "NOT_ISSUED"


def test_latest_reconciliation_captures_xrp_audio_continuity_and_sellbird_evidence():
    data = load_map()
    xrp = data["latest_xrp_ingestion_observation"]
    assert xrp["run_number"] == 222
    assert xrp["forecast_status"] == "NOT_ISSUED"
    assert xrp["event_timeline"]["events"] == 150
    assert xrp["event_timeline"]["verified_receipt_links"] == 0
    assert xrp["evaluation"]["walk_forward_rows"] == 632
    assert xrp["evaluation"]["horizons"] == ["1h"]

    audio = data["latest_audio_full_song_qc"]
    assert audio["aligned_stems"] == 9
    assert audio["native_daw_project_available"] is False
    assert audio["human_listening"] == "NOT_PERFORMED"
    assert audio["user_acceptance"] == "NOT_VERIFIED"
    assert audio["mix"]["clip_samples"] == 0

    continuity = data["latest_continuity_validation_run11"]
    assert continuity["local_state_ledger"] == "IMPLEMENTED_AND_TESTED"
    assert continuity["authenticated_cross_host_sync"] == "NOT_IMPLEMENTED"

    sellbird = data["latest_sellbird_audit_run11"]
    assert sellbird["license"] == "AGPL-3.0-only"
    assert sellbird["status"] == "SOURCE_AUDIT_EXECUTED_NOT_INSTALLED"
    assert sellbird["outbound_sending"] == "PAUSED"
    assert data["commercial_readiness_run66_4"]["verified_prospects"] == 0

    alignment = data["latest_mission_prompt_alignment"]
    assert alignment["manifest_status"] == "THREE_COEQUAL_ACTIVE_PRIORITY_1_MISSIONS_ON_MAIN"
    assert alignment["status"] == "MANIFEST_AND_SCHEDULER_VERIFIED; RUNTIME_PROMPT_FIX_BRANCH_ONLY_NOT_MERGED"
