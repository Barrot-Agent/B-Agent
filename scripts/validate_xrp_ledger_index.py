#!/usr/bin/env python3
"""Validate the XRP research-ledger index and its immutable snapshot reference.

Supports the legacy inline index for migration verification and the compact
snapshot-reference format. Read-only: never writes or rewrites evidence.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "data" / "xrp_intelligence" / "research_ledger.json"
SNAPSHOT_PREFIX = "data/xrp_intelligence/snapshots/"
ARCHIVE_PREFIX = "data/xrp_intelligence/ledger_archive/v1/"
SOURCE_REVISION_PREFIX = "data/xrp_intelligence/source_revisions/"
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
INDEX_ONLY_FIELDS = {
    "snapshot_blob_sha",
    "snapshot_blob_sha_checked_at_utc",
    "snapshot_commit_sha",
    "post_snapshot_verification",
}


def git_blob_sha(data: bytes) -> str:
    """Return Git's SHA-1 blob object ID for exact file bytes."""
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def _safe_snapshot_path(value: Any) -> tuple[Path | None, str | None]:
    if not isinstance(value, str) or not value:
        return None, "snapshot_path must be a non-empty string"
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not value.startswith(SNAPSHOT_PREFIX):
        return None, "snapshot_path must stay inside data/xrp_intelligence/snapshots/"
    if path.suffix != ".json":
        return None, "snapshot_path must point to a JSON snapshot"
    return path, None


def _safe_archive_path(value: Any) -> tuple[Path | None, str | None]:
    if not isinstance(value, str) or not value:
        return None, "archive path must be a non-empty string"
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not value.startswith(ARCHIVE_PREFIX):
        return None, "archive path must stay inside data/xrp_intelligence/ledger_archive/v1/"
    if path.suffix != ".json":
        return None, "archive path must point to a JSON shard"
    return path, None


def _safe_source_revision_path(value: Any) -> tuple[Path | None, str | None]:
    if not isinstance(value, str) or not value:
        return None, "source revision path must be a non-empty string"
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not value.startswith(SOURCE_REVISION_PREFIX):
        return None, "source revision path must stay inside data/xrp_intelligence/source_revisions/"
    if path.suffix != ".json":
        return None, "source revision path must point to a JSON addendum"
    return path, None


def resolve_archive_array(value: Any, expected_array_name: str, repo_root: Path) -> tuple[list[Any], list[str], int]:
    """Resolve a legacy inline list or a Git-blob-verified archive pointer."""
    if isinstance(value, list):
        return value, [], 0
    if not isinstance(value, dict) or value.get("record_type") != "archive_pointer":
        return [], [f"{expected_array_name} must be a list or archive_pointer object"], 0
    errors: list[str] = []
    if value.get("array_name") != expected_array_name:
        errors.append(f"{expected_array_name} archive pointer array_name mismatch")
    if value.get("archive_schema_version") != "1.0":
        errors.append(f"{expected_array_name} archive schema version must be 1.0")
    chunks = value.get("chunks")
    if not isinstance(chunks, list):
        return [], errors + [f"{expected_array_name} archive chunks must be a list"], 0
    expected_chunk_count = value.get("chunk_count")
    if not isinstance(expected_chunk_count, int) or expected_chunk_count < 1 or len(chunks) != expected_chunk_count:
        errors.append(f"{expected_array_name} archive chunk_count mismatch")
    records: list[Any] = []
    for position, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            errors.append(f"{expected_array_name} archive chunk {position} must be an object")
            continue
        if chunk.get("chunk_index") != position:
            errors.append(f"{expected_array_name} archive chunk order/index mismatch at {position}")
        relative_path, path_error = _safe_archive_path(chunk.get("path"))
        if path_error:
            errors.append(f"{expected_array_name} archive chunk {position}: {path_error}")
            continue
        expected_blob_sha = chunk.get("git_blob_sha")
        if not isinstance(expected_blob_sha, str) or not SHA1_RE.fullmatch(expected_blob_sha):
            errors.append(f"{expected_array_name} archive chunk {position} has invalid git_blob_sha")
            continue
        try:
            raw = (repo_root / relative_path).read_bytes()
        except OSError as exc:
            errors.append(f"{expected_array_name} archive chunk {position} cannot be read: {exc}")
            continue
        if git_blob_sha(raw) != expected_blob_sha:
            errors.append(f"{expected_array_name} archive chunk {position} Git blob SHA mismatch")
        try:
            archive = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{expected_array_name} archive chunk {position} JSON invalid: {exc}")
            continue
        if not isinstance(archive, dict) or archive.get("record_type") != "xrp_research_ledger_archive_shard":
            errors.append(f"{expected_array_name} archive chunk {position} has wrong record_type")
            continue
        if archive.get("schema_version") != "1.0" or archive.get("archive_schema_version") != "1.0":
            errors.append(f"{expected_array_name} archive chunk {position} schema mismatch")
        if archive.get("array_name") != expected_array_name:
            errors.append(f"{expected_array_name} archive chunk {position} array_name mismatch")
        if archive.get("chunk_index") != position:
            errors.append(f"{expected_array_name} archive chunk {position} global index mismatch")
        # Append-only archives preserve the chunk_count recorded when each shard
        # was created. Older shards therefore legitimately carry a smaller
        # generation count than the current pointer's total chunk_count.
        archive_chunk_count = archive.get("chunk_count")
        if (
            type(archive_chunk_count) is not int
            or archive_chunk_count < position + 1
            or archive_chunk_count > expected_chunk_count
        ):
            errors.append(f"{expected_array_name} archive chunk {position} append-generation metadata mismatch")
        shard_records = archive.get("records")
        if not isinstance(shard_records, list):
            errors.append(f"{expected_array_name} archive chunk {position} records must be a list")
            continue
        if archive.get("record_count") != len(shard_records) or chunk.get("record_count") != len(shard_records):
            errors.append(f"{expected_array_name} archive chunk {position} record_count mismatch")
        records.extend(shard_records)
    if value.get("record_count") != len(records):
        errors.append(f"{expected_array_name} archive total record_count mismatch")
    return records, errors, len(chunks)


