"""
Barrot Repository Awareness Engine.

Maintains a structural model of the repository so Barrot can reason about
its own infrastructure before proposing or applying changes.

The engine is observational. It inventories source files, classes, functions,
imports, tests, trust integrations, and change relationships without modifying
production code.
"""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "evolution"
AWARENESS_FILE = DATA_DIR / "repository_awareness.json"


IGNORED_DIRS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
}


class RepositoryAwarenessEngine:
    """Build and query Barrot's structural repository model."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root or ROOT).resolve()
        self.data_dir = self.root / "data" / "evolution"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _python_files(self) -> list[Path]:
        files = []

        for path in self.root.rglob("*.py"):
            relative = path.relative_to(self.root)

            if any(part in IGNORED_DIRS for part in relative.parts):
                continue

            files.append(path)

        return sorted(files)

    @staticmethod
    def _hash_file(path: Path) -> str:
        return hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

    def _parse_file(self, path: Path) -> dict[str, Any]:
        relative = str(path.relative_to(self.root))

        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            return {
                "path": relative,
                "status": "unparseable",
                "reason": str(exc),
                "hash": self._hash_file(path),
                "classes": [],
                "functions": [],
                "imports": [],
                "line_count": 0,
            }

        classes = []
        functions = []
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "bases": [
                        ast.unparse(base)
                        for base in node.bases
                    ],
                    "methods": [
                        child.name
                        for child in node.body
                        if isinstance(
                            child,
                            (ast.FunctionDef, ast.AsyncFunctionDef),
                        )
                    ],
                })

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "async": isinstance(node, ast.AsyncFunctionDef),
                })

            elif isinstance(node, ast.Import):
                imports.extend(
                    alias.name
                    for alias in node.names
                )

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.extend(
                    f"{module}.{alias.name}"
                    for alias in node.names
                )

        return {
            "path": relative,
            "status": "indexed",
            "hash": self._hash_file(path),
            "line_count": len(source.splitlines()),
            "classes": classes,
            "functions": functions,
            "imports": sorted(set(imports)),
        }

    def _git_state(self) -> dict[str, Any]:
        def run(*args: str) -> str:
            try:
                return subprocess.check_output(
                    ["git", *args],
                    cwd=self.root,
                    stderr=subprocess.DEVNULL,
                    text=True,
                ).strip()
            except (OSError, subprocess.CalledProcessError):
                return ""

        return {
            "branch": run("branch", "--show-current"),
            "head": run("rev-parse", "HEAD"),
            "status": run("status", "--short"),
        }

    def build(self) -> dict[str, Any]:
        files = [
            self._parse_file(path)
            for path in self._python_files()
        ]

        trust_files = [
            item["path"]
            for item in files
            if (
                "trust" in item["path"].lower()
                or any(
                    "TrustEngine" in str(function)
                    or "TrustEngine" in str(cls)
                    for cls in item["classes"]
                    for function in cls.get("methods", [])
                )
            )
        ]

        integration_files = [
            item["path"]
            for item in files
            if any(
                keyword in " ".join(item["imports"])
                or keyword.lower() in item["path"].lower()
                for keyword in (
                    "TrustEngine",
                    "EvidenceStore",
                    "EvidenceNormalizationEngine",
                    "CrossCorroborationEngine",
                    "ConfidenceCalibrationEngine",
                    "CognitiveIntegrityLoop",
                    "EvolutionEngine",
                )
            )
        ]

        tests = [
            item["path"]
            for item in files
            if item["path"].startswith("tests/")
        ]

        manifest = {
            "schema": "BARROT-REPO-AWARENESS-1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repository": str(self.root),
            "git": self._git_state(),
            "statistics": {
                "python_files": len(files),
                "test_files": len(tests),
                "trust_related_files": len(set(trust_files)),
                "integration_files": len(set(integration_files)),
            },
            "architecture": {
                "trust_layer": sorted(set(trust_files)),
                "integration_layer": sorted(set(integration_files)),
                "test_layer": sorted(tests),
            },
            "files": files,
        }

        AWARENESS_FILE.write_text(
            json.dumps(
                manifest,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return manifest

    def load(self) -> dict[str, Any]:
        if not AWARENESS_FILE.exists():
            return self.build()

        try:
            return json.loads(
                AWARENESS_FILE.read_text(
                    encoding="utf-8"
                )
            )
        except (OSError, json.JSONDecodeError):
            return self.build()

    def refresh(self) -> dict[str, Any]:
        return self.build()

    def find_component(self, name: str) -> list[dict[str, Any]]:
        """Find exact classes and functions in the live repository."""
        results: list[dict[str, Any]] = []

        for path in self._python_files():
            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(path))
            except (OSError, UnicodeDecodeError, SyntaxError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    node_type = "class"
                elif isinstance(
                    node,
                    (ast.FunctionDef, ast.AsyncFunctionDef),
                ):
                    node_type = "function"
                else:
                    continue

                if node.name != name:
                    continue

                results.append({
                    "path": str(path.relative_to(self.root)),
                    "type": node_type,
                    "name": node.name,
                    "line": node.lineno,
                })

        return results


    def dependencies_for(self, path: str) -> list[str]:
        manifest = self.load()

        for file in manifest.get("files", []):
            if file["path"] == path:
                return file.get("imports", [])

        return []

    def cross_analysis(self) -> dict[str, Any]:
        manifest = self.load()

        architecture = manifest.get("architecture", {})

        trust_layer = architecture.get(
            "trust_layer",
            [],
        )

        integration_layer = architecture.get(
            "integration_layer",
            [],
        )

        test_layer = architecture.get(
            "test_layer",
            [],
        )

        return {
            "schema": "BARROT-CROSS-ANALYSIS-1",
            "trust_layer": trust_layer,
            "integration_layer": integration_layer,
            "test_layer": test_layer,
            "relationships": {
                "trust_to_integration": [
                    path
                    for path in integration_layer
                    if path not in trust_layer
                ],
                "trust_tests": [
                    path
                    for path in test_layer
                    if "trust" in path.lower()
                    or "corroboration" in path.lower()
                    or "calibration" in path.lower()
                ],
            },
            "interpretation": {
                "trust_isolated": len(integration_layer) == 0,
                "trust_integrated": len(integration_layer) > 0,
                "test_coverage_present": len(test_layer) > 0,
            },
        }

    def snapshot(self) -> dict[str, Any]:
        manifest = self.refresh()
        return {
            "repository": manifest["repository"],
            "git": manifest["git"],
            "statistics": manifest["statistics"],
            "cross_analysis": self.cross_analysis(),
        }
