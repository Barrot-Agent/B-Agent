from barrot_agent.capability_parity import (
    Capability,
    CapabilityMatrix,
    CapabilityStatus,
)
from barrot_agent.roadmap import build_upgrade_roadmap, roadmap_to_dict


def test_roadmap_prioritizes_high_priority_gaps():
    matrix = CapabilityMatrix(
        [
            Capability(
                "memory", "state", "memory", CapabilityStatus.IMPLEMENTED,
                CapabilityStatus.IMPLEMENTED, CapabilityStatus.PARTIAL, "medium",
            ),
            Capability(
                "safety", "governance", "safety", CapabilityStatus.IMPLEMENTED,
                CapabilityStatus.IMPLEMENTED, CapabilityStatus.MISSING, "critical",
            ),
        ]
    )

    roadmap = build_upgrade_roadmap(matrix)

    assert [item.capability for item in roadmap] == ["safety", "memory"]
    assert roadmap[0].order == 1
    assert "benchmark" in roadmap[0].acceptance_gate


def test_roadmap_serialization_preserves_limitations():
    result = roadmap_to_dict(CapabilityMatrix([]))

    assert result["items"] == []
    assert result["limitations"]
