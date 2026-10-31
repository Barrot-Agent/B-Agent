"""
Test Quality Analyzer.

Checks whether tests actually validate behavior, not just whether a test
file exists - the FrontierCode benchmark's distinguishing dimension for
production-ready coding agents (Cognition, June 2026).

Two real, structural checks:
  1. Every def test_* function is parsed for an actual assertion
     (assert statement, pytest.raises, or self.assertX call). Test
     functions with zero assertions can pass trivially and are flagged.
  2. Every top-level module with public functions/classes is checked for
     a plausibly corresponding test file (test_<name>.py or
     <name>_test.py, anywhere in the repo). Missing coverage is flagged
     at low severity - a naming-convention heuristic, not proof of
     absence, so it's reported as a gap to review, not a defect.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from apex_lattice.analyzers.base import BaseAnalyzer

_ASSERT_CALL_NAMES = {"assertRaises", "raises", "assertEqual", "assertTrue", "assertFalse",
                       "assertIn", "assertIsNone", "assertIsNotNone", "assertAlmostEqual"}


class Analyzer(BaseAnalyzer):
    name = "test_quality_analyzer"

    def analyze(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        test_files: list[Path] = []
        source_files: list[Path] = []
        for path in self._iter_source_files((".py",)):
            name = path.name
            if name.startswith("test_") or name.endswith("_test.py"):
                test_files.append(path)
            elif not name.startswith("_") and "/.apex_lattice/" not in str(path):
                source_files.append(path)

        for tf in test_files:
            findings.extend(self._check_assertions(tf))

        findings.extend(self._check_coverage_gaps(source_files, test_files))

        return {"findings": findings}

    def _check_assertions(self, path: Path) -> list[dict[str, Any]]:
        results = []
        source = self._read_text(path)
        if not source.strip():
            return results
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return results
        rel = path.relative_to(self.repo_root)

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("test"):
                continue
            has_assertion = self._has_assertion(node)
            if not has_assertion:
                results.append(
                    self._make_finding(
                        title="Test with no assertion",
                        description=(
                            f"`{node.name}` in `{rel}` (line {node.lineno}) contains no "
                            "assert statement or assertion call - it will pass even if "
                            "the code under test is broken."
                        ),
                        severity="high",
                        evidence=[f"{rel}:{node.lineno}: def {node.name}"],
                        tags=["test-quality", "weak-test"],
                    )
                )
        return results

    @staticmethod
    def _has_assertion(node: ast.AST) -> bool:
        for n in ast.walk(node):
            if isinstance(n, ast.Assert):
                return True
            if isinstance(n, ast.Call):
                func = n.func
                fname = func.attr if isinstance(func, ast.Attribute) else (
                    func.id if isinstance(func, ast.Name) else ""
                )
                if fname in _ASSERT_CALL_NAMES:
                    return True
        return False

    def _check_coverage_gaps(
        self, source_files: list[Path], test_files: list[Path]
    ) -> list[dict[str, Any]]:
        test_stems = set()
        for tf in test_files:
            stem = tf.stem
            if stem.startswith("test_"):
                test_stems.add(stem[len("test_"):])
            if stem.endswith("_test"):
                test_stems.add(stem[: -len("_test")])

        results = []
        for sf in source_files:
            if sf.stem in ("__init__", "__main__", "conftest", "setup"):
                continue
            if not self._has_public_defs(sf):
                continue
            if sf.stem not in test_stems:
                rel = sf.relative_to(self.repo_root)
                results.append(
                    self._make_finding(
                        title="No matching test file found",
                        description=(
                            f"`{rel}` defines public functions/classes but no "
                            f"`test_{sf.stem}.py` or `{sf.stem}_test.py` was found "
                            "anywhere in the repo (naming-convention check only - "
                            "review before assuming it's actually untested)."
                        ),
                        severity="low",
                        evidence=[str(rel)],
                        tags=["test-quality", "coverage-gap"],
                    )
                )
        return results

    def _has_public_defs(self, path: Path) -> bool:
        source = self._read_text(path)
        if not source.strip():
            return False
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return False
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not node.name.startswith("_"):
                    return True
        return False
