import json

import pytest

from barrot_agent.sources.source_registry import (
    SourceEvidence,
    SourceIngestion,
    SourceKnowledge,
    SourceLifecycle,
    SourceProvenance,
    SourceRecord,
    SourceRegistry,
    SourceIdentity,
    SourceVersion,
    register_file_source,
)


def make_record(source_id="test-source"):
    return SourceRecord(
        identity=SourceIdentity(
            source_id=source_id,
            source_type="test",
            name="Test Source",
            origin="unit-test",
            uri="test://source",
            publisher="Barrot",
        ),
        version=SourceVersion(
            version="1",
            content_hash="abc123",
        ),
    )


def test_register_and_reload(tmp_path):
    path = tmp_path / "registry.json"

    registry = SourceRegistry(path)
    registry.register(make_record())

    reloaded = SourceRegistry(path)
    record = reloaded.require("test-source")

    assert record.identity.name == "Test Source"
    assert record.version.content_hash == "abc123"


def test_duplicate_hash_is_idempotent(tmp_path):
    registry = SourceRegistry(tmp_path / "registry.json")

    first = registry.register(make_record())
    second = registry.register(make_record())

    assert first.to_dict() == second.to_dict()
    assert registry.summary()["source_count"] == 1


def test_source_update_preserves_identity(tmp_path):
    registry = SourceRegistry(tmp_path / "registry.json")
    registry.register(make_record())

    updated = registry.update(
        "test-source",
        evidence=SourceEvidence(
            observations=["observed"],
            confidence=0.9,
        ),
        knowledge=SourceKnowledge(
            concepts=["concept"],
            identified_gaps=["missing-context"],
        ),
    )

    assert updated.identity.source_id == "test-source"
    assert updated.evidence.confidence == 0.9
    assert updated.knowledge.identified_gaps == ["missing-context"]


def test_find_gaps(tmp_path):
    registry = SourceRegistry(tmp_path / "registry.json")
    registry.register(
        SourceRecord(
            identity=SourceIdentity(
                source_id="gap-source",
                source_type="dataset",
                name="Gap Dataset",
                origin="test",
            ),
            knowledge=SourceKnowledge(
                identified_gaps=["gap-a", "gap-b"]
            ),
        )
    )

    assert registry.find_gaps() == {
        "gap-source": ["gap-a", "gap-b"]
    }


def test_source_deletion_is_blocked(tmp_path):
    registry = SourceRegistry(tmp_path / "registry.json")
    registry.register(make_record())

    with pytest.raises(RuntimeError):
        registry.remove("test-source")

    assert registry.require("test-source").identity.name == "Test Source"


def test_file_registration_hashes_content(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("Barrot source data", encoding="utf-8")

    registry = SourceRegistry(tmp_path / "registry.json")

    record = register_file_source(
        registry,
        source_id="file-source",
        source_type="document",
        name="Test Document",
        origin="local",
        path=source,
    )

    assert len(record.version.content_hash) == 64
    assert record.ingestion.mmi_status == "REGISTERED"
    assert registry.summary()["source_count"] == 1


def test_summary(tmp_path):
    registry = SourceRegistry(tmp_path / "registry.json")

    registry.register(
        SourceRecord(
            identity=SourceIdentity(
                source_id="a",
                source_type="paper",
                name="Paper",
                origin="test",
            ),
            knowledge=SourceKnowledge(
                identified_gaps=["gap"]
            ),
        )
    )

    registry.register(
        SourceRecord(
            identity=SourceIdentity(
                source_id="b",
                source_type="dataset",
                name="Dataset",
                origin="test",
            )
        )
    )

    summary = registry.summary()

    assert summary["source_count"] == 2
    assert summary["active_count"] == 2
    assert summary["gap_count"] == 1
    assert summary["types"] == ["dataset", "paper"]


def test_registration_timestamp_is_system_generated_and_persisted(tmp_path, monkeypatch):
    from barrot_agent.sources import source_registry as source_registry_module

    fixed = "2026-11-02T04:00:00+00:00"
    monkeypatch.setattr(source_registry_module, "utc_now", lambda: fixed)
    path = tmp_path / "registry.json"
    registry = SourceRegistry(path)
    record = make_record()
    record.registered_at_utc = "1999-01-01T00:00:00Z"
    registry.register(record)
    assert record.registered_at_utc == fixed
    reloaded = SourceRegistry(path)
    assert reloaded.require("test-source").registered_at_utc == fixed


def test_source_id_cannot_be_reused_for_changed_snapshot_content(tmp_path):
    registry = SourceRegistry(tmp_path / "registry.json")
    first = make_record()
    registry.register(first)
    changed = make_record()
    changed.version.content_hash = "def456"
    with pytest.raises(ValueError, match="source_id is immutable"):
        registry.register(changed)
    assert registry.require("test-source").version.content_hash == "abc123"


def test_new_snapshot_version_uses_new_source_id_and_preserves_supersession(tmp_path):
    registry = SourceRegistry(tmp_path / "registry.json")
    first = make_record("snapshot-v1")
    registry.register(first)
    second = make_record("snapshot-v2")
    second.version.content_hash = "def456"
    second.version.supersedes = "snapshot-v1"
    registry.register(second)
    assert registry.require("snapshot-v1").version.content_hash == "abc123"
    assert registry.require("snapshot-v2").version.content_hash == "def456"
    assert registry.require("snapshot-v2").version.supersedes == "snapshot-v1"


def test_registration_cutoff_is_timezone_aware_and_fail_closed(tmp_path, monkeypatch):
    from barrot_agent.sources import source_registry as source_registry_module

    monkeypatch.setattr(source_registry_module, "utc_now", lambda: "2026-11-02T04:00:00+00:00")
    registry = SourceRegistry(tmp_path / "registry.json")
    registry.register(make_record())
    assert registry.require_registered_by("test-source", "2026-11-02T04:00:01Z").identity.source_id == "test-source"
    with pytest.raises(ValueError, match="registered after the permitted cutoff"):
        registry.require_registered_by("test-source", "2026-11-02T03:59:59Z")
    with pytest.raises(ValueError, match="timezone"):
        registry.require_registered_by("test-source", "2026-11-02T04:00:01")


def test_legacy_registry_without_registration_timestamp_is_not_cutoff_verified(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"records": {"test-source": make_record().to_dict()}}), encoding="utf-8")
    registry = SourceRegistry(path)
    with pytest.raises(ValueError, match="registration timestamp is unavailable"):
        registry.require_registered_by("test-source", "2026-11-02T04:00:00Z")


def test_file_snapshot_hash_verification_and_tamper_detection(tmp_path):
    source = tmp_path / "snapshot.json"
    source.write_text('{"value": 1}', encoding="utf-8")
    registry = SourceRegistry(tmp_path / "registry.json")
    record = register_file_source(
        registry,
        source_id="snapshot-v1",
        source_type="dataset",
        name="Snapshot",
        origin="unit-test",
        path=source,
    )
    assert registry.verify_content_hash("snapshot-v1")
    assert registry.read_verified_content("snapshot-v1") == source.read_bytes()
    assert record.version.snapshot_path
    source.write_text('{"value": 2}', encoding="utf-8")
    assert registry.verify_content_hash("snapshot-v1") is False
    with pytest.raises(ValueError, match="do not match registered content hash"):
        registry.read_verified_content("snapshot-v1")
