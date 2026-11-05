import pytest

safetensors = pytest.importorskip("safetensors.torch")
torch = pytest.importorskip("torch")

from barrot_agent.weight_space.safetensors_lab import inspect_safetensors


def test_inspect_safetensors_is_metadata_only(tmp_path):
    path = tmp_path / "tiny.safetensors"
    safetensors.save_file({"layer.weight": torch.zeros((2, 3)), "layer.bias": torch.ones((2,))}, str(path))
    before = path.read_bytes()
    inventory = inspect_safetensors(path)
    assert inventory.tensor_count == 2 and inventory.total_elements == 8
    assert [item["name"] for item in inventory.tensors] == ["layer.bias", "layer.weight"]
    assert path.read_bytes() == before and len(inventory.artifact_sha256) == 64


def test_inspector_rejects_non_safetensors(tmp_path):
    path = tmp_path / "model.bin"
    path.write_bytes(b"not a model")
    with pytest.raises(ValueError):
        inspect_safetensors(path)


def test_inspector_accepts_huggingface_style_safetensors_symlink(tmp_path):
    blob = tmp_path / "cache-blob.safetensors"
    named = tmp_path / "model.safetensors"
    safetensors.save_file({"weight": torch.ones((2,))}, str(blob))
    named.symlink_to(blob)
    inventory = inspect_safetensors(named)
    assert inventory.tensor_count == 1
    assert inventory.artifact_sha256
