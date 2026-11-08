import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA = "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
RESEARCH_HEAD = "3632f2ea440f37179b71d032b1e267d0dd7a2ff4"


def load_map():
    return json.loads(
        (ROOT / "research" / "xrp_intelligence" / "nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )


def test_run59_preserves_run58_and_records_current_research_head():
    data = load_map()
    current = data["current_run_observations"]
    prior59 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 59)
    assert current["run_id"] >= 59
    assert any(item.get("run_id") == 58 for item in data["prior_run_observations"])
    assert prior59["observed_main_sha"] == MAIN_SHA
    assert prior59["research_head"] == RESEARCH_HEAD
    assert any("20261108T162835Z-xrp-derivatives-oi-universe-late-session-reconciliation.json" in item for item in prior59["new_research_artifacts"])
    assert any("20261108T164100Z-sbi-vc-trade-rlusd-chain-and-reserve-snapshot-correction.json" in item for item in prior59["new_research_artifacts"])
    assert current["prediction_engine"]["endpoints"] == 35
    assert current["prediction_engine"]["scheduled_public_sources"] == 33
    assert data["forecast_status"] == "NOT_ISSUED"


def test_run59_research_ci_is_bound_to_exact_head_and_full_suite():
    data = load_map()
    prior59 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 59)
    ci = prior59["exact_head_ci"]["research"]
    assert ci["head"] == RESEARCH_HEAD
    assert ci["full_suite"]["run_id"] == 42501293664
    assert ci["full_suite"]["passed"] == 2493
    assert ci["full_suite"]["subtests_passed"] == 8
    assert ci["core_suite"]["passed"] == 498
    assert ci["dependency_audit"]["run_id"] == 42501293459
    assert ci["fail_closed_gate"]["run_id"] == 42501293434


def test_run59_merge_gate_remains_closed_without_approvals_or_pages_authority():
    data = load_map()
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


def test_run59_handoff_keeps_the_historical_run58_header_and_appends_run59():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert handoff.startswith("# Current integrated Barrot handoff — 2026-11-08T16:03:05Z")
    assert "## Run 58 — current repository, endpoint inventory correction, exact-head verification and merge gate" in handoff[:3000]
    assert "## Run 59 —" in handoff
    assert "20261108T162835Z-xrp-derivatives-oi-universe-late-session-reconciliation.json" in handoff
    assert "20261108T164100Z-sbi-vc-trade-rlusd-chain-and-reserve-snapshot-correction.json" in handoff
    assert "Forecast status: NOT_ISSUED" in handoff
