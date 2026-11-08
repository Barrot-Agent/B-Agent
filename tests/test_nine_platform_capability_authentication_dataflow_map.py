from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map.json"


def load_map() -> dict:
    return json.loads(MAP.read_text(encoding="utf-8"))


def test_map_contains_exactly_the_nine_requested_platforms():
    data = load_map()
    expected = {"ChatGPT", "Claude", "Grok", "Gemini", "Copilot", "Codex", "Hugging Face", "Kaggle", "Databricks"}
    assert set(data["platforms"]) == expected


def test_unverified_platforms_are_never_marked_as_live():
    data = load_map()
    for name, platform in data["platforms"].items():
        if name == "ChatGPT":
            assert platform["authentication_status"] == "VERIFIED_CURRENT_SESSION"
            assert platform["data_flow"]["verified"] is True
        else:
            assert platform["data_flow"]["verified"] is False
    assert data["coordination_status"]["verified_external_platforms_beyond_current_chatgpt_github_connector"] == 0
    assert data["coordination_status"]["independent_tasks_assigned_across_nine_platforms"] is False
    assert data["coordination_status"]["structured_evidence_exchange_across_nine_platforms"] is False


def test_copilot_review_comments_are_not_approvals_or_persistent_auth():
    copilot = load_map()["platforms"]["Copilot"]
    assert copilot["authentication_status"] == "ONE_OFF_GITHUB_REVIEW_ACTIVITY_ONLY"
    assert "COMMENTED is not APPROVED" in copilot["limitations"][0]
    assert copilot["data_flow"]["persistent_connection"] is False


def test_huggingface_and_databricks_failures_are_not_mislabeled_as_verified():
    data = load_map()["platforms"]
    assert data["Hugging Face"]["authentication_status"] == "INCONCLUSIVE_FAILED_HEALTH_CHECK"
    assert data["Hugging Face"]["data_flow"]["verified"] is False
    assert data["Databricks"]["authentication_status"] == "AUTHORIZATION_FAILED_HTTP_403"
    assert data["Databricks"]["data_flow"]["verified"] is False
    assert data["Databricks"]["data_flow"]["write_performed"] is False


def test_kaggle_is_not_connected_or_submitted_and_groq_is_out_of_scope():
    data = load_map()
    assert data["platforms"]["Kaggle"]["authentication_status"] == "NOT_TESTED"
    assert data["platforms"]["Kaggle"]["data_flow"]["submission_performed"] is False
    assert "Groq" in data["out_of_scope_provider_notes"]
    assert "not Grok" in data["out_of_scope_provider_notes"]["Groq"]["distinction"]


def test_no_credentials_or_external_actions_were_exposed_or_performed():
    safety = load_map()["least_privilege_and_safety"]
    assert safety["secret_values_read"] is False
    assert safety["credentials_exported"] is False
    assert safety["deployment"] is False
    assert safety["kaggle_submission"] is False
    assert safety["paper_trade"] is False
    assert safety["real_money_action"] is False
