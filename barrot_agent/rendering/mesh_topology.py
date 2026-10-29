"""Dependency-free triangle mesh topology inspection."""
from __future__ import annotations

import math
from collections import Counter
from typing import Any, Sequence


def analyze_mesh_topology(
    vertices: Sequence[Sequence[float]],
    faces: Sequence[Sequence[int]],
) -> dict[str, Any]:
    """Measure triangle validity and edge incidence from explicit mesh data."""
    points = []
    for i, vertex in enumerate(vertices):
        if len(vertex) != 3:
            raise ValueError(f"Vertex {i} must contain exactly 3 coordinates")
        point = tuple(float(v) for v in vertex)
        if not all(math.isfinite(v) for v in point):
            raise ValueError(f"Vertex {i} contains a non-finite coordinate")
        points.append(point)

    triangles = []
    degenerate = 0
    for i, face in enumerate(faces):
        if len(face) != 3:
            raise ValueError(f"Face {i} must contain exactly 3 vertex indices")
        if any(not isinstance(v, int) or isinstance(v, bool) for v in face):
            raise ValueError(f"Face {i} contains a non-integer vertex index")
        a, b, c = face
        if min(a, b, c) < 0 or max(a, b, c) >= len(points):
            raise ValueError(f"Face {i} references a vertex outside the mesh")
        if len({a, b, c}) != 3:
            degenerate += 1
        else:
            p, q, r = points[a], points[b], points[c]
            u = tuple(q[j] - p[j] for j in range(3))
            v = tuple(r[j] - p[j] for j in range(3))
            cross = (
                u[1] * v[2] - u[2] * v[1],
                u[2] * v[0] - u[0] * v[2],
                u[0] * v[1] - u[1] * v[0],
            )
            if sum(x * x for x in cross) <= 1e-24:
                degenerate += 1
        triangles.append((a, b, c))

    incidence = Counter()
    for a, b, c in triangles:
        for x, y in ((a, b), (b, c), (c, a)):
            incidence[(min(x, y), max(x, y))] += 1

    boundary = sum(count == 1 for count in incidence.values())
    non_manifold = sum(count > 2 for count in incidence.values())
    watertight = bool(triangles) and boundary == 0 and non_manifold == 0 and degenerate == 0

    return {
        "triangle_count": len(triangles),
        "vertex_count": len(points),
        "degenerate_triangles": degenerate,
        "non_manifold_edges": non_manifold,
        "open_boundaries": boundary,
        "is_watertight": watertight,
        "topology_status": "ASSESSED",
        "edge_count": len(incidence),
    }
