"""
Material System - Layered materials, procedural shading, PBR workflow.

Implements:
- Physically Based Rendering (PBR) material model
- Layered material composition
- Procedural texture synthesis
- Dynamic material parameter updates
- Shader permutation management
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple


class ShadingModel(Enum):
    """PBR shading model selection."""
    DEFAULT_LIT = auto()
    SUBSURFACE = auto()
    SKIN = auto()
    CLEAR_COAT = auto()
    TWO_SIDED_FOLIAGE = auto()
    HAIR = auto()
    CLOTH = auto()
    EYE = auto()
    UNLIT = auto()


@dataclass
class TextureMap:
    """Represents a texture map with data and metadata."""
    width: int = 4
    height: int = 4
    channels: int = 4
    data: List[float] = field(default_factory=list)  # Flat RGBA data
    mip_levels: int = 1
    is_srgb: bool = True
    bindless_index: int = -1

    def __post_init__(self) -> None:
        if not self.data:
            self.data = [0.0] * (self.width * self.height * self.channels)

    def sample(self, u: float, v: float) -> Tuple[float, float, float, float]:
        """Sample the texture at UV coordinates."""
        u = u % 1.0
        v = v % 1.0
        x = int(u * (self.width - 1))
        y = int(v * (self.height - 1))
        idx = (y * self.width + x) * self.channels
        if idx + 3 < len(self.data):
            return (
                self.data[idx],
                self.data[idx + 1],
                self.data[idx + 2],
                self.data[idx + 3] if self.channels > 3 else 1.0,
            )
        return (0.0, 0.0, 0.0, 1.0)


@dataclass
class PBRParameters:
    """Physical properties of a PBR material."""
    base_color: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    metallic: float = 0.0
    roughness: float = 0.5
    ao: float = 1.0
    emissive: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    normal_strength: float = 1.0
    opacity: float = 1.0
    ior: float = 1.5                   # Index of refraction
    subsurface_color: Tuple[float, float, float] = (1.0, 0.2, 0.1)
    subsurface_radius: float = 0.0
    clear_coat_intensity: float = 0.0
    clear_coat_roughness: float = 0.05
    sheen_color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    sheen_roughness: float = 0.5


@dataclass
class MaterialLayer:
    """A single layer in a layered material."""
    name: str = "Layer"
    params: PBRParameters = field(default_factory=PBRParameters)
    blend_mask: Optional[TextureMap] = None
    blend_mode: str = "alpha"   # alpha, multiply, add, overlay
    weight: float = 1.0

    def get_blend_weight(self, u: float, v: float) -> float:
        """Get the blend weight at UV coordinates."""
        if self.blend_mask:
            sample = self.blend_mask.sample(u, v)
            return sample[0] * self.weight
        return self.weight


@dataclass
class MaterialInstance:
    """A fully resolved material with all layers and textures."""
    name: str = "Material"
    shading_model: ShadingModel = ShadingModel.DEFAULT_LIT
    layers: List[MaterialLayer] = field(default_factory=list)
    base_color_map: Optional[TextureMap] = None
    normal_map: Optional[TextureMap] = None
    metallic_roughness_map: Optional[TextureMap] = None
    emissive_map: Optional[TextureMap] = None
    ao_map: Optional[TextureMap] = None
    tiling: Tuple[float, float] = (1.0, 1.0)
    uv_offset: Tuple[float, float] = (0.0, 0.0)
    dynamic_params: Dict[str, Any] = field(default_factory=dict)

    def evaluate(self, u: float, v: float) -> PBRParameters:
        """Evaluate material at UV coordinates, blending all layers."""
        # Apply UV tiling and offset
        su = u * self.tiling[0] + self.uv_offset[0]
        sv = v * self.tiling[1] + self.uv_offset[1]

        # Start with base params
        result = PBRParameters()

        if self.base_color_map:
            sample = self.base_color_map.sample(su, sv)
            result.base_color = sample[:3]

        if self.metallic_roughness_map:
            sample = self.metallic_roughness_map.sample(su, sv)
            result.roughness = sample[1]
            result.metallic = sample[2]

        if self.ao_map:
            sample = self.ao_map.sample(su, sv)
            result.ao = sample[0]

        if self.emissive_map:
            sample = self.emissive_map.sample(su, sv)
            result.emissive = sample[:3]

        # Blend layers
        for layer in self.layers:
            w = layer.get_blend_weight(su, sv)
            if w <= 0.0:
                continue
            lp = layer.params
            if layer.blend_mode == "alpha":
                result.base_color = (
                    result.base_color[0] * (1 - w) + lp.base_color[0] * w,
                    result.base_color[1] * (1 - w) + lp.base_color[1] * w,
                    result.base_color[2] * (1 - w) + lp.base_color[2] * w,
                )
                result.roughness = result.roughness * (1 - w) + lp.roughness * w
                result.metallic = result.metallic * (1 - w) + lp.metallic * w

        return result


class ProceduralTextureGenerator:
    """Generates procedural textures using noise and mathematical patterns."""

    def generate_noise(
        self, width: int, height: int, scale: float = 1.0, octaves: int = 4
    ) -> TextureMap:
        """Generate a seamless Perlin-like noise texture."""
        data = []
        for y in range(height):
            for x in range(width):
                value = self._fbm(
                    x / width * scale,
                    y / height * scale,
                    octaves,
                )
                value = (value + 1.0) * 0.5  # Normalize to [0, 1]
                data.extend([value, value, value, 1.0])
        return TextureMap(width=width, height=height, channels=4, data=data, is_srgb=False)

    def generate_checkerboard(
        self,
        width: int,
        height: int,
        cells: int = 8,
        color_a: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        color_b: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> TextureMap:
        """Generate a checkerboard pattern."""
        data = []
        for y in range(height):
            for x in range(width):
                cx = int(x / width * cells)
                cy = int(y / height * cells)
                if (cx + cy) % 2 == 0:
                    data.extend([*color_a, 1.0])
                else:
                    data.extend([*color_b, 1.0])
        return TextureMap(width=width, height=height, channels=4, data=data)

    def generate_normal_map(
        self, height_map: TextureMap, strength: float = 1.0
    ) -> TextureMap:
        """Derive a normal map from a heightmap."""
        w, h = height_map.width, height_map.height
        data = []
        for y in range(h):
            for x in range(w):
                x1 = max(0, x - 1)
                x2 = min(w - 1, x + 1)
                y1 = max(0, y - 1)
                y2 = min(h - 1, y + 1)

                h_left = height_map.sample(x1 / w, y / h)[0]
                h_right = height_map.sample(x2 / w, y / h)[0]
                h_down = height_map.sample(x / w, y1 / h)[0]
                h_up = height_map.sample(x / w, y2 / h)[0]

                dx = (h_right - h_left) * strength
                dy = (h_up - h_down) * strength
                dz = 1.0

                length = math.sqrt(dx * dx + dy * dy + dz * dz)
                nx = dx / length * 0.5 + 0.5
                ny = dy / length * 0.5 + 0.5
                nz = dz / length * 0.5 + 0.5
                data.extend([nx, ny, nz, 1.0])
        return TextureMap(width=w, height=h, channels=4, data=data, is_srgb=False)

    @staticmethod
    def _fbm(x: float, y: float, octaves: int) -> float:
        """Fractional Brownian Motion noise."""
        value = 0.0
        amplitude = 0.5
        frequency = 1.0
        for _ in range(octaves):
            value += amplitude * ProceduralTextureGenerator._smooth_noise(
                x * frequency, y * frequency
            )
            amplitude *= 0.5
            frequency *= 2.0
        return value

    @staticmethod
    def _smooth_noise(x: float, y: float) -> float:
        """Simple smooth noise function."""
        ix = int(x)
        iy = int(y)
        fx = x - ix
        fy = y - iy

        # Smooth step
        ux = fx * fx * (3 - 2 * fx)
        uy = fy * fy * (3 - 2 * fy)

        def rand2(a: int, b: int) -> float:
            n = a * 127 + b * 311
            return math.sin(n * 7919.0) * 0.5

        a = rand2(ix, iy)
        b = rand2(ix + 1, iy)
        c = rand2(ix, iy + 1)
        d = rand2(ix + 1, iy + 1)

        return a + (b - a) * ux + (c - a) * uy + (a - b - c + d) * ux * uy


class BRDFEvaluator:
    """Evaluates physically based BRDFs for shading."""

    @staticmethod
    def ggx_ndf(n_dot_h: float, roughness: float) -> float:
        """GGX Normal Distribution Function."""
        alpha = roughness * roughness
        alpha_sq = alpha * alpha
        denom = (n_dot_h * n_dot_h * (alpha_sq - 1.0) + 1.0)
        return alpha_sq / max(math.pi * denom * denom, 1e-8)

    @staticmethod
    def schlick_fresnel(
        f0: Tuple[float, float, float], cos_theta: float
    ) -> Tuple[float, float, float]:
        """Schlick's approximation for Fresnel reflectance."""
        one_minus = max(0.0, 1.0 - cos_theta)
        p = one_minus ** 5
        return (
            f0[0] + (1 - f0[0]) * p,
            f0[1] + (1 - f0[1]) * p,
            f0[2] + (1 - f0[2]) * p,
        )

    @staticmethod
    def smith_geometry(n_dot_v: float, n_dot_l: float, roughness: float) -> float:
        """Smith shadowing-masking term."""
        k = (roughness + 1.0) ** 2 / 8.0
        g1v = n_dot_v / max(n_dot_v * (1 - k) + k, 1e-8)
        g1l = n_dot_l / max(n_dot_l * (1 - k) + k, 1e-8)
        return g1v * g1l

    def evaluate(
        self,
        params: PBRParameters,
        light_dir: Tuple[float, float, float],
        view_dir: Tuple[float, float, float],
        normal: Tuple[float, float, float],
        light_color: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    ) -> Tuple[float, float, float]:
        """Evaluate the Cook-Torrance BRDF."""
        n_dot_l = max(0.0, sum(a * b for a, b in zip(normal, light_dir)))
        n_dot_v = max(0.0, sum(a * b for a, b in zip(normal, view_dir)))
        if n_dot_l < 1e-4 or n_dot_v < 1e-4:
            return (0.0, 0.0, 0.0)

        half = tuple(
            (a + b) for a, b in zip(light_dir, view_dir)
        )
        h_len = max(math.sqrt(sum(h * h for h in half)), 1e-8)
        half_norm = tuple(h / h_len for h in half)

        n_dot_h = max(0.0, sum(a * b for a, b in zip(normal, half_norm)))
        h_dot_v = max(0.0, sum(a * b for a, b in zip(half_norm, view_dir)))

        f0_dielectric = 0.04
        f0 = (
            f0_dielectric * (1 - params.metallic) + params.base_color[0] * params.metallic,
            f0_dielectric * (1 - params.metallic) + params.base_color[1] * params.metallic,
            f0_dielectric * (1 - params.metallic) + params.base_color[2] * params.metallic,
        )

        D = self.ggx_ndf(n_dot_h, params.roughness)
        F = self.schlick_fresnel(f0, h_dot_v)
        G = self.smith_geometry(n_dot_v, n_dot_l, params.roughness)

        denom = max(4.0 * n_dot_v * n_dot_l, 1e-8)
        specular = (D * G / denom,) * 3
        specular = tuple(specular[i] * F[i] for i in range(3))

        kd = tuple((1 - F[i]) * (1 - params.metallic) for i in range(3))
        diffuse = tuple(
            kd[i] * params.base_color[i] / math.pi for i in range(3)
        )

        result = tuple(
            (diffuse[i] + specular[i]) * n_dot_l * light_color[i]
            for i in range(3)
        )
        return tuple(max(0.0, min(10.0, v)) for v in result)


