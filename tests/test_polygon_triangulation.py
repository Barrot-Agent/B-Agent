import unittest

from barrot_agent.rendering.polygon_triangulation import triangulate_polygon


def area2_xy(a, b, c):
    return ((b[0] - a[0]) * (c[1] - a[1])
            - (b[1] - a[1]) * (c[0] - a[0]))


class PolygonTriangulationTests(unittest.TestCase):
    def test_concave_polygon_area_is_preserved(self):
        # U-shaped polygon; a fan from the first vertex can cross the notch.
        vertices = [
            (0, 0, 0), (3, 0, 0), (3, 3, 0), (2, 3, 0),
            (2, 1, 0), (1, 1, 0), (1, 3, 0), (0, 3, 0),
        ]
        polygon = list(range(8))
        triangles = triangulate_polygon(vertices, polygon)
        self.assertEqual(len(triangles), len(polygon) - 2)

        triangle_area2 = sum(
            abs(area2_xy(vertices[a], vertices[b], vertices[c]))
            for a, b, c in triangles
        )
        polygon_area2 = abs(sum(
            vertices[i][0] * vertices[(i + 1) % len(polygon)][1]
            - vertices[(i + 1) % len(polygon)][0] * vertices[i][1]
            for i in range(len(polygon))
        ))
        self.assertAlmostEqual(triangle_area2, polygon_area2)
        self.assertAlmostEqual(polygon_area2 / 2, 7.0)

    def test_convex_quad_produces_two_triangles(self):
        vertices = [(0,0,0), (2,0,0), (2,2,0), (0,2,0)]
        self.assertEqual(len(triangulate_polygon(vertices, [0,1,2,3])), 2)

    def test_degenerate_polygon_is_rejected(self):
        vertices = [(0,0,0), (1,0,0), (2,0,0)]
        with self.assertRaises(ValueError):
            triangulate_polygon(vertices, [0,1,2])

    def test_repeated_vertex_is_rejected(self):
        vertices = [(0,0,0), (1,0,0), (0,1,0)]
        with self.assertRaises(ValueError):
            triangulate_polygon(vertices, [0,1,2,0])


if __name__ == "__main__":
    unittest.main()
