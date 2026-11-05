"""Read-only inspection of safetensors model weights."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class TensorInventory:
    artifact_path: str
    artifact_sha256: str
    tensor_count: int
    tensors: tuple[dict[str, Any], ...]
    total_elements: int
    def to_dict(self) -> dict[str, Any]: return asdict(self)

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest()

def inspect_safetensors(path: str | Path) -> TensorInventory:
    """Inventory tensor names, shapes, dtypes and element counts without loading tensors."""
    artifact = Path(path).expanduser().resolve(strict=True)
    if not artifact.is_file() or artifact.suffix != ".safetensors": raise ValueError("input must be an existing .safetensors file")
    try:
        from safetensors import safe_open
    except ImportError as exc: raise RuntimeError("safetensors is required for weight-space inspection") from exc
    records: list[dict[str, Any]] = []; total = 0
    with safe_open(str(artifact), framework="pt", device="cpu") as model:
        for name in sorted(model.keys()):
            view = model.get_slice(name); shape = tuple(int(d) for d in view.get_shape())
            elements = 1
            for dimension in shape: elements *= dimension
            total += elements
            records.append({"name": name, "shape": list(shape), "dtype": str(view.get_dtype()), "elements": elements})
    return TensorInventory(str(artifact), _sha256(artifact), len(records), tuple(records), total)
