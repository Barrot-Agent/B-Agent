"""Structured physical world models for Code-as-World."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Vector3:
    x: float
    y: float
    z: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass
class WorldObject:
    id: str
    kind: str
    position: Vector3
    size: Vector3
    mass: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "position": self.position.to_dict(),
            "size": self.size.to_dict(),
            "mass": self.mass,
            "metadata": self.metadata,
        }


@dataclass
class WorldState:
    time_seconds: float
    objects: list[WorldObject] = field(
        default_factory=list,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "time_seconds": self.time_seconds,
            "objects": [
                obj.to_dict()
                for obj in self.objects
            ],
        }


@dataclass
class PhysicalWorld:
    source_path: str
    fps: float
    states: list[WorldState] = field(
        default_factory=list,
    )
    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "fps": self.fps,
            "states": [
                state.to_dict()
                for state in self.states
            ],
            "metadata": self.metadata,
        }
