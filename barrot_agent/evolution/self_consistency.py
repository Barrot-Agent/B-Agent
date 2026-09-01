"""
Barrot Self-Consistency Engine.

Repository-native structural validation for Barrot.
Observational only: never modifies production code.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from barrot_agent.evolution.self_model import BarrotSelfModel


class SelfConsistencyEngine:
    """Validate Barrot's live repository model."""

    SCHEMA = "BARROT-SELF-CONSISTENCY-1"

    def __init__(
        self,
        model: BarrotSelfModel | None = None,
    ) -> None:
        self.model = model or BarrotSelfModel()

    def inspect(self) -> dict[str, Any]:
        """Run deterministic repository consistency checks."""

        awareness = self.model.awareness.refresh()
        files = awareness.get("files", [])

        issues: list[dict[str, Any]] = []

        self._check_duplicates(
            files,
            issues,
            self.model.awareness.root,
        )
        self._check_unparseable(files, issues)
        self._check_internal_dependencies(files, issues)

        duplicate_count = sum(
            1
            for issue in issues
            if issue["type"] == "duplicate_component"
        )

        unparseable_count = sum(
            1
            for issue in issues
            if issue["type"] == "unparseable_file"
        )

        dependency_count = sum(
            1
            for issue in issues
            if issue["type"]
            == "missing_internal_dependency"
        )

        indexed_files = sum(
            1
            for item in files
            if item.get("status") == "indexed"
        )

        return {
            "schema": self.SCHEMA,
            "repository": str(
                self.model.awareness.root
            ),
            "issues": issues,
            "issue_count": len(issues),
            "structurally_consistent": not issues,
            "statistics": {
                "files": len(files),
                "indexed_files": indexed_files,
                "duplicate_components": duplicate_count,
                "unparseable_files": unparseable_count,
                "missing_internal_dependencies": (
                    dependency_count
                ),
                "total_issues": len(issues),
            },
            "checks": {
                "duplicate_components": True,
                "unparseable_files": True,
                "internal_dependencies": True,
            },
        }

    @staticmethod
    def _check_duplicates(
        files: list[dict[str, Any]],
        issues: list[dict[str, Any]],
        repository_root: Any,
    ) -> None:
        """
        Detect materially duplicated top-level implementations.

        A same-named symbol is not inherently a contradiction.
        A duplicate is reported when the same class/function name
        has the same normalized AST implementation in different files.
        """

        import ast
        import hashlib

        locations: dict[
            tuple[str, str, str],
            list[dict[str, Any]],
        ] = defaultdict(list)

        ignored_roots = {
            "tests",
            "scripts",
            ".architecture_duplicate_backup",
            ".git",
            ".pytest_cache",
            "__pycache__",
            ".venv",
            "venv",
        }

        repository_root = Path(repository_root)

        for item in files:
            if item.get("status") != "indexed":
                continue

            path = item.get("path", "")
            parts = Path(path).parts

            if parts and parts[0] in ignored_roots:
                continue

            root = repository_root / path

            try:
                source = root.read_text(
                    encoding="utf-8"
                )
                tree = ast.parse(
                    source,
                    filename=path,
                )
            except (
                OSError,
                UnicodeDecodeError,
                SyntaxError,
            ):
                continue

            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    component_type = "class"
                elif isinstance(
                    node,
                    (ast.FunctionDef, ast.AsyncFunctionDef),
                ):
                    component_type = "function"
                else:
                    continue

                name = node.name

                normalized = ast.dump(
                    node,
                    annotate_fields=True,
                    include_attributes=False,
                )

                fingerprint = hashlib.sha256(
                    normalized.encode("utf-8")
                ).hexdigest()

                locations[
                    (
                        component_type,
                        name,
                        fingerprint,
                    )
                ].append({
                    "path": path,
                    "line": node.lineno,
                    "scope": "module",
                })

        for (
            component,
            matches,
        ) in locations.items():

            component_type, name, fingerprint = (
                component
            )

            unique_paths = {
                match["path"]
                for match in matches
            }

            if len(unique_paths) <= 1:
                continue

            issues.append({
                "type": "duplicate_component",
                "component_type": component_type,
                "name": name,
                "fingerprint": fingerprint,
                "locations": matches,
            })

    @staticmethod
    def _check_unparseable(
        files: list[dict[str, Any]],
        issues: list[dict[str, Any]],
    ) -> None:
        for item in files:
            if item.get("status") != "unparseable":
                continue

            issues.append({
                "type": "unparseable_file",
                "path": item.get("path"),
                "reason": item.get("reason"),
            })

    @staticmethod
    def _check_internal_dependencies(
        files: list[dict[str, Any]],
        issues: list[dict[str, Any]],
    ) -> None:
        known_modules: set[str] = set()

        for item in files:
            path = item.get("path", "")

            if not path.endswith(".py"):
                continue

            module = path[:-3].replace(
                "/",
                ".",
            )

            if module.endswith(
                ".__init__"
            ):
                module = module[:-9]

            known_modules.add(module)

        for item in files:
            if item.get("status") != "indexed":
                continue

            source = item.get(
                "path",
                "",
            )

            for dependency in item.get(
                "imports",
                [],
            ):
                if not dependency.startswith(
                    "barrot_agent"
                ):
                    continue

                if SelfConsistencyEngine._module_exists(
                    dependency,
                    known_modules,
                ):
                    continue

                issues.append({
                    "type": (
                        "missing_internal_dependency"
                    ),
                    "source": source,
                    "dependency": dependency,
                })

    @staticmethod
    def _module_exists(
        dependency: str,
        known_modules: set[str],
    ) -> bool:
        if dependency in known_modules:
            return True

        for module in known_modules:
            if module.startswith(
                dependency + "."
            ):
                return True

            if dependency.startswith(
                module + "."
            ):
                return True

        return False
