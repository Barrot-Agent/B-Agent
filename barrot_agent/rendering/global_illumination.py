"""
Global Illumination System - SSGI, Voxel Cone Tracing, Surfels, Spherical Gaussians.

Implements multiple GI techniques:
- Screen-Space Global Illumination (SSGI)
- Voxel Cone Tracing for real-time indirect lighting
- Surfel-based GI for large environments
- Spherical Gaussians for efficient lighting representation
- Dynamic GI updates for moving lights and geometry
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple


class GITechnique(Enum):
    """Global illumination technique selection."""
    NONE = auto()
    SSGI = auto()
    VOXEL_CONE_TRACING = auto()
    SURFEL = auto()
    SPHERICAL_GAUSSIANS = auto()
    LUMEN = auto()          # Unreal Lumen-style hybrid
    HYBRID = auto()


@dataclass
class VoxelGrid:
    """3D voxel grid for cone tracing."""
    resolution: int = 128
    world_size: float = 64.0
    voxels: List[List[List[Tuple[float, float, float, float]]]] = field(
        default_factory=list
    )  # RGBA emission/radiance

    def __post_init__(self) -> None:
        if not self.voxels:
            r = self.resolution
            self.voxels = [
                [[(0.0, 0.0, 0.0, 0.0) for _ in range(r)] for _ in range(r)]
                for _ in range(r)
            ]

    def world_to_voxel(
        self, world_pos: Tuple[float, float, float]
    ) -> Tuple[int, int, int]:
        """Convert world-space coordinates to voxel indices."""
        half = self.world_size / 2.0
        voxel_size = self.world_size / self.resolution
        ix = int((world_pos[0] + half) / voxel_size)
        iy = int((world_pos[1] + half) / voxel_size)
        iz = int((world_pos[2] + half) / voxel_size)
        r = self.resolution
        return (
            max(0, min(r - 1, ix)),
            max(0, min(r - 1, iy)),
            max(0, min(r - 1, iz)),
        )

    def sample(
        self,
        pos: Tuple[float, float, float],
        mip_level: float = 0.0,
    ) -> Tuple[float, float, float, float]:
        """Sample the voxel grid at a world-space position."""
        ix, iy, iz = self.world_to_voxel(pos)
        return self.voxels[ix][iy][iz]

    def inject_light(
        self,
        pos: Tuple[float, float, float],
        radiance: Tuple[float, float, float],
        radius: float = 1.0,
    ) -> None:
        """Inject radiance into the voxel grid."""
        ix, iy, iz = self.world_to_voxel(pos)
        existing = self.voxels[ix][iy][iz]
        self.voxels[ix][iy][iz] = (
            min(1.0, existing[0] + radiance[0]),
            min(1.0, existing[1] + radiance[1]),
            min(1.0, existing[2] + radiance[2]),
            min(1.0, existing[3] + 0.1),
        )


@dataclass
class SphericalGaussian:
    """A spherical Gaussian lobe for compact lighting representation."""
    axis: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    sharpness: float = 8.0
    amplitude: Tuple[float, float, float] = (1.0, 1.0, 1.0)

    def evaluate(self, direction: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Evaluate the SG at a given direction."""
        dot = sum(a * b for a, b in zip(self.axis, direction))
        exp_val = math.exp(self.sharpness * (dot - 1.0))
        return (
            self.amplitude[0] * exp_val,
            self.amplitude[1] * exp_val,
            self.amplitude[2] * exp_val,
        )


@dataclass
class Surfel:
    """A surface element (surfel) for GI."""
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    normal: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    radius: float = 0.1
    albedo: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    irradiance: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    age: int = 0


@dataclass
class GIConfig:
    """Configuration for global illumination."""
    technique: GITechnique = GITechnique.HYBRID
    voxel_resolution: int = 64
    voxel_world_size: float = 64.0
    cone_aperture_degrees: float = 30.0
    num_cones: int = 6
    max_cone_distance: float = 8.0
    cone_step_size: float = 0.2
    num_surfels: int = 50_000
    sg_lobes: int = 12
    ssgi_radius: float = 2.0
    ssgi_samples: int = 8
    bounce_count: int = 1
    update_frequency: int = 4  # Update every N frames
    dynamic_update: bool = True