def validate_index_data(index: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(index, dict):
        return {"status": "BLOCKED", "errors": ["index must be a JSON object"]}
    if index.get("record_type") != "xrp_intelligence_research_ledger":
        errors.append("unexpected record_type")

    sources, source_errors, source_shards = resolve_archive_array(index.get("sources"), "sources", repo_root)
    errors.extend(source_errors)
    source_ids: list[str] = []
    for i, source in enumerate(sources):
        if not isinstance(source, dict) or not isinstance(source.get("id"), str) or not source["id"]:
            errors.append(f"sources[{i}] has no non-empty id")
        else:
            source_ids.append(source["id"])
    if len(source_ids) != len(set(source_ids)):
        errors.append("duplicate source IDs")

    run_updates, run_errors, run_shards = resolve_archive_array(index.get("run_updates"), "run_updates", repo_root)
    errors.extend(run_errors)
    limitations, limitation_errors, limitation_shards = resolve_archive_array(index.get("limitations", []), "limitations", repo_root)
    errors.extend(limitation_errors)

    # The compact v3 index duplicates archive totals in archive_policy and
    # ledger_metrics for human/audit consumers. Fail closed if those summaries
    # drift from the authoritative immutable pointers.
    archive_policy_counts_reconciled: bool | None = None
    if index.get("index_format_version") == "3.0":
        policy_errors: list[str] = []
        archive_policy = index.get("archive_policy")
        if not isinstance(archive_policy, dict):
            policy_errors.append("v3 archive_policy must be an object")
        else:
            if archive_policy.get("archive_schema_version") != "1.0":
                policy_errors.append("archive_policy archive_schema_version must be 1.0")
            policy_arrays = archive_policy.get("arrays")
            if not isinstance(policy_arrays, dict):
                policy_errors.append("archive_policy arrays must be an object")
            else:
                for array_name in ("sources", "run_updates", "limitations"):
                    pointer = index.get(array_name)
                    policy_entry = policy_arrays.get(array_name)
                    if not isinstance(pointer, dict) or pointer.get("record_type") != "archive_pointer":
                        policy_errors.append(f"{array_name} v3 index must use an archive_pointer")
                        continue
                    if not isinstance(policy_entry, dict):
                        policy_errors.append(f"archive_policy arrays.{array_name} must be an object")
                        continue
                    for count_name in ("record_count", "chunk_count"):
                        pointer_count = pointer.get(count_name)
                        policy_count = policy_entry.get(count_name)
                        if type(pointer_count) is not int or type(policy_count) is not int or policy_count != pointer_count:
                            policy_errors.append(
                                f"archive_policy arrays.{array_name} {count_name} must match live pointer"
                            )
            expected_shards = source_shards + run_shards + limitation_shards
            if type(archive_policy.get("archive_shards_total")) is not int or archive_policy.get("archive_shards_total") != expected_shards:
                policy_errors.append("archive_policy archive_shards_total must match live pointer chunk totals")
        ledger_metrics = index.get("ledger_metrics")
        if isinstance(ledger_metrics, dict):
            expected_metrics = {
                "source_records": len(source_ids),
                "run_updates": len(run_updates),
                "limitations": len(limitations),
                "archive_shards": source_shards + run_shards + limitation_shards,
            }
            for metric_name, expected_value in expected_metrics.items():
                if metric_name in ledger_metrics and ledger_metrics.get(metric_name) != expected_value:
                    policy_errors.append(f"ledger_metrics.{metric_name} must match live archive pointers")
        errors.extend(policy_errors)
        archive_policy_counts_reconciled = not policy_errors

    latest = index.get("latest_snapshot")
    if not isinstance(latest, dict):
        errors.append("latest_snapshot must be an object")
        latest = {}

    # Source-revision addenda are index-level provenance pointers outside the
    # immutable source archive. Verify their paths, Git blob hashes and identity
    # fields; an unarchived source ID is permitted only while the addendum
    # explicitly declares pending_archive_append.
    revision_addenda = latest.get("source_revision_addenda", [])
    revision_errors: list[str] = []
    revision_checked = 0
    revision_pending_archive_append = 0
    seen_revision_paths: set[str] = set()
    seen_revision_ids: set[str] = set()
    if revision_addenda is None:
        revision_addenda = []
    if not isinstance(revision_addenda, list):
        revision_errors.append("latest_snapshot.source_revision_addenda must be a list")
        revision_addenda = []
    for position, pointer in enumerate(revision_addenda):
        if not isinstance(pointer, dict):
            revision_errors.append(f"source_revision_addenda[{position}] must be an object")
            continue
        relative_revision_path, revision_path_error = _safe_source_revision_path(pointer.get("path"))
        if revision_path_error:
            revision_errors.append(f"source_revision_addenda[{position}]: {revision_path_error}")
            continue
        path_key = str(relative_revision_path)
        if path_key in seen_revision_paths:
            revision_errors.append(f"duplicate source revision path: {path_key}")
        seen_revision_paths.add(path_key)
        expected_revision_sha = pointer.get("blob_sha")
        if not isinstance(expected_revision_sha, str) or not SHA1_RE.fullmatch(expected_revision_sha):
            revision_errors.append(f"source_revision_addenda[{position}] has invalid blob_sha")
            continue
        try:
            revision_raw = (repo_root / relative_revision_path).read_bytes()
        except OSError as exc:
            revision_errors.append(f"source_revision_addenda[{position}] cannot be read: {exc}")
            continue
        revision_checked += 1
        actual_revision_sha = git_blob_sha(revision_raw)
        if actual_revision_sha != expected_revision_sha:
            revision_errors.append(
                f"source_revision_addenda[{position}] Git blob SHA mismatch: "
                f"expected={expected_revision_sha}, actual={actual_revision_sha}"
            )
        try:
            revision = json.loads(revision_raw)
        except json.JSONDecodeError as exc:
            revision_errors.append(f"source_revision_addenda[{position}] JSON invalid: {exc}")
            continue
        if not isinstance(revision, dict):
            revision_errors.append(f"source_revision_addenda[{position}] must contain a JSON object")
            continue
        if revision.get("record_type") != "source_revision_addendum":
            revision_errors.append(f"source_revision_addenda[{position}] has wrong record_type")
        if revision.get("schema_version") != "1.0":
            revision_errors.append(f"source_revision_addenda[{position}] schema_version must be 1.0")
        revision_id = revision.get("revision_id")
        if not isinstance(revision_id, str) or not revision_id:
            revision_errors.append(f"source_revision_addenda[{position}] has no non-empty revision_id")
        else:
            if revision_id in seen_revision_ids:
                revision_errors.append(f"duplicate source revision ID: {revision_id}")
            seen_revision_ids.add(revision_id)
        if pointer.get("revision_id") != revision_id:
            revision_errors.append(f"source_revision_addenda[{position}] revision_id pointer mismatch")
        if pointer.get("captured_at_utc") != revision.get("captured_at_utc"):
            revision_errors.append(f"source_revision_addenda[{position}] captured_at_utc pointer mismatch")
        pointer_source_id = pointer.get("source_id")
        revision_source_id = revision.get("source_id")
        if pointer_source_id is not None and pointer_source_id != revision_source_id:
            revision_errors.append(f"source_revision_addenda[{position}] source_id pointer mismatch")
        pending_archive_append = revision.get("pending_archive_append")
        if type(pending_archive_append) is not bool:
            revision_errors.append(f"source_revision_addenda[{position}] pending_archive_append must be boolean")
        elif pending_archive_append:
            revision_pending_archive_append += 1
            pointer_status = str(pointer.get("status", ""))
            if "PENDING_ARCHIVE_APPEND" not in pointer_status:
                revision_errors.append(f"source_revision_addenda[{position}] pending archive status mismatch")
        elif isinstance(revision_source_id, str) and revision_source_id not in source_ids:
            revision_errors.append(
                f"source_revision_addenda[{position}] source_id is absent from archive but not marked pending"
            )
    errors.extend(revision_errors)

    is_pointer = latest.get("record_type") == "snapshot_reference"
    path_value = latest.get("snapshot_path")
    relative_path, path_error = _safe_snapshot_path(path_value)
    if path_error:
        errors.append(path_error)
        relative_path = None

    expected_sha = latest.get("snapshot_blob_sha")
    if not isinstance(expected_sha, str) or not SHA1_RE.fullmatch(expected_sha):
        errors.append("snapshot_blob_sha must be a 40-character lowercase Git blob SHA")

    snapshot: dict[str, Any] | None = None
    actual_sha: str | None = None
    if relative_path is not None:
        full_path = repo_root / relative_path
        try:
            raw = full_path.read_bytes()
            actual_sha = git_blob_sha(raw)
            if expected_sha != actual_sha:
                errors.append(f"snapshot blob SHA mismatch: expected={expected_sha}, actual={actual_sha}")
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                errors.append("snapshot file must contain a JSON object")
            else:
                snapshot = parsed
        except OSError as exc:
            errors.append(f"snapshot file cannot be read: {exc}")
        except json.JSONDecodeError as exc:
            errors.append(f"snapshot JSON is invalid: {exc}")

    if snapshot is not None:
        for field in ("captured_at_utc", "snapshot_id", "snapshot_path"):
            if latest.get(field) != snapshot.get(field):
                errors.append(f"snapshot reference {field} does not match snapshot file")
        if is_pointer:
            index_format_version = index.get("index_format_version")
            if index_format_version not in {"2.0", "3.0"}:
                errors.append("sharded ledger index_format_version must be 2.0 or 3.0")
            if latest.get("index_format_version") != index_format_version:
                errors.append("snapshot reference index_format_version must match ledger index_format_version")
            commit_sha = latest.get("snapshot_commit_sha")
            if not isinstance(commit_sha, str) or not SHA1_RE.fullmatch(commit_sha):
                errors.append("snapshot_commit_sha must be a 40-character lowercase SHA")
        else:
            legacy_payload = copy.deepcopy(latest)
            for field in INDEX_ONLY_FIELDS:
                legacy_payload.pop(field, None)
            if legacy_payload != snapshot:
                errors.append("legacy inline snapshot differs from its immutable snapshot file")

    missing_snapshot_source_ids: list[str] = []
    if snapshot is not None and isinstance(snapshot.get("source_ids"), list):
        missing_snapshot_source_ids = sorted(set(snapshot["source_ids"]) - set(source_ids))
        if missing_snapshot_source_ids:
            errors.append(f"snapshot references unknown source IDs: {missing_snapshot_source_ids}")

    return {
        "status": "PASS" if not errors else "BLOCKED",
        "errors": errors,
        "index_format_version": index.get("index_format_version", "legacy-inline"),
        "source_count": len(source_ids),
        "run_update_count": len(run_updates),
        "limitation_count": len(limitations),
        "archive_shards_checked": source_shards + run_shards + limitation_shards,
        "source_revision_addenda_checked": revision_checked,
        "source_revision_addenda_pending_archive_append": revision_pending_archive_append,
        "archive_policy_counts_reconciled": archive_policy_counts_reconciled,
        "snapshot_path": path_value,
        "snapshot_blob_sha_expected": expected_sha,
        "snapshot_blob_sha_actual": actual_sha,
        "snapshot_reference_mode": is_pointer,
        "state_mutated": False,
    }


def validate_index(index_path: Path = DEFAULT_INDEX, repo_root: Path = ROOT) -> dict[str, Any]:
    try:
        index = json.loads(index_path.read_bytes())
    except OSError as exc:
        return {"status": "BLOCKED", "errors": [f"index file cannot be read: {exc}"], "state_mutated": False}
    except json.JSONDecodeError as exc:
        return {"status": "BLOCKED", "errors": [f"index JSON is invalid: {exc}"], "state_mutated": False}
    return validate_index_data(index, repo_root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = validate_index(args.index, args.root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
