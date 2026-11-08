import json
from pathlib import Path

from barrot_agent.evolution.xrp_public_ingestion import ENDPOINTS, SCHEDULED_ENDPOINTS


ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
INTEGRATION_HEAD = "eeb4950d6cbda6a32870dfe074f671c4ccbc843e"
RESEARCH_HEAD = "674919abe365e915877e7f1f4211df347dfc39a9"


def test_run58_handoff_binds_exact_repository_heads_and_ci():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert handoff.startswith("# Current integrated Barrot handoff — 2026-11-08T16:03:05Z")
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
    assert len(ENDPOINTS) == 35
    assert len(SCHEDULED_ENDPOINTS) == 33
    assert len({source_id for source_id, _ in ENDPOINTS}) == 35
    data = json.loads(
        (ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    current = data["current_run_observations"]
    engine = current["prediction_engine"]
    assert current["run_id"] == 58
    assert engine["endpoints"] == len(ENDPOINTS)
    assert engine["scheduled_public_sources"] == len(SCHEDULED_ENDPOINTS)
    assert engine["endpoint_ids"] == [source_id for source_id, _ in ENDPOINTS]
    assert engine["scheduled_endpoint_ids"] == [source_id for source_id, _ in SCHEDULED_ENDPOINTS]
    assert data["prediction_engine"]["endpoints"] == len(ENDPOINTS)
    assert data["prediction_engine"]["scheduled_public_sources"] == len(SCHEDULED_ENDPOINTS)


def test_run58_merge_gate_remains_blocked_without_approvals_or_deployment_authority():
    data = json.loads(
        (ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
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
