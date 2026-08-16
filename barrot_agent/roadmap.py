"""Generate a grounded upgrade roadmap from Barrot's capability matrix."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from barrot_agent.capability_parity import (
    Capability,
    CapabilityMatrix,
    CapabilityStatus,
    DEFAULT_CAPABILITY_MATRIX,
)


_PRIORITY_WEIGHT = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@dataclass(frozen=True)
class RoadmapItem:
    """One bounded upgrade step with an observable acceptance gate."""

    order: int
    capability: str
    category: str
    priority: str
    current_status: str
    objective: str
    acceptance_gate: str
    evidence: tuple[str, ...]


def _objective(capability: Capability) -> str:
    if capability.barrot is CapabilityStatus.EXTERNAL_PROVIDER:
        return f"Integrate and verify a provider for {capability.description.lower()}."
    return f"Raise Barrot from {capability.barrot.value} to implemented for {capability.description.lower()}."


def _gate(capability: Capability) -> str:
    if capability.key == "safety":
        return "All safety benchmarks pass and unauthorized actions remain blocked."
    if capability.key == "coding":
        return "Repository changes pass targeted tests, review, and security checks."
    if capability.key == "tools_mcp":
        return "Tool schemas validate and approved calls produce provenance records."
    return f"Add a deterministic benchmark for {capability.key} and record a passing result."


def build_upgrade_roadmap(
    matrix: CapabilityMatrix = DEFAULT_CAPABILITY_MATRIX,
) -> list[RoadmapItem]:
    """Return prioritized gaps without claiming capabilities are complete."""
    gaps = sorted(
        matrix.gaps(),
        key=lambda item: (_PRIORITY_WEIGHT.get(item.priority, 99), item.key),
    )
    return [
        RoadmapItem(
            order=index,
            capability=item.key,
            category=item.category,
            priority=item.priority,
            current_status=item.barrot.value,
            objective=_objective(item),
            acceptance_gate=_gate(item),
            evidence=item.evidence,
        )
        for index, item in enumerate(gaps, start=1)
    ]


def roadmap_to_dict(
    matrix: CapabilityMatrix = DEFAULT_CAPABILITY_MATRIX,
) -> dict[str, Any]:
    """Serialize the roadmap and its source capability snapshot."""
    items = build_upgrade_roadmap(matrix)
    return {
        "source": "barrot_agent.capability_parity.DEFAULT_CAPABILITY_MATRIX",
        "items": [asdict(item) for item in items],
        "limitations": [
            "This roadmap measures observable repository capabilities, not proprietary model internals.",
            "Each item must pass its acceptance gate before being marked implemented.",
        ],
    }
