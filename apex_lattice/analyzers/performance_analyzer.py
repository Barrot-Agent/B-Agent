"""
Performance Analyzer.

Looks for common performance anti-patterns: nested loops over large
structures, synchronous blocking calls inside async functions, and
missing caching opportunities.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from apex_lattice.analyzers.base import BaseAnalyzer

_SLEEP_RE = re.compile(r"\btime\.sleep\s*\(")
_REQUESTS_SYNC_RE = re.compile(r"\brequests\.(get|post|put|delete|patch)\s*\(")


class Analyzer(BaseAnalyzer):
    name = "performance_analyzer"

    def analyze(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        for path in self._iter_source_files((".py",)):
            source = self._read_text(path)
            rel = path.relative_to(self.repo_root)

            findings.extend(self._check_sync_in_async(rel, source))
            findings.extend(self._check_blocking_sleep(rel, source))
            findings.extend(self._check_nested_loops(rel, source))

        return {"findings": findings}

    # ------------------------------------------------------------------
    def _check_sync_in_async(self, rel: Path, source: str) -> list[dict[str, Any]]:
        """Flag synchronous requests.* calls inside async functions."""
        results = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return results

        for node in ast.walk(tree):
            if not isinstance(node, ast.AsyncFunctionDef):
                continue
            func_src_lines = source.splitlines()[node.lineno - 1 : getattr(node, "end_lineno", node.lineno)]
            func_src = "\n".join(func_src_lines)
            for match in _REQUESTS_SYNC_RE.finditer(func_src):
                lineno = node.lineno + func_src[: match.start()].count("\n")
                results.append(
                    self._make_finding(
                        title="Synchronous HTTP call inside async function",
                        description=(
                            f"`requests.{match.group(1)}` in async function "
                            f"`{node.name}` at `{rel}:{lineno}` blocks the "
                            "event loop. Use `httpx` or `aiohttp` instead."
                        ),
                        severity="high",
                        evidence=[f"{rel}:{lineno}"],
                        tags=["performance", "async"],
                    )
                )
        return results

    def _check_blocking_sleep(self, rel: Path, source: str) -> list[dict[str, Any]]:
        results = []
        for i, line in enumerate(source.splitlines(), 1):
            if _SLEEP_RE.search(line):
                results.append(
                    self._make_finding(
                        title="Blocking time.sleep detected",
                        description=(
                            f"`time.sleep` at `{rel}:{i}` blocks execution. "
                            "Use `asyncio.sleep` in async contexts."
                        ),
                        severity="medium",
                        evidence=[f"{rel}:{i}: {line.strip()}"],
                        tags=["performance", "blocking"],
                    )
                )
        return results

    def _check_nested_loops(self, rel: Path, source: str) -> list[dict[str, Any]]:
        """Detect triply-nested for-loops as O(n³) risk."""
        results = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return results

        def _depth(node: ast.AST, current: int = 0) -> int:
            if isinstance(node, (ast.For, ast.While)):
                current += 1
            return max(
                (_depth(child, current) for child in ast.iter_child_nodes(node)),
                default=current,
            )

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                if _depth(node) >= 3:
                    results.append(
                        self._make_finding(
                            title="Deeply nested loop",
                            description=(
                                f"Triply-nested loop at `{rel}:{node.lineno}` "
                                "may indicate an O(n³) algorithm. Consider "
                                "refactoring with indexed lookups or vectorized ops."
                            ),
                            severity="medium",
                            evidence=[f"{rel}:{node.lineno}"],
                            tags=["performance", "algorithm"],
                        )
                    )
        return results