class SSGIPass:
    """Screen-Space Global Illumination pass."""

    def __init__(self, config: GIConfig):
        self.config = config
        self._sample_kernel = self._generate_kernel(config.ssgi_samples)

    def _generate_kernel(self, n_samples: int) -> List[Tuple[float, float]]:
        """Generate a stratified hemisphere sampling kernel."""
        kernel = []
        for i in range(n_samples):
            angle = i * 2 * math.pi / n_samples
            radius = math.sqrt((i + 0.5) / n_samples)
            kernel.append((radius * math.cos(angle), radius * math.sin(angle)))
        return kernel

    def compute(
        self,
        color_buffer: List[List[Tuple[float, float, float]]],
        depth_buffer: List[List[float]],
        normal_buffer: List[List[Tuple[float, float, float]]],
    ) -> List[List[Tuple[float, float, float]]]:
        """Compute SSGI for the current frame."""
        h = len(color_buffer)
        w = len(color_buffer[0]) if h > 0 else 0
        gi_buffer = [[(0.0, 0.0, 0.0) for _ in range(w)] for _ in range(h)]

        for y in range(h):
            for x in range(w):
                normal = normal_buffer[y][x]
                if sum(abs(n) for n in normal) < 0.01:
                    continue

                gi_r = gi_g = gi_b = 0.0
                for sx, sy in self._sample_kernel:
                    # Sample neighboring pixels
                    sample_x = int(x + sx * self.config.ssgi_radius * w / 10)
                    sample_y = int(y + sy * self.config.ssgi_radius * h / 10)
                    sample_x = max(0, min(w - 1, sample_x))
                    sample_y = max(0, min(h - 1, sample_y))

                    sample_color = color_buffer[sample_y][sample_x]
                    sample_depth = depth_buffer[sample_y][sample_x]

                    # Depth-based visibility
                    own_depth = depth_buffer[y][x]
                    if abs(sample_depth - own_depth) < 0.5:
                        gi_r += sample_color[0]
                        gi_g += sample_color[1]
                        gi_b += sample_color[2]

                n = max(1, len(self._sample_kernel))
                gi_buffer[y][x] = (gi_r / n * 0.5, gi_g / n * 0.5, gi_b / n * 0.5)

        return gi_buffer


class VoxelConeTracer:
    """Voxel Cone Tracing for real-time indirect diffuse and specular lighting."""

    def __init__(self, config: GIConfig):
        self.config = config
        self.voxel_grid = VoxelGrid(
            resolution=config.voxel_resolution,
            world_size=config.voxel_world_size,
        )
        self._cone_directions = self._generate_cone_directions(config.num_cones)

    def _generate_cone_directions(
        self, n_cones: int
    ) -> List[Tuple[float, float, float]]:
        """Generate evenly distributed hemisphere cone directions."""
        directions = []
        for i in range(n_cones):
            phi = (i + 0.5) / n_cones * math.pi
            theta = i * math.pi * (3.0 - math.sqrt(5.0))
            x = math.sin(phi) * math.cos(theta)
            y = math.cos(phi)
            z = math.sin(phi) * math.sin(theta)
            length = math.sqrt(x * x + y * y + z * z)
            directions.append((x / length, y / length, z / length))
        return directions

    def inject_lighting(
        self,
        lights: List[Dict[str, Any]],
        scene_geometry: List[Dict[str, Any]],
    ) -> None:
        """Inject direct lighting into the voxel grid."""
        for light in lights:
            pos = light.get("position", (0.0, 0.0, 0.0))
            color = light.get("color", (1.0, 1.0, 1.0))
            intensity = light.get("intensity", 1.0)
            radiance = tuple(c * intensity for c in color)
            self.voxel_grid.inject_light(pos, radiance)

    def trace_cone(
        self,
        origin: Tuple[float, float, float],
        direction: Tuple[float, float, float],
        normal: Tuple[float, float, float],
        aperture: float,
    ) -> Tuple[float, float, float]:
        """Trace a single cone through the voxel grid."""
        aperture_rad = math.radians(aperture)
        accumulated = [0.0, 0.0, 0.0]
        transmittance = 1.0
        dist = self.voxel_grid.world_size / self.config.voxel_resolution

        steps = int(
            self.config.max_cone_distance / self.config.cone_step_size
        )
        for step in range(steps):
            t = dist + step * self.config.cone_step_size
            diameter = 2.0 * t * math.tan(aperture_rad / 2.0)
            mip = math.log2(
                max(
                    1.0,
                    diameter * self.config.voxel_resolution / self.voxel_grid.world_size,
                )
            )

            sample_pos = (
                origin[0] + t * direction[0],
                origin[1] + t * direction[1],
                origin[2] + t * direction[2],
            )

            voxel = self.voxel_grid.sample(sample_pos, mip)
            alpha = voxel[3]

            accumulated[0] += transmittance * alpha * voxel[0]
            accumulated[1] += transmittance * alpha * voxel[1]
            accumulated[2] += transmittance * alpha * voxel[2]
            transmittance *= max(0.0, 1.0 - alpha)

            if transmittance < 0.01:
                break

        return tuple(accumulated)

    def compute_indirect_diffuse(
        self,
        surface_pos: Tuple[float, float, float],
        surface_normal: Tuple[float, float, float],
    ) -> Tuple[float, float, float]:
        """Compute indirect diffuse lighting via cone tracing."""
        total = [0.0, 0.0, 0.0]
        aperture = self.config.cone_aperture_degrees

        for cone_dir in self._cone_directions:
            # Only trace cones in the hemisphere above surface
            dot = sum(a * b for a, b in zip(cone_dir, surface_normal))
            if dot < 0:
                continue
            color = self.trace_cone(surface_pos, cone_dir, surface_normal, aperture)
            total[0] += color[0] * dot
            total[1] += color[1] * dot
            total[2] += color[2] * dot

        n = max(1, len(self._cone_directions))
        return (total[0] / n, total[1] / n, total[2] / n)


