import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "xrp_intelligence" / "20261105T220437Z-xrp-spot-perps-etf-cutoff-snapshot.json"
CORRECTION = ROOT / "research" / "xrp_intelligence" / "20261105T221000Z-xrp-capture-time-interval-correction.json"


def test_capture_time_correction_is_append_only_and_bound_to_original_blob():
    original_bytes = SOURCE.read_bytes()
    original = json.loads(original_bytes)
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    git_blob = b"blob " + str(len(original_bytes)).encode("ascii") + b"\0" + original_bytes
    assert hashlib.sha1(git_blob).hexdigest() == correction["source_artifact_blob_sha"]
    assert correction["source_artifact_path"].endswith("20261105T220437Z-xrp-spot-perps-etf-cutoff-snapshot.json")
    assert original["captured_at_utc"] == correction["original_claimed_captured_at_utc"]
    assert original["market_snapshot"]["kraken_spot"]["raw_response_body_text_sha256"] == correction["preserved_facts"]["kraken_response_body_sha256"]


def test_exact_retrieval_time_is_unknown_and_cutoff_uses_conservative_upper_bound():
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    assert correction["exact_retrieval_time_utc"] is None
    assert correction["retrieval_time_lower_bound_utc"] == "2026-11-05T22:04:37Z"
    assert correction["retrieval_time_upper_bound_utc"] == "2026-11-05T22:08:06Z"
    assert correction["conservative_known_at_utc"] == "2026-11-05T22:08:06Z"
    assert correction["superseded_fields"]["captured_at_utc"]["corrected_value"] is None
    assert correction["superseded_fields"]["data_cutoff_utc"]["corrected_value"] == correction["conservative_known_at_utc"]


def test_source_timestamps_and_market_values_are_preserved_without_false_precision():
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    assert correction["preserved_facts"]["numeric_market_values_changed"] is False
    assert correction["preserved_facts"]["source_urls_changed"] is False
    assert correction["preserved_facts"]["provider_event_timestamp_for_kraken_spot"] is None
    assert correction["preserved_facts"]["kraken_futures_provider_update_time_utc"] == "2026-11-05T21:49:00Z"
    assert correction["preserved_facts"]["tradradar_provider_update_time_utc"] == "2026-11-05T21:10:00Z"
    assert correction["point_in_time_policy"]["may_be_used_for_earlier_cutoffs"] is False
    assert correction["point_in_time_policy"]["model_eligible"] is False
    assert correction["correction_application"]["original_artifact_modified"] is False
    assert correction["directional_forecast_issued"] is False
