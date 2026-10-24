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
        self.assertEqual(report.geometry.topology_status, "ASSESSED")


if __name__ == "__main__":
    unittest.main()
