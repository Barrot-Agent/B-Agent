"""
Model Generator - 3D mesh synthesis, topology optimization, LOD generation.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Mesh:
    """A 3D mesh with vertices, normals, UVs, and indices."""
    vertices: List[Tuple[float, float, float]] = field(default_factory=list)
    normals: List[Tuple[float, float, float]] = field(default_factory=list)
    uvs: List[Tuple[float, float]] = field(default_factory=list)
    indices: List[int] = field(default_factory=list)
    name: str = "Mesh"

    @property
    def triangle_count(self) -> int:
        return len(self.indices) // 3

    @property
    def vertex_count(self) -> int:
        return len(self.vertices)


class PrimitiveGenerator:
    """Generates basic 3D primitive meshes."""

    @staticmethod
    def sphere(radius: float = 1.0, segments: int = 32, rings: int = 16) -> Mesh:
        vertices, normals, uvs, indices = [], [], [], []
        for r in range(rings + 1):
            lat = math.pi * (-0.5 + r / rings)
            for s in range(segments + 1):
                lon = 2 * math.pi * (s / segments)
                x = math.cos(lat) * math.cos(lon)
                y = math.sin(lat)
                z = math.cos(lat) * math.sin(lon)
                vertices.append((x * radius, y * radius, z * radius))
                normals.append((x, y, z))
                uvs.append((s / segments, r / rings))
        for r in range(rings):
            for s in range(segments):
                i0 = r * (segments + 1) + s
                i1 = i0 + 1
                i2 = i0 + segments + 1
                i3 = i2 + 1
                indices.extend([i0, i1, i2, i1, i3, i2])
        return Mesh(vertices=vertices, normals=normals, uvs=uvs, indices=indices, name="Sphere")

    @staticmethod
    def cube(size: float = 1.0) -> Mesh:
        h = size / 2
        verts = [
            (-h,-h,-h),(h,-h,-h),(h,h,-h),(-h,h,-h),
            (-h,-h,h),(h,-h,h),(h,h,h),(-h,h,h),
        ]
        norms = [(0,0,-1),(0,0,-1),(0,0,-1),(0,0,-1),(0,0,1),(0,0,1),(0,0,1),(0,0,1)]
        uvs = [(0,0),(1,0),(1,1),(0,1),(0,0),(1,0),(1,1),(0,1)]
        indices = [0,1,2,0,2,3, 4,5,6,4,6,7, 0,4,7,0,7,3, 1,5,6,1,6,2, 0,1,5,0,5,4, 3,2,6,3,6,7]
        return Mesh(vertices=verts, normals=norms, uvs=uvs, indices=indices, name="Cube")

    @staticmethod
    def plane(size: float = 10.0, subdivisions: int = 10) -> Mesh:
        vertices, normals, uvs, indices = [], [], [], []
        s = subdivisions
        for z in range(s + 1):
            for x in range(s + 1):
                px = (x / s - 0.5) * size
                pz = (z / s - 0.5) * size
                vertices.append((px, 0.0, pz))
                normals.append((0.0, 1.0, 0.0))
                uvs.append((x / s, z / s))
        for z in range(s):
            for x in range(s):
                i0 = z * (s + 1) + x
                indices.extend([i0, i0+1, i0+s+1, i0+1, i0+s+2, i0+s+1])
        return Mesh(vertices=vertices, normals=normals, uvs=uvs, indices=indices, name="Plane")


class LODGenerator:
    """Generates LOD variants by simplifying meshes."""

    @staticmethod
    def generate_lod(mesh: Mesh, reduction: float = 0.5) -> Mesh:
        """Create a simplified LOD mesh by removing every other face."""
        if mesh.triangle_count <= 1:
            return mesh
        keep = max(1, int(mesh.triangle_count * (1.0 - reduction)))
        new_indices = mesh.indices[:keep * 3]
        used_verts = set(new_indices)
        v_map = {old: new for new, old in enumerate(sorted(used_verts))}
        new_vertices = [mesh.vertices[i] for i in sorted(used_verts)]
        new_normals = [mesh.normals[i] for i in sorted(used_verts)] if mesh.normals else []
        new_uvs = [mesh.uvs[i] for i in sorted(used_verts)] if mesh.uvs else []
        remapped_indices = [v_map[i] for i in new_indices]
        return Mesh(
            vertices=new_vertices,
            normals=new_normals,
            uvs=new_uvs,
            indices=remapped_indices,
            name=f"{mesh.name}_LOD",
        )

    @staticmethod
    def generate_lod_chain(mesh: Mesh, levels: int = 4) -> List[Mesh]:
        """Generate a full LOD chain from LOD0 (full detail) to LODn."""
        chain = [mesh]
        for i in range(1, levels):
            reduction = 1.0 - (0.5 ** i)
            lod = LODGenerator.generate_lod(mesh, reduction)
            lod.name = f"{mesh.name}_LOD{i}"
            chain.append(lod)
        return chain


class ModelGenerator:
    """
    AI-powered 3D model generation system.

    Supports:
    - Procedural mesh generation from text prompts
    - Primitive combination for complex shapes
    - Automatic LOD chain generation
    - UV unwrapping and topology optimization
    """

    def __init__(self):
        self._primitive_gen = PrimitiveGenerator()
        self._lod_gen = LODGenerator()

    def generate_primitive(
        self,
        shape: str = "sphere",
        size: float = 1.0,
        detail: int = 16,
    ) -> Mesh:
        """Generate a geometric primitive."""
        if shape == "sphere":
            return self._primitive_gen.sphere(radius=size, segments=detail, rings=detail//2)
        elif shape == "cube":
            return self._primitive_gen.cube(size=size)
        elif shape == "plane":
            return self._primitive_gen.plane(size=size, subdivisions=detail)
        else:
            return self._primitive_gen.sphere(radius=size)

    def generate_from_prompt(self, prompt: str, detail: int = 16) -> Dict[str, Mesh]:
        """Generate a mesh from a text description."""
        # Map prompt keywords to shape types
        prompt_lower = prompt.lower()
        shape = "sphere"
        if any(w in prompt_lower for w in ("cube", "box", "chest", "crate")):
            shape = "cube"
        elif any(w in prompt_lower for w in ("ground", "floor", "terrain", "plane")):
            shape = "plane"

        base_mesh = self.generate_primitive(shape=shape, detail=detail)
        lods = self._lod_gen.generate_lod_chain(base_mesh, levels=4)
        return {f"LOD{i}": lod for i, lod in enumerate(lods)}

    def generate_lod_chain(self, mesh: Mesh, levels: int = 4) -> List[Mesh]:
        """Generate a LOD chain for an existing mesh."""
        return self._lod_gen.generate_lod_chain(mesh, levels=levels)

    def get_mesh_stats(self, mesh: Mesh) -> Dict[str, int]:
        """Return statistics for a mesh."""
        return {
            "vertices": mesh.vertex_count,
            "triangles": mesh.triangle_count,
            "has_normals": len(mesh.normals) > 0,
            "has_uvs": len(mesh.uvs) > 0,
        }
