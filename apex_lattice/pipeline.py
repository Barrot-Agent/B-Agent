"""
SandboxPipeline — runs data through an isolated analysis environment.

Input data is the set of ``.log`` files already present under
``.apex_lattice/`` (e.g. the Millennium Problem analyses that Barrot
has pre-generated).  Each file is parsed into a structured record and
stored under ``.apex_lattice/sandbox/`` as a JSON artefact so that
downstream components can query it without re-reading raw text.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

_APEX_DIR = Path(".apex_lattice")
_SANDBOX_DIR = _APEX_DIR / "sandbox"

# Files we consider "raw input" for the pipeline
_LOG_GLOB = "*.log"


class SandboxPipeline:
    """
    Processes raw input files into structured sandbox artefacts.

    Parameters
    ----------
    apex_dir:
        Root of the ``.apex_lattice`` workspace (defaults to
        ``.apex_lattice`` in the current working directory).
    """

    def __init__(self, apex_dir: Path | str | None = None) -> None:
        self._apex = Path(apex_dir) if apex_dir else _APEX_DIR
        self._sandbox = self._apex / "sandbox"
        self._sandbox.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> list[dict[str, Any]]:
        """
        Process all raw log files and return a list of artefact records.
        Each record is also persisted to the sandbox directory as JSON.
        """
        artefacts: list[dict[str, Any]] = []
        for log_file in sorted(self._apex.glob(_LOG_GLOB)):
            artefact = self._process_file(log_file)
            self._persist(artefact)
            artefacts.append(artefact)
        return artefacts

    def load_artefacts(self) -> list[dict[str, Any]]:
        """Return all previously processed artefacts from the sandbox."""
        artefacts: list[dict[str, Any]] = []
        for json_file in sorted(self._sandbox.glob("*.json")):
            try:
                artefacts.append(json.loads(json_file.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                pass
        return artefacts

    def clear(self) -> None:
        """Remove all artefacts from the sandbox directory."""
        for f in self._sandbox.glob("*.json"):
            f.unlink()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _process_file(self, log_file: Path) -> dict[str, Any]:
        """Parse a single log file into a structured artefact."""
        raw = log_file.read_text(encoding="utf-8", errors="replace")
        lines = raw.splitlines()

        # Basic structural extraction
        word_count = len(raw.split())
        section_headings = [
            line.strip("# ").strip()
            for line in lines
            if line.startswith("###") or line.startswith("##")
        ]

        return {
            "id": log_file.stem,
            "source": str(log_file),
            "processed_at": time.time(),
            "word_count": word_count,
            "line_count": len(lines),
            "section_headings": section_headings,
            "preview": raw[:500],
            "raw": raw,
        }

    def _persist(self, artefact: dict[str, Any]) -> None:
        dest = self._sandbox / f"{artefact['id']}.json"
        # Exclude the full raw text from the persisted artefact to keep files small
        to_save = {k: v for k, v in artefact.items() if k != "raw"}
        dest.write_text(json.dumps(to_save, indent=2), encoding="utf-8")
