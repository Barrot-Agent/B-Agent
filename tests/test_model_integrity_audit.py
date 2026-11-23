import hashlib
import json

import pytest

from scripts.model_integrity_audit import audit_model


def test_audit_hashes_model_files_and_records_runtime_metadata(tmp_path):
    (tmp_path / "config.json").write_text(
        json.dumps({"architectures": ["ExampleForCausalLM"], "model_type": "example"}),
        encoding="utf-8",
    )
    (tmp_path / "tokenizer_config.json").write_text(
        json.dumps({"tokenizer_class": "ExampleTokenizer", "model_max_length": 4096}),
        encoding="utf-8",
    )
    weights = tmp_path / "model.gguf"
    weights.write_bytes(b"immutable-model-fixture")
    before = weights.read_bytes()

    report = audit_model(str(tmp_path), 1024)

    weight_record = next(item for item in report["files"] if item["path"] == "model.gguf")
    assert weight_record["sha256"] == hashlib.sha256(before).hexdigest()
    assert report["model_identity"]["model_type"] == "example"
    assert report["model_identity"]["tokenizer_class"] == "ExampleTokenizer"
    assert report["audit_mode"] == "READ_ONLY_METADATA_AND_HASHES"
    assert weights.read_bytes() == before


def test_audit_does_not_hash_files_over_limit(tmp_path):
    weights = tmp_path / "weights.bin"
    weights.write_bytes(b"0123456789")

    report = audit_model(str(tmp_path), 4)

    record = report["files"][0]
    assert record["sha256_status"] == "NOT_HASHED_SIZE_LIMIT"
    assert "sha256" not in record


def test_audit_reports_invalid_json_and_missing_shards(tmp_path):
    (tmp_path / "config.json").write_text("{broken", encoding="utf-8")
    (tmp_path / "model.safetensors.index.json").write_text(
        json.dumps({"weight_map": {"layer.weight": "missing-00001.safetensors"}}),
        encoding="utf-8",
    )

    report = audit_model(str(tmp_path), 1024)

    assert any(item.startswith("INVALID_JSON:config.json") for item in report["warnings"])
    assert any(item.startswith("MISSING_SHARDS:") for item in report["warnings"])


def test_audit_skips_symlinked_files(tmp_path):
    real = tmp_path / "real.gguf"
    real.write_bytes(b"fixture")
    link = tmp_path / "linked.gguf"
    try:
        link.symlink_to(real)
    except OSError:
        pytest.skip("symlinks are unavailable on this platform")

    report = audit_model(str(tmp_path), 1024)

    assert [item["path"] for item in report["files"]] == ["real.gguf"]
    assert "SYMLINK_SKIPPED:linked.gguf" in report["warnings"]


def test_audit_rejects_symlink_root(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "alias"
    try:
        link.symlink_to(real, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks are unavailable on this platform")

    with pytest.raises(ValueError, match="must not be a symlink"):
        audit_model(str(link), 1024)
