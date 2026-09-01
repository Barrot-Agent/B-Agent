"""
Barrot Self-Model.

Repository-backed, read-only model of Barrot's architecture,
trust system, evidence system, calibration system, dependencies,
dependents, impact, and self-audit state.
"""

from __future__ import annotations

from typing import Any

from barrot_agent.evolution.confidence_calibration import (
    ConfidenceCalibrationEngine,
)
from barrot_agent.evolution.evidence_store import EvidenceStore
from barrot_agent.evolution.repository_awareness import (
    RepositoryAwarenessEngine,
)


class BarrotSelfModel:
    """Unified live model of Barrot's repository."""

    SCHEMA = "BARROT-SELF-MODEL-1"

    def __init__(
        self,
        awareness: RepositoryAwarenessEngine | None = None,
    ) -> None:
        self.awareness = (
            awareness
            or RepositoryAwarenessEngine()
        )
        self.calibration = (
            ConfidenceCalibrationEngine()
        )
        self.evidence = EvidenceStore()

    def _files(self) -> list[dict[str, Any]]:
        return self.awareness.load().get(
            "files",
            [],
        )

    def snapshot(self) -> dict[str, Any]:
        awareness = self.awareness.refresh()
        files = awareness.get("files", [])

        return {
            "schema": self.SCHEMA,
            "repository": str(
                self.awareness.root
            ),
            "repository_awareness": awareness,
            "architecture": {
                "nodes": len(files),
                "edges": self._edge_count(files),
            },
            "trust": self._trust_model(
                awareness
            ),
            "evidence": self.evidence.summary(),
            "calibration": (
                self.calibration.summary()
            ),
            "queries": {
                "component": True,
                "dependencies": True,
                "dependents": True,
                "impact": True,
                "trust": True,
                "self_audit": True,
            },
        }

    @staticmethod
    def _edge_count(
        files: list[dict[str, Any]],
    ) -> int:
        return sum(
            len(item.get("imports", []))
            for item in files
            if item.get("status") == "indexed"
        )

    @staticmethod
    def _trust_model(
        awareness: dict[str, Any],
    ) -> dict[str, Any]:
        cross = awareness.get(
            "cross_analysis",
            {},
        )
        interpretation = cross.get(
            "interpretation",
            {},
        )

        return {
            "components": cross.get(
                "trust_layer",
                [],
            ),
            "integration_count": len(
                cross.get(
                    "integration_layer",
                    [],
                )
            ),
            "integrated": bool(
                interpretation.get(
                    "trust_integrated"
                )
            ),
            "test_coverage": bool(
                interpretation.get(
                    "test_coverage_present"
                )
            ),
        }

    def component(
        self,
        name: str,
    ) -> dict[str, Any]:
        matches = (
            self.awareness.find_component(
                name
            )
        )

        unique: dict[
            tuple[Any, ...],
            dict[str, Any],
        ] = {}

        for match in matches:
            key = (
                match.get("path"),
                match.get("type"),
                match.get("name"),
                match.get("line"),
            )
            unique[key] = match

        results = []

        for match in unique.values():
            path = match["path"]

            results.append({
                **match,
                "dependencies": (
                    self._dependencies_for_path(
                        path
                    )
                ),
                "dependents": (
                    self._dependents_for_path(
                        path
                    )
                ),
            })

        return {
            "query": name,
            "matches": results,
            "count": len(results),
        }

    def dependencies(
        self,
        component: str,
    ) -> dict[str, Any]:
        path = self._resolve_path(component)

        return {
            "component": component,
            "resolved": path is not None,
            "path": path,
            "dependencies": (
                self._dependencies_for_path(
                    path
                )
                if path
                else []
            ),
        }

    def dependents(
        self,
        component: str,
    ) -> dict[str, Any]:
        path = self._resolve_path(component)

        return {
            "component": component,
            "resolved": path is not None,
            "path": path,
            "dependents": (
                self._dependents_for_path(
                    path
                )
                if path
                else []
            ),
        }

    def impact(
        self,
        component: str,
    ) -> dict[str, Any]:
        path = self._resolve_path(component)

        if path is None:
            return {
                "component": component,
                "resolved": False,
                "dependencies": [],
                "dependents": [],
                "direct_impact_count": 0,
            }

        dependencies = (
            self._dependencies_for_path(path)
        )
        dependents = (
            self._dependents_for_path(path)
        )

        return {
            "component": component,
            "resolved": True,
            "path": path,
            "dependencies": dependencies,
            "dependents": dependents,
            "direct_impact_count": len(
                dependents
            ),
        }

    def trust(self) -> dict[str, Any]:
        snapshot = self.snapshot()

        return {
            "trust_architecture": snapshot[
                "trust"
            ],
            "calibration": snapshot[
                "calibration"
            ],
        }

    def self_audit(self) -> dict[str, Any]:
        awareness = self.awareness.refresh()
        files = awareness.get(
            "files",
            [],
        )

        unparseable = [
            {
                "path": item.get("path"),
                "reason": item.get("reason"),
            }
            for item in files
            if item.get("status")
            == "unparseable"
        ]

        known_modules = {
            self._module_name(
                item["path"]
            )
            for item in files
            if item.get(
                "path",
                "",
            ).endswith(".py")
        }

        missing_dependencies = []

        for item in files:
            if item.get("status") != "indexed":
                continue

            source = item.get("path", "")

            for dependency in item.get(
                "imports",
                [],
            ):
                if not dependency.startswith(
                    "barrot_agent"
                ):
                    continue

                if not any(
                    module == dependency
                    or module.startswith(
                        dependency + "."
                    )
                    or dependency.startswith(
                        module + "."
                    )
                    for module in known_modules
                ):
                    missing_dependencies.append({
                        "source": source,
                        "dependency": dependency,
                    })

        return {
            "schema": (
                "BARROT-SELF-AUDIT-1"
            ),
            "repository": str(
                self.awareness.root
            ),
            "indexed_files": (
                len(files)
                - len(unparseable)
            ),
            "unparseable_files": unparseable,
            "missing_internal_dependencies": (
                missing_dependencies
            ),
            "repository_state": awareness.get(
                "git",
                {},
            ),
            "trust": self._trust_model(
                awareness
            ),
            "structurally_sound": (
                not unparseable
                and not missing_dependencies
            ),
        }

    def ask(
        self,
        query: str,
    ) -> dict[str, Any]:
        text = query.lower().strip()

        if not text:
            return {
                "query": query,
                "intent": "snapshot",
                "result": self.snapshot(),
            }

        if (
            "audit" in text
            or "self-aware" in text
            or "self aware" in text
            or "self consistency" in text
            or "self-consistency" in text
        ):
            return {
                "query": query,
                "intent": "self_audit",
                "result": self.self_audit(),
            }

        if "trust" in text:
            return {
                "query": query,
                "intent": "trust",
                "result": self.trust(),
            }

        name = self._extract_component(
            query
        )

        if (
            "impact" in text
            or "affected" in text
        ):
            return {
                "query": query,
                "intent": "impact",
                "result": self.impact(name),
            }

        if (
            "dependent" in text
            or "depends on me" in text
        ):
            return {
                "query": query,
                "intent": "dependents",
                "result": self.dependents(name),
            }

        if "depend" in text:
            return {
                "query": query,
                "intent": "dependencies",
                "result": self.dependencies(name),
            }

        return {
            "query": query,
            "intent": "component",
            "result": self.component(name),
        }

    def _resolve_path(
        self,
        component: str,
    ) -> str | None:
        normalized = component.replace(
            chr(92),
            "/",
        )

        if normalized.endswith(".py"):
            for item in self._files():
                if item.get("path") == normalized:
                    return normalized

        matches = self.awareness.find_component(
            component
        )

        if matches:
            return matches[0]["path"]

        module = normalized.replace(
            ".",
            "/",
        )

        if not module.endswith(".py"):
            module += ".py"

        for item in self._files():
            if item.get("path") == module:
                return module

        return None

    def _dependencies_for_path(
        self,
        path: str | None,
    ) -> list[str]:
        if path is None:
            return []

        for item in self._files():
            if item.get("path") == path:
                return item.get(
                    "imports",
                    [],
                )

        return []

    def _dependents_for_path(
        self,
        path: str | None,
    ) -> list[str]:
        if path is None:
            return []

        module = path[:-3].replace(
            "/",
            ".",
        )

        dependents = []

        for item in self._files():
            if item.get("path") == path:
                continue

            imports = item.get(
                "imports",
                [],
            )

            if any(
                dependency == module
                or dependency.startswith(
                    module + "."
                )
                or module.startswith(
                    dependency + "."
                )
                for dependency in imports
            ):
                dependents.append(
                    item["path"]
                )

        return sorted(set(dependents))

    @staticmethod
    def _module_name(
        path: str,
    ) -> str:
        module = path[:-3].replace(
            "/",
            ".",
        )

        if module.endswith(
            ".__init__"
        ):
            module = module[:-9]

        return module

    @staticmethod
    def _extract_component(
        query: str,
    ) -> str:
        tokens = [
            token.strip(
                "`'\".,:!?()[]{}"
            )
            for token in query.split()
        ]

        candidates = [
            token
            for token in tokens
            if token.endswith(
                (
                    "Engine",
                    "Pipeline",
                    "Store",
                    "Loop",
                    "Graph",
                    "Model",
                    "Adapter",
                )
            )
        ]

        return (
            candidates[-1]
            if candidates
            else (
                tokens[-1]
                if tokens
                else ""
            )
        )
