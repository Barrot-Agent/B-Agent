"""Artifact-backed, append-only recovery of the known XRP feature-store fork.

This module imports one verified historical snapshot into a later cumulative
checkpoint. It never rewrites prior snapshots or receipt chains. The new store
receipt time is the actual recovery time, so point-in-time queries cannot see
the recovered data before the recovery was performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .feature_store import FeatureStoreError, HistoricalFeatureStore
from .xrp_public_ingestion import RawReceiptArchive, XRPIngestionError


SCHEMA_VERSION = "barrot.xrp.historical-feature-store-reconciliation.v1"
SOURCE_RUN_ID = "44844953105"
FORK_RUN_ID = "44848909814"
COMMON_PARENT_RUN_ID = "44844499889"
COMMON_SNAPSHOT_ID = "4e74ae80bcc0542007b7fcb43b73fb139078289628fcff8393760419e302d342"
FORK_SNAPSHOT_ID = "8f820fa811e0e328c82c24beabd8e708a341598d13c796437176b4cd1b05efc0"
FORK_SNAPSHOT_MANIFEST_SHA256 = "16df765d3170da5e74cb615f58c57594e069ad541cdfa0584e5c77114fe96652"
BACKFILL_SNAPSHOT_ID = "0d5af2b3fdffb6ddb397579413c33218ed174f8e61969910adaef654ae9212aa"
BACKFILL_MANIFEST_SHA256 = "e19be22480a27170dc597835bfe8d9a3b1f9c61c3df03b33fa1ffbc5122d589c"
BACKFILL_RECORD_COUNT = 118
BACKFILL_SOURCE_COUNT = 11
INDEX_SCHEMA = "barrot.xrp.cross-run-receipt-chain.v1"


class XRPFeatureStoreBackfillError(ValueError):
    """A historical feature-store recovery failed a provenance or PIT gate."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iso(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise XRPFeatureStoreBackfillError("reconciliation clock must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise XRPFeatureStoreBackfillError(f"required JSON artifact is missing or unsafe: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise XRPFeatureStoreBackfillError(f"invalid JSON artifact: {path}") from exc
    if not isinstance(value, dict):
        raise XRPFeatureStoreBackfillError(f"JSON artifact must contain an object: {path}")
    return value


def _artifact_tree_sha256(root: Path) -> str:
    if root.is_symlink() or not root.is_dir():
        raise XRPFeatureStoreBackfillError(f"artifact root is missing or unsafe: {root}")
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise XRPFeatureStoreBackfillError("artifact trees cannot contain symbolic links")
        if path.is_file():
            entries.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": _sha256_file(path),
                }
            )
    if not entries:
        raise XRPFeatureStoreBackfillError(f"artifact tree is empty: {root}")
    return _sha256_bytes(_canonical(entries).encode("utf-8"))


