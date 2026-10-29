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


def validate_index_data(index: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(index, dict):
        return {"status": "BLOCKED", "errors": ["index must be a JSON object"]}
    if index.get("record_type") != "xrp_intelligence_research_ledger":
        errors.append("unexpected record_type")

    sources = index.get("sources")
    if not isinstance(sources, list):
        errors.append("sources must be a list")
        sources = []
    source_ids: list[str] = []
    for i, source in enumerate(sources):
        if not isinstance(source, dict) or not isinstance(source.get("id"), str) or not source["id"]:
            errors.append(f"sources[{i}] has no non-empty id")
        else:
            source_ids.append(source["id"])
    if len(source_ids) != len(set(source_ids)):
        errors.append("duplicate source IDs")

    run_updates = index.get("run_updates")
    if not isinstance(run_updates, list):
        errors.append("run_updates must be a list")
        run_updates = []

    latest = index.get("latest_snapshot")
    if not isinstance(latest, dict):
        errors.append("latest_snapshot must be an object")
        latest = {}

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
            if latest.get("index_format_version") != "2.0":
                errors.append("snapshot reference must declare index_format_version 2.0")
            commit_sha = latest.get("snapshot_commit_sha")
            if not isinstance(commit_sha, str) or not SHA1_RE.fullmatch(commit_sha):
                errors.append("snapshot_commit_sha must be a 40-character lowercase SHA")
        else:
            legacy_payload = copy.deepcopy(latest)
            for field in INDEX_ONLY_FIELDS:
                legacy_payload.pop(field, None)
            if legacy_payload != snapshot:
                errors.append("legacy inline snapshot differs from its immutable snapshot file")

    return {
        "status": "PASS" if not errors else "BLOCKED",
        "errors": errors,
        "index_format_version": index.get("index_format_version", "legacy-inline"),
        "source_count": len(source_ids),
        "run_update_count": len(run_updates),
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
