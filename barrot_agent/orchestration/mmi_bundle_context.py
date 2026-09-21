"""Deterministic MMI context for governed development bundles.

This module only reads already-produced MMI learning output.
It does not acquire sources, mutate the repository, execute commands,
or promote hypotheses into verified facts.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


MMI_RECORD = Path(".barrot/mmi_learning/MMI_LEARNING_RECORD.json")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_mmi_bundle_context(
    path: Path = MMI_RECORD,
) -> dict[str, Any]:
    """Return deterministic, provenance-bound MMI context."""
    if not path.exists():
        return {
            "available": False,
            "reason": "MMI_LEARNING_RECORD_MISSING",
        }

    data = json.loads(path.read_text())

    return {
        "available": True,
        "protocol": data.get("protocol"),
        "generated_at": data.get("generated_at"),
        "source_manifest": data.get("source_manifest"),
        "observations": data.get("observations", []),
        "unresolved_gaps": data.get("unresolved_gaps", []),
        "record_sha256": _sha256(path),
        "record_path": str(path),
    }
