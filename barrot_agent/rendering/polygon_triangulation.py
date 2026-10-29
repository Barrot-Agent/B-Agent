"""Dependency-free ear-clipping triangulation for simple planar polygons."""
from __future__ import annotations

import math
from typing import Sequence


def triangulate_polygon(
    vertices: Sequence[Sequence[float]], polygon: Sequence[int]
) -> list[tuple[int, int, int]]:
    """Triangulate a simple planar polygon using projected ear clipping.

    Supports concave polygons. Rejects degenerate polygons or cases for which
    a valid ear cannot be found. Does not guarantee detection of every
    self-intersecting or non-planar input.
    """
    if len(polygon) < 3 or len(set(polygon)) != len(polygon):
        raise ValueError("polygon needs at least three distinct vertex indices")

    points = []
    for index in polygon:
        if index < 0 or index >= len(vertices):
            raise ValueError("vertex index out of range")
        point = vertices[index]
        if len(point) != 3:
            raise ValueError("vertices must have three coordinates")
        try:
            converted = tuple(float(v) for v in point)
        except (TypeError, ValueError) as exc:
            raise ValueError("vertex coordinates must be finite numbers") from exc
        if not all(math.isfinite(value) for value in converted):
            raise ValueError("vertex coordinates must be finite numbers")
        points.append(converted)

    # Newell normal; drop the axis with the largest normal component.
    nx = ny = nz = 0.0
    for i, p in enumerate(points):
        q = points[(i + 1) % len(points)]
        nx += (p[1] - q[1]) * (p[2] + q[2])
        ny += (p[2] - q[2]) * (p[0] + q[0])
        nz += (p[0] - q[0]) * (p[1] + q[1])

    axis = max(range(3), key=lambda a: abs((nx, ny, nz)[a]))
    if abs((nx, ny, nz)[axis]) < 1e-12:
        raise ValueError("polygon is degenerate or has near-zero projected area")

    projected = [tuple(p[a] for a in range(3) if a != axis) for p in points]

    def cross(a, b, c):
        return ((b[0] - a[0]) * (c[1] - a[1])
                - (b[1] - a[1]) * (c[0] - a[0]))

    area2 = sum(
        projected[i][0] * projected[(i + 1) % len(projected)][1]
        - projected[(i + 1) % len(projected)][0] * projected[i][1]
        for i in range(len(projected))
    )
    if abs(area2) < 1e-12:
        raise ValueError("polygon has near-zero projected area")
    orientation = 1.0 if area2 > 0 else -1.0

    # Preserve legacy fan ordering for strictly convex polygons.
    turns = [
        orientation * cross(
            projected[(i - 1) % len(projected)],
            projected[i],
            projected[(i + 1) % len(projected)],
        )
        for i in range(len(projected))
    ]
    if all(turn > 1e-12 for turn in turns):
        return [
            (polygon[0], polygon[i], polygon[i + 1])
            for i in range(1, len(polygon) - 1)
        ]

    def inside_triangle(p, a, b, c):
        e = 1e-12
        return (
            orientation * cross(a, b, p) >= -e
            and orientation * cross(b, c, p) >= -e
            and orientation * cross(c, a, p) >= -e
        )

    remaining = list(range(len(polygon)))
    result = []
    max_iterations = len(remaining) * len(remaining)

    while len(remaining) > 3 and max_iterations:
        max_iterations -= 1
        ear_found = False

        for pos in range(len(remaining)):
            prev_i = remaining[(pos - 1) % len(remaining)]
            curr_i = remaining[pos]
            next_i = remaining[(pos + 1) % len(remaining)]
            a, b, c = projected[prev_i], projected[curr_i], projected[next_i]

            if orientation * cross(a, b, c) <= 1e-12:
                continue

            if any(
                inside_triangle(projected[other], a, b, c)
                for other in remaining
                if other not in (prev_i, curr_i, next_i)
            ):
                continue

            result.append((polygon[prev_i], polygon[curr_i], polygon[next_i]))
            del remaining[pos]
            ear_found = True
            break

        if not ear_found:
            raise ValueError("could not find a valid ear; polygon may be malformed")

    if len(remaining) != 3:
        raise ValueError("triangulation did not converge")

    a, b, c = (projected[i] for i in remaining)
    if orientation * cross(a, b, c) <= 1e-12:
        raise ValueError("final triangle is degenerate")

    result.append(tuple(polygon[i] for i in remaining))
    return result
