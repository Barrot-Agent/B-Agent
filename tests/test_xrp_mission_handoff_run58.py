import json
from pathlib import Path

from barrot_agent.evolution.xrp_public_ingestion import ENDPOINTS, SCHEDULED_ENDPOINTS, WEEKLY_ENDPOINTS


ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
INTEGRATION_HEAD = "eeb4950d6cbda6a32870dfe074f671c4ccbc843e"
RESEARCH_HEAD = "674919abe365e915877e7f1f4211df347dfc39a9"
HISTORICAL_MAP = ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map.json"
CURRENT_MAP = ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map_current.json"


def test_legacy_handoff_history_and_run112_current_handoff_bind_exact_heads_and_ci():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert handoff.startswith("# Current integrated Barrot handoff — ")
    assert "## Run 60 — current repository, exact-head verification and institutional-rails correction" in handoff[:3_000]
    assert "## Run 58 — current repository, endpoint inventory correction, exact-head verification and merge gate" in handoff[:3_000]
    for value in (MAIN_SHA, INTEGRATION_HEAD, RESEARCH_HEAD):
        assert value in handoff
    assert "1,208 passed, 8 subtests passed" in handoff
    assert "2,472 passed, 8 subtests passed" in handoff
    assert "42494136348" in handoff
    assert "42494136372" in handoff
    assert "42494136346" in handoff
    assert "42494763390" in handoff
    assert "42494763413" in handoff
    assert "42494763434" in handoff
    assert "Forecast status: NOT_ISSUED" in handoff
    assert "No merge was performed" in handoff

    current_handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF_CURRENT.md").read_text(encoding="utf-8")
    assert current_handoff.startswith("# Run 112 —")
    assert "# Run 111 —" in current_handoff
    assert "1,347 passed" in current_handoff
    assert "59.48%" in current_handoff
    assert "Forecast status: NOT_ISSUED" in current_handoff
    assert "42747463986" in current_handoff
    assert "42747463965" in current_handoff
    assert "42747463968" in current_handoff
    assert "42743666268" in current_handoff


def test_current_endpoint_registry_matches_v1_1_map_and_preserves_historical_run58_archive():
    assert len(ENDPOINTS) == 48
    assert len(SCHEDULED_ENDPOINTS) == 43
    assert len(WEEKLY_ENDPOINTS) == 3
    assert len({source_id for source_id, _ in ENDPOINTS}) == 48

    historical = json.loads(HISTORICAL_MAP.read_text(encoding="utf-8"))
    archived = historical["current_run_observations"]
    archived_engine = archived["prediction_engine"]
    assert archived["run_id"] == 70
    assert any(item.get("run_id") == 58 for item in historical["prior_run_observations"])
    assert archived_engine["endpoints"] == len(archived_engine["endpoint_ids"]) == 35
    assert archived_engine["scheduled_public_sources"] == len(archived_engine["scheduled_endpoint_ids"]) == 33

    current_data = json.loads(CURRENT_MAP.read_text(encoding="utf-8"))
    assert current_data["schema_version"] == "1.1.0"
    assert current_data["mission_priority"] == 1
    assert current_data["forecast_status"] == "NOT_ISSUED"
    assert current_data["repository_state"]["main_sha"] == "b4e36c91c380da89e7b60d00f984bd7ac123ce74"
    assert current_data["integration_branch"] == "integration/xrp-v3-unified-main-20261112"
    assert current_data["integration_pr"]["number"] == 1662
    assert current_data["integration_pr"]["draft"] is True
    assert current_data["integration_pr"]["behind_by"] == 0

    engine = current_data["prediction_engine_status"]
    assert engine["source_definitions_total"] == len(ENDPOINTS)
    assert engine["hourly_sources"] == len(SCHEDULED_ENDPOINTS)
    assert engine["weekly_cftc_sources"] == len(WEEKLY_ENDPOINTS)
    assert engine["scheduled_sources"] == len(SCHEDULED_ENDPOINTS) + len(WEEKLY_ENDPOINTS)
    assert engine["excluded_noncommercial_xrpl_node_sources"] == 2
    assert engine["out_of_sample_lift"] is False
    assert engine["forecast_status"] == "NOT_ISSUED"

    ingestion = current_data["workflow_safety_audit"]
    assert ingestion["xrp_public_ingestion_workflow_on_main"] is False
    assert ingestion["xrp_public_ingestion_workflow_on_integration"] is True
    assert ingestion["scheduled_ingestion_main_run_verified"] is False

    assert current_data["primary_brain_declared_by_repository"]["status"] == "DECLARED_NOT_AUTHENTICATED"
    assert current_data["primary_brain_declared_by_repository"]["verified"] is False
    assert current_data["least_privilege_and_safety"]["main_branch_write_performed"] is False
    assert current_data["least_privilege_and_safety"]["pages_deployment_authorized"] is False
    assert current_data["coordination_status"]["no_external_model_data_transfer"] is True
    assert current_data["coordination_status"]["structured_evidence_exchange_across_nine_platforms"] is False
    assert set(current_data["platforms"]) == {"ChatGPT", "Claude", "Grok", "Gemini", "Copilot", "Codex", "Hugging Face", "Kaggle", "Databricks"}
    for name, platform in current_data["platforms"].items():
        if name != "ChatGPT":
            assert platform["data_flow"]["verified"] is False

def test_run58_merge_gate_remains_blocked_without_approvals_or_deployment_authority():
    data = json.loads(HISTORICAL_MAP.read_text(encoding="utf-8"))
    current = data["current_run_observations"]
    assert current["reviews"]["pr_1640"]["approving_reviews"] == 0
    assert current["reviews"]["pr_1643"]["approving_reviews"] == 0
    assert current["reviews"]["pr_1640"]["threads_unresolved"] == 0
    assert current["reviews"]["pr_1643"]["threads_unresolved"] == 0
    assert current["merge_state"]["branch_protection_status"] == "UNVERIFIED_HTTP_403"
    assert current["merge_state"]["pages_deployment_authorized"] is False
    assert current["merge_state"]["merge_performed"] is False
    assert current["external_actions"]["main_write"] is False
    assert current["external_actions"]["deployment"] is False
    assert current["forecast_status"] == "NOT_ISSUED"
