from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from barrot_agent.evolution.feature_store import HistoricalFeatureStore
from barrot_agent.evolution.point_in_time_features import build_feature_snapshot
from barrot_agent.evolution.xrp_feature_store_backfill import (
    XRPFeatureStoreBackfillError,
    reconcile_historical_snapshot,
    verify_existing_reconciliation,
)
from barrot_agent.evolution.xrp_public_ingestion import RawReceiptArchive, _feature_record


MAIN_SHA = "a" * 40
PARENT_RUN = "44844499889"
SOURCE_RUN = "44844953105"
FORK_RUN = "44848909814"
CHILD_RUN = "44855063970"


class MutableClock:
    def __init__(self, value: datetime):
        self.value = value

    def __call__(self) -> datetime:
        return self.value


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _write_parent_index(path: Path) -> None:
    payload = {
        "schema_version": "barrot.xrp.cross-run-receipt-chain.v1",
        "sequence": 1,
        "continuity_status": "BOOTSTRAP",
        "continuity_verified": True,
        "previous": None,
        "previous_manifest_sha256": None,
        "previous_cross_run_chain_sha256": None,
        "current_run": {
            "repository": "Barrot-Agent/B-Agent",
            "run_id": PARENT_RUN,
            "run_attempt": "1",
            "sha": MAIN_SHA,
            "workflow_ref": "Barrot-Agent/B-Agent/.github/workflows/xrp-public-ingestion.yml@refs/heads/main",
            "event_name": "schedule",
        },
        "current_receipt_chain": {
            "manifest_sha256": "0" * 64,
            "chain_head_sha256": "0" * 64,
            "receipt_log_sha256": "0" * 64,
            "chain_log_sha256": "0" * 64,
            "receipt_count": 0,
        },
        "raw_artifact": {
            "run_id": PARENT_RUN,
            "artifact_name": f"xrp-public-raw-{PARENT_RUN}",
            "retention_days": 90,
        },
        "external_anchor_status": "NOT_ANCHORED",
        "limitations": ["test parent index"],
    }
    payload["cross_run_chain_sha256"] = _sha(_canonical(payload).encode("utf-8"))
    path.write_text(_canonical(payload), encoding="utf-8")


def _set_run_context(monkeypatch, run_id: str) -> None:
    monkeypatch.setenv("GITHUB_REPOSITORY", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("GITHUB_RUN_ID", run_id)
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "1")
    monkeypatch.setenv("GITHUB_SHA", MAIN_SHA)
    monkeypatch.setenv(
        "GITHUB_WORKFLOW_REF",
        "Barrot-Agent/B-Agent/.github/workflows/xrp-public-ingestion.yml@refs/heads/main",
    )
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")


def _create_raw_run(root: Path, run_id: str, previous_index: Path, monkeypatch, payload: bytes):
    raw_root = root / "raw"
    archive = RawReceiptArchive(raw_root)
    captured = "2026-11-21T00:00:02.000000Z"
    source_id = f"exchange_{run_id}"
    source_uri = f"https://example.com/{source_id}"
    receipt = archive.store(
        source_id=source_id,
        source_uri=source_uri,
        captured_at_utc=captured,
        raw_bytes=payload,
        source_data_as_of_utc="2026-11-21T00:00:01.000000Z",
        model_eligible=True,
    )
    _set_run_context(monkeypatch, run_id)
    archive.write_manifest(
        root / "receipt_manifest.json",
        previous_manifest_path=previous_index,
        continuity_status="CONTINUED",
        cross_run_path=root / "cross_run_receipt_chain.json",
    )
    return receipt, root / "cross_run_receipt_chain.json", source_id, source_uri


def _snapshot(tag: str, captured: str, source_id: str, source_uri: str, digest: str):
    event_time = "2026-11-21T00:00:01.000000Z"
    record = _feature_record(
        feature_id=f"xrp.spot.test.{tag}",
        value=0.5 + len(tag) / 100,
        unit="USD/XRP",
        event_time_utc=event_time,
        source_data_as_of_utc=event_time,
        captured_at_utc=captured,
        source_id=source_id,
        source_uri=source_uri,
        raw_sha256=digest,
        independence_group=source_id,
        venue=source_id,
        instrument="XRP-USD spot",
        currency_pair="XRP/USD",
        market_type="spot",
    )
    return build_feature_snapshot(
        [record],
        cutoff_utc=captured,
        captured_at_utc=captured,
        asset_scope=["XRP"],
    )


