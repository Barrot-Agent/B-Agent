from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "data/xrp_intelligence/hand_offs").glob("*-xrp-intelligence-and-v3-run-handoff.json"))


def load():
    assert FILES, "Current XRP/V3 handoff missing"
    return json.loads(FILES[-1].read_text(encoding="utf-8"))


def test_handoff_preserves_main_and_reports_branch_protection_limits():
    d = load()
    assert d["repo_state"]["default_branch"] == "main"
    assert re.fullmatch(r"[0-9a-f]{40}", d["repo_state"]["verified_main_sha"])
    protection = d["repo_state"]["branch_protection"]
    assert protection["branch_api_reports_protected"] is True
    assert protection["required_status_check_contexts"] == []
    assert protection["repository_rulesets"][0]["enforcement"] == "disabled"
    assert "capitalized" in d["repo_state"]["branch_name_warning"]


def test_handoff_keeps_prediction_status_honest():
    d = load()
    assert d["prediction_engine"]["status"] == "IMPLEMENTED_NOT_POPULATED"
    assert d["prediction_engine"]["forecast_status"] == "NOT_ISSUED"
    assert "No verified XRP forecasts" in d["prediction_engine"]["no_skill_claim"]


def test_handoff_records_open_unmerged_prs_and_exact_head_verification():
    d = load()
    by_number = {p["number"]: p for p in d["pull_requests"]}
    for number in (1474, 1475, 1476, 1477):
        p = by_number[number]
        assert p["state"] == "open_draft_unmerged"
        assert p["verification"]["ci_conclusion"] == "success"
        assert p["verification"]["gate_conclusion"] == "success"
        assert p["verification"]["merge_enabled"] is False
    assert by_number[1477]["verification"]["test_summary"] == "424 tests and 8 subtests passed"
    assert d["repo_state"]["no_merge_force_push_or_manual_dispatch"] is True


def test_handoff_records_confirmed_firelight_kraken_usdc_relationship():
    d = load()
    relationship = d["firelight_kraken_relationship"]
    assert relationship["status"] == "CONFIRMED_OFFICIAL_FIRELIGHT_ANNOUNCEMENTS"
    assert relationship["roles"]["sentora"].startswith("Curates")
    assert relationship["mechanism"]["fee_asset"] == "USDC"
    assert "converted to FXRP" in relationship["mechanism"]["fee_conversion"]
    assert relationship["mechanism"]["first_loss_buffer"].startswith("Exists")


def test_handoff_distinguishes_verified_and_unverified_platforms():
    d = load()
    assert set(d["platform_status"]["verified_live"]) == {"ChatGPT", "GitHub"}
    assert "Databricks" in d["platform_status"]["unverified_live"]
