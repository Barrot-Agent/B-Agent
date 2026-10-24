import pytest

from barrot_agent.rendering.mesh_topology import analyze_mesh_topology


def tetrahedron():
    vertices = [
        (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)
    ]
    faces = [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    return vertices, faces


def test_closed_tetrahedron_is_watertight():
    result = analyze_mesh_topology(*tetrahedron())
    assert result["is_watertight"] is True
    assert result["open_boundaries"] == 0
    assert result["non_manifold_edges"] == 0
    assert result["degenerate_triangles"] == 0
    assert result["topology_status"] == "ASSESSED"


def test_open_triangle_has_three_boundary_edges():
    result = analyze_mesh_topology([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [(0, 1, 2)])
    assert result["is_watertight"] is False
    assert result["open_boundaries"] == 3


def test_degenerate_face_is_detected():
    result = analyze_mesh_topology(
        [(0, 0, 0), (1, 0, 0), (2, 0, 0)], [(0, 1, 2)]
    )
    assert result["degenerate_triangles"] == 1
    assert result["is_watertight"] is False


def test_non_manifold_edge_is_detected():
    vertices = [
        (0, 0, 0), (1, 0, 0), (0, 1, 0),
        (0, -1, 0), (0, 0, 1),
    ]
    faces = [(0, 1, 2), (1, 0, 3), (0, 1, 4)]
    result = analyze_mesh_topology(vertices, faces)
    assert result["non_manifold_edges"] == 1
    assert result["is_watertight"] is False


@pytest.mark.parametrize("vertices,faces", [
    ([(0, 0)], [(0, 0, 0)]),
    ([(0, 0, 0)], [(0, 1, 2)]),
    ([(float("nan"), 0, 0)], []),
    ([(0, 0, 0)], [(0, 0)]),
])
def test_invalid_mesh_input_is_rejected(vertices, faces):
    with pytest.raises(ValueError):
        analyze_mesh_topology(vertices, faces)
