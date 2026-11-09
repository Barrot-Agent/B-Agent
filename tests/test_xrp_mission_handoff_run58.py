import json
from pathlib import Path

from barrot_agent.evolution.xrp_public_ingestion import ENDPOINTS, SCHEDULED_ENDPOINTS


ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
INTEGRATION_HEAD = "eeb4950d6cbda6a32870dfe074f671c4ccbc843e"
RESEARCH_HEAD = "674919abe365e915877e7f1f4211df347dfc39a9"
HISTORICAL_MAP = ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map.json"
CURRENT_MAP = ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map_current.json"


def test_run58_handoff_binds_exact_repository_heads_and_ci():
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


def test_run58_endpoint_registry_and_map_counts_match():
    assert len(ENDPOINTS) == 38
    assert len(SCHEDULED_ENDPOINTS) == 36
    assert len({source_id for source_id, _ in ENDPOINTS}) == 38

    historical = json.loads(HISTORICAL_MAP.read_text(encoding="utf-8"))
    archived = historical["current_run_observations"]
    archived_engine = archived["prediction_engine"]
    assert archived["run_id"] == 70
    assert any(item.get("run_id") == 58 for item in historical["prior_run_observations"])
    assert archived_engine["endpoints"] == len(archived_engine["endpoint_ids"]) == 35
    assert archived_engine["scheduled_public_sources"] == len(archived_engine["scheduled_endpoint_ids"]) == 33

    current_data = json.loads(CURRENT_MAP.read_text(encoding="utf-8"))
    current = current_data["current_run_observations"]
    engine = current["prediction_engine"]
    assert current["run_id"] == 81
    assert any(item.get("run_id") == 80 for item in current_data["prior_run_observations"])
    assert engine["endpoints"] == len(ENDPOINTS)
    assert engine["scheduled_public_sources"] == len(SCHEDULED_ENDPOINTS)
    assert engine["endpoint_ids"] == [source_id for source_id, _ in ENDPOINTS]
    assert engine["scheduled_endpoint_ids"] == [source_id for source_id, _ in SCHEDULED_ENDPOINTS]
    assert current_data["prediction_engine"]["endpoints"] == len(ENDPOINTS)
    assert current_data["prediction_engine"]["scheduled_public_sources"] == len(SCHEDULED_ENDPOINTS)


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
