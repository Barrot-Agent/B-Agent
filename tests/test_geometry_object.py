"""Tests for the typed geometry object facade."""
import pytest

from barrot_agent.geometry.object import GeomObject
from barrot_agent.rendering.mesh_topology import analyze_mesh_topology


def tetrahedron():
    vertices = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
    faces = [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    return vertices, faces


def test_from_mesh_keeps_representation_and_counts():
    vertices, faces = tetrahedron()
    object_ = GeomObject.from_mesh(vertices, faces, provenance="fixture:tetrahedron")
    assert object_.kind == "triangle_mesh"
    assert len(object_.vertices) == 4
    assert len(object_.faces) == 4
    assert object_.provenance == "fixture:tetrahedron"


def test_topology_delegates_to_existing_analyzer():
    vertices, faces = tetrahedron()
    object_ = GeomObject.from_mesh(vertices, faces)
    assert object_.topology() == analyze_mesh_topology(vertices, faces)
    assert object_.topology()["is_watertight"] is True


def test_invalid_inputs_are_rejected_before_normalization():
    cases = [
        ([(0, 0)], [(0, 0, 0)]),
        ([(0, 0, 0)], [(0, 1, 2)]),
        ([(float("nan"), 0, 0)], []),
        ([(0, 0, 0)], [(0, 0)]),
        ([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [(0, 1, True)]),
    ]
    for vertices, faces in cases:
        with pytest.raises(ValueError):
            GeomObject.from_mesh(vertices, faces)


def test_provenance_does_not_affect_equality():
    vertices, faces = tetrahedron()
    first = GeomObject.from_mesh(vertices, faces, provenance="a")
    second = GeomObject.from_mesh(vertices, faces, provenance="b")
    assert first == second
    assert first.provenance != second.provenance
