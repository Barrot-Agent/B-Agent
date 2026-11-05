"""Read-only inspection of safetensors model weights."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
import tempfile
from typing import Any


@dataclass(frozen=True)
class TensorInventory:
    """Metadata inventory cryptographically bound to one checkpoint snapshot."""

    artifact_path: str
    artifact_sha256: str
    tensor_count: int
    tensors: tuple[dict[str, Any], ...]
    total_elements: int

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible inventory."""
        return asdict(self)


def inspect_safetensors(path: str | Path) -> TensorInventory:
    """Hash and inspect one stable temporary snapshot without loading tensor values."""
    supplied = Path(path).expanduser()
    if supplied.suffix != ".safetensors":
        raise ValueError("input must have a .safetensors suffix")
    artifact = supplied.resolve(strict=True)
    if not artifact.is_file():
        raise ValueError("input must be an existing .safetensors file")
    try:
        from safetensors import safe_open
    except ImportError as exc:
        raise RuntimeError("safetensors is required for weight-space inspection") from exc

    digest = hashlib.sha256()
    records: list[dict[str, Any]] = []
    total = 0
    # Copy and hash the exact same byte stream, then inspect only that private
    # snapshot. Concurrent replacement of the source cannot split metadata/hash.
    with tempfile.NamedTemporaryFile(suffix=".safetensors") as snapshot:
        with artifact.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
                snapshot.write(chunk)
        snapshot.flush()
        with safe_open(snapshot.name, framework="pt", device="cpu") as model:
            for name in sorted(model.keys()):
                view = model.get_slice(name)
                shape = tuple(int(dimension) for dimension in view.get_shape())
                elements = 1
                for dimension in shape:
                    elements *= dimension
                total += elements
                records.append({
                    "name": name,
                    "shape": list(shape),
                    "dtype": str(view.get_dtype()),
                    "elements": elements,
                })
    return TensorInventory(
        str(artifact), digest.hexdigest(), len(records), tuple(records), total
    )