def _verify_index(path: Path, expected_run_id: str | None = None) -> dict[str, Any]:
    payload = _read_json(path)
    if payload.get("schema_version") != INDEX_SCHEMA:
        raise XRPFeatureStoreBackfillError(f"unsupported receipt-index schema: {path}")
    stored_hash = payload.get("cross_run_chain_sha256")
    without_hash = {key: value for key, value in payload.items() if key != "cross_run_chain_sha256"}
    expected_hash = _sha256_bytes(_canonical(without_hash).encode("utf-8"))
    if stored_hash != expected_hash:
        raise XRPFeatureStoreBackfillError(f"cross-run receipt-index hash mismatch: {path}")
    sequence = payload.get("sequence")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        raise XRPFeatureStoreBackfillError(f"invalid cross-run sequence: {path}")
    run = payload.get("current_run")
    if not isinstance(run, Mapping):
        raise XRPFeatureStoreBackfillError(f"missing current-run identity: {path}")
    run_id = run.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise XRPFeatureStoreBackfillError(f"invalid current-run ID: {path}")
    if expected_run_id is not None and run_id != str(expected_run_id):
        raise XRPFeatureStoreBackfillError(
            f"receipt index run ID {run_id} does not match expected {expected_run_id}"
        )
    if run.get("repository") != "Barrot-Agent/B-Agent":
        raise XRPFeatureStoreBackfillError("receipt index belongs to an unexpected repository")
    if not str(run.get("workflow_ref") or "").endswith("@refs/heads/main"):
        raise XRPFeatureStoreBackfillError("receipt index was not produced by the main branch")
    if payload.get("continuity_verified") is not True:
        raise XRPFeatureStoreBackfillError("receipt index does not verify its own predecessor chain")
    current_chain = payload.get("current_receipt_chain")
    raw_artifact = payload.get("raw_artifact")
    if not isinstance(current_chain, Mapping) or not isinstance(raw_artifact, Mapping):
        raise XRPFeatureStoreBackfillError("receipt index is missing current receipt/raw-artifact metadata")
    if raw_artifact.get("run_id") != run_id:
        raise XRPFeatureStoreBackfillError("raw-artifact run ID does not match receipt-index run ID")
    if raw_artifact.get("artifact_name") != f"xrp-public-raw-{run_id}":
        raise XRPFeatureStoreBackfillError("raw-artifact name does not match receipt-index run ID")
    for field in ("manifest_sha256", "chain_head_sha256", "receipt_log_sha256", "chain_log_sha256"):
        value = current_chain.get(field)
        if not isinstance(value, str) or len(value) != 64:
            raise XRPFeatureStoreBackfillError(f"receipt index has an invalid {field}")
    if isinstance(current_chain.get("receipt_count"), bool) or not isinstance(current_chain.get("receipt_count"), int):
        raise XRPFeatureStoreBackfillError("receipt index has an invalid receipt count")
    if sequence > 1:
        previous = payload.get("previous")
        if not isinstance(previous, Mapping):
            raise XRPFeatureStoreBackfillError("continued receipt index has no predecessor")
        if previous.get("run_id") != payload.get("previous", {}).get("run_id"):
            raise XRPFeatureStoreBackfillError("receipt index predecessor identity is invalid")
        if previous.get("sequence") != sequence - 1:
            raise XRPFeatureStoreBackfillError("receipt index sequence does not follow its predecessor")
        if previous.get("cross_run_chain_sha256") != payload.get("previous_cross_run_chain_sha256"):
            raise XRPFeatureStoreBackfillError("receipt index predecessor chain hashes disagree")
        if previous.get("manifest_sha256") != payload.get("previous_manifest_sha256"):
            raise XRPFeatureStoreBackfillError("receipt index predecessor manifest hashes disagree")
    return payload


def _verify_index_chain(
    current_index_path: Path,
    ancestry_index_dir: Path,
    fork_run_id: str,
) -> list[dict[str, Any]]:
    if ancestry_index_dir.is_symlink() or not ancestry_index_dir.is_dir():
        raise XRPFeatureStoreBackfillError("receipt-index ancestry directory is missing or unsafe")
    index_by_run: dict[str, tuple[Path, dict[str, Any]]] = {}
    paths = [current_index_path, *sorted(ancestry_index_dir.glob("*.json"))]
    for path in paths:
        if not path.is_file():
            continue
        payload = _verify_index(path)
        run_id = str(payload["current_run"]["run_id"])
        existing = index_by_run.get(run_id)
        if existing is not None:
            if existing[0].read_bytes() != path.read_bytes():
                raise XRPFeatureStoreBackfillError(f"conflicting index artifacts for run {run_id}")
            continue
        index_by_run[run_id] = (path, payload)

    current_payload = _verify_index(current_index_path)
    current_run_id = str(current_payload["current_run"]["run_id"])
    path_from_current: list[dict[str, Any]] = [current_payload]
    visited = {current_run_id}
    while current_run_id != str(fork_run_id):
        current = path_from_current[-1]
        previous = current.get("previous")
        if not isinstance(previous, Mapping):
            raise XRPFeatureStoreBackfillError(
                f"main receipt chain ended before historical fork run {fork_run_id}"
            )
        parent_run_id = str(previous.get("run_id") or "")
        if not parent_run_id or parent_run_id in visited:
            raise XRPFeatureStoreBackfillError("receipt-index ancestry contains a missing parent or cycle")
        parent_entry = index_by_run.get(parent_run_id)
        if parent_entry is None:
            raise XRPFeatureStoreBackfillError(
                f"missing receipt-index artifact for predecessor run {parent_run_id}"
            )
        parent_path, parent = parent_entry
        if previous.get("cross_run_chain_sha256") != parent.get("cross_run_chain_sha256"):
            raise XRPFeatureStoreBackfillError("receipt-index parent chain hash does not match its child")
        if previous.get("manifest_sha256") != _sha256_file(parent_path):
            raise XRPFeatureStoreBackfillError("receipt-index parent manifest byte hash does not match its child")
        if previous.get("sequence") != parent.get("sequence"):
            raise XRPFeatureStoreBackfillError("receipt-index parent sequence does not match its child")
        if current.get("sequence") != parent.get("sequence") + 1:
            raise XRPFeatureStoreBackfillError("receipt-index sequence has a gap")
        if parent.get("current_run", {}).get("run_id") != parent_run_id:
            raise XRPFeatureStoreBackfillError("receipt-index parent run identity mismatch")
        visited.add(parent_run_id)
        path_from_current.append(parent)
        current_run_id = parent_run_id

    return list(reversed(path_from_current))


