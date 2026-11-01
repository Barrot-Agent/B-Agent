from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "data/xrp_intelligence/hand_offs").glob("*-xrp-intelligence-and-v3-run-handoff.json"))


def load():
    assert FILES, "Current XRP/V3 handoff missing"
    return json.loads(FILES[-1].read_text(encoding="utf-8"))


def test_handoff_preserves_main_and_separates_main_from_legacy_Main():
    d = load()
    assert d["repo_state"]["default_branch"] == "main"
    assert d["repo_state"]["verified_main_sha"] == "ce1139c7c032e0bdca93efcf2ea963a5ace56b6e"
    assert "capitalized" in d["repo_state"]["branch_name_warning"]


def test_handoff_keeps_prediction_status_honest():
    d = load()
    assert d["prediction_engine"]["status"] == "IMPLEMENTED_NOT_POPULATED"
    assert d["prediction_engine"]["forecast_status"] == "NOT_ISSUED"
    assert "No verified XRP forecasts" in d["prediction_engine"]["no_skill_claim"]


def test_handoff_records_open_unmerged_prs_and_verified_test_evidence():
    d = load()
    by_number = {p["number"]: p for p in d["pull_requests"]}
    assert by_number[1474]["state"] == "open_draft_unmerged"
    assert by_number[1475]["verification"].startswith("417 tests")
    assert by_number[1477]["verification"].startswith("393 tests")
    assert d["repo_state"]["no_merge_force_push_or_manual_dispatch"] is True


def test_handoff_distinguishes_verified_and_unverified_platforms():
    d = load()
    assert set(d["platform_status"]["verified_live"]) == {"ChatGPT", "GitHub"}
    assert "Databricks" in d["platform_status"]["unverified_live"]
