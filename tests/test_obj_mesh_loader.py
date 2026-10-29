import tempfile
import unittest
from pathlib import Path

from barrot_agent.rendering.obj_mesh_loader import load_obj_mesh
from barrot_agent.rendering.asset_loader import AssetLoader, AssetFormat
from barrot_agent.rendering.quality_metrics import QualityMetrics


class ObjMeshLoaderTests(unittest.TestCase):
    def write_obj(self, content):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "mesh.obj"
        path.write_text(content, encoding="utf-8")
        return path

    def test_triangle_with_slash_indices(self):
        path = self.write_obj(
            "v 0 0 0\nv 1 0 0\nv 0 1 0\n"
            "vt 0 0\nvt 1 0\nvt 0 1\n"
            "f 1/1 2/2 3/3\n"
        )
        mesh = load_obj_mesh(path)
        self.assertEqual(len(mesh["vertices"]), 3)
        self.assertEqual(mesh["faces"], [(0, 1, 2)])

    def test_quad_is_triangulated(self):
        path = self.write_obj(
            "v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\n"
            "f 1 2 3 4\n"
        )
        mesh = load_obj_mesh(path)
        self.assertEqual(mesh["faces"], [(0, 1, 2), (0, 2, 3)])
        self.assertEqual(
            mesh["triangulation"],
            "EAR_CLIPPING_WITH_CONVEX_FAN_COMPATIBILITY",
        )

    def test_concave_polygon_is_triangulated(self):
        path = self.write_obj(
            "v 0 0 0\nv 3 0 0\nv 3 3 0\nv 2 3 0\n"
            "v 2 1 0\nv 1 1 0\nv 1 3 0\nv 0 3 0\n"
            "f 1 2 3 4 5 6 7 8\n"
        )
        mesh = load_obj_mesh(path)
        self.assertEqual(len(mesh["faces"]), 6)
        self.assertEqual(
            mesh["triangulation"],
            "EAR_CLIPPING_WITH_CONVEX_FAN_COMPATIBILITY",
        )

    def test_negative_indices(self):
        path = self.write_obj(
            "v 0 0 0\nv 1 0 0\nv 0 1 0\nf -3 -2 -1\n"
        )
        self.assertEqual(load_obj_mesh(path)["faces"], [(0, 1, 2)])

    def test_invalid_zero_index_is_rejected(self):
        path = self.write_obj(
            "v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 0\n"
        )
        with self.assertRaises(ValueError):
            load_obj_mesh(path)

    def test_quality_metrics_report_open_boundaries(self):
        path = self.write_obj(
            "v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n"
        )
        mesh = load_obj_mesh(path)
        report = QualityMetrics().validate(
            asset_name=path.name,
            triangle_count=len(mesh["faces"]),
            texture_count=0,
            mesh_vertices=mesh["vertices"],
            mesh_faces=mesh["faces"],
        )
        self.assertFalse(report.geometry.is_watertight)
        self.assertEqual(report.geometry.open_boundaries, 3)
        boundary_issues = [
            issue for issue in report.geometry.issues if issue.code == "GEO_003"
        ]
        self.assertEqual(len(boundary_issues), 1)
        self.assertIn("3 open boundary edges", boundary_issues[0].message)

    def test_lod_zero_does_not_collide_with_default_lod_cache(self):
        path = self.write_obj(
            "v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n"
        )
        loader = AssetLoader(default_lod=1)
        lod_zero = loader.load(str(path), format=AssetFormat.OBJ, target_lod=0)
        lod_one = loader.load(str(path), format=AssetFormat.OBJ, target_lod=1)
        self.assertEqual(lod_zero.metadata.lod_level, 0)
        self.assertEqual(lod_one.metadata.lod_level, 1)
        self.assertIsNot(lod_zero, lod_one)

    def test_missing_or_empty_mesh_data_is_not_assessed(self):
        cases = [
            (None, None),
            ([], []),
            ([(0.0, 0.0, 0.0)], []),
            ([], [(0, 1, 2)]),
        ]
        for vertices, faces in cases:
            with self.subTest(vertices=vertices, faces=faces):
                report = QualityMetrics().validate(
                    asset_name="missing-mesh",
                    triangle_count=0,
                    texture_count=0,
                    mesh_vertices=vertices,
                    mesh_faces=faces,
                )
                self.assertIsNone(report.geometry.is_watertight)
                self.assertEqual(report.geometry.topology_status, "NOT_ASSESSED")

    def test_loader_uses_real_obj_counts_and_topology(self):
        path = self.write_obj(
            "v 0 0 0\nv 1 0 0\nv 0 1 0\nv 0 0 1\n"
            "f 1 3 2\nf 1 2 4\nf 2 3 4\nf 3 1 4\n"
        )
        asset = AssetLoader().load(
            str(path), format=AssetFormat.OBJ, target_lod=1
        )
        self.assertEqual(asset.metadata.vertex_count, 4)
        self.assertEqual(asset.metadata.triangle_count, 4)
        self.assertEqual(asset.mesh_data["geometry_status"], "ASSESSED")
        self.assertTrue(asset.mesh_data["topology_analysis"]["is_watertight"])

        report = QualityMetrics().validate(
            asset_name=path.name,
            triangle_count=asset.metadata.triangle_count,
            texture_count=0,
            mesh_vertices=asset.mesh_data["vertices"],
            mesh_faces=asset.mesh_data["faces"],
        )
        self.assertTrue(report.geometry.is_watertight)
        self.assertEqual(report.geometry.degenerate_triangles, 0)
        self.assertEqual(report.geometry.open_boundaries, 0)
        self.assertEqual(report.geometry.non_manifold_edges, 0)
        self.assertEqual(report.geometry.topology_status, "ASSESSED")


if __name__ == "__main__":
    unittest.main()
