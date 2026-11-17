"""Tests for the structural signature."""
import pytest

from barrot_agent.geometry.object import GeomObject
from barrot_agent.geometry.signature import (
    INVARIANT_SETS,
    canonical_form,
    structural_signature,
)


def tetrahedron():
    vertices = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
    faces = [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    return vertices, faces


def relabel(vertices, faces, order):
    """Return a mesh with new vertex i equal to old vertex order[i]."""
    mapping = {old: new for new, old in enumerate(order)}
    new_vertices = [vertices[old] for old in order]
    new_faces = [tuple(mapping[index] for index in face) for face in faces]
    return new_vertices, new_faces


def signature(vertices=None, faces=None, **kwargs):
    if vertices is None:
        vertices, faces = tetrahedron()
    return structural_signature(GeomObject.from_mesh(vertices, faces), **kwargs)


def test_digest_is_declared_and_stable():
    first = signature()
    second = signature()
    assert first.digest == second.digest
    assert first.digest.startswith("sha256:")
    assert first.transform_class == "RELABEL"
    assert first.tolerance == 1e-9


def test_vertex_permutation_does_not_change_digest():
    vertices, faces = tetrahedron()
    order = [2, 0, 3, 1]
    permuted_vertices, permuted_faces = relabel(vertices, faces, order)
    assert signature(permuted_vertices, permuted_faces).digest == signature().digest


def test_face_rotation_does_not_change_digest():
    vertices, faces = tetrahedron()
    rotated = [(face[1], face[2], face[0]) for face in faces]
    assert signature(vertices, rotated).digest == signature().digest


def test_face_order_does_not_change_digest():
    vertices, faces = tetrahedron()
    assert signature(vertices, list(reversed(faces))).digest == signature().digest


def test_moved_vertex_changes_digest():
    vertices, faces = tetrahedron()
    moved = list(vertices)
    moved[0] = (0.001, 0.0, 0.0)
    assert signature(moved, faces).digest != signature().digest


def test_reversed_winding_changes_digest():
    vertices, faces = tetrahedron()
    reversed_faces = [(face[0], face[2], face[1]) for face in faces]
    assert signature(vertices, reversed_faces).digest != signature().digest


def test_provenance_is_not_part_of_the_digest():
    vertices, faces = tetrahedron()
    first = structural_signature(
        GeomObject.from_mesh(vertices, faces, provenance="source:a")
    )
    second = structural_signature(
        GeomObject.from_mesh(vertices, faces, provenance="source:b")
    )
    assert first.digest == second.digest
    assert first.provenance == "source:a"
    assert second.provenance == "source:b"


def test_duplicate_coordinates_are_not_merged():
    vertices, faces = tetrahedron()
    with_duplicate = vertices + [(5.0, 5.0, 5.0)]
    assert signature(with_duplicate, faces).digest != signature().digest


def test_tolerance_must_be_positive_and_finite():
    for bad in (0, -1e-9, float("nan"), float("inf"), True, "1e-9"):
        with pytest.raises(ValueError):
            signature(tolerance=bad)


def test_unknown_invariant_set_is_rejected():
    with pytest.raises(ValueError):
        signature(invariant_set_id="mesh.unknown")


def test_unsupported_transform_class_is_rejected():
    with pytest.raises(ValueError):
        signature(transform_class="ROTATION")


def test_invariants_match_the_declared_set():
    descriptor = signature()
    topology = GeomObject.from_mesh(*tetrahedron()).topology()
    expected = {name: topology[name] for name in INVARIANT_SETS["mesh.v1"]}
    assert descriptor.invariants == expected
    assert descriptor.invariants["is_watertight"] is True


def test_canonical_form_is_order_independent():
    vertices, faces = tetrahedron()
    order = [1, 3, 0, 2]
    permuted_vertices, permuted_faces = relabel(vertices, faces, order)
    left = GeomObject.from_mesh(vertices, faces)
    right = GeomObject.from_mesh(permuted_vertices, permuted_faces)
    assert canonical_form(left, 1e-9) == canonical_form(right, 1e-9)


def test_canonical_form_requires_a_geom_object():
    with pytest.raises(TypeError):
        canonical_form({"vertices": []}, 1e-9)


def shared_coordinate_mesh():
    """Two vertices at the same coordinate, both used by faces."""
    vertices = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1.0, 0.0, 0.0)]
    faces = [(0, 1, 2), (0, 3, 2), (1, 2, 3)]
    return vertices, faces


def test_shared_coordinate_survives_every_relabeling():
    vertices, faces = shared_coordinate_mesh()
    expected = signature(vertices, faces).digest
    for order in ([3, 1, 0, 2], [1, 0, 3, 2], [0, 2, 3, 1], [2, 3, 1, 0]):
        permuted_vertices, permuted_faces = relabel(vertices, faces, order)
        assert signature(permuted_vertices, permuted_faces).digest == expected


def test_shared_coordinate_differs_from_single_vertex_use():
    vertices, faces = shared_coordinate_mesh()
    single = (vertices[:3], [(0, 1, 2)])
    assert signature(vertices, faces).digest != signature(*single).digest


def test_permutation_bound_refuses_instead_of_guessing():
    vertices = [(0.0, 0.0, 0.0)] * 8 + [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
    with pytest.raises(ValueError, match="exceeds the bound"):
        structural_signature(
            GeomObject(kind="triangle_mesh", vertices=tuple(vertices), faces=((0, 1, 2),))
        )
