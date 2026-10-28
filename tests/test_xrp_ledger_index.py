import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_xrp_ledger_index.py"
SPEC = importlib.util.spec_from_file_location("xrp_ledger_index_validator", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def fixture_pair(tmp_path, *, unsafe_path=False, wrong_sha=False, duplicate_ids=False):
    relative = "../escape.json" if unsafe_path else "data/xrp_intelligence/snapshots/fixture.json"
    snapshot = {
        "captured_at_utc": "2026-10-28T00:00:00Z",
        "snapshot_id": "fixture-snapshot",
        "snapshot_path": relative,
        "main_modified_by_this_run": False,
        "merge_performed": False,
    }
    raw = (json.dumps(snapshot, indent=2) + "\n").encode("utf-8")
    snapshot_path = tmp_path / relative
    if not unsafe_path:
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_bytes(raw)
    sha = VALIDATOR.git_blob_sha(raw)
    if wrong_sha:
        sha = "0" * 40
    latest = {
        "record_type": "snapshot_reference",
        "index_format_version": "2.0",
        "schema_version": "1.0",
        "captured_at_utc": snapshot["captured_at_utc"],
        "snapshot_id": snapshot["snapshot_id"],
        "snapshot_path": relative,
        "snapshot_blob_sha": sha,
        "snapshot_commit_sha": "1" * 40,
    }
    sources = [{"id": "SRC-ONE"}, {"id": "SRC-ONE"}] if duplicate_ids else [{"id": "SRC-ONE"}]
    index = {
        "schema_version": "1.0",
        "record_type": "xrp_intelligence_research_ledger",
        "index_format_version": "2.0",
        "latest_snapshot": latest,
        "sources": sources,
        "run_updates": [],
    }
    return index, snapshot


def test_pointer_resolves_and_hash_verifies(tmp_path):
    index, _ = fixture_pair(tmp_path)
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "PASS"
    assert report["snapshot_reference_mode"] is True
    assert report["state_mutated"] is False


def test_bad_snapshot_hash_fails_closed(tmp_path):
    index, _ = fixture_pair(tmp_path, wrong_sha=True)
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "BLOCKED"
    assert any("SHA mismatch" in error for error in report["errors"])


def test_path_traversal_is_rejected(tmp_path):
    index, _ = fixture_pair(tmp_path, unsafe_path=True)
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "BLOCKED"
    assert any("stay inside" in error for error in report["errors"])


def test_duplicate_source_ids_fail_closed(tmp_path):
    index, _ = fixture_pair(tmp_path, duplicate_ids=True)
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "BLOCKED"
    assert "duplicate source IDs" in report["errors"]


def test_legacy_inline_index_remains_readable(tmp_path):
    index, snapshot = fixture_pair(tmp_path)
    legacy = dict(snapshot)
    legacy["snapshot_blob_sha"] = index["latest_snapshot"]["snapshot_blob_sha"]
    legacy["snapshot_blob_sha_checked_at_utc"] = "2026-10-28T00:01:00Z"
    legacy["snapshot_commit_sha"] = "2" * 40
    legacy["post_snapshot_verification"] = {"status": "PASS"}
    index["latest_snapshot"] = legacy
    index.pop("index_format_version", None)
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "PASS"
    assert report["snapshot_reference_mode"] is False


def test_current_repository_ledger_validates_read_only():
    report = VALIDATOR.validate_index(ROOT / "data" / "xrp_intelligence" / "research_ledger.json", ROOT)
    assert report["status"] == "PASS", report
    assert report["snapshot_reference_mode"] is True
    assert report["state_mutated"] is False
