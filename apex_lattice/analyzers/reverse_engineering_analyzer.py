"""
Reverse Engineering Analyzer.

Produces a structural breakdown of each Python module in the repo:
public inputs (function/method signatures), outputs (presence and shape
of return statements), dependencies (imports), and likely design intent
inferred from concrete structural signals (base classes, decorators,
naming conventions) - not from any external or fabricated source.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from apex_lattice.analyzers.base import BaseAnalyzer

_DESIGN_SIGNALS = {
    "ABC": "defines an interface/contract other classes must implement",
    "Protocol": "defines a structural typing contract",
    "Enum": "defines a closed, fixed set of values",
    "dataclass": "used as a plain data container",
    "Exception": "custom error type for this module's failure modes",
}


class Analyzer(BaseAnalyzer):
    name = "reverse_engineering_analyzer"

    def analyze(self) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []

        for path in self._iter_source_files((".py",)):
            source = self._read_text(path)
            if not source.strip():
                continue
            rel = path.relative_to(self.repo_root)
            try:
                tree = ast.parse(source)
            except SyntaxError as exc:
                findings.append(
                    self._make_finding(
                        title="Module fails to parse",
                        description=f"`{rel}` is not valid Python: {exc}",
                        severity="high",
                        evidence=[f"{rel}: {exc}"],
                        tags=["reverse-engineering", "broken"],
                    )
                )
                continue

            findings.extend(self._breakdown_classes(rel, tree))
            findings.extend(self._breakdown_functions(rel, tree))
            findings.extend(self._breakdown_dependencies(rel, tree))

        return {"findings": findings}

    def _breakdown_classes(self, rel: Path, tree: ast.AST) -> list[dict[str, Any]]:
        results = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            bases = [self._name_of(b) for b in node.bases]
            decorators = [self._name_of(d) for d in node.decorator_list]
            signals = [
                _DESIGN_SIGNALS[b] for b in bases + decorators if b in _DESIGN_SIGNALS
            ]
            methods = [
                n.name for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not n.name.startswith("_")
            ]
            desc = f"`{node.name}` in `{rel}`"
            if bases:
                desc += f" - inherits from {', '.join(bases)}"
            if signals:
                desc += f". Structural role: {'; '.join(signals)}"
            if methods:
                desc += f". Public interface: {', '.join(methods[:8])}"
                if len(methods) > 8:
                    desc += f" (+{len(methods) - 8} more)"
            results.append(
                self._make_finding(
                    title=f"Class breakdown: {node.name}",
                    description=desc,
                    severity="info",
                    evidence=[f"{rel}:{node.lineno}: class {node.name}"],
                    tags=["reverse-engineering", "structure"],
                )
            )
        return results

    def _breakdown_functions(self, rel: Path, tree: ast.AST) -> list[dict[str, Any]]:
        results = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith("_"):
                continue
            args = [a.arg for a in node.args.args if a.arg != "self"]
            has_return = any(
                isinstance(n, ast.Return) and n.value is not None
                for n in ast.walk(node)
            )
            has_yield = any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(node))
            output_kind = "generator" if has_yield else ("value" if has_return else "side-effect only")
            results.append(
                self._make_finding(
                    title=f"Function signature: {node.name}",
                    description=(
                        f"`{node.name}({', '.join(args)})` in `{rel}` - "
                        f"output type: {output_kind}."
                    ),
                    severity="info",
                    evidence=[f"{rel}:{node.lineno}: def {node.name}"],
                    tags=["reverse-engineering", "signature"],
                )
            )
        return results

    def _breakdown_dependencies(self, rel: Path, tree: ast.AST) -> list[dict[str, Any]]:
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        if not imports:
            return []
        return [
            self._make_finding(
                title="Module dependencies",
                description=f"`{rel}` imports: {', '.join(sorted(imports))}.",
                severity="info",
                evidence=[f"{rel}: {len(imports)} top-level import(s)"],
                tags=["reverse-engineering", "dependencies"],
            )
        ]

    @staticmethod
    def _name_of(node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        if isinstance(node, ast.Call):
            return Analyzer._name_of(node.func)
        return ast.dump(node).split("(")[0]
