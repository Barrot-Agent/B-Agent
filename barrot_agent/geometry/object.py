"""Typed geometric object wrapping the existing mesh code.

This is a facade, not a second implementation. Validation and topology come
from ``barrot_agent.rendering.mesh_topology``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from barrot_agent.rendering.mesh_topology import analyze_mesh_topology


@dataclass(frozen=True)
class GeomObject:
    """A validated triangle mesh with provenance.

    ``kind`` names the representation, so the signature and relation layers
    never have to guess what they are looking at.
    """

    kind: str
    vertices: tuple[tuple[float, float, float], ...]
    faces: tuple[tuple[int, int, int], ...]
    provenance: str = field(default="", compare=False)

    @classmethod
    def from_mesh(
        cls,
        vertices: Sequence[Sequence[float]],
        faces: Sequence[Sequence[int]],
        *,
        kind: str = "triangle_mesh",
        provenance: str = "",
    ) -> "GeomObject":
        """Validate raw mesh data and return the typed object.

        Raises ValueError on the same inputs ``analyze_mesh_topology``
        rejects. Nothing is coerced before validation, so booleans, NaN and
        short tuples are rejected rather than silently accepted.
        """
        analyze_mesh_topology(vertices, faces)
        normalized_vertices = tuple(
            tuple(float(coordinate) for coordinate in vertex) for vertex in vertices
        )
        normalized_faces = tuple(tuple(face) for face in faces)
        return cls(
            kind=kind,
            vertices=normalized_vertices,
            faces=normalized_faces,
            provenance=provenance,
        )

    def topology(self) -> dict[str, Any]:
        """Topology snapshot from the existing analyzer."""
        return analyze_mesh_topology(self.vertices, self.faces)
