from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json"
HISTORICAL = ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map.json"


def test_run73_current_snapshot_preserves_historical_map():
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    historical = json.loads(HISTORICAL.read_text(encoding="utf-8"))
    observation = current["current_run_observations"]

    assert current["captured_at_utc"] == current["last_verified_at_utc"]
    assert current["last_verified_at_utc"] == current["captured_at_utc"]
    assert observation["run_id"] == 73
    assert observation["captured_at_utc"] == current["captured_at_utc"]
    assert current["captured_at_utc"].startswith("2026-11-09T")
    assert observation["main_sha"] == "d4d43be3427375cf79d190e768976de062e20287"
    assert observation["integration_head_before_handoff_commit"] == "5b09c4ac686e6a4b9166b383b4c261a61e511462"
    assert observation["research_head"] == "92b66e11844313b1316429bc3b5678915af68565"

    assert historical["captured_at_utc"] == "2026-11-08T22:30:23Z"
    assert historical["last_verified_at_utc"] == historical["captured_at_utc"]
    assert historical["observed_integration_head_before_map_commit"] == "a98ce73d392294a31303001891ca8ede5fd9703c"
    assert historical["current_run_observations"]["run_id"] == 70


def test_run73_prediction_engine_contract_remains_fail_closed():
    data = json.loads(CURRENT.read_text(encoding="utf-8"))
    observation = data["current_run_observations"]
    engine = observation["prediction_engine"]

    assert engine["endpoints"] == 35
    assert engine["scheduled_public_sources"] == 33
    assert engine["excluded_xrpl_node_sources"] == 2
    assert engine["forecast_status"] == "NOT_ISSUED"
    assert engine["oos_lift"] is False
    assert engine["real_data_calibration"] is False
    assert engine["shadow_outcomes"] is False
    assert engine["trusted_evaluator_key"] is False
    assert observation["forecast_status"] == "NOT_ISSUED"


def test_run73_platform_map_keeps_external_data_flows_unverified():
    data = json.loads(CURRENT.read_text(encoding="utf-8"))
    assert data["platforms"]["ChatGPT"]["authentication_status"] == "VERIFIED_CURRENT_SESSION"
    assert data["platforms"]["ChatGPT"]["data_flow"]["verified"] is True
    for name, platform in data["platforms"].items():
        if name != "ChatGPT":
            assert platform["data_flow"]["verified"] is False
    assert data["coordination_status"]["external_platform_data_exchange_performed"] is False


def test_run73_market_receipt_preimages_match_sha256_and_staleness_gate():
    data = json.loads(CURRENT.read_text(encoding="utf-8"))
    market = data["current_run_observations"]["latest_market_crosscheck"]
    bodies = market["raw_response_bodies"]

    assert hashlib.sha256(bodies["kraken_xrpusd"].encode()).hexdigest() == market["spot"]["kraken_xrpusd"]["receipt_sha256"]
    assert hashlib.sha256(bodies["okx_xrpusdt"].encode()).hexdigest() == market["spot"]["okx_xrpusdt"]["receipt_sha256"]
    assert market["spot"]["kraken_xrpusd"]["provider_event_time_utc"] is None
    assert market["spot"]["okx_xrpusdt"]["age_seconds_at_recheck"] > 300
    assert market["usd_usdt_normalized"] is False
    assert market["model_admission"] is False
    assert hashlib.sha256(bodies["coinpaprika_xrp"].encode()).hexdigest() == market["spot"]["coinpaprika_xrp"]["receipt_sha256"]
    assert market["spot"]["coinpaprika_xrp"]["age_seconds_at_recheck"] > 300
    assert market["spot"]["coinpaprika_xrp"]["model_eligible"] is False


def test_run73_merge_and_forecast_safety_gates_remain_closed():
    data = json.loads(CURRENT.read_text(encoding="utf-8"))
    observation = data["current_run_observations"]

    assert observation["reviews"]["pr_1640"]["approving_reviews"] == 0
    assert observation["reviews"]["pr_1640"]["threads_resolved"] == 22
    assert observation["reviews"]["pr_1643"]["approving_reviews"] == 0
    assert observation["reviews"]["pr_1643"]["threads_resolved"] == 19
    assert observation["merge_state"]["merge_performed"] is False
    assert observation["external_actions"]["deployment"] is False
    assert observation["external_actions"]["real_money"] is False
    assert observation["forecast_status"] == "NOT_ISSUED"


def test_run73_current_ci_failure_is_recorded_without_relabeling_as_green():
    data = json.loads(CURRENT.read_text(encoding="utf-8"))
    integration = data["current_run_observations"]["ci_evidence"]["integration"]
    failed = integration["latest_handoff_map_head"]

    assert failed["full_suite"]["result"] == "failure"
    assert failed["full_suite"]["passed"] == 1221
    assert failed["full_suite"]["failed"] == 1
    assert failed["core_suite"]["result"] == "success"
    assert failed["wheel_verification"] == "skipped after full-suite failure"
    assert integration["dependency_audit"]["result"] == "success"
    assert integration["fail_closed_gate"]["automatic_merge_disabled"] is True


def test_run73_sbi_start_bond_separates_jpy_coupon_from_xrp_reward():
    data = json.loads(CURRENT.read_text(encoding="utf-8"))
    bond = data["current_run_observations"]["sbi_start_bond"]

    assert bond["issue_amount_jpy"] == 10_000_000_000
    assert bond["sold_out"] is True
    assert bond["coupon_currency"] == "JPY"
    assert bond["coupon_rate_percent"] == 2.15
    assert bond["xrp_reward_separate_from_coupon"] is True
    assert bond["initial_reward_jpy_per_100k_face"] == 200
    assert bond["initial_reward_percent_of_face"] == 0.2
    assert bond["maximum_theoretical_initial_reward_jpy_if_full_issue_qualifies"] == 20_000_000
    assert bond["bond_token_ledger"] == "ibet for Fin (BOOSTRY)"
    assert bond["reward_asset_ledger"] == "XRP Ledger"
    assert bond["future_coupon_date_reward_asset_guaranteed"] is False
    assert bond["direct_ripple_involvement_verified"] is False