def _verify_raw_artifact(
    artifact_root: Path,
    index_path: Path,
    expected_run_id: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], str]:
    if artifact_root.is_symlink() or not artifact_root.is_dir():
        raise XRPFeatureStoreBackfillError(f"raw artifact root is missing or unsafe: {artifact_root}")
    raw_root = artifact_root / "raw"
    if raw_root.is_symlink() or not raw_root.is_dir():
        raise XRPFeatureStoreBackfillError("raw artifact is missing its content-addressed raw directory")
    index = _verify_index(index_path, expected_run_id)
    embedded_index_path = artifact_root / "cross_run_receipt_chain.json"
    embedded_index = _verify_index(embedded_index_path, expected_run_id)
    if _canonical(embedded_index) != _canonical(index):
        raise XRPFeatureStoreBackfillError("separate receipt-index artifact differs from raw-artifact index")
    receipt_manifest_path = artifact_root / "receipt_manifest.json"
    receipt_manifest = _read_json(receipt_manifest_path)
    manifest_bytes = receipt_manifest_path.read_bytes()
    verification = RawReceiptArchive(raw_root).verify()
    if receipt_manifest.get("verification_status") != "PASS":
        raise XRPFeatureStoreBackfillError("raw receipt manifest does not report PASS")
    for field, value in verification.items():
        if receipt_manifest.get(field) != value:
            raise XRPFeatureStoreBackfillError(f"raw receipt manifest disagrees on {field}")
    chain = index["current_receipt_chain"]
    if _sha256_bytes(manifest_bytes) != chain.get("manifest_sha256"):
        raise XRPFeatureStoreBackfillError("raw receipt-manifest bytes do not match the cross-run index")
    for field in (
        "chain_head_sha256",
        "receipt_log_sha256",
        "chain_log_sha256",
        "receipt_count",
    ):
        if verification.get(field) != chain.get(field):
            raise XRPFeatureStoreBackfillError(f"raw receipt chain does not match index field {field}")
    context = receipt_manifest.get("github_actions_context")
    if not isinstance(context, Mapping) or str(context.get("run_id")) != str(expected_run_id):
        raise XRPFeatureStoreBackfillError("raw receipt manifest run identity does not match its artifact")
    receipt_by_hash: dict[str, dict[str, Any]] = {}
    receipts_path = raw_root / "receipts.jsonl"
    for line_number, line in enumerate(receipts_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise XRPFeatureStoreBackfillError(f"raw receipt log has an empty line at {line_number}")
        receipt = json.loads(line)
        digest = receipt.get("raw_content_sha256")
        if not isinstance(digest, str) or digest in receipt_by_hash:
            raise XRPFeatureStoreBackfillError("raw receipt log has an invalid or duplicate content hash")
        receipt_by_hash[digest] = receipt
    return verification, receipt_by_hash, _artifact_tree_sha256(artifact_root)


def _verified_source_snapshot(
    source_database: Path,
    snapshot_id: str,
    expected_manifest_sha256: str,
    expected_record_count: int,
    expected_source_count: int,
    common_snapshot_id: str,
) -> tuple[dict[str, Any], list[dict[str, str]], str, str]:
    if source_database.is_symlink() or not source_database.is_file():
        raise XRPFeatureStoreBackfillError("source feature-store database is missing or unsafe")
    with tempfile.TemporaryDirectory(prefix="xrp-backfill-source-") as temp:
        copy_path = Path(temp) / "source.sqlite3"
        shutil.copy2(source_database, copy_path)
        source_store = HistoricalFeatureStore(copy_path)
        verification = source_store.verify_all_snapshots()
        if verification.get("valid") is not True:
            raise XRPFeatureStoreBackfillError("source feature-store artifact failed full snapshot verification")
        exact = source_store.verified_snapshot(snapshot_id)
        manifest = exact["manifest"]
        manifest_sha = _sha256_bytes(_canonical(manifest).encode("utf-8"))
        if manifest_sha != expected_manifest_sha256:
            raise XRPFeatureStoreBackfillError("source snapshot manifest hash does not match the pinned value")
        if len(manifest.get("records", [])) != expected_record_count:
            raise XRPFeatureStoreBackfillError("source snapshot record count does not match the pinned value")
        if manifest.get("eligible_record_count") != expected_record_count:
            raise XRPFeatureStoreBackfillError("source snapshot eligible count does not match the pinned value")
        lineage = source_store.source_lineage(snapshot_id)
        if len(lineage) != expected_source_count:
            raise XRPFeatureStoreBackfillError("source snapshot source count does not match the pinned value")
        common = source_store.verified_snapshot(common_snapshot_id)
        common_manifest_sha = _sha256_bytes(_canonical(common["manifest"]).encode("utf-8"))
        if any(record.get("model_eligible") is not True for record in manifest["records"]):
            raise XRPFeatureStoreBackfillError("source snapshot contains a non-eligible model record")
        return (
            {
                "snapshot_id": exact["snapshot_id"],
                "data_cutoff_utc": exact["data_cutoff_utc"],
                "captured_at_utc": exact["captured_at_utc"],
                "source_stored_at_utc": exact["stored_at_utc"],
                "manifest": manifest,
                "manifest_sha256": manifest_sha,
                "record_count": expected_record_count,
                "source_count": expected_source_count,
                "verification": exact["verification"],
            },
            lineage,
            _sha256_file(source_database),
            common_manifest_sha,
        )


def _verify_source_lineage(
    lineage: list[dict[str, str]],
    receipt_by_hash: Mapping[str, Mapping[str, Any]],
) -> None:
    for source in lineage:
        receipt = receipt_by_hash.get(source["raw_content_sha256"])
        if receipt is None:
            raise XRPFeatureStoreBackfillError(
                f"source {source['source_id']} has no matching raw receipt"
            )
        if (
            receipt.get("source_id") != source["source_id"]
            or receipt.get("source_uri") != source["source_uri"]
            or receipt.get("raw_bytes_retained") is not True
        ):
            raise XRPFeatureStoreBackfillError(
                f"source {source['source_id']} raw receipt does not match snapshot lineage"
            )


def _verify_sibling_fork(
    source_index: Mapping[str, Any],
    fork_index: Mapping[str, Any],
    parent_run_id: str,
) -> None:
    source_previous = source_index.get("previous")
    fork_previous = fork_index.get("previous")
    if not isinstance(source_previous, Mapping) or not isinstance(fork_previous, Mapping):
        raise XRPFeatureStoreBackfillError("historical fork heads do not both have a predecessor")
    if (
        source_previous.get("run_id") != str(parent_run_id)
        or fork_previous.get("run_id") != str(parent_run_id)
        or source_previous.get("sequence") != 1
        or fork_previous.get("sequence") != 1
        or source_previous.get("cross_run_chain_sha256") != fork_previous.get("cross_run_chain_sha256")
        or source_previous.get("manifest_sha256") != fork_previous.get("manifest_sha256")
    ):
        raise XRPFeatureStoreBackfillError("historical receipt indexes are not sibling heads of the expected parent")
    if source_index.get("sequence") != 2 or fork_index.get("sequence") != 2:
        raise XRPFeatureStoreBackfillError("historical fork heads are not both sequence two")
    if source_index.get("cross_run_chain_sha256") == fork_index.get("cross_run_chain_sha256"):
        raise XRPFeatureStoreBackfillError("historical fork heads unexpectedly share the same chain hash")
    if source_index.get("current_run", {}).get("sha") != fork_index.get("current_run", {}).get("sha"):
        raise XRPFeatureStoreBackfillError("historical sibling runs were not captured from the same main commit")


def _record_ids(records: list[dict[str, Any]]) -> set[str]:
    return {str(record["record_id"]) for record in records}


def _verify_visibility(
    store: HistoricalFeatureStore,
    manifest: Mapping[str, Any],
    stored_at_utc: str,
) -> dict[str, Any]:
    stored_at = datetime.fromisoformat(stored_at_utc.replace("Z", "+00:00"))
    before_at = _iso(stored_at - timedelta(microseconds=1))
    after_at = _iso(stored_at + timedelta(microseconds=1))
    expected_ids = _record_ids(list(manifest.get("records", [])))
    before_records = store.records_through("XRP", before_at)
    after_records = store.records_through("XRP", after_at)
    before_ids = _record_ids(before_records)
    after_ids = _record_ids(after_records)
    if expected_ids & before_ids:
        raise XRPFeatureStoreBackfillError("backfilled records are visible before their actual store receipt time")
    missing_after = sorted(expected_ids - after_ids)
    if missing_after:
        raise XRPFeatureStoreBackfillError(
            f"backfilled records are not visible after their store receipt time: {len(missing_after)} missing"
        )
    return {
        "before_as_of_utc": before_at,
        "after_as_of_utc": after_at,
        "backfilled_record_count": len(expected_ids),
        "visible_before_receipt": False,
        "visible_after_receipt": True,
        "before_record_count": len(before_records),
        "after_record_count": len(after_records),
    }


def verify_existing_reconciliation(
    target_database: str | Path,
    receipt_path: str | Path,
) -> dict[str, Any]:
    target_path = Path(target_database)
    receipt_file = Path(receipt_path)
    receipt = _read_json(receipt_file)
    if receipt.get("schema_version") != SCHEMA_VERSION or receipt.get("status") != "RECONCILED":
        raise XRPFeatureStoreBackfillError("existing reconciliation receipt has an unsupported schema or status")
    stored_hash = receipt.get("reconciliation_sha256")
    without_hash = {key: value for key, value in receipt.items() if key != "reconciliation_sha256"}
    if stored_hash != _sha256_bytes(_canonical(without_hash).encode("utf-8")):
        raise XRPFeatureStoreBackfillError("existing reconciliation receipt hash mismatch")
    snapshot = receipt.get("backfill_snapshot")
    if not isinstance(snapshot, Mapping):
        raise XRPFeatureStoreBackfillError("existing reconciliation receipt has no backfill snapshot")
    store = HistoricalFeatureStore(target_path)
    exact = store.verified_snapshot(str(snapshot.get("snapshot_id") or ""))
    manifest = exact["manifest"]
    if (
        _sha256_bytes(_canonical(manifest).encode("utf-8")) != snapshot.get("manifest_sha256")
        or exact["stored_at_utc"] != snapshot.get("stored_at_utc")
        or len(manifest.get("records", [])) != snapshot.get("record_count")
    ):
        raise XRPFeatureStoreBackfillError("existing reconciliation receipt does not match the restored feature store")
    visibility = _verify_visibility(store, manifest, exact["stored_at_utc"])
    if receipt.get("point_in_time_visibility") != visibility:
        raise XRPFeatureStoreBackfillError("existing reconciliation point-in-time visibility evidence has changed")
    return {
        "status": "VERIFIED_EXISTING",
        "snapshot_id": exact["snapshot_id"],
        "stored_at_utc": exact["stored_at_utc"],
        "reconciliation_sha256": stored_hash,
        "feature_store": store.verify_all_snapshots(),
        "point_in_time_visibility": visibility,
    }


def reconcile_historical_snapshot(
    *,
    target_database: str | Path,
    source_database: str | Path,
    source_raw_artifact_root: str | Path,
    source_index_path: str | Path,
    fork_raw_artifact_root: str | Path,
    fork_index_path: str | Path,
    ancestry_index_dir: str | Path,
    current_index_path: str | Path,
    output_path: str | Path,
    artifact_inventory_path: str | Path | None = None,
    source_run_id: str = SOURCE_RUN_ID,
    fork_run_id: str = FORK_RUN_ID,
    common_parent_run_id: str = COMMON_PARENT_RUN_ID,
    common_snapshot_id: str = COMMON_SNAPSHOT_ID,
    fork_snapshot_id: str = FORK_SNAPSHOT_ID,
    fork_snapshot_manifest_sha256: str = FORK_SNAPSHOT_MANIFEST_SHA256,
    backfill_snapshot_id: str = BACKFILL_SNAPSHOT_ID,
    backfill_manifest_sha256: str = BACKFILL_MANIFEST_SHA256,
    expected_record_count: int = BACKFILL_RECORD_COUNT,
    expected_source_count: int = BACKFILL_SOURCE_COUNT,
    clock: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    output_file = Path(output_path)
    if output_file.exists():
        return verify_existing_reconciliation(target_database, output_file)

    source_index_file = Path(source_index_path)
    fork_index_file = Path(fork_index_path)
    source_index = _verify_index(source_index_file, source_run_id)
    fork_index = _verify_index(fork_index_file, fork_run_id)
    _verify_sibling_fork(source_index, fork_index, common_parent_run_id)

    source_raw_verification, source_receipts, source_raw_tree_sha = _verify_raw_artifact(
        Path(source_raw_artifact_root), source_index_file, source_run_id
    )
    fork_raw_verification, _, fork_raw_tree_sha = _verify_raw_artifact(
        Path(fork_raw_artifact_root), fork_index_file, fork_run_id
    )
    source_snapshot, source_lineage, source_database_sha = _verified_source_snapshot(
        Path(source_database),
        backfill_snapshot_id,
        backfill_manifest_sha256,
        expected_record_count,
        expected_source_count,
        common_snapshot_id,
    )
    _verify_source_lineage(source_lineage, source_receipts)

    lineage = _verify_index_chain(
        Path(current_index_path),
        Path(ancestry_index_dir),
        fork_run_id,
    )
    if not lineage or lineage[0]["current_run"]["run_id"] != str(fork_run_id):
        raise XRPFeatureStoreBackfillError("main receipt chain does not begin at the expected fork head")
    current_index = _verify_index(Path(current_index_path))
    if lineage[-1]["current_run"]["run_id"] != current_index["current_run"]["run_id"]:
        raise XRPFeatureStoreBackfillError("main receipt chain does not terminate at the supplied current index")
    if any(item["current_run"]["run_id"] == str(source_run_id) for item in lineage):
        raise XRPFeatureStoreBackfillError("the source sibling fork was incorrectly included in the main lineage")

    artifact_inventory: dict[str, Any] = {}
    if artifact_inventory_path is not None:
        artifact_inventory = _read_json(Path(artifact_inventory_path))

    target_path = Path(target_database)
    if target_path.is_symlink() or not target_path.is_file():
        raise XRPFeatureStoreBackfillError("cumulative target feature-store checkpoint is missing or unsafe")
    store_receipt_clock = clock or (lambda: datetime.now(timezone.utc))
    recovery_clock_value = store_receipt_clock()
    if not isinstance(recovery_clock_value, datetime) or recovery_clock_value.tzinfo is None or recovery_clock_value.utcoffset() is None:
        raise XRPFeatureStoreBackfillError("feature-store recovery clock must be timezone-aware")
    recovery_clock_value = recovery_clock_value.astimezone(timezone.utc)
    target_store = HistoricalFeatureStore(target_path, clock=lambda: recovery_clock_value)
    before_verification = target_store.verify_all_snapshots()
    if before_verification.get("valid") is not True:
        raise XRPFeatureStoreBackfillError("cumulative target feature store failed pre-backfill verification")

    common = target_store.verified_snapshot(common_snapshot_id)
    common_manifest_sha = _sha256_bytes(_canonical(common["manifest"]).encode("utf-8"))
    if common_manifest_sha != source_common_manifest_sha:
        raise XRPFeatureStoreBackfillError("source and target common-ancestor snapshot manifests differ")
    fork_snapshot = target_store.verified_snapshot(fork_snapshot_id)
    fork_manifest_sha = _sha256_bytes(_canonical(fork_snapshot["manifest"]).encode("utf-8"))
    if fork_manifest_sha != fork_snapshot_manifest_sha256:
        raise XRPFeatureStoreBackfillError("cumulative target does not contain the verified historical main-branch fork snapshot")

    existing_snapshot = None
    try:
        existing_snapshot = target_store.verified_snapshot(backfill_snapshot_id)
    except FeatureStoreError as exc:
        if "unknown snapshot_id" not in str(exc):
            raise XRPFeatureStoreBackfillError("existing backfill snapshot failed verification") from exc

    if existing_snapshot is None:
        receipt_time = recovery_clock_value
        receipt_time_s = _iso(receipt_time)
        stored = target_store.append_snapshot(source_snapshot["manifest"])
        if stored.get("created") is not True or stored.get("stored_at_utc") != receipt_time_s:
            raise XRPFeatureStoreBackfillError("append-only feature-store backfill did not create the expected store receipt")
        existing_snapshot = target_store.verified_snapshot(backfill_snapshot_id)
    else:
        receipt_time_s = existing_snapshot["stored_at_utc"]
        if datetime.fromisoformat(receipt_time_s.replace("Z", "+00:00")) <= datetime.fromisoformat(
            existing_snapshot["captured_at_utc"].replace("Z", "+00:00")
        ):
            raise XRPFeatureStoreBackfillError("existing backfill snapshot was stored at or before its source capture")

    if _sha256_bytes(_canonical(existing_snapshot["manifest"]).encode("utf-8")) != backfill_manifest_sha256:
        raise XRPFeatureStoreBackfillError("target backfill snapshot manifest differs from the verified source")
    visibility = _verify_visibility(target_store, existing_snapshot["manifest"], receipt_time_s)
    after_verification = target_store.verify_all_snapshots()
    if after_verification.get("valid") is not True:
        raise XRPFeatureStoreBackfillError("cumulative feature store failed post-backfill verification")
    checkpoint = target_store.checkpoint()
    target_database_sha = _sha256_file(target_path)

    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "RECONCILED",
        "reconciliation_created_at_utc": _iso(store_receipt_clock()),
        "repository": "Barrot-Agent/B-Agent",
        "main_index": {
            "run_id": lineage[-1]["current_run"]["run_id"],
            "sequence": lineage[-1]["sequence"],
            "cross_run_chain_sha256": lineage[-1]["cross_run_chain_sha256"],
            "index_file_sha256": _sha256_file(Path(current_index_path)),
        },
        "historical_fork": {
            "common_parent_run_id": str(common_parent_run_id),
            "common_parent_chain_sha256": source_index["previous_cross_run_chain_sha256"],
            "sibling_heads": [
                {
                    "run_id": str(source_run_id),
                    "sequence": source_index["sequence"],
                    "cross_run_chain_sha256": source_index["cross_run_chain_sha256"],
                    "index_file_sha256": _sha256_file(source_index_file),
                    "raw_receipt_count": source_raw_verification["receipt_count"],
                    "retained_raw_payload_count": source_raw_verification["retained_raw_payload_count"],
                    "raw_artifact_tree_sha256": source_raw_tree_sha,
                },
                {
                    "run_id": str(fork_run_id),
                    "sequence": fork_index["sequence"],
                    "cross_run_chain_sha256": fork_index["cross_run_chain_sha256"],
                    "index_file_sha256": _sha256_file(fork_index_file),
                    "raw_receipt_count": fork_raw_verification["receipt_count"],
                    "retained_raw_payload_count": fork_raw_verification["retained_raw_payload_count"],
                    "raw_artifact_tree_sha256": fork_raw_tree_sha,
                },
            ],
            "main_lineage_from_fork": [
                {
                    "run_id": item["current_run"]["run_id"],
                    "sequence": item["sequence"],
                    "cross_run_chain_sha256": item["cross_run_chain_sha256"],
                }
                for item in lineage
            ],
            "prior_receipts_rewritten": False,
        },
        "source_feature_store_artifact": {
            "run_id": str(source_run_id),
            "database_sha256": source_database_sha,
            "snapshot_id": source_snapshot["snapshot_id"],
            "source_manifest_sha256": source_snapshot["manifest_sha256"],
            "source_stored_at_utc": source_snapshot["source_stored_at_utc"],
            "record_count": source_snapshot["record_count"],
            "source_count": source_snapshot["source_count"],
            "raw_source_lineage_verified": True,
            "raw_receipt_log_sha256": source_raw_verification["receipt_log_sha256"],
            "raw_chain_log_sha256": source_raw_verification["chain_log_sha256"],
        },
        "backfill_snapshot": {
            "snapshot_id": existing_snapshot["snapshot_id"],
            "manifest_sha256": backfill_manifest_sha256,
            "captured_at_utc": existing_snapshot["captured_at_utc"],
            "stored_at_utc": existing_snapshot["stored_at_utc"],
            "record_count": expected_record_count,
            "source_count": expected_source_count,
            "store_receipt_time_is_actual_recovery_time": True,
        },
        "feature_store_after": {
            "snapshot_count": after_verification["snapshot_count"],
            "verified_snapshot_count": after_verification["verified_count"],
            "record_count": visibility["after_record_count"],
            "database_sha256_after_checkpoint": target_database_sha,
            "checkpoint": checkpoint,
        },
        "point_in_time_visibility": visibility,
        "artifact_inventory": artifact_inventory,
        "external_anchor_status": "NOT_ANCHORED",
        "limitations": [
            "This reconciliation links both historical sibling receipt-chain heads and verifies the current main lineage; it does not rewrite either prior chain.",
            "GitHub Actions artifacts are retention-limited and are not independent WORM storage or a trusted timestamp authority.",
            "The actual feature-store receipt time prevents this recovered snapshot from appearing in earlier as-of views; it does not change the source capture time.",
            "A verified historical feature-store backfill is not a market-data quality certificate, a walk-forward result, or permission to issue forecasts.",
        ],
    }
    receipt["reconciliation_sha256"] = _sha256_bytes(_canonical(receipt).encode("utf-8"))
    output_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output_file.open("x", encoding="utf-8") as handle:
            handle.write(_canonical(receipt) + "\n")
            handle.flush()
    except FileExistsError:
        return verify_existing_reconciliation(target_database, output_file)
    return {
        "status": "RECONCILED",
        "reconciliation_sha256": receipt["reconciliation_sha256"],
        "receipt_path": str(output_file),
        "backfill_snapshot": receipt["backfill_snapshot"],
        "feature_store_after": receipt["feature_store_after"],
        "point_in_time_visibility": visibility,
        "main_lineage_run_ids": [item["current_run"]["run_id"] for item in lineage],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify or append the pinned historical XRP feature-store snapshot.")
    parser.add_argument("--target-db", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--verify-existing", action="store_true")
    parser.add_argument("--source-db")
    parser.add_argument("--source-raw-artifact-root")
    parser.add_argument("--source-index")
    parser.add_argument("--fork-raw-artifact-root")
    parser.add_argument("--fork-index")
    parser.add_argument("--ancestry-index-dir")
    parser.add_argument("--current-index")
    parser.add_argument("--artifact-inventory")
    args = parser.parse_args()
    try:
        if args.verify_existing:
            result = verify_existing_reconciliation(args.target_db, args.output)
        else:
            required = (
                args.source_db,
                args.source_raw_artifact_root,
                args.source_index,
                args.fork_raw_artifact_root,
                args.fork_index,
                args.ancestry_index_dir,
                args.current_index,
            )
            if any(not value for value in required):
                raise XRPFeatureStoreBackfillError("all source, fork and current-index paths are required")
            result = reconcile_historical_snapshot(
                target_database=args.target_db,
                source_database=args.source_db,
                source_raw_artifact_root=args.source_raw_artifact_root,
                source_index_path=args.source_index,
                fork_raw_artifact_root=args.fork_raw_artifact_root,
                fork_index_path=args.fork_index,
                ancestry_index_dir=args.ancestry_index_dir,
                current_index_path=args.current_index,
                output_path=args.output,
                artifact_inventory_path=args.artifact_inventory,
            )
        print(json.dumps(result, indent=2, sort_keys=True))
    except (XRPFeatureStoreBackfillError, FeatureStoreError, XRPIngestionError, OSError, ValueError) as exc:
        print(f"XRP historical feature-store reconciliation blocked: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
