"""Structural signature for a geometry object.

A signature is an evidence-bearing descriptor relative to a declared invariant
set and transform class. Equal digests mean "same canonical form under these
declarations"; they do not prove mathematical equivalence.

Supported transform class: RELABEL (vertex and face ordering). Coordinate
transformations are deliberately rejected: this canonical form is not
rotation or translation invariant, and pretending otherwise would be false.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from typing import Any, Iterable

from barrot_agent.geometry.object import GeomObject

SUPPORTED_TRANSFORMS = ("RELABEL",)

#: Named invariant sets. A digest is only meaningful together with its set id.
INVARIANT_SETS: dict[str, tuple[str, ...]] = {
    "mesh.v1": (
        "vertex_count",
        "triangle_count",
        "open_boundaries",
        "non_manifold_edges",
        "degenerate_triangles",
        "is_watertight",
    ),
}


@dataclass(frozen=True)
class Signature:
    """Descriptor returned by :func:`structural_signature`."""

    digest: str
    invariant_set_id: str
    transform_class: str
    tolerance: float
    representation: str
    invariants: dict[str, Any]
    provenance: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "digest": self.digest,
            "invariant_set_id": self.invariant_set_id,
            "transform_class": self.transform_class,
            "tolerance": self.tolerance,
            "representation": self.representation,
            "invariants": dict(self.invariants),
            "provenance": self.provenance,
        }


def _check_tolerance(tolerance: float) -> float:
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)):
        raise ValueError("tolerance must be a positive finite number")
    value = float(tolerance)
    if not math.isfinite(value) or value <= 0:
        raise ValueError("tolerance must be a positive finite number")
    return value


def _quantize(value: float, tolerance: float) -> int:
    scaled = value / tolerance
    if not math.isfinite(scaled):
        raise ValueError("coordinate is outside the representable range")
    return int(round(scaled))


def _incidence(quantized: list[tuple[int, int, int]], faces: Iterable[Any]) -> list[list[int]]:
    incident: list[list[int]] = [[] for _ in quantized]
    for face in faces:
        for position, vertex in enumerate(face):
            for other in face[position + 1:]:
                incident[vertex].append(other)
                incident[other].append(vertex)
    return incident


#: Upper bound on permutations tried when several vertices share a coordinate.
#: Beyond this the function refuses instead of returning an unstable digest.
MAX_PERMUTATIONS = 1000


def _ordered_form(
    quantized: list[tuple[int, int, int]],
    faces: Iterable[Any],
    order: list[int],
) -> dict[str, Any]:
    new_index = {old: new for new, old in enumerate(order)}

    canonical_faces = []
    for face in faces:
        rotated = tuple(new_index[vertex] for vertex in face)
        start = rotated.index(min(rotated))
        canonical_faces.append(rotated[start:] + rotated[:start])
    canonical_faces.sort()

    return {
        "vertices": [quantized[old] for old in order],
        "faces": canonical_faces,
    }


def canonical_form(object_: GeomObject, tolerance: float) -> dict[str, Any]:
    """Return the canonical, order-independent form used for hashing.

    Vertices are ordered by quantized coordinate. Vertices that share a
    coordinate are ambiguous, so every permutation of each tied group is
    tried and the lexicographically smallest form is kept. That makes the
    result independent of input order even when coordinates collide. The
    search is bounded by :data:`MAX_PERMUTATIONS`; past the bound the
    function raises rather than returning a digest that changes with input
    order. Winding is significant.
    """
    if not isinstance(object_, GeomObject):
        raise TypeError("canonical_form expects a GeomObject")
    tolerance = _check_tolerance(tolerance)

    quantized = [
        tuple(_quantize(coordinate, tolerance) for coordinate in vertex)
        for vertex in object_.vertices
    ]

    groups: dict[tuple[int, int, int], list[int]] = {}
    for index, point in enumerate(quantized):
        groups.setdefault(point, []).append(index)

    tied: list[list[int]] = []
    for point in sorted(groups):
        members = groups[point]
        if len(members) > 1:
            tied.append(members)

    combinations = 1
    for members in tied:
        combinations *= math.factorial(len(members))
    if combinations > MAX_PERMUTATIONS:
        raise ValueError(
            "cannot canonicalize: "
            f"{combinations} permutations of coordinate-tied vertices "
            f"exceeds the bound of {MAX_PERMUTATIONS}"
        )

    best: dict[str, Any] | None = None
    for choice in itertools.product(*(itertools.permutations(m) for m in tied)):
        assigned = iter(choice)
        order: list[int] = []
        for point in sorted(groups):
            members = groups[point]
            order.extend(next(assigned) if len(members) > 1 else members)
        candidate = _ordered_form(quantized, object_.faces, order)
        if best is None or (candidate["vertices"], candidate["faces"]) < (
            best["vertices"],
            best["faces"],
        ):
            best = candidate

    return {
        "kind": object_.kind,
        "vertices": best["vertices"],
        "faces": best["faces"],
    }


def structural_signature(
    object_: GeomObject,
    *,
    tolerance: float = 1e-9,
    invariant_set_id: str = "mesh.v1",
    transform_class: str = "RELABEL",
) -> Signature:
    """Build the structural signature for ``object_``.

    The digest covers geometry only. Provenance is returned alongside it and
    never changes the digest.
    """
    if transform_class not in SUPPORTED_TRANSFORMS:
        raise ValueError(
            f"unsupported transform class {transform_class!r}; "
            f"supported: {', '.join(SUPPORTED_TRANSFORMS)}"
        )
    try:
        invariant_names: Iterable[str] = INVARIANT_SETS[invariant_set_id]
    except KeyError:
        raise ValueError(f"unknown invariant set: {invariant_set_id!r}") from None

    form = canonical_form(object_, tolerance)
    payload = json.dumps(form, sort_keys=True, separators=(",", ":"))
    digest = "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

    topology = object_.topology()
    invariants = {name: topology[name] for name in invariant_names}

    return Signature(
        digest=digest,
        invariant_set_id=invariant_set_id,
        transform_class=transform_class,
        tolerance=float(tolerance),
        representation=object_.kind,
        invariants=invariants,
        provenance=object_.provenance,
    )
