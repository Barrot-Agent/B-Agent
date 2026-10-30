import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_xrp_ledger_index.py"
SPEC = importlib.util.spec_from_file_location("xrp_ledger_index_validator", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def fixture_pair(tmp_path, *, unsafe_path=False, wrong_sha=False, duplicate_ids=False, index_format_version="2.0"):
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
        "index_format_version": index_format_version,
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
        "index_format_version": index_format_version,
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


def test_v3_snapshot_pointer_matches_ledger_format(tmp_path):
    index, _ = fixture_pair(tmp_path, index_format_version="3.0")
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "PASS", report
    assert report["index_format_version"] == "3.0"


def test_snapshot_pointer_format_must_match_ledger_format(tmp_path):
    index, _ = fixture_pair(tmp_path, index_format_version="3.0")
    index["latest_snapshot"]["index_format_version"] = "2.0"
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "BLOCKED"
    assert any("must match ledger index_format_version" in error for error in report["errors"])


def test_unsupported_sharded_index_format_fails_closed(tmp_path):
    index, _ = fixture_pair(tmp_path, index_format_version="4.0")
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "BLOCKED"
    assert any("must be 2.0 or 3.0" in error for error in report["errors"])


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
    index_path = ROOT / "data" / "xrp_intelligence" / "research_ledger.json"
    index_data = json.loads(index_path.read_text(encoding="utf-8"))
    report = VALIDATOR.validate_index(index_path, ROOT)
    assert report["status"] == "PASS", report
    assert report["snapshot_reference_mode"] is True
    assert report["state_mutated"] is False
    assert report["source_count"] == index_data["sources"]["record_count"]
    assert report["run_update_count"] == index_data["run_updates"]["record_count"]
    assert report["limitation_count"] == index_data["limitations"]["record_count"]
    assert report["archive_shards_checked"] == sum(
        index_data[name]["chunk_count"] for name in ("sources", "run_updates", "limitations")
    )


def _write_archive_shard(tmp_path, array_name, records, *, chunk_index=0, chunk_count=1):
    relative = f"data/xrp_intelligence/ledger_archive/v1/{array_name}-{chunk_index:03d}.json"
    payload = {"schema_version": "1.0", "record_type": "xrp_research_ledger_archive_shard", "archive_schema_version": "1.0", "array_name": array_name, "chunk_index": chunk_index, "chunk_count": chunk_count, "record_count": len(records), "records": records}
    raw = (json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return {"chunk_index": chunk_index, "path": relative, "git_blob_sha": VALIDATOR.git_blob_sha(raw), "record_count": len(records)}


def _archive_pointer(array_name, shard_specs, record_count):
    return {"record_type": "archive_pointer", "archive_schema_version": "1.0", "array_name": array_name, "record_count": record_count, "chunk_count": len(shard_specs), "chunks": shard_specs}


def test_sharded_arrays_resolve_and_roundtrip_exactly(tmp_path):
    source_records = [{"id": "SRC-A", "title": "alpha"}, {"id": "SRC-B", "title": "beta"}]
    run_records = [{"recorded_at_utc": "2026-10-29T00:00:00Z", "source_ids": ["SRC-A", "SRC-B"]}]
    limit_records = ["one limitation", "second limitation"]
    source_specs = [_write_archive_shard(tmp_path, "sources", [source_records[0]], chunk_index=0, chunk_count=2), _write_archive_shard(tmp_path, "sources", [source_records[1]], chunk_index=1, chunk_count=2)]
    run_specs = [_write_archive_shard(tmp_path, "run_updates", run_records)]
    limit_specs = [_write_archive_shard(tmp_path, "limitations", limit_records)]
    a, ea, _ = VALIDATOR.resolve_archive_array(_archive_pointer("sources", source_specs, 2), "sources", tmp_path)
    b, eb, _ = VALIDATOR.resolve_archive_array(_archive_pointer("run_updates", run_specs, 1), "run_updates", tmp_path)
    c, ec, _ = VALIDATOR.resolve_archive_array(_archive_pointer("limitations", limit_specs, 2), "limitations", tmp_path)
    assert ea == eb == ec == []
    assert a == source_records and b == run_records and c == limit_records


def test_sharded_index_validates_and_reports_archive_counts(tmp_path):
    index, _ = fixture_pair(tmp_path)
    ss = [_write_archive_shard(tmp_path, "sources", [{"id": "SRC-ONE"}])]
    rs = [_write_archive_shard(tmp_path, "run_updates", [{"source_ids": ["SRC-ONE"]}])]
    ls = [_write_archive_shard(tmp_path, "limitations", ["preserve me"])]
    index["sources"] = _archive_pointer("sources", ss, 1)
    index["run_updates"] = _archive_pointer("run_updates", rs, 1)
    index["limitations"] = _archive_pointer("limitations", ls, 1)
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "PASS", report
    assert report["source_count"] == 1 and report["run_update_count"] == 1 and report["limitation_count"] == 1
    assert report["archive_shards_checked"] == 3


def test_archive_digest_mismatch_fails_closed(tmp_path):
    index, _ = fixture_pair(tmp_path)
    specs = [_write_archive_shard(tmp_path, "sources", [{"id": "SRC-ONE"}])]
    specs[0]["git_blob_sha"] = "0" * 40
    index["sources"] = _archive_pointer("sources", specs, 1)
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "BLOCKED"
    assert any("Git blob SHA mismatch" in error for error in report["errors"])


def test_archive_path_traversal_fails_closed(tmp_path):
    index, _ = fixture_pair(tmp_path)
    pointer = _archive_pointer("sources", [{"chunk_index": 0, "path": "../escape.json", "git_blob_sha": "0" * 40, "record_count": 1}], 1)
    index["sources"] = pointer
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "BLOCKED" and any("stay inside" in error for error in report["errors"])


def test_archive_missing_file_fails_closed(tmp_path):
    index, _ = fixture_pair(tmp_path)
    pointer = _archive_pointer("sources", [{"chunk_index": 0, "path": "data/xrp_intelligence/ledger_archive/v1/missing.json", "git_blob_sha": "0" * 40, "record_count": 1}], 1)
    index["sources"] = pointer
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "BLOCKED" and any("cannot be read" in error for error in report["errors"])


def test_duplicate_source_ids_across_archive_shards_fail_closed(tmp_path):
    index, _ = fixture_pair(tmp_path)
    specs = [_write_archive_shard(tmp_path, "sources", [{"id": "SRC-DUP"}], chunk_index=0, chunk_count=2), _write_archive_shard(tmp_path, "sources", [{"id": "SRC-DUP"}], chunk_index=1, chunk_count=2)]
    index["sources"] = _archive_pointer("sources", specs, 2)
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "BLOCKED" and "duplicate source IDs" in report["errors"]


def test_append_only_shards_allow_prior_generation_chunk_counts(tmp_path):
    # The first shard was created when the archive had one chunk; the second
    # was appended later. Both immutable shards remain valid under a two-chunk
    # pointer without rewriting the first shard's creation-time metadata.
    first = _write_archive_shard(tmp_path, "sources", [{"id": "SRC-A"}], chunk_index=0, chunk_count=1)
    second = _write_archive_shard(tmp_path, "sources", [{"id": "SRC-B"}], chunk_index=1, chunk_count=2)
    pointer = _archive_pointer("sources", [first, second], 2)
    records, errors, checked = VALIDATOR.resolve_archive_array(pointer, "sources", tmp_path)
    assert errors == []
    assert records == [{"id": "SRC-A"}, {"id": "SRC-B"}]
    assert checked == 2


def test_archive_chunk_count_before_global_index_fails_closed(tmp_path):
    index, _ = fixture_pair(tmp_path)
    first = _write_archive_shard(tmp_path, "sources", [{"id": "SRC-A"}], chunk_index=0, chunk_count=1)
    invalid_second = _write_archive_shard(tmp_path, "sources", [{"id": "SRC-B"}], chunk_index=1, chunk_count=1)
    index["sources"] = _archive_pointer("sources", [first, invalid_second], 2)
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "BLOCKED"
    assert any("append-generation metadata mismatch" in error for error in report["errors"])


def test_archive_chunk_count_cannot_exceed_pointer_total(tmp_path):
    index, _ = fixture_pair(tmp_path)
    invalid_first = _write_archive_shard(tmp_path, "sources", [{"id": "SRC-A"}], chunk_index=0, chunk_count=3)
    second = _write_archive_shard(tmp_path, "sources", [{"id": "SRC-B"}], chunk_index=1, chunk_count=2)
    index["sources"] = _archive_pointer("sources", [invalid_first, second], 2)
    report = VALIDATOR.validate_index_data(index, tmp_path)
    assert report["status"] == "BLOCKED"
    assert any("append-generation metadata mismatch" in error for error in report["errors"])
