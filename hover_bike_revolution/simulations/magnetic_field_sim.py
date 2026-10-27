"""
magnetic_field_sim.py — Magnetic field simulation for Halbach array levitation.

Simulates the magnetic field distribution above a Halbach array and produces
a 2-D field map (x, z) for visualisation and analysis.
"""

from __future__ import annotations

import math
from typing import Any

MU_0 = 4 * math.pi * 1e-7  # vacuum permeability (H/m)


def halbach_field_z(
    x: float,
    z: float,
    b_remanence: float,
    wavelength_m: float,
    magnet_height_m: float,
    n_periods: int = 4,
) -> tuple[float, float]:
    """
    Compute the (Bx, Bz) magnetic field at point (x, z) above a Halbach array.

    Uses the Fourier series approximation for an infinite, ideal Halbach array.
    The array lies in the x-y plane with the enhanced field on the +z side.

    Parameters
    ----------
    x:
        Horizontal position along the array (m).
    z:
        Height above the array surface (m, must be > 0).
    b_remanence:
        Remanent flux density of the magnet material (T).
    wavelength_m:
        Spatial wavelength of the array (m).
    magnet_height_m:
        Magnet block height (m).
    n_periods:
        Number of spatial periods to include in sum (more = more accurate).

    Returns
    -------
    (Bx, Bz) in Tesla.
    """
    if z <= 0:
        z = 1e-6  # avoid singularity at the surface

    k = 2 * math.pi / wavelength_m
    Bx = 0.0
    Bz = 0.0

    # Sum over odd harmonics only (ideal Halbach — even harmonics cancel)
    for n in range(1, n_periods * 2, 2):
        kn = n * k
        factor = (
            b_remanence
            * math.sin(math.pi / 4)  # 4-pole orientation factor
            * (1 - math.exp(-kn * magnet_height_m))
            * math.exp(-kn * z)
        )
        Bx += factor * math.sin(kn * x) / n
        Bz += factor * math.cos(kn * x) / n

    return Bx, Bz


def field_magnitude(bx: float, bz: float) -> float:
    return math.sqrt(bx**2 + bz**2)


def generate_field_map(
    x_range_m: tuple[float, float] = (0.0, 0.6),
    z_range_m: tuple[float, float] = (0.01, 0.35),
    nx: int = 30,
    nz: int = 20,
    b_remanence: float = 1.45,
    wavelength_m: float = 0.2,
    magnet_height_m: float = 0.01,
) -> dict[str, Any]:
    """
    Generate a 2-D magnetic field map above a Halbach array.

    Returns a dictionary suitable for JSON serialisation containing
    the grid coordinates and field magnitudes.
    """
    xs = [x_range_m[0] + (x_range_m[1] - x_range_m[0]) * i / (nx - 1) for i in range(nx)]
    zs = [z_range_m[0] + (z_range_m[1] - z_range_m[0]) * j / (nz - 1) for j in range(nz)]

    rows: list[dict[str, Any]] = []
    for z in zs:
        for x in xs:
            bx, bz = halbach_field_z(x, z, b_remanence, wavelength_m, magnet_height_m)
            b = field_magnitude(bx, bz)
            rows.append(
                {
                    "x_m": round(x, 4),
                    "z_m": round(z, 4),
                    "Bx_T": round(bx, 6),
                    "Bz_T": round(bz, 6),
                    "B_T": round(b, 6),
                }
            )

    return {
        "grid_points": len(rows),
        "nx": nx,
        "nz": nz,
        "x_range_m": list(x_range_m),
        "z_range_m": list(z_range_m),
        "parameters": {
            "b_remanence_t": b_remanence,
            "wavelength_m": wavelength_m,
            "magnet_height_m": magnet_height_m,
        },
        "data": rows,
        "peak_field_t": max(r["B_T"] for r in rows),
        "field_at_150mm_t": next((r["B_T"] for r in rows if abs(r["z_m"] - 0.15) < 0.01), None),
    }


if __name__ == "__main__":
    import json

    result = generate_field_map()
    print(f"Grid: {result['grid_points']} points")
    print(f"Peak field: {result['peak_field_t']:.4f} T")
    print(f"Field at 150 mm: {result['field_at_150mm_t']:.6f} T")
