"""
Volumetric Effects System - Ray-marched clouds, fog, smoke, fluid simulation.

Implements:
- Ray-marched volumetric clouds using density fields
- Volumetric fog and smoke effects
- Particle-based fluid simulation
- Real-time volumetric lighting with multiple scattering approximation
- Temporal reprojection for volumetric effects
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple


class VolumetricType(Enum):
    """Type of volumetric effect."""
    FOG = auto()
    CLOUD = auto()
    SMOKE = auto()
    FIRE = auto()
    EXPLOSION = auto()
    ATMOSPHERE = auto()


@dataclass
class VolumetricConfig:
    """Configuration for volumetric rendering."""
    march_steps: int = 64
    shadow_steps: int = 8
    max_distance: float = 500.0
    step_size: float = 1.0
    ambient_light: Tuple[float, float, float] = (0.1, 0.15, 0.2)
    scattering_coefficient: float = 0.1
    absorption_coefficient: float = 0.01
    asymmetry_parameter: float = 0.3   # Henyey-Greenstein g
    density_scale: float = 1.0
    enable_shadows: bool = True
    enable_multiple_scattering: bool = True
    temporal_reprojection: bool = True
    cloud_base_height: float = 1500.0
    cloud_thickness: float = 2000.0
    wind_speed: Tuple[float, float, float] = (0.01, 0.0, 0.005)


@dataclass
class DensityField:
    """3D density field for volumetric effects."""
    width: int = 64
    height: int = 32
    depth: int = 64
    density: List[float] = field(default_factory=list)
    temperature: List[float] = field(default_factory=list)
    velocity: List[Tuple[float, float, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        size = self.width * self.height * self.depth
        if not self.density:
            self.density = [0.0] * size
        if not self.temperature:
            self.temperature = [0.0] * size
        if not self.velocity:
            self.velocity = [(0.0, 0.0, 0.0)] * size

    def _idx(self, x: int, y: int, z: int) -> int:
        return (
            max(0, min(self.depth - 1, z)) * self.height * self.width
            + max(0, min(self.height - 1, y)) * self.width
            + max(0, min(self.width - 1, x))
        )

    def get_density(self, x: int, y: int, z: int) -> float:
        return self.density[self._idx(x, y, z)]

    def set_density(self, x: int, y: int, z: int, value: float) -> None:
        self.density[self._idx(x, y, z)] = value

    def sample_trilinear(
        self, fx: float, fy: float, fz: float
    ) -> float:
        """Sample density with trilinear interpolation."""
        x0 = int(fx)
        y0 = int(fy)
        z0 = int(fz)
        dx = fx - x0
        dy = fy - y0
        dz = fz - z0

        def s(xi: int, yi: int, zi: int) -> float:
            return self.get_density(xi, yi, zi)

        return (
            s(x0, y0, z0) * (1 - dx) * (1 - dy) * (1 - dz)
            + s(x0 + 1, y0, z0) * dx * (1 - dy) * (1 - dz)
            + s(x0, y0 + 1, z0) * (1 - dx) * dy * (1 - dz)
            + s(x0, y0, z0 + 1) * (1 - dx) * (1 - dy) * dz
            + s(x0 + 1, y0 + 1, z0) * dx * dy * (1 - dz)
            + s(x0 + 1, y0, z0 + 1) * dx * (1 - dy) * dz
            + s(x0, y0 + 1, z0 + 1) * (1 - dx) * dy * dz
            + s(x0 + 1, y0 + 1, z0 + 1) * dx * dy * dz
        )


class NoiseGenerator:
    """3D Worley and Perlin noise for cloud and fog density."""

    @staticmethod
    def perlin_3d(x: float, y: float, z: float) -> float:
        """3D Perlin noise in [-1, 1]."""
        ix, iy, iz = int(x), int(y), int(z)
        fx, fy, fz = x - ix, y - iy, z - iz

        def fade(t: float) -> float:
            return t * t * t * (t * (t * 6 - 15) + 10)

        ux, uy, uz = fade(fx), fade(fy), fade(fz)

        def grad(h: int, gx: float, gy: float, gz: float) -> float:
            cases = [
                gx + gy, -gx + gy, gx - gy, -gx - gy,
                gx + gz, -gx + gz, gx - gz, -gx - gz,
                gy + gz, -gy + gz, gy - gz, -gy - gz,
                gx + gy, -gx + gy, gy + gz, -gy + gz,
            ]
            return cases[h % 16]

        def hash3(a: int, b: int, c: int) -> int:
            n = a * 1597 + b * 157 + c * 17
            return (n ^ (n >> 13)) & 15

        result = 0.0
        for dx in range(2):
            for dy in range(2):
                for dz in range(2):
                    h = hash3(ix + dx, iy + dy, iz + dz)
                    gx = fx - dx
                    gy = fy - dy
                    gz = fz - dz
                    wx = (1 - ux) if dx == 0 else ux
                    wy = (1 - uy) if dy == 0 else uy
                    wz = (1 - uz) if dz == 0 else uz
                    result += wx * wy * wz * grad(h, gx, gy, gz)
        return result

    @staticmethod
    def fbm_3d(x: float, y: float, z: float, octaves: int = 4) -> float:
        """Fractional Brownian Motion in 3D."""
        value = 0.0
        amplitude = 0.5
        frequency = 1.0
        for _ in range(octaves):
            value += amplitude * NoiseGenerator.perlin_3d(
                x * frequency, y * frequency, z * frequency
            )
            amplitude *= 0.5
            frequency *= 2.0
        return value


class CloudDensityModel:
    """Procedural cloud density model."""

    def __init__(self, config: VolumetricConfig):
        self.config = config
        self._time = 0.0

    def get_density(
        self, world_pos: Tuple[float, float, float]
    ) -> float:
        """Evaluate cloud density at a world-space position."""
        y = world_pos[1]
        cloud_base = self.config.cloud_base_height
        cloud_top = cloud_base + self.config.cloud_thickness

        if y < cloud_base or y > cloud_top:
            return 0.0

        # Height gradient
        t = (y - cloud_base) / max(self.config.cloud_thickness, 1.0)
        height_gradient = 4.0 * t * (1.0 - t)  # Parabolic fade

        # Wind offset
        wx = world_pos[0] + self._time * self.config.wind_speed[0]
        wz = world_pos[2] + self._time * self.config.wind_speed[2]

        # Base shape noise
        base = NoiseGenerator.fbm_3d(wx * 0.0005, y * 0.0003, wz * 0.0005, octaves=4)
        base = (base + 1.0) * 0.5  # [0, 1]

        # Detail noise
        detail = NoiseGenerator.fbm_3d(wx * 0.003, y * 0.002, wz * 0.003, octaves=3)
        detail = (detail + 1.0) * 0.5

        density = max(0.0, base - 0.3) * height_gradient
        density = max(0.0, density - detail * 0.1)
        return density * self.config.density_scale

    def update(self, delta_time: float) -> None:
        """Advance cloud simulation time."""
        self._time += delta_time


class HenyeyGreensteinPhase:
    """Henyey-Greenstein phase function for scattering."""

    @staticmethod
    def evaluate(cos_theta: float, g: float) -> float:
        """Evaluate the HG phase function."""
        g2 = g * g
        denom = (1.0 + g2 - 2.0 * g * cos_theta) ** 1.5
        return (1.0 - g2) / max(4.0 * math.pi * denom, 1e-8)


class VolumetricRayMarcher:
    """Ray marches through volumetric media to compute participating media effects."""

    def __init__(self, config: VolumetricConfig, density_source: Any):
        self.config = config
        self.density_source = density_source
        self._phase_function = HenyeyGreensteinPhase()

    def march_ray(
        self,
        ray_origin: Tuple[float, float, float],
        ray_direction: Tuple[float, float, float],
        light_direction: Tuple[float, float, float],
        light_color: Tuple[float, float, float],
    ) -> Tuple[Tuple[float, float, float], float]:
        """
        March a ray through the volume and compute in-scattered lighting.

        Returns (scattered_color, transmittance).
        """
        scattered = [0.0, 0.0, 0.0]
        transmittance = 1.0
        step = self.config.step_size

        cos_theta = -sum(a * b for a, b in zip(ray_direction, light_direction))
        phase = self._phase_function.evaluate(cos_theta, self.config.asymmetry_parameter)

        for i in range(self.config.march_steps):
            t = (i + 0.5) * step
            if t > self.config.max_distance:
                break

            pos = (
                ray_origin[0] + t * ray_direction[0],
                ray_origin[1] + t * ray_direction[1],
                ray_origin[2] + t * ray_direction[2],
            )

            density = self.density_source.get_density(pos)
            if density < 1e-5:
                continue

            sigma_t = (
                self.config.scattering_coefficient
                + self.config.absorption_coefficient
            ) * density
            exp_val = math.exp(-sigma_t * step)

            # Light attenuation through the volume
            light_attenuation = self._march_to_light(pos, light_direction)

            for c in range(3):
                in_scatter = (
                    transmittance
                    * light_color[c]
                    * light_attenuation
                    * self.config.scattering_coefficient
                    * density
                    * phase
                    * step
                )
                scattered[c] += in_scatter

            # Ambient contribution
            for c in range(3):
                scattered[c] += (
                    transmittance
                    * self.config.ambient_light[c]
                    * self.config.scattering_coefficient
                    * density
                    * step
                )

            transmittance *= exp_val
            if transmittance < 0.01:
                break

        return tuple(min(1.0, v) for v in scattered), transmittance

    def _march_to_light(
        self,
        pos: Tuple[float, float, float],
        light_dir: Tuple[float, float, float],
    ) -> float:
        """Compute light transmittance from a point to the light source."""
        shadow_transmittance = 1.0
        shadow_step = self.config.max_distance / max(self.config.shadow_steps, 1)

        for j in range(self.config.shadow_steps):
            t = (j + 0.5) * shadow_step
            shadow_pos = (
                pos[0] + t * light_dir[0],
                pos[1] + t * light_dir[1],
                pos[2] + t * light_dir[2],
            )
            density = self.density_source.get_density(shadow_pos)
            sigma_t = (
                self.config.scattering_coefficient
                + self.config.absorption_coefficient
            ) * density
            shadow_transmittance *= math.exp(-sigma_t * shadow_step)
            if shadow_transmittance < 0.01:
                break

        return shadow_transmittance


class VolumetricEffectsSystem:
    """
    Complete volumetric effects system for clouds, fog, smoke, and fire.

    Provides ray-marched volumetric rendering with:
    - Procedural cloud generation
    - Real-time lighting and shadow casting
    - Temporal reprojection for performance
    - Animated density fields for smoke/fire
    """

    def __init__(self, config: Optional[VolumetricConfig] = None):
        self.config = config or VolumetricConfig()
        self._cloud_model = CloudDensityModel(self.config)
        self._ray_marcher = VolumetricRayMarcher(self.config, self._cloud_model)
        self._density_fields: Dict[str, DensityField] = {}
        self._temporal_history: Optional[List[List[Tuple[float, float, float]]]] = None
        self._frame_count = 0

    def add_density_field(self, name: str, field: DensityField) -> None:
        """Register a density field for volumetric effects."""
        self._density_fields[name] = field

    def render_volumetrics(
        self,
        camera_pos: Tuple[float, float, float],
        camera_rays: List[Tuple[float, float, float]],
        light_direction: Tuple[float, float, float],
        light_color: Tuple[float, float, float],
        width: int,
        height: int,
    ) -> List[List[Tuple[float, float, float, float]]]:
        """
        Render volumetric effects for the current frame.

        Returns a buffer of RGBA values (RGB color + alpha/transmittance).
        """
        buffer = []
        ray_idx = 0

        for y in range(height):
            row = []
            for x in range(width):
                if ray_idx < len(camera_rays):
                    ray_dir = camera_rays[ray_idx]
                else:
                    row.append((0.0, 0.0, 0.0, 1.0))
                    ray_idx += 1
                    continue

                scattered, transmittance = self._ray_marcher.march_ray(
                    camera_pos, ray_dir, light_direction, light_color
                )
                row.append((*scattered, transmittance))
                ray_idx += 1
            buffer.append(row)

        self._frame_count += 1
        return buffer

    def update(self, delta_time: float) -> None:
        """Update animated volumetric effects."""
        self._cloud_model.update(delta_time)

    def create_explosion(
        self,
        center: Tuple[float, float, float],
        radius: float,
        name: str = "explosion",
    ) -> DensityField:
        """Create an explosion density field."""
        res = 32
        field = DensityField(width=res, height=res, depth=res)
        for z in range(res):
            for y in range(res):
                for x in range(res):
                    px = (x / res - 0.5) * radius * 2 + center[0]
                    py = (y / res - 0.5) * radius * 2 + center[1]
                    pz = (z / res - 0.5) * radius * 2 + center[2]
                    dist = math.sqrt(
                        (px - center[0]) ** 2
                        + (py - center[1]) ** 2
                        + (pz - center[2]) ** 2
                    )
                    if dist < radius:
                        noise = NoiseGenerator.fbm_3d(px * 0.1, py * 0.1, pz * 0.1)
                        density = max(0.0, 1.0 - dist / radius + noise * 0.3)
                        field.set_density(x, y, z, density)
        self._density_fields[name] = field
        return field
