from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json"


def _load_map() -> dict:
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def test_run175_current_main_successor_snapshot_is_explicit() -> None:
    data = _load_map()
    run = data["run175_snapshot"]
    assert data["latest_run_id"] == "Run175"
    assert data["current_repository_state"]["main_sha"] == "5b2a9c46eb878250dfec99190e294909cd5835bf"
    assert run["main_sha"] == "5b2a9c46eb878250dfec99190e294909cd5835bf"
    assert run["successor_head_before_run175_commit"] == "692caffaba27e9653fddfde3823785efad096e17"
    assert run["ci"]["tests_collected"] == 3808
    assert run["ci"]["tests_passed"] == 3807
    assert run["ci"]["tests_failed"] == 0
    assert run["ci"]["tests_skipped"] == 1
    assert run["ci"]["subtests_passed"] == 19
    assert run["ci"]["inclusive_coverage_pct"] == 64.02
    assert run["prediction"]["forecast_status"] == "NOT_ISSUED"
    assert run["prediction"]["accuracy_status"] == "NOT_EVALUATED"
    assert run["pr_1662"]["state"] == "closed"
    assert run["pr_1662"]["merged"] is False
    assert run["open_prs"]["count"] == 8
    assert run["tree_reconciliation"]["main_paths_missing_after_restore"] == 0


def test_run175_restores_current_main_barrot_state_blobs_byte_for_byte() -> None:
    data = _load_map()
    expected = data["run175_snapshot"]["preservation"]["restored_main_blob_sha1"]
    assert len(expected) == 10
    for relative_path, expected_sha in expected.items():
        payload = (ROOT / relative_path).read_bytes()
        header = b"blob " + str(len(payload)).encode("ascii") + b"\\0"
        actual_sha = hashlib.sha1(header + payload).hexdigest()
        assert actual_sha == expected_sha, relative_path


def test_run175_platform_map_does_not_claim_unverified_external_connections() -> None:
    data = _load_map()
    platforms = data["run175_snapshot"]["platforms"]
    assert platforms["ChatGPT"]["authentication_status"] == "VERIFIED_CURRENT_SESSION"
    assert platforms["Claude"]["authentication_status"] == "UNVERIFIED_NO_AUTH_TEST"
    assert platforms["Grok"]["authentication_status"] == "UNVERIFIED_NO_AUTH_TEST"
    assert platforms["Gemini"]["authentication_status"] == "UNVERIFIED_NO_AUTH_TEST"
    assert platforms["Codex"]["authentication_status"] == "UNVERIFIED_NO_AUTH_TEST"
    assert platforms["Groq"]["dispatch"] is False
    assert platforms["ChatGPT"]["external_model_transfer"] is False