class MaterialSystem:
    """
    Unified material system for PBR rendering.

    Manages material instances, procedural textures, and BRDF evaluation.
    Supports layered materials for complex surface appearances.
    """

    def __init__(self):
        self._materials: Dict[str, MaterialInstance] = {}
        self._procedural_gen = ProceduralTextureGenerator()
        self._brdf = BRDFEvaluator()

    def create_material(
        self,
        name: str,
        base_color: Tuple[float, float, float] = (0.8, 0.8, 0.8),
        roughness: float = 0.5,
        metallic: float = 0.0,
        shading_model: ShadingModel = ShadingModel.DEFAULT_LIT,
    ) -> MaterialInstance:
        """Create and register a new PBR material."""
        layer = MaterialLayer(
            name="Base",
            params=PBRParameters(
                base_color=base_color,
                roughness=roughness,
                metallic=metallic,
            ),
        )
        mat = MaterialInstance(
            name=name,
            shading_model=shading_model,
            layers=[layer],
        )
        self._materials[name] = mat
        return mat

    def add_layer(
        self, material_name: str, layer: MaterialLayer
    ) -> Optional[MaterialInstance]:
        """Add a layer to an existing material."""
        mat = self._materials.get(material_name)
        if mat:
            mat.layers.append(layer)
        return mat

    def generate_procedural_material(
        self,
        name: str,
        style: str = "noise",
        width: int = 256,
        height: int = 256,
    ) -> MaterialInstance:
        """Generate a material with procedural textures."""
        if style == "checkerboard":
            base_tex = self._procedural_gen.generate_checkerboard(width, height)
        else:
            base_tex = self._procedural_gen.generate_noise(width, height)

        height_tex = self._procedural_gen.generate_noise(
            width, height, scale=2.0, octaves=3
        )
        normal_tex = self._procedural_gen.generate_normal_map(height_tex)

        mat = MaterialInstance(
            name=name,
            base_color_map=base_tex,
            normal_map=normal_tex,
        )
        self._materials[name] = mat
        return mat

    def evaluate_brdf(
        self,
        material_name: str,
        u: float,
        v: float,
        light_dir: Tuple[float, float, float],
        view_dir: Tuple[float, float, float],
        normal: Tuple[float, float, float],
        light_color: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    ) -> Tuple[float, float, float]:
        """Evaluate shading for a material at a surface point."""
        mat = self._materials.get(material_name)
        if not mat:
            params = PBRParameters()
        else:
            params = mat.evaluate(u, v)
        return self._brdf.evaluate(params, light_dir, view_dir, normal, light_color)

    def update_dynamic_param(
        self, material_name: str, param_name: str, value: Any
    ) -> bool:
        """Update a dynamic material parameter at runtime."""
        mat = self._materials.get(material_name)
        if mat:
            mat.dynamic_params[param_name] = value
            return True
        return False

    def get_material(self, name: str) -> Optional[MaterialInstance]:
        """Get a material instance by name."""
        return self._materials.get(name)

    def list_materials(self) -> List[str]:
        """Return list of all registered material names."""
        return list(self._materials.keys())
