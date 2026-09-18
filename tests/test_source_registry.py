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
