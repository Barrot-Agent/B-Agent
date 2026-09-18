"""Repository-wide Python dependency and change-impact analysis for V3."""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class RepositoryImpact:
    target: str
    dependencies: list[str]
    dependents: list[str]
    related_tests: list[str]
    risk_level: str

    def to_dict(self) -> dict:
        return asdict(self)


class RepositoryCausality:
    """Build a conservative Python import graph and identify downstream impact."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.python_files = self._discover_python_files()
        self.imports = self._build_import_graph()
        self.reverse_imports = self._build_reverse_graph()

    def _discover_python_files(self) -> list[Path]:
        files: list[Path] = []

        for path in self.root.rglob("*.py"):
            if "__pycache__" in path.parts or ".git" in path.parts:
                continue

            relative_parts = path.relative_to(self.root).parts
            if any((self.root / Path(*relative_parts[:index]) / ".git").is_dir()
                   for index in range(1, len(relative_parts))):
                continue

            files.append(path)

        return sorted(files)

    def _module_name(self, path: Path) -> str:
        relative = path.relative_to(self.root).with_suffix("")
        parts = list(relative.parts)
        if parts and parts[-1] == "__init__":
            parts.pop()
        return ".".join(parts)

    @staticmethod
    def _resolve_import(node: ast.AST) -> list[str]:
        if isinstance(node, ast.Import):
            return [alias.name for alias in node.names]
        if isinstance(node, ast.ImportFrom) and node.module:
            return [node.module]
        return []

    def _build_import_graph(self) -> dict[str, set[str]]:
        graph: dict[str, set[str]] = {}

        for path in self.python_files:
            module = self._module_name(path)
            graph.setdefault(module, set())

            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    graph[module].update(self._resolve_import(node))

        return graph

    def _build_reverse_graph(self) -> dict[str, set[str]]:
        reverse: dict[str, set[str]] = {}
        for source, targets in self.imports.items():
            for target in targets:
                reverse.setdefault(target, set()).add(source)
        return reverse

    def _matching_dependents(self, module: str) -> set[str]:
        matches: set[str] = set()

        for imported, users in self.reverse_imports.items():
            if (
                imported == module
                or imported.startswith(module + ".")
                or module.startswith(imported + ".")
            ):
                matches.update(users)

        return matches

    def _related_tests(self, module: str) -> list[str]:
        name = module.split(".")[-1]
        matches: list[str] = []

        for path in self.python_files:
            if "tests" not in path.parts:
                continue
            if name in path.stem:
                matches.append(str(path.relative_to(self.root)))

        return sorted(set(matches))

    def analyze(self, target: str | Path) -> RepositoryImpact:
        path = Path(target)
        if not path.is_absolute():
            path = (self.root / path).resolve()

        try:
            relative = path.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(f"Target is outside repository root: {target}") from exc

        if path.suffix != ".py":
            return RepositoryImpact(
                target=str(relative),
                dependencies=[],
                dependents=[],
                related_tests=[],
                risk_level="low",
            )

        module = self._module_name(path)
        dependencies = sorted(self.imports.get(module, set()))
        dependents = sorted(self._matching_dependents(module))
        related_tests = self._related_tests(module)

        impact_size = len(dependents) + len(related_tests)
        if impact_size >= 10:
            risk_level = "high"
        elif impact_size >= 3:
            risk_level = "medium"
        else:
            risk_level = "low"

        return RepositoryImpact(
            target=str(relative),
            dependencies=dependencies,
            dependents=dependents,
            related_tests=related_tests,
            risk_level=risk_level,
        )

    def analyze_many(
        self, targets: Iterable[str | Path]
    ) -> list[RepositoryImpact]:
        return [self.analyze(target) for target in targets]
