"""Regression tests for the append-only XRP observation eligibility overlay."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "xrp_intelligence" / "20261104T001118Z-xrp-derivatives-and-etf-flow-reconciliation.json"
OVERLAY = ROOT / "research" / "xrp_intelligence" / "20261104T193100Z-derivatives-etf-model-eligibility-overlay.json"


def test_all_derivatives_and_etf_observations_are_explicitly_model_ineligible():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    source_ids = {item["observation_id"] for item in source["observations"]}
    corrected = overlay["correction"]["observations"]
    corrected_ids = {item["observation_id"] for item in corrected}

    assert source_ids == corrected_ids
    assert len(corrected) == len(source["observations"])
    assert all(item["model_eligible"] is False for item in corrected)
    assert all(item["reason"].strip() for item in corrected)
    assert overlay["preservation"]["source_artifact_modified"] is False
    assert overlay["preservation"]["raw_source_receipts_modified"] is False
    assert overlay["preservation"]["consumer_application_status"] == "NOT_EXECUTED"
    assert overlay["preservation"]["forecast_issued"] is False
