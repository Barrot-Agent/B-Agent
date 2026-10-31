"""
Capability Analyzer.

Identifies opportunities to expand system capabilities:
- Missing test infrastructure
- Absence of CI/CD configuration
- Lack of logging configuration
- Missing documentation (README, docstrings)
- Opportunity for async upgrade
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from apex_lattice.analyzers.base import BaseAnalyzer


class Analyzer(BaseAnalyzer):
    name = "capability_analyzer"

    def analyze(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        findings.extend(self._check_test_infrastructure())
        findings.extend(self._check_ci_config())
        findings.extend(self._check_logging())
        findings.extend(self._check_readme())
        findings.extend(self._check_docstrings())

        return {"findings": findings}

    # ------------------------------------------------------------------
    def _check_test_infrastructure(self) -> list[dict[str, Any]]:
        test_dirs = ["tests", "test", "spec"]
        found = any((self.repo_root / d).is_dir() for d in test_dirs)
        if not found:
            return [
                self._make_finding(
                    title="No test infrastructure found",
                    description=(
                        "No `tests/` or `test/` directory detected. "
                        "Add a test suite using `pytest` to improve "
                        "reliability and enable regression detection."
                    ),
                    severity="medium",
                    tags=["capability", "testing"],
                )
            ]
        return []

    def _check_ci_config(self) -> list[dict[str, Any]]:
        ci_indicators = [
            ".github/workflows",
            ".gitlab-ci.yml",
            ".circleci",
            "Jenkinsfile",
            ".travis.yml",
        ]
        found = any((self.repo_root / p).exists() for p in ci_indicators)
        if not found:
            return [
                self._make_finding(
                    title="No CI/CD configuration detected",
                    description=(
                        "Add a CI/CD pipeline (e.g. GitHub Actions) to "
                        "automate testing, linting and deployment."
                    ),
                    severity="medium",
                    tags=["capability", "ci-cd"],
                )
            ]
        return []

    def _check_logging(self) -> list[dict[str, Any]]:
        """Flag if no file uses the logging module."""
        uses_logging = False
        for path in self._iter_source_files((".py",)):
            source = self._read_text(path)
            if "import logging" in source or "from logging" in source:
                uses_logging = True
                break
        if not uses_logging:
            return [
                self._make_finding(
                    title="No structured logging detected",
                    description=(
                        "No Python `logging` usage found. Replace bare "
                        "`print()` calls with `logging` to support "
                        "log levels, formatting and output routing."
                    ),
                    severity="low",
                    tags=["capability", "observability"],
                )
            ]
        return []

    def _check_readme(self) -> list[dict[str, Any]]:
        readme_variants = ["README.md", "README.rst", "README.txt", "README"]
        found = any((self.repo_root / r).exists() for r in readme_variants)
        if not found:
            return [
                self._make_finding(
                    title="Missing README",
                    description=(
                        "No README file found. Add a README describing "
                        "the project purpose, setup instructions and "
                        "usage examples."
                    ),
                    severity="low",
                    tags=["capability", "documentation"],
                )
            ]
        return []

    def _check_docstrings(self) -> list[dict[str, Any]]:
        """Report public functions/classes without docstrings."""
        results = []
        for path in self._iter_source_files((".py",)):
            source = self._read_text(path)
            rel = path.relative_to(self.repo_root)
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue
                if node.name.startswith("_"):
                    continue
                if not (ast.get_docstring(node)):
                    results.append(
                        self._make_finding(
                            title="Missing docstring",
                            description=(
                                f"Public `{node.name}` at `{rel}:{node.lineno}` "
                                "has no docstring. Add one to improve "
                                "discoverability and maintainability."
                            ),
                            severity="info",
                            evidence=[f"{rel}:{node.lineno}"],
                            tags=["capability", "documentation"],
                        )
                    )
        return results