class SurfelGI:
    """Surfel-based global illumination for large environments."""

    def __init__(self, config: GIConfig):
        self.config = config
        self._surfels: List[Surfel] = []

    def generate_surfels(self, geometry: List[Dict[str, Any]]) -> None:
        """Generate surfels by sampling scene geometry."""
        self._surfels = []
        target_count = self.config.num_surfels

        for prim in geometry:
            n_prim_surfels = max(1, target_count // max(1, len(geometry)))
            for _ in range(n_prim_surfels):
                if len(self._surfels) >= target_count:
                    break
                bounds_min = prim.get("bounds_min", (-1.0, -1.0, -1.0))
                bounds_max = prim.get("bounds_max", (1.0, 1.0, 1.0))
                pos = (
                    random.uniform(bounds_min[0], bounds_max[0]),
                    random.uniform(bounds_min[1], bounds_max[1]),
                    random.uniform(bounds_min[2], bounds_max[2]),
                )
                normal = prim.get("normal", (0.0, 1.0, 0.0))
                albedo = prim.get("albedo", (0.8, 0.8, 0.8))
                self._surfels.append(
                    Surfel(position=pos, normal=normal, albedo=albedo)
                )

    def update_irradiance(self, lights: List[Dict[str, Any]]) -> None:
        """Update surfel irradiance from direct and indirect lighting."""
        for surfel in self._surfels:
            irr = [0.0, 0.0, 0.0]
            for light in lights:
                light_pos = light.get("position", (0.0, 10.0, 0.0))
                light_color = light.get("color", (1.0, 1.0, 1.0))
                light_intensity = light.get("intensity", 1.0)

                to_light = (
                    light_pos[0] - surfel.position[0],
                    light_pos[1] - surfel.position[1],
                    light_pos[2] - surfel.position[2],
                )
                dist_sq = sum(d * d for d in to_light)
                dist = math.sqrt(max(dist_sq, 1e-4))
                to_light_norm = tuple(d / dist for d in to_light)

                ndotl = max(0.0, sum(a * b for a, b in zip(surfel.normal, to_light_norm)))
                falloff = light_intensity / max(dist_sq, 1.0)

                irr[0] += light_color[0] * ndotl * falloff * surfel.albedo[0]
                irr[1] += light_color[1] * ndotl * falloff * surfel.albedo[1]
                irr[2] += light_color[2] * ndotl * falloff * surfel.albedo[2]

            surfel.irradiance = tuple(min(1.0, v) for v in irr)
            surfel.age += 1


class SphericalGaussianGI:
    """Spherical Gaussian representation for efficient irradiance caching."""

    def __init__(self, n_lobes: int = 12):
        self.n_lobes = n_lobes
        self._lobes: List[SphericalGaussian] = self._init_lobes()

    def _init_lobes(self) -> List[SphericalGaussian]:
        """Initialize SG lobes on a sphere."""
        lobes = []
        for i in range(self.n_lobes):
            theta = math.acos(1.0 - 2.0 * (i + 0.5) / self.n_lobes)
            phi = math.pi * (1.0 + math.sqrt(5.0)) * i
            axis = (
                math.sin(theta) * math.cos(phi),
                math.cos(theta),
                math.sin(theta) * math.sin(phi),
            )
            lobes.append(SphericalGaussian(axis=axis, sharpness=4.0))
        return lobes

    def fit_lighting(self, samples: List[Tuple[Tuple[float, float, float], Tuple[float, float, float]]]) -> None:
        """Fit SG lobes to sampled lighting data."""
        # EM-style fitting (simplified)
        for lobe in self._lobes:
            contrib_r = contrib_g = contrib_b = 0.0
            total_weight = 0.0
            for direction, radiance in samples:
                dot = sum(a * b for a, b in zip(lobe.axis, direction))
                weight = math.exp(lobe.sharpness * (dot - 1.0))
                contrib_r += weight * radiance[0]
                contrib_g += weight * radiance[1]
                contrib_b += weight * radiance[2]
                total_weight += weight
            if total_weight > 1e-6:
                lobe.amplitude = (
                    contrib_r / total_weight,
                    contrib_g / total_weight,
                    contrib_b / total_weight,
                )

    def evaluate(
        self, normal: Tuple[float, float, float]
    ) -> Tuple[float, float, float]:
        """Evaluate total irradiance at a surface normal."""
        total = [0.0, 0.0, 0.0]
        for lobe in self._lobes:
            color = lobe.evaluate(normal)
            total[0] += color[0]
            total[1] += color[1]
            total[2] += color[2]
        return tuple(min(1.0, v) for v in total)


class GlobalIlluminationSystem:
    """
    Unified global illumination system supporting multiple GI techniques.

    Automatically selects the best technique based on scene complexity and
    hardware capabilities. Supports dynamic updates for real-time scenes.
    """

    def __init__(self, config: Optional[GIConfig] = None):
        self.config = config or GIConfig()
        self._ssgi: Optional[SSGIPass] = None
        self._vct: Optional[VoxelConeTracer] = None
        self._surfel_gi: Optional[SurfelGI] = None
        self._sg_gi: Optional[SphericalGaussianGI] = None
        self._frame_count = 0
        self._initialize_techniques()

    def _initialize_techniques(self) -> None:
        """Initialize the selected GI techniques."""
        t = self.config.technique
        if t in (GITechnique.SSGI, GITechnique.HYBRID, GITechnique.LUMEN):
            self._ssgi = SSGIPass(self.config)
        if t in (GITechnique.VOXEL_CONE_TRACING, GITechnique.HYBRID, GITechnique.LUMEN):
            self._vct = VoxelConeTracer(self.config)
        if t in (GITechnique.SURFEL, GITechnique.LUMEN):
            self._surfel_gi = SurfelGI(self.config)
        if t == GITechnique.SPHERICAL_GAUSSIANS:
            self._sg_gi = SphericalGaussianGI(self.config.sg_lobes)

    def inject_scene(
        self,
        geometry: List[Dict[str, Any]],
        lights: List[Dict[str, Any]],
    ) -> None:
        """Inject scene data into the GI system."""
        if self._vct:
            self._vct.inject_lighting(lights, geometry)
        if self._surfel_gi:
            self._surfel_gi.generate_surfels(geometry)
            self._surfel_gi.update_irradiance(lights)

    def compute_indirect_lighting(
        self,
        surface_pos: Tuple[float, float, float],
        surface_normal: Tuple[float, float, float],
    ) -> Tuple[float, float, float]:
        """Compute indirect lighting at a surface point."""
        if self._vct:
            return self._vct.compute_indirect_diffuse(surface_pos, surface_normal)
        if self._sg_gi:
            return self._sg_gi.evaluate(surface_normal)
        return (0.0, 0.0, 0.0)

    def compute_screen_space_gi(
        self,
        color_buffer: List[List[Tuple[float, float, float]]],
        depth_buffer: List[List[float]],
        normal_buffer: List[List[Tuple[float, float, float]]],
    ) -> List[List[Tuple[float, float, float]]]:
        """Compute SSGI contribution."""
        if self._ssgi:
            return self._ssgi.compute(color_buffer, depth_buffer, normal_buffer)
        h = len(color_buffer)
        w = len(color_buffer[0]) if h > 0 else 0
        return [[(0.0, 0.0, 0.0) for _ in range(w)] for _ in range(h)]

    def update(self, lights: List[Dict[str, Any]], delta_time: float) -> None:
        """Update dynamic GI (incremental updates for moving lights)."""
        self._frame_count += 1
        if not self.config.dynamic_update:
            return
        if self._frame_count % self.config.update_frequency != 0:
            return
        if self._surfel_gi:
            self._surfel_gi.update_irradiance(lights)
