import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "research" / "xrp_intelligence" / "20261105T063600Z-nine-platform-capability-authentication-map.json"


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_map_contains_exactly_the_nine_requested_platforms_once():
    data = load()
    names = [item["name"] for item in data["platforms"]]
    assert data["platform_count"] == 9
    assert len(names) == 9
    assert len(set(names)) == 9
    assert set(names) == {
        "ChatGPT", "Claude", "Grok", "Gemini", "Copilot",
        "Codex", "Hugging Face", "Kaggle", "Databricks",
    }


def test_only_chatgpt_is_counted_as_a_verified_live_platform():
    data = load()
    assert data["verified_live_platform_count"] == 1
    assert data["verified_live_platforms"] == ["ChatGPT current session"]
    assert data["verified_connector_paths"] == ["ChatGPT -> GitHub repository connector"]
    statuses = {item["name"]: item["connection_status"] for item in data["platforms"]}
    assert statuses["ChatGPT"] == "VERIFIED_CURRENT_SESSION"
    assert statuses["Copilot"] == "OBSERVED_REVIEW_EVENTS_ONLY_NOT_A_PERSISTENT_CONNECTION"
    for name in {"Claude", "Grok", "Gemini", "Codex", "Hugging Face", "Kaggle", "Databricks"}:
        assert statuses[name] == "NOT_VERIFIED_CONNECTED"


def test_copilot_review_events_are_not_mislabeled_as_authenticated_coordination():
    data = load()
    copilot = next(item for item in data["platforms"] if item["name"] == "Copilot")
    assert "not a persistent" in copilot["connection_status"].lower()
    assert "No ChatGPT-to-Copilot data exchange was verified." in copilot["data_flow"]


def test_evidence_packet_and_red_team_protocol_preserve_disagreement():
    data = load()
    required = {
        "task_id", "claim_id", "source_id", "source_url", "published_at",
        "retrieved_at_utc", "data_cutoff_utc", "counterevidence",
        "raw_content_sha256", "independence_group", "agent_authentication_state",
        "repository_commit_sha",
    }
    assert required <= set(data["structured_evidence_packet_schema"])
    assert "Preserve minority objections" in data["coordination_protocol"]["disagreement_resolution"]
    assert "attempts to falsify" in data["coordination_protocol"]["red_team"]


def test_least_privilege_and_external_action_boundaries_are_explicit():
    data = load()
    assert "no main write" in data["least_privilege_policy"]["coding_agents"]
    assert "no exchange/broker credentials" in data["least_privilege_policy"]["market_access"]
    assert data["safety"]["public_and_authorized_data_only"] is True
    assert data["safety"]["no_private_data"] is True
    assert data["safety"]["no_unapproved_external_mutation"] is True
    assert "No Kaggle submission" in " ".join(data["execution_status"]["not_executed"])


def test_previous_draft_map_is_preserved_as_lineage_not_overwritten():
    data = load()
    lineage = data["source_lineage"]
    assert lineage["prior_draft_pr"] == 1597
    assert lineage["prior_artifact_path"] == "research/xrp_intelligence/20261103-nine-platform-capability-authentication-map.json"
    assert lineage["prior_draft_head"] == "f61485585474dee0164ddc4c46e3a03dc953724f"
    assert "older draft artifact remains preserved" in lineage["update_rule"]
