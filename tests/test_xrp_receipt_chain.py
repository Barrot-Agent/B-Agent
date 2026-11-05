import json
from pathlib import Path

import pytest

from barrot_agent.evolution.xrp_public_ingestion import RawReceiptArchive, XRPIngestionError


ZERO_HASH = "0" * 64


def store_receipt(archive, raw=b"verified public source bytes", *, retain=True):
    return archive.store(
        source_id="test_public_source",
        source_uri="https://example.com/public-data",
        captured_at_utc="2026-11-05T17:00:00Z",
        raw_bytes=raw,
        source_data_as_of_utc="2026-11-05T16:59:00Z",
        model_eligible=True,
        retain_raw_bytes=retain,
        raw_retention_reason="" if retain else "publisher terms require digest-only retention",
    )


def test_receipt_archive_builds_and_verifies_a_per_run_hash_chain(tmp_path):
    archive = RawReceiptArchive(tmp_path / "raw")
    first = store_receipt(archive, b"first")
    second = store_receipt(archive, b"second")

    verification = archive.verify()
    chain = [json.loads(line) for line in archive.chain_path.read_text(encoding="utf-8").splitlines()]

    assert verification["verified"] is True
    assert verification["receipt_count"] == 2
    assert verification["retained_raw_payload_count"] == 2
    assert verification["digest_only_receipt_count"] == 0
    assert chain[0]["sequence"] == 1
    assert chain[0]["previous_chain_sha256"] == ZERO_HASH
    assert chain[0]["receipt_id"] == first["receipt_id"]
    assert chain[1]["sequence"] == 2
    assert chain[1]["previous_chain_sha256"] == chain[0]["chain_sha256"]
    assert chain[1]["receipt_id"] == second["receipt_id"]
    assert verification["chain_head_sha256"] == chain[1]["chain_sha256"]


def test_receipt_archive_detects_raw_payload_tampering(tmp_path):
    archive = RawReceiptArchive(tmp_path / "raw")
    receipt = store_receipt(archive, b"original bytes")
    payload_path = archive.root.parent / receipt["raw_payload_path"]
    payload_path.write_bytes(b"modified bytes")

    with pytest.raises(XRPIngestionError, match="do not match canonical size and SHA-256"):
        archive.verify()


def test_receipt_archive_detects_receipt_log_tampering(tmp_path):
    archive = RawReceiptArchive(tmp_path / "raw")
    store_receipt(archive)
    receipt = json.loads(archive.receipts_path.read_text(encoding="utf-8"))
    receipt["source_id"] = "tampered_source"
    archive.receipts_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")

    with pytest.raises(XRPIngestionError, match="receipt ID does not match canonical receipt metadata"):
        archive.verify()


def test_receipt_archive_detects_chain_deletion_or_reordering(tmp_path):
    archive = RawReceiptArchive(tmp_path / "raw")
    store_receipt(archive, b"first")
    store_receipt(archive, b"second")
    lines = archive.chain_path.read_text(encoding="utf-8").splitlines()
    archive.chain_path.write_text(lines[1] + "\n" + lines[0] + "\n", encoding="utf-8")

    with pytest.raises(XRPIngestionError, match="receipt chain identity mismatch|predecessor mismatch"):
        archive.verify()


def test_digest_only_receipts_are_chained_without_retaining_restricted_bytes(tmp_path):
    archive = RawReceiptArchive(tmp_path / "raw")
    receipt = store_receipt(archive, b"restricted source bytes", retain=False)
    verification = archive.verify()

    assert receipt["raw_bytes_retained"] is False
    assert receipt["raw_payload_path"] is None
    assert verification["receipt_count"] == 1
    assert verification["retained_raw_payload_count"] == 0
    assert verification["digest_only_receipt_count"] == 1


def test_legacy_receipt_log_is_verified_before_chain_bootstrap(tmp_path):
    archive = RawReceiptArchive(tmp_path / "raw")
    store_receipt(archive, b"legacy bytes")
    archive.chain_path.unlink()

    migrated = RawReceiptArchive(tmp_path / "raw")
    verification = migrated.verify()

    assert migrated._legacy_chain_bootstrap is True
    assert verification["verified"] is True
    assert verification["receipt_count"] == 1
    assert verification["retained_raw_payload_count"] == 1


def test_run_manifest_binds_github_workflow_identity_without_claiming_per_source_timestamping(tmp_path, monkeypatch):
    archive = RawReceiptArchive(tmp_path / "raw")
    store_receipt(archive)
    monkeypatch.setenv("GITHUB_REPOSITORY", "Barrot-Agent/B-Agent")
    monkeypatch.setenv("GITHUB_RUN_ID", "42000000000")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "1")
    monkeypatch.setenv("GITHUB_SHA", "a" * 40)
    monkeypatch.setenv("GITHUB_WORKFLOW_REF", "Barrot-Agent/B-Agent/.github/workflows/xrp-public-ingestion.yml@refs/heads/main")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")

    manifest = archive.write_manifest(tmp_path / "receipt_chain_manifest.json")
    persisted = json.loads((tmp_path / "receipt_chain_manifest.json").read_text(encoding="utf-8"))

    assert manifest == persisted
    assert manifest["verification_status"] == "PASS"
    assert manifest["github_run_context_available"] is True
    assert manifest["github_actions_context"]["run_id"] == "42000000000"
    assert manifest["github_actions_context"]["sha"] == "a" * 40
    assert manifest["per_source_independent_timestamp_anchor"] is False
    assert manifest["chain_head_sha256"] == archive.verify()["chain_head_sha256"]


def test_raw_ingestion_workflow_uploads_the_receipt_chain_manifest():
    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github"
        / "workflows"
        / "xrp-public-ingestion.yml"
    ).read_text(encoding="utf-8")

    assert "artifacts/xrp_ingestion/raw/**" in workflow
    assert "artifacts/xrp_ingestion/receipt_manifest.json" in workflow
    assert "artifacts/xrp_ingestion/receipt_chain_manifest.json" in workflow
