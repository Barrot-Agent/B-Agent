import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "research/xrp_intelligence/20261107T175608Z-xrpc-future-dated-holdings-leakage-reconciliation.json"
CORRECTION = ROOT / "research/xrp_intelligence/20261107T181119Z-xrpc-retrieval-window-timestamp-correction.json"


def test_retrieval_start_correction_preserves_original_artifact_and_binds_blob():
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    assert correction["append_only"] is True
    assert correction["supersedes_artifact_path"] == str(ORIGINAL.relative_to(ROOT))
    assert correction["supersedes_artifact_git_blob_sha1"] == "0a785d9f2716602336aeae08f700b53e93b09825"
    assert original["retrieval_window_start_utc"] == "2026-11-07T17:13:00Z"
    assert correction["incorrect_prior_value"] == original["retrieval_window_start_utc"]


def test_page_update_and_actual_retrieval_start_are_separate_timestamps():
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    assert correction["preserved_values"]["cryptokeyhole_page_updated_at_utc"] == "2026-11-07T17:13:00Z"
    assert correction["corrected_value"] == "2026-11-07T17:31:19Z"
    assert correction["corrected_value"] < correction["preserved_values"]["data_cutoff_utc"]
    assert correction["model_admission"] is False
    assert correction["forecast_status"] == "NOT_ISSUED"
