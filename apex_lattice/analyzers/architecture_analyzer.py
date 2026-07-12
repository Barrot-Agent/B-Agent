"""
Architecture Analyzer.

Examines high-level structural properties:
- Missing __init__.py files in sub-directories
- Circular import indicators (heuristic)
- Absence of configuration management
- Package layout best practices
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from apex_lattice.analyzers.base import BaseAnalyzer


class Analyzer(BaseAnalyzer):
    name = "architecture_analyzer"

    def analyze(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        findings.extend(self._check_missing_inits())
        findings.extend(self._check_config_management())
        findings.extend(self._check_deep_nesting())
        findings.extend(self._check_circular_imports())

        return {"findings": findings}

    # ------------------------------------------------------------------
    def _check_missing_inits(self) -> list[dict[str, Any]]:
        results = []
        for d in self.repo_root.rglob("*"):
            if not d.is_dir():
                continue
            # skip hidden dirs and virtual envs
            parts = d.parts
            if any(
                p.startswith(".") or p in ("__pycache__", "node_modules", "venv", ".venv")
                for p in parts
            ):
                continue
            py_files = list(d.glob("*.py"))
            if py_files and not (d / "__init__.py").exists():
                results.append(
                    self._make_finding(
                        title="Missing __init__.py",
                        description=(
                            f"Directory `{d.relative_to(self.repo_root)}` "
                            "contains Python files but no `__init__.py`. "
                            "Add one to make it a proper package."
                        ),
                        severity="low",
                        evidence=[str(d.relative_to(self.repo_root))],
                        tags=["architecture", "packaging"],
                    )
                )
        return results

    def _check_config_management(self) -> list[dict[str, Any]]:
        """Suggest config management if no .env / config file is present."""
        results = []
        config_indicators = [
            ".env",
            ".env.example",
            "config.py",
            "config.yaml",
            "config.toml",
            "settings.py",
            "settings.toml",
        ]
        found = any((self.repo_root / name).exists() for name in config_indicators)
        if not found:
            results.append(
                self._make_finding(
                    title="No configuration management detected",
                    description=(
                        "No `.env`, `config.py`, or `settings.*` file found. "
                        "Consider using `python-dotenv` or `pydantic-settings` "
                        "to manage environment-specific configuration."
                    ),
                    severity="medium",
                    tags=["architecture", "config"],
                )
            )
        return results

    def _check_deep_nesting(self) -> list[dict[str, Any]]:
        """Flag package trees deeper than 4 levels."""
        results = []
        for p in self.repo_root.rglob("__init__.py"):
            depth = len(p.relative_to(self.repo_root).parts) - 1
            if depth > 4:
                results.append(
                    self._make_finding(
                        title="Deeply nested package",
                        description=(
                            f"`{p.parent.relative_to(self.repo_root)}` is "
                            f"{depth} levels deep. Consider flattening the "
                            "module hierarchy."
                        ),
                        severity="low",
                        evidence=[str(p.relative_to(self.repo_root))],
                        tags=["architecture", "complexity"],
                    )
                )
        return results

    def _check_circular_imports(self) -> list[dict[str, Any]]:
        """Detect bidirectional imports between modules using AST-based parsing."""
        results = []
        imports: dict[str, set[str]] = {}

        for path in self._iter_source_files((".py",)):
            source = self._read_text(path)
            mod = ".".join(path.relative_to(self.repo_root).with_suffix("").parts)
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            deps: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    deps.add(node.module)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        deps.add(alias.name)
            imports[mod] = deps

        seen_pairs: set[tuple[str, str]] = set()
        for mod_a, deps_a in imports.items():
            for mod_b in deps_a:
                if mod_b == mod_a:
                    continue  # skip self-reference
                if mod_b not in imports:
                    continue
                if mod_a not in imports.get(mod_b, set()):
                    continue
                pair = tuple(sorted([mod_a, mod_b]))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)  # type: ignore[arg-type]
                results.append(
                    self._make_finding(
                        title="Potential circular import",
                        description=(
                            f"`{mod_a}` and `{mod_b}` appear to import "
                            "each other, which may cause ImportError at "
                            "runtime."
                        ),
                        severity="medium",
                        evidence=[f"{mod_a} <-> {mod_b}"],
                        tags=["architecture", "circular-import"],
                    )
                )

        return results
