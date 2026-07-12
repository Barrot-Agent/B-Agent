"""
Sandbox Analysis Pipeline.

Each analysis cycle runs inside its own isolated sandbox directory under
.apex_lattice/sandbox/<cycle_id>/.  The pipeline collects raw data from the
registered analyzers and returns a list of raw result dicts.
"""

from __future__ import annotations

import importlib
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apex_lattice.audit import AuditTrail

_SANDBOX_BASE = Path(".apex_lattice") / "sandbox"

# Ordered list of built-in analyzer module paths
_DEFAULT_ANALYZERS = [
    "apex_lattice.analyzers.code_analyzer",
    "apex_lattice.analyzers.performance_analyzer",
    "apex_lattice.analyzers.security_analyzer",
    "apex_lattice.analyzers.dependency_analyzer",
    "apex_lattice.analyzers.architecture_analyzer",
    "apex_lattice.analyzers.capability_analyzer",
]


class SandboxPipeline:
    """Runs each analyzer in an isolated sandbox directory and collects results."""

    def __init__(
        self,
        cycle_id: str | None = None,
        repo_root: Path | None = None,
        base_dir: Path | None = None,
        analyzer_modules: list[str] | None = None,
    ) -> None:
        self.cycle_id = cycle_id or f"cycle_{uuid.uuid4().hex[:8]}"
        self.repo_root = (repo_root or Path(".")).resolve()
        self._base_dir = base_dir or Path(".")
        self._sandbox_dir = (self._base_dir / _SANDBOX_BASE / self.cycle_id).resolve()
        self._analyzer_modules = analyzer_modules or _DEFAULT_ANALYZERS
        self.audit = AuditTrail(self.cycle_id, base_dir=self._base_dir)

    # ------------------------------------------------------------------
    def run(self) -> list[dict[str, Any]]:
        """Execute the full pipeline and return raw analyzer results."""
        self.audit.log("pipeline_start", {"repo_root": str(self.repo_root)})
        self._setup_sandbox()

        results: list[dict[str, Any]] = []
        for module_path in self._analyzer_modules:
            result = self._run_analyzer(module_path)
            if result:
                results.append(result)

        self.audit.log("pipeline_complete", {"result_count": len(results)})
        self._teardown_sandbox()
        return results

    # ------------------------------------------------------------------
    def _setup_sandbox(self) -> None:
        self._sandbox_dir.mkdir(parents=True, exist_ok=True)
        self.audit.log("sandbox_created", {"path": str(self._sandbox_dir)})

    def _teardown_sandbox(self) -> None:
        """Remove the temporary sandbox workspace."""
        if self._sandbox_dir.exists():
            shutil.rmtree(self._sandbox_dir, ignore_errors=True)
        self.audit.log("sandbox_destroyed", {"path": str(self._sandbox_dir)})

    def _run_analyzer(self, module_path: str) -> dict[str, Any] | None:
        """Dynamically load and run a single analyzer module."""
        analyzer_name = module_path.split(".")[-1]
        self.audit.log("analyzer_start", {"analyzer": analyzer_name})
        try:
            module = importlib.import_module(module_path)
            analyzer_class = getattr(module, "Analyzer")
            instance = analyzer_class(
                repo_root=self.repo_root,
                sandbox_dir=self._sandbox_dir,
            )
            result = instance.analyze()
            result.setdefault("analyzer", analyzer_name)
            result.setdefault("cycle_id", self.cycle_id)
            result.setdefault("analyzed_at", datetime.now(timezone.utc).isoformat())
            self.audit.log(
                "analyzer_complete",
                {"analyzer": analyzer_name, "finding_count": len(result.get("findings", []))},
            )
            return result
        except Exception as exc:  # noqa: BLE001
            self.audit.log("analyzer_error", {"analyzer": analyzer_name, "error": str(exc)})
            return None
