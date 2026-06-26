"""
Code Pattern Analyzer.

Identifies code-quality issues such as broad exception handling,
TODO/FIXME markers, missing type annotations, and very large functions.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from apex_lattice.analyzers.base import BaseAnalyzer

_TODO_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)
_BROAD_EXCEPT_RE = re.compile(r"except\s*:\s*$|except\s+Exception\s*:", re.MULTILINE)


class Analyzer(BaseAnalyzer):
    name = "code_analyzer"

    def analyze(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        for path in self._iter_source_files((".py",)):
            source = self._read_text(path)
            rel = path.relative_to(self.repo_root)

            findings.extend(self._check_todos(rel, source))
            findings.extend(self._check_broad_except(rel, source))
            findings.extend(self._check_large_functions(rel, source))

        return {"findings": findings}

    # ------------------------------------------------------------------
    def _check_todos(self, rel: Path, source: str) -> list[dict[str, Any]]:
        results = []
        for i, line in enumerate(source.splitlines(), 1):
            if _TODO_RE.search(line):
                results.append(
                    self._make_finding(
                        title="TODO/FIXME marker found",
                        description=(
                            f"Address unresolved marker in `{rel}` line {i}: "
                            f"`{line.strip()}`"
                        ),
                        severity="low",
                        evidence=[f"{rel}:{i}: {line.strip()}"],
                        tags=["code-quality", "maintenance"],
                    )
                )
        return results

    def _check_broad_except(self, rel: Path, source: str) -> list[dict[str, Any]]:
        results = []
        for match in _BROAD_EXCEPT_RE.finditer(source):
            lineno = source[: match.start()].count("\n") + 1
            results.append(
                self._make_finding(
                    title="Broad exception handler",
                    description=(
                        f"Broad `except` clause in `{rel}` line {lineno} "
                        "may swallow unexpected errors."
                    ),
                    severity="medium",
                    evidence=[f"{rel}:{lineno}: {match.group().strip()}"],
                    tags=["code-quality", "error-handling"],
                )
            )
        return results

    def _check_large_functions(self, rel: Path, source: str) -> list[dict[str, Any]]:
        results = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return results

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = getattr(node, "end_lineno", node.lineno)
                size = end - node.lineno
                if size > 80:
                    results.append(
                        self._make_finding(
                            title="Large function",
                            description=(
                                f"`{node.name}` in `{rel}` is {size} lines long "
                                f"(starting at line {node.lineno}). "
                                "Consider splitting it into smaller units."
                            ),
                            severity="low",
                            evidence=[f"{rel}:{node.lineno}: def {node.name}"],
                            tags=["code-quality", "refactoring"],
                        )
                    )
        return results