def _build_case(tmp_path: Path, monkeypatch):
    parent = tmp_path / "parent-index.json"
    _write_parent_index(parent)

    source_root = tmp_path / "source-artifact"
    source_root.mkdir()
    source_receipt, source_index, source_id, source_uri = _create_raw_run(
        source_root, SOURCE_RUN, parent, monkeypatch, b'{"source":"source-run"}'
    )
    source_snapshot = _snapshot(
        "source",
        "2026-11-21T00:10:00.000000Z",
        source_id,
        source_uri,
        source_receipt["raw_content_sha256"],
    )

    fork_root = tmp_path / "fork-artifact"
    fork_root.mkdir()
    fork_receipt, fork_index, fork_source_id, fork_source_uri = _create_raw_run(
        fork_root, FORK_RUN, parent, monkeypatch, b'{"source":"fork-run"}'
    )
    fork_snapshot = _snapshot(
        "fork",
        "2026-11-21T00:20:00.000000Z",
        fork_source_id,
        fork_source_uri,
        fork_receipt["raw_content_sha256"],
    )

    child_root = tmp_path / "child-artifact"
    child_root.mkdir()
    child_receipt, child_index, child_source_id, child_source_uri = _create_raw_run(
        child_root, CHILD_RUN, fork_index, monkeypatch, b'{"source":"main-descendant"}'
    )
    child_snapshot = _snapshot(
        "child",
        "2026-11-21T00:30:00.000000Z",
        child_source_id,
        child_source_uri,
        child_receipt["raw_content_sha256"],
    )

    source_db = tmp_path / "source.sqlite3"
    source_clock = MutableClock(datetime(2026, 11, 21, 0, 1, tzinfo=timezone.utc))
    source_store = HistoricalFeatureStore(source_db, clock=source_clock)
    common = _snapshot(
        "common",
        "2026-11-21T00:00:00.000000Z",
        "common_source",
        "https://example.com/common",
        "a" * 64,
    )
    source_store.append_snapshot(common)
    source_clock.value = datetime(2026, 11, 21, 0, 11, tzinfo=timezone.utc)
    source_store.append_snapshot(source_snapshot)

    target_db = tmp_path / "target.sqlite3"
    target_clock = MutableClock(datetime(2026, 11, 21, 0, 1, tzinfo=timezone.utc))
    target_store = HistoricalFeatureStore(target_db, clock=target_clock)
    target_store.append_snapshot(common)
    target_clock.value = datetime(2026, 11, 21, 0, 21, tzinfo=timezone.utc)
    target_store.append_snapshot(fork_snapshot)
    target_clock.value = datetime(2026, 11, 21, 0, 31, tzinfo=timezone.utc)
    target_store.append_snapshot(child_snapshot)

    ancestry = tmp_path / "ancestry"
    ancestry.mkdir()
    fork_copy = ancestry / f"{FORK_RUN}.json"
    child_copy = ancestry / f"{CHILD_RUN}.json"
    shutil.copy2(fork_index, fork_copy)
    shutil.copy2(child_index, child_copy)

    separate_indexes = tmp_path / "separate-indexes"
    separate_indexes.mkdir()
    source_index_copy = separate_indexes / "source.json"
    fork_index_copy = separate_indexes / "fork.json"
    current_index_copy = separate_indexes / "current.json"
    shutil.copy2(source_index, source_index_copy)
    shutil.copy2(fork_index, fork_index_copy)
    shutil.copy2(child_index, current_index_copy)

    source_store = HistoricalFeatureStore(source_db)
    source_manifest_sha = _sha(_canonical(source_snapshot).encode("utf-8"))
    fork_manifest_sha = _sha(_canonical(fork_snapshot).encode("utf-8"))
    return {
        "source_db": source_db,
        "target_db": target_db,
        "source_root": source_root,
        "fork_root": fork_root,
        "source_index": source_index_copy,
        "fork_index": fork_index_copy,
        "current_index": current_index_copy,
        "ancestry": ancestry,
        "output": tmp_path / "historical-reconciliation.json",
        "common_id": common["snapshot_id"],
        "fork_id": fork_snapshot["snapshot_id"],
        "fork_manifest_sha": fork_manifest_sha,
        "source_id": source_snapshot["snapshot_id"],
        "source_manifest_sha": source_manifest_sha,
    }


