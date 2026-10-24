"""Dependency-free regression tests for triangle mesh topology."""
import unittest

from barrot_agent.rendering.mesh_topology import analyze_mesh_topology


def tetrahedron():
    vertices = [
        (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)
    ]
    faces = [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    return vertices, faces


class MeshTopologyTests(unittest.TestCase):
    def test_closed_tetrahedron_is_watertight(self):
        result = analyze_mesh_topology(*tetrahedron())
        self.assertIs(result["is_watertight"], True)
        self.assertEqual(result["open_boundaries"], 0)
        self.assertEqual(result["non_manifold_edges"], 0)
        self.assertEqual(result["degenerate_triangles"], 0)
        self.assertEqual(result["topology_status"], "ASSESSED")

    def test_open_triangle_has_three_boundary_edges(self):
        result = analyze_mesh_topology(
            [(0, 0, 0), (1, 0, 0), (0, 1, 0)], [(0, 1, 2)]
        )
        self.assertIs(result["is_watertight"], False)
        self.assertEqual(result["open_boundaries"], 3)

    def test_degenerate_face_is_detected(self):
        result = analyze_mesh_topology(
            [(0, 0, 0), (1, 0, 0), (2, 0, 0)], [(0, 1, 2)]
        )
        self.assertEqual(result["degenerate_triangles"], 1)
        self.assertIs(result["is_watertight"], False)

    def test_non_manifold_edge_is_detected(self):
        vertices = [
            (0, 0, 0), (1, 0, 0), (0, 1, 0),
            (0, -1, 0), (0, 0, 1),
        ]
        faces = [(0, 1, 2), (1, 0, 3), (0, 1, 4)]
        result = analyze_mesh_topology(vertices, faces)
        self.assertEqual(result["non_manifold_edges"], 1)
        self.assertIs(result["is_watertight"], False)

    def test_invalid_mesh_inputs_are_rejected(self):
        cases = [
            ([(0, 0)], [(0, 0, 0)]),
            ([(0, 0, 0)], [(0, 1, 2)]),
            ([(float("nan"), 0, 0)], []),
            ([(0, 0, 0)], [(0, 0)]),
        ]
        for vertices, faces in cases:
            with self.subTest(vertices=vertices, faces=faces):
                with self.assertRaises(ValueError):
                    analyze_mesh_topology(vertices, faces)


if __name__ == "__main__":
    unittest.main()
