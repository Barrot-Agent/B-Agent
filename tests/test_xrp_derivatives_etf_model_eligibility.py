"""Regression tests for the append-only XRP observation eligibility overlay."""
from __future__ import annotations

import hashlib
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


def test_overlay_is_bound_to_exact_git_blob_of_original_source_artifact():
    source_bytes = SOURCE.read_bytes()
    git_object = f"blob {len(source_bytes)}\0".encode("ascii") + source_bytes
    expected_blob_sha = hashlib.sha1(git_object).hexdigest()
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

    assert overlay["schema_version"] == "barrot.xrp.research-correction.v1"
    assert overlay["artifact_type"] == "append_only_observation_eligibility_correction"
    assert overlay["source_artifact"] == SOURCE.relative_to(ROOT).as_posix()
    assert overlay["source_artifact_blob_sha"] == expected_blob_sha
    assert overlay["preservation"]["correction_mode"] == "append_only_observation_overlay"
