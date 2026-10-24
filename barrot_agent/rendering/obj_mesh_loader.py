"""Dependency-free parser for polygon geometry in local Wavefront OBJ files."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any


def load_obj_mesh(source: str | Path) -> dict[str, Any]:
    """Parse OBJ vertex positions and triangulated faces.

    Supports v records, polygon f records, slash-separated face tokens,
    and positive or negative OBJ vertex indices. Texture coordinates,
    normals, materials, groups, and other records are intentionally ignored.
    """
    path = Path(source)
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []

    with path.open("r", encoding="utf-8-sig", errors="strict") as stream:
        for line_number, raw in enumerate(stream, 1):
            line = raw.partition("#")[0].strip()
            if not line:
                continue

            fields = line.split()
            record = fields[0]

            if record == "v":
                if len(fields) < 4:
                    raise ValueError(
                        f"{path}:{line_number}: vertex requires three coordinates"
                    )
                try:
                    point = tuple(float(value) for value in fields[1:4])
                except ValueError as exc:
                    raise ValueError(
                        f"{path}:{line_number}: invalid vertex coordinate"
                    ) from exc
                if not all(math.isfinite(value) for value in point):
                    raise ValueError(
                        f"{path}:{line_number}: non-finite vertex coordinate"
                    )
                vertices.append(point)

            elif record == "f":
                if len(fields) < 4:
                    raise ValueError(
                        f"{path}:{line_number}: face requires at least three vertices"
                    )

                polygon: list[int] = []
                for token in fields[1:]:
                    vertex_token = token.split("/", 1)[0]
                    try:
                        obj_index = int(vertex_token)
                    except ValueError as exc:
                        raise ValueError(
                            f"{path}:{line_number}: invalid face index {token!r}"
                        ) from exc

                    if obj_index == 0:
                        raise ValueError(
                            f"{path}:{line_number}: OBJ vertex indices cannot be zero"
                        )

                    index = obj_index - 1 if obj_index > 0 else len(vertices) + obj_index
                    if index < 0 or index >= len(vertices):
                        raise ValueError(
                            f"{path}:{line_number}: face index {obj_index} "
                            "references a vertex not yet defined"
                        )
                    polygon.append(index)

                if len(set(polygon)) < 3:
                    raise ValueError(
                        f"{path}:{line_number}: face has fewer than three unique vertices"
                    )

                from .polygon_triangulation import triangulate_polygon
                try:
                    faces.extend(triangulate_polygon(vertices, polygon))
                except ValueError as exc:
                    raise ValueError(
                        f"{path}:{line_number}: invalid or unsupported polygon: {exc}"
                    ) from exc

    if not vertices:
        raise ValueError(f"{path}: no vertex records found")
    if not faces:
        raise ValueError(f"{path}: no polygon face records found")

    return {
        "vertices": vertices,
        "faces": faces,
        "source_format": "obj",
        "geometry_status": "PARSED",
        "triangulation": "EAR_CLIPPING_WITH_CONVEX_FAN_COMPATIBILITY",
    }
