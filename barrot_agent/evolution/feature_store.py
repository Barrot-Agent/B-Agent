"""Local SQLite storage for point-in-time feature snapshots.

The store records the exact validated manifest and its source lineage. A
snapshot is visible to an as-of query only after its store receipt time, which
prevents a historical backfill created today from masquerading as data that
Barrot possessed in the past. SQL triggers deter ordinary application-level
updates/deletes, and verify_snapshot cross-checks rows against the manifest.
This is not an adversarial tamper-proof boundary: a file owner can drop triggers
or rewrite the database and recompute unkeyed hashes. Production use needs an
external signed/checkpointed receipt or independently controlled immutable log.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .point_in_time_features import FeatureSnapshotError, validate_feature_record

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SCHEMA_VERSION = 1


class FeatureStoreError(ValueError):
    """A feature snapshot cannot be safely persisted or retrieved."""


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _utc(value: Any, field: str) -> tuple[datetime, str]:
    if not isinstance(value, str) or not value.strip():
        raise FeatureStoreError(f"{field} must be a timezone-aware ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise FeatureStoreError(f"{field} is not valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise FeatureStoreError(f"{field} must include a timezone")
    normalized = parsed.astimezone(timezone.utc)
    return normalized, normalized.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _validate_manifest(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, Mapping):
        raise FeatureStoreError("snapshot must be a mapping")
    required = (
        "snapshot_id",
        "asset_scope",
        "cutoff_utc",
        "captured_at_utc",
        "input_record_count",
        "eligible_record_count",
        "excluded_record_count",
        "source_ids",
        "source_independence_groups",
        "unique_source_independence_group_count",
        "records",
    )
    missing = [key for key in required if key not in snapshot]
    if missing:
        raise FeatureStoreError("snapshot missing fields: " + ", ".join(missing))

    snapshot_id = snapshot["snapshot_id"]
    if not isinstance(snapshot_id, str) or not _SHA256.fullmatch(snapshot_id):
        raise FeatureStoreError("snapshot_id must be a SHA-256 hex digest")

    manifest_without_id = dict(snapshot)
    manifest_without_id.pop("snapshot_id")
    if _sha256(_canonical(manifest_without_id)) != snapshot_id:
        raise FeatureStoreError("snapshot_id does not match the canonical manifest")

    cutoff, cutoff_s = _utc(snapshot["cutoff_utc"], "cutoff_utc")
    captured, captured_s = _utc(snapshot["captured_at_utc"], "captured_at_utc")
    if captured < cutoff:
        raise FeatureStoreError("captured_at_utc cannot precede cutoff_utc")

    assets = snapshot["asset_scope"]
    if not isinstance(assets, list) or not assets or any(
        not isinstance(item, str) or not item.strip() for item in assets
    ):
        raise FeatureStoreError("asset_scope must be a non-empty list of strings")
    normalized_assets = sorted({item.strip().upper() for item in assets})

    records = snapshot["records"]
    if not isinstance(records, list) or not records:
        raise FeatureStoreError("records must be a non-empty list")
    if snapshot["eligible_record_count"] != len(records):
        raise FeatureStoreError("eligible_record_count does not match records")
    if snapshot["input_record_count"] != (
        snapshot["eligible_record_count"] + snapshot["excluded_record_count"]
    ):
        raise FeatureStoreError("input_record_count does not reconcile to eligible and excluded")

    record_ids = []
    normalized_sources: dict[str, dict[str, str]] = {}
    groups: set[str] = set()
    normalized_records = []
    for record in records:
        try:
            checked = validate_feature_record(
                record,
                cutoff_s,
                captured_at_utc=captured_s,
            )
        except FeatureSnapshotError as exc:
            raise FeatureStoreError(f"invalid stored feature record: {exc}") from exc
        if not checked["eligible"]:
            raise FeatureStoreError(
                "model-facing snapshot contains an ineligible record: "
                + ",".join(checked["exclusion_reasons"])
            )
        normalized = checked["record"]
        if record != normalized:
            raise FeatureStoreError("feature record must be in canonical normalized form")
        if record.get("normalized_content_sha256") != normalized["normalized_content_sha256"]:
            raise FeatureStoreError("normalized feature content hash does not match")
        record_ids.append(normalized["record_id"])
        normalized_records.append(normalized)
        for source in normalized["sources"]:
            source_id = source["source_id"]
            previous = normalized_sources.get(source_id)
            if previous is not None and previous != source:
                raise FeatureStoreError(
                    f"source_id {source_id!r} has conflicting provenance in one snapshot"
                )
            normalized_sources[source_id] = source
            groups.add(source["independence_group"])

    if len(record_ids) != len(set(record_ids)):
        raise FeatureStoreError("snapshot contains duplicate record IDs")
    if not set(record["asset"] for record in normalized_records).issubset(set(normalized_assets)):
        raise FeatureStoreError("record asset is outside asset_scope")

    source_ids = sorted(normalized_sources)
    declared_source_ids = snapshot["source_ids"]
    if not isinstance(declared_source_ids, list) or sorted(set(declared_source_ids)) != source_ids:
        raise FeatureStoreError("source_ids does not match feature record provenance")
    declared_groups = snapshot["source_independence_groups"]
    if not isinstance(declared_groups, list) or sorted(set(declared_groups)) != sorted(groups):
        raise FeatureStoreError("source_independence_groups does not match feature record provenance")
    if snapshot["unique_source_independence_group_count"] != len(groups):
        raise FeatureStoreError("unique source independence group count does not match provenance")

    return {
        "snapshot_id": snapshot_id,
        "cutoff_utc": cutoff_s,
        "captured_at_utc": captured_s,
        "asset_scope": normalized_assets,
        "records": normalized_records,
        "sources": [normalized_sources[key] for key in source_ids],
        "source_count": len(source_ids),
        "manifest_json": _canonical(dict(snapshot)),
        "manifest_sha256": _sha256(_canonical(dict(snapshot))),
    }


class HistoricalFeatureStore:
    """Append-only local store with point-in-time retrieval semantics."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        clock: Callable[[], datetime] | None = None,
    ):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.database_path), timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 30000")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, _SCHEMA_VERSION):
                raise FeatureStoreError(
                    f"unsupported feature-store schema version {version}"
                )
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    data_cutoff_utc TEXT NOT NULL,
                    captured_at_utc TEXT NOT NULL,
                    stored_at_utc TEXT NOT NULL,
                    asset_scope_json TEXT NOT NULL,
                    manifest_json TEXT NOT NULL,
                    manifest_sha256 TEXT NOT NULL,
                    record_count INTEGER NOT NULL,
                    source_count INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS feature_records (
                    snapshot_id TEXT NOT NULL REFERENCES snapshots(snapshot_id) ON DELETE RESTRICT,
                    record_id TEXT NOT NULL,
                    feature_id TEXT NOT NULL,
                    asset TEXT NOT NULL,
                    event_time_utc TEXT NOT NULL,
                    known_at_utc TEXT NOT NULL,
                    source_data_as_of_utc TEXT NOT NULL,
                    ingested_at_utc TEXT NOT NULL,
                    revision_available_at_utc TEXT NOT NULL,
                    quality_status TEXT NOT NULL,
                    model_eligible INTEGER NOT NULL CHECK (model_eligible IN (0, 1)),
                    source_ids_json TEXT NOT NULL,
                    record_json TEXT NOT NULL,
                    PRIMARY KEY (snapshot_id, record_id)
                );

                CREATE TABLE IF NOT EXISTS source_snapshots (
                    snapshot_id TEXT NOT NULL REFERENCES snapshots(snapshot_id) ON DELETE RESTRICT,
                    source_id TEXT NOT NULL,
                    independence_group TEXT NOT NULL,
                    source_uri TEXT NOT NULL,
                    raw_content_sha256 TEXT NOT NULL,
                    PRIMARY KEY (snapshot_id, source_id)
                );

                CREATE INDEX IF NOT EXISTS idx_feature_records_asof
                    ON feature_records(asset, feature_id, known_at_utc, source_data_as_of_utc);
                CREATE INDEX IF NOT EXISTS idx_snapshots_cutoff
                    ON snapshots(data_cutoff_utc, stored_at_utc);

                CREATE TRIGGER IF NOT EXISTS snapshots_no_update
                BEFORE UPDATE ON snapshots
                BEGIN SELECT RAISE(ABORT, 'append-only feature store'); END;

                CREATE TRIGGER IF NOT EXISTS snapshots_no_delete
                BEFORE DELETE ON snapshots
                BEGIN SELECT RAISE(ABORT, 'append-only feature store'); END;

                CREATE TRIGGER IF NOT EXISTS feature_records_no_update
                BEFORE UPDATE ON feature_records
                BEGIN SELECT RAISE(ABORT, 'append-only feature store'); END;

                CREATE TRIGGER IF NOT EXISTS feature_records_no_delete
                BEFORE DELETE ON feature_records
                BEGIN SELECT RAISE(ABORT, 'append-only feature store'); END;

                CREATE TRIGGER IF NOT EXISTS source_snapshots_no_update
                BEFORE UPDATE ON source_snapshots
                BEGIN SELECT RAISE(ABORT, 'append-only feature store'); END;

                CREATE TRIGGER IF NOT EXISTS source_snapshots_no_delete
                BEFORE DELETE ON source_snapshots
                BEGIN SELECT RAISE(ABORT, 'append-only feature store'); END;
                """
            )
            if version == 0:
                connection.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")

    def append_snapshot(self, snapshot: Mapping[str, Any]) -> dict[str, Any]:
        """Validate and append a complete manifest; receipt time cannot precede capture."""
        validated = _validate_manifest(snapshot)
        stored_at = self._clock()
        if not isinstance(stored_at, datetime) or stored_at.tzinfo is None or stored_at.utcoffset() is None:
            raise FeatureStoreError("feature-store clock must return a timezone-aware datetime")
        stored_at = stored_at.astimezone(timezone.utc)
        captured = datetime.fromisoformat(
            validated["captured_at_utc"].replace("Z", "+00:00")
        )
        if captured > stored_at:
            raise FeatureStoreError("captured_at_utc cannot be later than store receipt time")
        stored_at_s = stored_at.isoformat(timespec="microseconds").replace("+00:00", "Z")

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT manifest_json, manifest_sha256, stored_at_utc "
                "FROM snapshots WHERE snapshot_id = ?",
                (validated["snapshot_id"],),
            ).fetchone()
            if existing is not None:
                if (
                    existing["manifest_json"] != validated["manifest_json"]
                    or existing["manifest_sha256"] != validated["manifest_sha256"]
                ):
                    raise FeatureStoreError("snapshot_id already exists with different content")
                return {
                    "snapshot_id": validated["snapshot_id"],
                    "created": False,
                    "stored_at_utc": existing["stored_at_utc"],
                    "record_count": len(validated["records"]),
                    "source_count": validated["source_count"],
                }

            connection.execute(
                """
                INSERT INTO snapshots (
                    snapshot_id, data_cutoff_utc, captured_at_utc, stored_at_utc,
                    asset_scope_json, manifest_json, manifest_sha256, record_count, source_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    validated["snapshot_id"],
                    validated["cutoff_utc"],
                    validated["captured_at_utc"],
                    stored_at_s,
                    _canonical(validated["asset_scope"]),
                    validated["manifest_json"],
                    validated["manifest_sha256"],
                    len(validated["records"]),
                    validated["source_count"],
                ),
            )
            for record in validated["records"]:
                source_ids = [source["source_id"] for source in record["sources"]]
                connection.execute(
                    """
                    INSERT INTO feature_records (
                        snapshot_id, record_id, feature_id, asset, event_time_utc,
                        known_at_utc, source_data_as_of_utc, ingested_at_utc,
                        revision_available_at_utc, quality_status, model_eligible,
                        source_ids_json, record_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        validated["snapshot_id"],
                        record["record_id"],
                        record["feature_id"],
                        record["asset"],
                        record["event_time_utc"],
                        record["known_at_utc"],
                        record["source_data_as_of_utc"],
                        record["ingested_at_utc"],
                        record["revision_available_at_utc"],
                        record["quality_status"],
                        1 if record["model_eligible"] else 0,
                        _canonical(source_ids),
                        _canonical(record),
                    ),
                )
            for source in validated["sources"]:
                connection.execute(
                    """
                    INSERT INTO source_snapshots (
                        snapshot_id, source_id, independence_group, source_uri, raw_content_sha256
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        validated["snapshot_id"],
                        source["source_id"],
                        source["independence_group"],
                        source["source_uri"],
                        source["raw_content_sha256"],
                    ),
                )

        return {
            "snapshot_id": validated["snapshot_id"],
            "created": True,
            "stored_at_utc": stored_at_s,
            "record_count": len(validated["records"]),
            "source_count": validated["source_count"],
        }

    def verified_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        """Return one exact snapshot only after full manifest, row and lineage verification."""
        if not isinstance(snapshot_id, str) or not _SHA256.fullmatch(snapshot_id):
            raise FeatureStoreError("snapshot_id must be a SHA-256 hex digest")
        verification = self.verify_snapshot(snapshot_id)
        if not verification["valid"]:
            raise FeatureStoreError(
                f"snapshot integrity verification failed for {snapshot_id}"
            )
        with self._connect() as connection:
            row = connection.execute(
                "SELECT snapshot_id, data_cutoff_utc, captured_at_utc, stored_at_utc, "
                "asset_scope_json, manifest_json FROM snapshots WHERE snapshot_id = ?",
                (snapshot_id,),
            ).fetchone()
        if row is None:
            raise FeatureStoreError(f"unknown snapshot_id {snapshot_id}")
        return {
            "snapshot_id": row["snapshot_id"],
            "data_cutoff_utc": row["data_cutoff_utc"],
            "captured_at_utc": row["captured_at_utc"],
            "stored_at_utc": row["stored_at_utc"],
            "asset_scope": json.loads(row["asset_scope_json"]),
            "manifest": json.loads(row["manifest_json"]),
            "verification": verification,
        }

    def snapshot_as_of(self, asset: str, as_of_utc: str) -> dict[str, Any] | None:
        """Return the latest snapshot actually stored by the requested as-of time."""
        if not isinstance(asset, str) or not asset.strip():
            raise FeatureStoreError("asset must be a non-empty string")
        _, as_of_s = _utc(as_of_utc, "as_of_utc")
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT snapshot_id, data_cutoff_utc, captured_at_utc, stored_at_utc,
                       asset_scope_json, manifest_json
                FROM snapshots
                WHERE data_cutoff_utc <= ? AND stored_at_utc <= ?
                ORDER BY data_cutoff_utc DESC, stored_at_utc DESC
                """,
                (as_of_s, as_of_s),
            ).fetchall()
        for row in rows:
            assets = json.loads(row["asset_scope_json"])
            if asset.strip().upper() not in assets:
                continue
            verification = self.verify_snapshot(row["snapshot_id"])
            if not verification["valid"]:
                raise FeatureStoreError(
                    f"snapshot integrity verification failed for {row['snapshot_id']}"
                )
            return {
                "snapshot_id": row["snapshot_id"],
                "data_cutoff_utc": row["data_cutoff_utc"],
                "captured_at_utc": row["captured_at_utc"],
                "stored_at_utc": row["stored_at_utc"],
                "manifest": json.loads(row["manifest_json"]),
            }
        return None

    def features_as_of(self, asset: str, as_of_utc: str) -> list[dict[str, Any]]:
        """Return model-facing records from the latest snapshot available by as-of time."""
        snapshot = self.snapshot_as_of(asset, as_of_utc)
        if snapshot is None:
            return []
        return [
            record
            for record in snapshot["manifest"]["records"]
            if record["asset"] == asset.strip().upper()
        ]

    def source_lineage(self, snapshot_id: str) -> list[dict[str, str]]:
        verification = self.verify_snapshot(snapshot_id)
        if not verification["valid"]:
            raise FeatureStoreError(
                f"snapshot integrity verification failed for {snapshot_id}"
            )
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT source_id, independence_group, source_uri, raw_content_sha256
                FROM source_snapshots
                WHERE snapshot_id = ?
                ORDER BY source_id
                """,
                (snapshot_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def verify_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT manifest_json, manifest_sha256, record_count, source_count, "
                "data_cutoff_utc, captured_at_utc, stored_at_utc, asset_scope_json "
                "FROM snapshots WHERE snapshot_id = ?",
                (snapshot_id,),
            ).fetchone()
            if row is None:
                raise FeatureStoreError(f"unknown snapshot_id {snapshot_id}")
            record_rows = connection.execute(
                "SELECT record_id, feature_id, asset, event_time_utc, known_at_utc, "
                "source_data_as_of_utc, ingested_at_utc, revision_available_at_utc, "
                "quality_status, model_eligible, source_ids_json, record_json "
                "FROM feature_records WHERE snapshot_id = ? ORDER BY record_id",
                (snapshot_id,),
            ).fetchall()
            source_rows = connection.execute(
                "SELECT source_id, independence_group, source_uri, raw_content_sha256 "
                "FROM source_snapshots WHERE snapshot_id = ? ORDER BY source_id",
                (snapshot_id,),
            ).fetchall()
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]

        manifest_json = row["manifest_json"]
        manifest_hash_ok = _sha256(manifest_json) == row["manifest_sha256"]
        digest_ok = False
        counts_ok = False
        records_ok = False
        lineage_ok = False
        snapshot_columns_ok = False
        try:
            manifest = json.loads(manifest_json)
            captured_at, captured_at_s = _utc(
                manifest["captured_at_utc"], "captured_at_utc"
            )
            stored_at, stored_at_s = _utc(row["stored_at_utc"], "stored_at_utc")
            snapshot_columns_ok = (
                row["data_cutoff_utc"] == _utc(manifest["cutoff_utc"], "cutoff_utc")[1]
                and row["captured_at_utc"] == captured_at_s
                and row["stored_at_utc"] == stored_at_s
                and stored_at >= captured_at
                and row["asset_scope_json"] == _canonical(
                    sorted({asset.strip().upper() for asset in manifest["asset_scope"]})
                )
            )
            base = dict(manifest)
            stored_id = base.pop("snapshot_id", None)
            digest_ok = (
                stored_id == snapshot_id
                and _sha256(_canonical(base)) == snapshot_id
            )
            expected_records = sorted(
                manifest["records"], key=lambda item: item["record_id"]
            )
            actual_records = []
            columns_ok = True
            for stored in record_rows:
                record = json.loads(stored["record_json"])
                actual_records.append(record)
                expected_columns = {
                    "record_id": record["record_id"],
                    "feature_id": record["feature_id"],
                    "asset": record["asset"],
                    "event_time_utc": record["event_time_utc"],
                    "known_at_utc": record["known_at_utc"],
                    "source_data_as_of_utc": record["source_data_as_of_utc"],
                    "ingested_at_utc": record["ingested_at_utc"],
                    "revision_available_at_utc": record["revision_available_at_utc"],
                    "quality_status": record["quality_status"],
                    "model_eligible": 1 if record["model_eligible"] else 0,
                    "source_ids_json": _canonical(
                        [source["source_id"] for source in record["sources"]]
                    ),
                    "record_json": _canonical(record),
                }
                columns_ok = columns_ok and all(
                    stored[key] == value for key, value in expected_columns.items()
                )

            actual_records.sort(key=lambda item: item["record_id"])
            records_ok = (
                columns_ok
                and _canonical(actual_records) == _canonical(expected_records)
            )

            expected_sources_by_id: dict[str, dict[str, str]] = {}
            for record in expected_records:
                for source in record["sources"]:
                    source_id = source["source_id"]
                    previous = expected_sources_by_id.get(source_id)
                    if previous is not None and previous != source:
                        raise ValueError("conflicting source provenance in manifest")
                    expected_sources_by_id[source_id] = {
                        "source_id": source_id,
                        "independence_group": source["independence_group"],
                        "source_uri": source["source_uri"],
                        "raw_content_sha256": source["raw_content_sha256"],
                    }
            expected_sources = [
                expected_sources_by_id[key] for key in sorted(expected_sources_by_id)
            ]
            actual_sources = [dict(source) for source in source_rows]
            lineage_ok = _canonical(actual_sources) == _canonical(expected_sources)

            counts_ok = (
                len(record_rows) == row["record_count"] == manifest["eligible_record_count"]
                and len(source_rows) == row["source_count"] == len(manifest["source_ids"])
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            digest_ok = False
            records_ok = False
            lineage_ok = False
            counts_ok = False
            snapshot_columns_ok = False

        return {
            "snapshot_id": snapshot_id,
            "valid": bool(
                digest_ok
                and manifest_hash_ok
                and counts_ok
                and records_ok
                and lineage_ok
                and snapshot_columns_ok
                and integrity == "ok"
            ),
            "digest_ok": digest_ok,
            "manifest_hash_ok": manifest_hash_ok,
            "counts_ok": counts_ok,
            "records_ok": records_ok,
            "lineage_ok": lineage_ok,
            "snapshot_columns_ok": snapshot_columns_ok,
            "sqlite_integrity": integrity,
            "record_count": len(record_rows),
            "source_count": len(source_rows),
        }
