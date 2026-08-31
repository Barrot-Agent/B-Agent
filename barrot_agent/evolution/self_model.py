"""
Barrot Self-Model.

Provides a unified, read-only model of Barrot's repository architecture,
trust infrastructure, evidence pipeline, tests, dependencies, and known
integration surfaces.

The self-model describes the system. It does not modify the repository.
"""

from __future__ import annotations

from typing import Any

from barrot_agent.evolution.architecture_graph import ArchitectureGraph
from barrot_agent.evolution.confidence_calibration import (
    ConfidenceCalibrationEngine,
)
from barrot_agent.evolution.repository_awareness import (
    RepositoryAwarenessEngine,
)
from barrot_agent.evolution.evidence_store import EvidenceStore


class BarrotSelfModel:
    """Unified repository-level model for Barrot's own reasoning."""

    def __init__(
        self,
        awareness: RepositoryAwarenessEngine | None = None,
    ) -> None:
        self.awareness = awareness or RepositoryAwarenessEngine()
        self.graph = ArchitectureGraph(self.awareness)
        self.calibration = ConfidenceCalibrationEngine()
        self.evidence = EvidenceStore()

    def snapshot(self) -> dict[str, Any]:
        """Return the complete current self-model."""
        awareness = self.awareness.refresh()
        graph = self.graph.build()

        return {
            "schema": "BARROT-SELF-MODEL-1",
            "repository": str(self.awareness.root),
            "repository_awareness": awareness,
            "architecture": {
                "nodes": len(graph["nodes"]),
                "edges": len(graph["edges"]),
            },
            "trust": self._trust_model(awareness),
            "evidence": self.evidence.summary(),
            "calibration": self.calibration.summary(),
            "queries": {
                "component": True,
                "dependencies": True,
                "dependents": True,
                "impact": True,
                "trust": True,
            },
        }

    def _trust_model(self, awareness: dict[str, Any]) -> dict[str, Any]:
        cross = awareness.get("cross_analysis", {})
        trust_layer = cross.get("trust_layer", [])
        integration = cross.get("integration_layer", [])

        return {
            "components": trust_layer,
            "integration_count": len(integration),
            "integrated": bool(
                cross.get("interpretation", {}).get("trust_integrated")
            ),
            "test_coverage": bool(
                cross.get("interpretation", {}).get("test_coverage_present")
            ),
        }

    def component(self, name: str) -> dict[str, Any]:
        """Locate a component and describe its immediate architecture."""
        matches = self.awareness.find_component(name)

        results = []

        for match in matches:
            path = match["path"]

            try:
                impact = self.graph.impact(path)
            except Exception:
                impact = {
                    "component": path,
                    "dependencies": [],
                    "dependents": [],
                    "direct_impact_count": 0,
                }

            results.append({
                **match,
                "impact": impact,
            })

        return {
            "query": name,
            "matches": results,
            "count": len(results),
        }

    def dependencies(self, component: str) -> dict[str, Any]:
        return {
            "component": component,
            "dependencies": self.graph.dependencies(component),
        }

    def dependents(self, component: str) -> dict[str, Any]:
        return {
            "component": component,
            "dependents": self.graph.dependents(component),
        }

    def impact(self, component: str) -> dict[str, Any]:
        return self.graph.impact(component)

    def trust(self) -> dict[str, Any]:
        snapshot = self.snapshot()

        return {
            "trust_architecture": snapshot["trust"],
            "calibration": snapshot["calibration"],
        }

    def ask(self, query: str) -> dict[str, Any]:
        """
        Resolve common architectural questions against the live repository.

        This is deliberately deterministic and repository-backed. A future
        reasoning layer can consume this structured result rather than relying
        on an approximate description of the codebase.
        """
        text = query.lower().strip()

        if "trust" in text:
            return {
                "query": query,
                "intent": "trust",
                "result": self.trust(),
            }

        if "depend" in text and "impact" not in text:
            name = self._extract_component(query)
            return {
                "query": query,
                "intent": "dependencies",
                "result": self.dependencies(name),
            }

        if "impact" in text or "affected" in text:
            name = self._extract_component(query)
            return {
                "query": query,
                "intent": "impact",
                "result": self.impact(name),
            }

        if "component" in text or "class" in text or "where is" in text:
            name = self._extract_component(query)
            return {
                "query": query,
                "intent": "component",
                "result": self.component(name),
            }

        return {
            "query": query,
            "intent": "snapshot",
            "result": self.snapshot(),
        }

    @staticmethod
    def _extract_component(query: str) -> str:
        tokens = [
            token.strip("`'\".,:!?()[]{}")
            for token in query.split()
        ]

        candidates = [
            token
            for token in tokens
            if token
            and (
                token.endswith("Engine")
                or token.endswith("Pipeline")
                or token.endswith("Store")
                or token.endswith("Loop")
                or token.endswith("Graph")
                or token.endswith("Model")
                or token.endswith("Adapter")
            )
        ]

        return candidates[-1] if candidates else tokens[-1]
