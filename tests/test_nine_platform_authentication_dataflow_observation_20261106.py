from __future__ import annotations

import hashlib
import json
from pathlib import Path

ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T152303Z-nine-platform-authentication-dataflow-observation.json"
)


def load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exact_nine_platforms_are_present_once():
    data = load_artifact()
    names = [x["name"] for x in data["platforms"]]
    assert data["platform_count"] == 9
    assert len(names) == 9
    assert set(names) == {"ChatGPT", "Claude", "Grok", "Gemini", "Copilot", "Codex", "Hugging Face", "Kaggle", "Databricks"}


def test_only_chatgpt_github_path_is_verified_live():
    data = load_artifact()
    assert data["verified_live_platform_count"] == 1
    assert data["verified_live_platforms"] == ["ChatGPT current session"]
    assert data["verified_connector_paths"] == ["ChatGPT -> GitHub repository connector"]
    assert data["no_nine_platform_live_coordination_claimed"] is True


def test_copilot_one_off_review_is_not_persistent_and_is_write_capable():
    data = load_artifact()
    row = next(x for x in data["platforms"] if x["name"] == "Copilot")
    assert row["connection_status"] == "OBSERVED_ONE_OFF_GITHUB_HOSTED_REVIEW_NOT_PERSISTENT"
    assert "test-only branch commit" in row["data_flow"]
    assert "write-capable" in row["data_flow"]
    assert "not a persistent connector" in row["data_flow"]


def test_other_platforms_are_not_misrepresented_as_authenticated():
    data = load_artifact()
    for name in ("Claude", "Grok", "Gemini", "Codex", "Hugging Face", "Kaggle", "Databricks"):
        row = next(x for x in data["platforms"] if x["name"] == name)
        assert row["connection_status"] == "NOT_VERIFIED_CONNECTED"
        if name == "Codex":
            assert "No Codex session or execution connection verified" in row["authentication_status"]
            assert "GitHub connector is separate" in row["authentication_status"]
        else:
            assert "No authenticated" in row["authentication_status"]


def test_user_account_read_permission_and_codeowners_are_preserved():
    data = load_artifact()
    user = next(x for x in data["source_registry"] if x["source_id"] == "github_user_permission")
    owners = next(x for x in data["source_registry"] if x["source_id"] == "github_codeowners")
    assert "permission for Scribedpengenius is read" in user["normalized_excerpt"]
    assert "@Barrot-Agent" in owners["normalized_excerpt"]


def test_no_secrets_or_external_writes_were_used():
    data = load_artifact()
    assert data["no_secret_values_read"] is True
    assert data["github_existing_pr_branch_writes_executed"] is True
    assert data["no_non_github_external_platform_write_executed"] is True
    assert data["no_data_sent_to_external_ai_providers"] is True
    assert data["least_privilege_policy"]["secrets_access_authorized"] is False
    assert data["least_privilege_policy"]["deployments_authorized"] is False


def test_all_normalized_evidence_hashes_match():
    for source in load_artifact()["source_registry"]:
        assert hashlib.sha256(source["normalized_excerpt"].encode("utf-8")).hexdigest() == source["normalized_excerpt_sha256"]


def test_review_comments_are_not_approvals_or_cross_platform_attestation():
    data = load_artifact()
    assert "not independent nine-platform authentication or approval" in data["red_team_status"]
    assert data["verified_live_platform_count"] == 1
