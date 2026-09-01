"""Bootstrap the next autonomous Barrot capability sequence."""

from barrot_agent.autonomy.capability_queue import (
    Capability,
    CapabilityQueue,
)


def main() -> None:
    queue = CapabilityQueue()

    capabilities = [
        Capability(
            id="code_as_world_foundation",
            name=(
                "Code-as-World foundation: "
                "video-to-structured-world pipeline"
            ),
            priority=10,
            metadata={
                "phase": "foundation",
            },
        ),
        Capability(
            id="video_observation",
            name=(
                "Video observation and scene extraction"
            ),
            priority=20,
            metadata={
                "phase": "perception",
            },
        ),
        Capability(
            id="world_representation",
            name=(
                "Structured physical world representation"
            ),
            priority=30,
            metadata={
                "phase": "representation",
            },
        ),
        Capability(
            id="physics_program_generation",
            name=(
                "Executable MuJoCo physics program generation"
            ),
            priority=40,
            metadata={
                "phase": "simulation",
            },
        ),
        Capability(
            id="simulation_validation",
            name=(
                "Simulation comparison and validation loop"
            ),
            priority=50,
            metadata={
                "phase": "validation",
            },
        ),
        Capability(
            id="autonomous_refinement",
            name=(
                "Autonomous iterative world refinement"
            ),
            priority=60,
            metadata={
                "phase": "autonomy",
            },
        ),
    ]

    for capability in capabilities:
        queue.add(capability)
        print(
            f"QUEUED: "
            f"{capability.priority} "
            f"{capability.id}"
        )

    next_item = queue.next()

    print()
    print("=== NEXT CAPABILITY ===")

    if next_item is None:
        print("NONE")
        return

    print(next_item.id)
    print(next_item.name)


if __name__ == "__main__":
    main()
