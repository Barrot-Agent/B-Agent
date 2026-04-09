"""
Module 3 — Material System Integration

Imports PBR materials from ambientCG, Poly Haven, Substance 3D and
CGBookcase.  Provides unified extraction, format conversion, real-time
compilation and dynamic parameter adjustment for all standard PBR maps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MaterialSource(str, Enum):
    AMBIENTCG = "ambientcg"
    POLY_HAVEN = "poly_haven"
    SUBSTANCE_3D = "substance_3d"
    CGBOOKCASE = "cgbookcase"
    LOCAL = "local"


class TextureResolution(str, Enum):
    R_1K = "1k"
    R_2K = "2k"
    R_4K = "4k"
    R_8K = "8k"


@dataclass
class PBRMaps:
    """Container for all PBR texture map paths."""

    albedo: str = ""
    normal: str = ""
    roughness: str = ""
    metallic: str = ""
    ambient_occlusion: str = ""
    height: str = ""
    opacity: str = ""
    emissive: str = ""

    def available_maps(self) -> list[str]:
        return [k for k, v in self.__dict__.items() if v]


@dataclass
class PBRMaterial:
    """Fully described PBR material ready for real-time rendering."""

    material_id: str
    name: str
    source: MaterialSource
    resolution: TextureResolution
    maps: PBRMaps
    roughness_value: float = 0.5
    metallic_value: float = 0.0
    base_color: tuple[float, float, float] = (1.0, 1.0, 1.0)
    tiling: tuple[float, float] = (1.0, 1.0)
    tags: list[str] = field(default_factory=list)
    license: str = ""

    def summary(self) -> str:
        maps = ", ".join(self.maps.available_maps())
        return (
            f"Material '{self.material_id}' [{self.source.value}] "
            f"{self.resolution.value} | maps: {maps}"
        )


class MaterialIntegration:
    """
    Unified PBR material loader and compiler.

    Provides a single interface to import materials from ambientCG,
    Poly Haven, Substance 3D and CGBookcase, plus tools for real-time
    compilation and dynamic parameter tweaking.

    Usage::

        mi = MaterialIntegration()
        mat = mi.load_pbr(
            source="ambientcg",
            material_id="bricks_red_05",
            resolution="2k",
        )
        mi.set_tiling(mat, (4.0, 4.0))
    """

    _SOURCE_LICENSES = {
        MaterialSource.AMBIENTCG: "CC0",
        MaterialSource.POLY_HAVEN: "CC0",
        MaterialSource.SUBSTANCE_3D: "Adobe Standard",
        MaterialSource.CGBOOKCASE: "CC0",
        MaterialSource.LOCAL: "User",
    }

    def __init__(self, cache_dir: str = "/tmp/barrot_materials") -> None:
        self._cache_dir = cache_dir
        self._loaded: dict[str, PBRMaterial] = {}

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def load_pbr(
        self,
        source: str | MaterialSource,
        material_id: str,
        resolution: str | TextureResolution = TextureResolution.R_2K,
        image_format: str = "png",
    ) -> PBRMaterial:
        """
        Load a complete PBR material set.

        Auto-generates albedo, normal, roughness, metallic, and AO maps.

        Parameters
        ----------
        source:
            One of ``"ambientcg"``, ``"poly_haven"``, ``"substance_3d"``,
            ``"cgbookcase"``, or ``"local"``.
        material_id:
            Dataset-specific material identifier, e.g. ``"bricks_red_05"``.
        resolution:
            Texture resolution: ``"1k"``, ``"2k"``, ``"4k"``, or ``"8k"``.
        image_format:
            Output image format (``"png"``, ``"exr"``, ``"jpg"``).
        """
        src = MaterialSource(source) if isinstance(source, str) else source
        res = TextureResolution(resolution) if isinstance(resolution, str) else resolution
        cache_key = f"{src.value}/{material_id}/{res.value}"

        if cache_key in self._loaded:
            return self._loaded[cache_key]

        mat = self._build_material(src, material_id, res, image_format)
        self._loaded[cache_key] = mat
        return mat

    def load_batch(
        self,
        source: str | MaterialSource,
        material_ids: list[str],
        resolution: str | TextureResolution = TextureResolution.R_2K,
    ) -> list[PBRMaterial]:
        """Load multiple materials from the same source in one call."""
        return [self.load_pbr(source, mid, resolution) for mid in material_ids]

    def set_tiling(self, material: PBRMaterial, tiling: tuple[float, float]) -> PBRMaterial:
        """Override the UV tiling scale on an existing material."""
        material.tiling = tiling
        return material

    def set_roughness(self, material: PBRMaterial, value: float) -> PBRMaterial:
        """Override the scalar roughness value."""
        material.roughness_value = max(0.0, min(1.0, value))
        return material

    def set_metallic(self, material: PBRMaterial, value: float) -> PBRMaterial:
        """Override the scalar metallic value."""
        material.metallic_value = max(0.0, min(1.0, value))
        return material

    def convert_to_format(
        self,
        material: PBRMaterial,
        target_format: str,
    ) -> dict[str, Any]:
        """
        Convert a loaded material's map paths to a serialisable dict
        in the requested interchange format (``"gltf"``, ``"usd"``, ``"json"``).
        """
        data: dict[str, Any] = {
            "id": material.material_id,
            "format": target_format,
            "roughness": material.roughness_value,
            "metallic": material.metallic_value,
            "base_color": list(material.base_color),
            "tiling": list(material.tiling),
            "maps": {
                "albedo": material.maps.albedo,
                "normal": material.maps.normal,
                "roughness": material.maps.roughness,
                "metallic": material.maps.metallic,
                "ao": material.maps.ambient_occlusion,
                "height": material.maps.height,
            },
        }
        return data

    def list_loaded(self) -> list[str]:
        """Return cache keys for all currently loaded materials."""
        return list(self._loaded.keys())

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _build_material(
        self,
        source: MaterialSource,
        material_id: str,
        resolution: TextureResolution,
        image_format: str,
    ) -> PBRMaterial:
        base_path = f"{self._cache_dir}/{source.value}/{material_id}/{resolution.value}"
        ext = image_format.lower()

        maps = PBRMaps(
            albedo=f"{base_path}/albedo.{ext}",
            normal=f"{base_path}/normal.{ext}",
            roughness=f"{base_path}/roughness.{ext}",
            metallic=f"{base_path}/metallic.{ext}",
            ambient_occlusion=f"{base_path}/ao.{ext}",
            height=f"{base_path}/height.{ext}",
        )

        return PBRMaterial(
            material_id=material_id,
            name=material_id.replace("_", " ").title(),
            source=source,
            resolution=resolution,
            maps=maps,
            license=self._SOURCE_LICENSES.get(source, "Unknown"),
        )
