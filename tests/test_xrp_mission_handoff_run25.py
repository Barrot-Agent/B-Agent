import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_run25_handoff_records_exact_heads_ci_and_bybit_scope():
    handoff = (ROOT / "BARROT_XRP_MISSION_HANDOFF.md").read_text(encoding="utf-8")
    assert "# Run 25 — 2026-11-07T14:08:30Z" in handoff
    assert "4bb067791a44e6c4bb8090861b39ec5d94ee5d15" in handoff
    assert "33dd72e6815e931da762cf3a362ffd271dcb6ab7" in handoff
    assert "1,128 passed, 8 subtests passed" in handoff
    assert "1,932 passed, 8 subtests passed" in handoff
    assert "xrp-public-market-v3.14" in handoff
    assert "xrp-public-market-v3.13" in handoff
    assert "RPI orders" in handoff
    assert "Forecast status: NOT_ISSUED" in handoff


def test_run26_platform_map_is_current_and_fail_closed():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    current = data["current_run_observations"]
    assert current["run_id"] == 26
    assert current["main_sha"] == "9100dbacb5f9f1b973b053a65ef1e91e96b64f72"
    assert current["integration_head_before_map_commit"] == "e44c3cc6e18df6715d3e78575a02b1bbca38531b"
    assert current["research_head"] == "42f5c98c6ebe19c066d938909cecc72aadefa258"
    assert current["integration"]["full_suite"].startswith("1,135 passed")
    assert current["research"]["full_suite"].startswith("1,950 passed")
    assert current["integration"]["wheel_verification"] == "passed"
    assert current["merge_state"]["merge_performed"] is False
    assert current["next_actions"]
    assert any(item.get("run_id") == 24 for item in data["prior_run_observations"])


def test_prior_run25_bybit_source_does_not_claim_live_execution_or_usd_normalization():
    data = json.loads(
        (ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json")
        .read_text(encoding="utf-8")
    )
    run25 = next(item for item in data["prior_run_observations"] if item.get("run_id") == 25)
    bybit = run25["bybit_adapter"]
    assert bybit["status"].endswith("NOT_LIVE_EXECUTED")
    assert "cts" in bybit["endpoints"][1]["timestamp_semantics"]
    assert any("RPI" in item for item in bybit["limitations"])
    assert any("USDT" in item and "USD" in item for item in bybit["limitations"])
