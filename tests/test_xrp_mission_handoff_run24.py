import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_run24_handoff_records_current_exact_heads_and_gates():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert "# Run 24" in handoff
    assert "97ec00d2fc8b684a5827e6016e5166680822ecaa" in handoff
    assert "db874a327399bb431e4a70265cf9627a864ef5c8" in handoff
    assert "1,119 passed, 8 subtests passed" in handoff
    assert "1,885 passed, 8 subtests passed" in handoff


def test_run24_handoff_preserves_pillars_health_failure_and_merge_blockers():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert "42375034124" in handoff
    assert "HTTP 403" in handoff
    assert "BUILD_ERROR" in handoff
    assert "zero approving reviews" in handoff.lower()
    assert "No merge was performed" in handoff


def test_run24_handoff_contains_primary_sbic_identity_resolution():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert "SBIC East Japan" in handoff
    assert "SBIC Central Japan" in handoff
    assert "SBIC West Japan" in handoff
    assert "Act No. 101" in handoff
    assert "SBI Holdings, Inc." in handoff


def test_run24_platform_map_is_current_and_fail_closed():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    current = data["current_run_observations"]
    assert current["run_id"] == 24
    assert current["main_sha"] == "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
    assert current["research_head"] == "db874a327399bb431e4a70265cf9627a864ef5c8"
    assert current["mission_ci"]["pr_1643"]["full_suite"].startswith("1,885 passed")
    assert current["merge_state"]["merge_performed"] is False
    assert current["prediction_engine"]["directional_forecast_status"] == "NOT_ISSUED"