def test_historical_backfill_verifies_both_fork_heads_and_actual_receipt_time(tmp_path, monkeypatch):
    case = _build_case(tmp_path, monkeypatch)
    recovery_time = datetime(2026, 11, 21, 1, 0, tzinfo=timezone.utc)
    result = reconcile_historical_snapshot(
        target_database=case["target_db"],
        source_database=case["source_db"],
        source_raw_artifact_root=case["source_root"],
        source_index_path=case["source_index"],
        fork_raw_artifact_root=case["fork_root"],
        fork_index_path=case["fork_index"],
        ancestry_index_dir=case["ancestry"],
        current_index_path=case["current_index"],
        output_path=case["output"],
        source_run_id=SOURCE_RUN,
        fork_run_id=FORK_RUN,
        common_parent_run_id=PARENT_RUN,
        common_snapshot_id=case["common_id"],
        fork_snapshot_id=case["fork_id"],
        fork_snapshot_manifest_sha256=case["fork_manifest_sha"],
        backfill_snapshot_id=case["source_id"],
        backfill_manifest_sha256=case["source_manifest_sha"],
        expected_record_count=1,
        expected_source_count=1,
        clock=lambda: recovery_time,
    )

    assert result["status"] == "RECONCILED"
    assert result["backfill_snapshot"]["stored_at_utc"] == "2026-11-21T01:00:00.000000Z"
    assert result["main_lineage_run_ids"] == [FORK_RUN, CHILD_RUN]
    assert result["point_in_time_visibility"]["visible_before_receipt"] is False
    assert result["point_in_time_visibility"]["visible_after_receipt"] is True
    assert result["point_in_time_visibility"]["backfilled_record_count"] == 1

    receipt = json.loads(case["output"].read_text(encoding="utf-8"))
    assert receipt["historical_fork"]["prior_receipts_rewritten"] is False
    assert [head["run_id"] for head in receipt["historical_fork"]["sibling_heads"]] == [
        SOURCE_RUN,
        FORK_RUN,
    ]
    assert receipt["backfill_snapshot"]["manifest_sha256"] == case["source_manifest_sha"]

    verified = verify_existing_reconciliation(case["target_db"], case["output"])
    assert verified["status"] == "VERIFIED_EXISTING"
    assert verified["snapshot_id"] == case["source_id"]


def test_historical_backfill_rejects_raw_payload_tampering_before_target_mutation(tmp_path, monkeypatch):
    case = _build_case(tmp_path, monkeypatch)
    payloads = list((case["source_root"] / "raw" / "sha256").glob("*.json"))
    assert len(payloads) == 1
    payloads[0].write_bytes(b'{"tampered":true}')

    before = HistoricalFeatureStore(case["target_db"]).snapshot_count()
    with pytest.raises(XRPFeatureStoreBackfillError, match="raw receipt"):
        reconcile_historical_snapshot(
            target_database=case["target_db"],
            source_database=case["source_db"],
            source_raw_artifact_root=case["source_root"],
            source_index_path=case["source_index"],
            fork_raw_artifact_root=case["fork_root"],
            fork_index_path=case["fork_index"],
            ancestry_index_dir=case["ancestry"],
            current_index_path=case["current_index"],
            output_path=case["output"],
            source_run_id=SOURCE_RUN,
            fork_run_id=FORK_RUN,
            common_parent_run_id=PARENT_RUN,
            common_snapshot_id=case["common_id"],
            fork_snapshot_id=case["fork_id"],
            fork_snapshot_manifest_sha256=case["fork_manifest_sha"],
            backfill_snapshot_id=case["source_id"],
            backfill_manifest_sha256=case["source_manifest_sha"],
            expected_record_count=1,
            expected_source_count=1,
            clock=lambda: datetime(2026, 11, 21, 1, 0, tzinfo=timezone.utc),
        )
    assert HistoricalFeatureStore(case["target_db"]).snapshot_count() == before
