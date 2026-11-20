from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "research/xrp_intelligence/20261108T063207Z-xrp-etf-flow-coverage-and-institutional-demand-reconciliation.json"
CORRECTION = ROOT / "research/xrp_intelligence/20261108T063932Z-xrp-etf-flow-capture-time-correction.json"


def test_run_start_is_not_misrepresented_as_exact_source_retrieval_time():
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    item = correction["correction"]
    assert original["captured_at_utc"] == item["original_value"]
    assert item["status"] == "MISLABELED_RUN_START_AS_CAPTURE_TIME"
    assert item["source_page_retrieval_time_utc"] is None
    interval = item["bounded_interval"]
    assert interval["not_before_utc"] == "2026-11-08T06:32:07Z"
    assert interval["not_after_utc"] == "2026-11-08T06:36:01Z"
    assert correction["model_admission"]["original_artifact_feature_eligible"] is False
    assert correction["model_admission"]["forecast_status"] == "NOT_ISSUED"
