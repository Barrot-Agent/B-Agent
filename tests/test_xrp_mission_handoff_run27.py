import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
INTEGRATION_HEAD = "9630d6fa68b6c0660582c8d239480c757ad983ff"
RESEARCH_HEAD = "b80298b19d90cc5a2fdf11849ee5c045142df33b"


def test_run27_handoff_is_latest_and_preserves_verified_heads():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert handoff.startswith("# Run 27 — 2026-11-07T17:24:52Z")
    for value in (MAIN_SHA, INTEGRATION_HEAD, RESEARCH_HEAD):
        assert value in handoff
    assert "1,138 passed, 8 subtests passed" in handoff
    assert "2,006 passed, 8 subtests passed" in handoff
    assert "Forecast status: NOT_ISSUED" in handoff
    assert "No merge performed" in handoff
    assert "SBI Group is a founding validator" in handoff
    assert "Coinbase is listed as an exchange participant" in handoff
    assert "not a direct SBI-Coinbase XRP partnership" in handoff


def test_run27_platform_map_has_exact_current_ci_and_preserves_run26():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    current = data["current_run_observations"]
    assert current["run_id"] == 27
    assert current["main_sha"] == MAIN_SHA
    assert current["integration_head_before_map_commit"] == INTEGRATION_HEAD
    assert current["research_head"] == RESEARCH_HEAD
    assert current["integration"]["full_suite"].startswith("1,138 passed")
    assert current["integration"]["core_suite"].startswith("632 passed")
    assert current["integration"]["coverage_pct"] == 58.25
    assert current["integration"]["wheel_verification"] == "passed"
    assert current["research"]["full_suite"].startswith("2,006 passed")
    assert current["research"]["core_suite"].startswith("498 passed")
    assert current["research"]["dependency_audit"].startswith("passed")
    assert current["research"]["fail_closed_gate"].startswith("passed")
    assert current["merge_state"]["merge_performed"] is False
    assert current["merge_state"]["independent_approvals"] == 0
    assert current["forecast_status"] == "NOT_ISSUED"
    assert any(item.get("run_id") == 26 for item in data["prior_run_observations"])
    assert data["platforms"]["ChatGPT"]["last_verified_at_utc"] == "2026-11-07T17:24:52Z"
    assert data["coordination_status"]["external_platform_data_exchange_performed"] is False


def test_run27_market_and_institutional_evidence_remains_excluded_from_numeric_forecast_features():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    current = data["current_run_observations"]
    market = current["market_snapshot"]
    assert market["kraken"]["provider_timestamp"] is None
    assert market["okx"]["age_seconds"] > 300
    assert market["binance_perpetual"]["age_seconds"] > 300
    assert market["limitations"]
    network = current["institutional_network"]
    assert "does not establish a direct SBI-Coinbase XRP partnership" in network["sbi_circle_arc"]
    assert "no XRP-specific balance disclosed" in network["coinbase_collateral"]
