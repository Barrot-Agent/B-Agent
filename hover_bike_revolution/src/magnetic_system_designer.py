"""
magnetic_system_designer.py — Halbach array magnetic levitation system designer.

Provides physics-based modelling of Halbach array configurations for magnetic
levitation, lift force calculations, stability analysis, and gap optimisation.

References
----------
- Halbach, K. (1980). Design of permanent multipole magnets with oriented
  rare earth cobalt material. Nuclear Instruments and Methods.
- Post, R.F. & Ryutov, D.D. (2000). The Inductrack concept.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

MU_0 = 4 * math.pi * 1e-7   # vacuum permeability (H/m)
GRAVITY = 9.81               # m/s²


# ---------------------------------------------------------------------------
# Halbach array geometry
# ---------------------------------------------------------------------------

@dataclass
class HalbachArray:
    """
    Parameters for a single-sided Halbach magnet array.

    A Halbach array concentrates the magnetic field on one side by rotating
    the magnetisation direction of successive magnets.  For n_poles poles per
    spatial period, the k-th magnet in the sequence is rotated by
    k × (π / n_poles) from horizontal.

    Attributes
    ----------
    magnet_length_mm:
        Length of each individual magnet block (direction of motion), mm.
    magnet_width_mm:
        Width of each magnet block (transverse), mm.
    magnet_height_mm:
        Thickness of each magnet block (vertical, direction of field), mm.
    n_poles:
        Number of magnets per spatial wavelength (typically 4 or 8).
    n_periods:
        Number of spatial periods in the array.
    remanence_t:
        Remanent flux density of the magnet material (T).
        N52 ≈ 1.45 T; N42 ≈ 1.32 T; N35 ≈ 1.21 T.
    """

    magnet_length_mm: float = 50.0
    magnet_width_mm: float = 25.0
    magnet_height_mm: float = 10.0
    n_poles: int = 4
    n_periods: int = 4
    remanence_t: float = 1.45   # N52

    # ------------------------------------------------------------------
    # Derived geometry
    # ------------------------------------------------------------------

    @property
    def spatial_wavelength_mm(self) -> float:
        """Spatial period λ of the array (mm)."""
        return self.n_poles * self.magnet_length_mm

    @property
    def spatial_wavelength_m(self) -> float:
        return self.spatial_wavelength_mm / 1000.0

    @property
    def magnet_height_m(self) -> float:
        return self.magnet_height_mm / 1000.0

    @property
    def total_length_mm(self) -> float:
        return self.spatial_wavelength_mm * self.n_periods

    @property
    def total_magnets(self) -> int:
        return self.n_poles * self.n_periods

    # ------------------------------------------------------------------
    # Magnetic field model (Halbach idealisation)
    # ------------------------------------------------------------------

    def peak_surface_field_t(self) -> float:
        """
        Peak magnetic flux density at the array surface (z = 0) using the
        standard Halbach array formula:

            B_peak = B_r × (1 − exp(−k×h)) × F_pole

        where k = 2π/λ, h = magnet height, F_pole is the pole-count factor.
        """
        k = 2 * math.pi / self.spatial_wavelength_m
        h = self.magnet_height_m
        f_pole = math.sin(math.pi / self.n_poles) / (math.pi / self.n_poles)
        return self.remanence_t * (1 - math.exp(-k * h)) * f_pole

    def field_at_gap_t(self, gap_m: float) -> float:
        """
        Magnetic flux density at height *gap_m* above the array surface.
        The field decays exponentially:  B(z) = B_0 × exp(−k × z)
        """
        k = 2 * math.pi / self.spatial_wavelength_m
        return self.peak_surface_field_t() * math.exp(-k * gap_m)

    # ------------------------------------------------------------------
    # Lift and drag estimates (Inductrack model)
    # ------------------------------------------------------------------

    def lift_force_per_unit_area_n_m2(
        self,
        gap_m: float,
        velocity_ms: float,
        track_resistivity_ohm_m: float = 2.65e-8,  # aluminium
        track_thickness_m: float = 0.006,
    ) -> float:
        """
        Lift force per unit array area (N/m²) using the Inductrack model
        (passive Halbach levitation above a conducting track).

        Parameters
        ----------
        gap_m:
            Air gap between array bottom and track surface (m).
        velocity_ms:
            Translational speed of the array over the track (m/s).
        track_resistivity_ohm_m:
            Electrical resistivity of the track material (Ω·m).
            Aluminium ≈ 2.65e-8, copper ≈ 1.72e-8.
        track_thickness_m:
            Thickness of the conducting track (m).
        """
        B0 = self.peak_surface_field_t()
        k = 2 * math.pi / self.spatial_wavelength_m

        # Track sheet resistance Σ = ρ / d  (Ω/sq)
        sigma_sheet = track_resistivity_ohm_m / track_thickness_m

        # Characteristic velocity v_c = σ_sheet × λ / (2 π × MU_0 × ...) — simplified
        # Using Post & Ryutov formulation: v_c = (ρ × k) / (MU_0)
        v_c = (track_resistivity_ohm_m * k) / MU_0

        # Lift pressure (N/m²)
        B_gap = B0 * math.exp(-k * gap_m)
        lift_pressure = (B_gap**2 / (2 * MU_0)) * (velocity_ms / v_c) / (
            1 + (velocity_ms / v_c) ** 2
        ) ** 0.5

        return lift_pressure

    def drag_force_per_unit_area_n_m2(
        self,
        gap_m: float,
        velocity_ms: float,
        track_resistivity_ohm_m: float = 2.65e-8,
        track_thickness_m: float = 0.006,
    ) -> float:
        """Drag force per unit array area (N/m²) — complementary to lift."""
        B0 = self.peak_surface_field_t()
        k = 2 * math.pi / self.spatial_wavelength_m
        v_c = (track_resistivity_ohm_m * k) / MU_0
        B_gap = B0 * math.exp(-k * gap_m)
        drag_pressure = (B_gap**2 / (2 * MU_0)) * (v_c / velocity_ms) / (
            1 + (v_c / velocity_ms) ** 2
        ) ** 0.5
        return drag_pressure

    def lift_to_drag_ratio(
        self,
        gap_m: float,
        velocity_ms: float,
        **kwargs: Any,
    ) -> float:
        """Lift-to-drag ratio at the given operating point."""
        lift = self.lift_force_per_unit_area_n_m2(gap_m, velocity_ms, **kwargs)
        drag = self.drag_force_per_unit_area_n_m2(gap_m, velocity_ms, **kwargs)
        return lift / drag if drag > 0 else float("inf")


# ---------------------------------------------------------------------------
# Active stabilisation model
# ---------------------------------------------------------------------------

@dataclass
class ActiveStabilisation:
    """
    Models the coil-based active stabilisation system that maintains
    constant hover height against disturbances.

    Parameters
    ----------
    coil_turns:
        Number of turns per correction coil.
    coil_resistance_ohm:
        DC resistance of each correction coil (Ω).
    supply_voltage_v:
        Available supply voltage for the correction coils (V).
    n_coils:
        Number of independent correction coils in the array.
    hall_sensor_resolution_mt:
        Hall effect sensor resolution in milli-Tesla.
    """

    coil_turns: int = 200
    coil_resistance_ohm: float = 2.5
    supply_voltage_v: float = 24.0
    n_coils: int = 8
    hall_sensor_resolution_mt: float = 1.0   # AH3503 ≈ 1.3 mT resolution

    @property
    def max_correction_current_a(self) -> float:
        return self.supply_voltage_v / self.coil_resistance_ohm

    @property
    def max_mmf_at(self) -> float:
        """Maximum magnetomotive force (A·turns) per coil."""
        return self.max_correction_current_a * self.coil_turns

    @property
    def idle_power_w(self) -> float:
        """Power dissipated when coils carry 10 % of max current (steady hover)."""
        i_idle = self.max_correction_current_a * 0.10
        return self.n_coils * i_idle**2 * self.coil_resistance_ohm

    @property
    def peak_power_w(self) -> float:
        """Peak correction power (all coils at max current)."""
        return self.n_coils * self.max_correction_current_a**2 * self.coil_resistance_ohm

    def correction_gap_change_mm(
        self,
        disturbance_force_n: float,
        array: HalbachArray,
        nominal_gap_m: float,
    ) -> float:
        """
        Estimate the gap deviation (mm) caused by a step disturbance force
        before the active system corrects it.

        Uses a linearised spring constant dF/dz of the magnetic lift.
        """
        dz = 0.001  # 1 mm perturbation for numerical derivative
        gap1 = nominal_gap_m
        gap2 = nominal_gap_m + dz

        area_m2 = (
            array.total_length_mm / 1000 * array.magnet_width_mm / 1000
        )

        # Numerical derivative of lift pressure w.r.t. gap
        lp1 = array.lift_force_per_unit_area_n_m2(gap1, 10.0) * area_m2
        lp2 = array.lift_force_per_unit_area_n_m2(gap2, 10.0) * area_m2
        k_spring = abs((lp2 - lp1) / dz)   # N/m

        if k_spring == 0:
            return float("inf")
        return (disturbance_force_n / k_spring) * 1000  # convert to mm


# ---------------------------------------------------------------------------
# System designer
# ---------------------------------------------------------------------------

@dataclass
class MagneticSystemDesigner:
    """
    High-level designer that optimises a complete maglev system for the
    hover bike's target mass and operating conditions.
    """

    target_mass_kg: float = 120.0          # bike + rider
    target_gap_mm: float = 150.0
    min_speed_levitate_ms: float = 5.0     # minimum speed for passive lift
    array: HalbachArray = field(default_factory=HalbachArray)
    stabiliser: ActiveStabilisation = field(default_factory=ActiveStabilisation)

    # ------------------------------------------------------------------
    # Optimisation helpers
    # ------------------------------------------------------------------

    def required_array_area_m2(self, velocity_ms: float | None = None) -> float:
        """
        Minimum combined array area (both arrays) needed to lift *target_mass_kg*.
        """
        v = velocity_ms or self.min_speed_levitate_ms
        gap_m = self.target_gap_mm / 1000.0
        lift_pressure = self.array.lift_force_per_unit_area_n_m2(gap_m, v)
        required_force_n = self.target_mass_kg * GRAVITY
        if lift_pressure <= 0:
            return float("inf")
        return required_force_n / lift_pressure

    def optimise_poles(
        self,
        candidate_poles: list[int] | None = None,
        velocity_ms: float = 10.0,
        gap_mm: float | None = None,
    ) -> dict[int, dict[str, float]]:
        """
        Evaluate lift-to-drag ratio for different pole counts and return
        a comparison table.
        """
        if candidate_poles is None:
            candidate_poles = [2, 4, 8, 16]
        gap_m = (gap_mm or self.target_gap_mm) / 1000.0
        results: dict[int, dict[str, float]] = {}
        for n in candidate_poles:
            arr = HalbachArray(
                magnet_length_mm=self.array.magnet_length_mm,
                magnet_width_mm=self.array.magnet_width_mm,
                magnet_height_mm=self.array.magnet_height_mm,
                n_poles=n,
                n_periods=self.array.n_periods,
                remanence_t=self.array.remanence_t,
            )
            results[n] = {
                "peak_surface_field_t": arr.peak_surface_field_t(),
                "field_at_gap_t": arr.field_at_gap_t(gap_m),
                "lift_pressure_n_m2": arr.lift_force_per_unit_area_n_m2(gap_m, velocity_ms),
                "drag_pressure_n_m2": arr.drag_force_per_unit_area_n_m2(gap_m, velocity_ms),
                "lift_to_drag": arr.lift_to_drag_ratio(gap_m, velocity_ms),
                "spatial_wavelength_mm": arr.spatial_wavelength_mm,
            }
        return results

    def gap_sweep(
        self,
        gap_range_mm: tuple[float, float] = (50.0, 300.0),
        steps: int = 20,
        velocity_ms: float = 10.0,
    ) -> list[dict[str, float]]:
        """
        Sweep over air-gap values and record lift force, drag force, and
        L/D ratio.
        """
        gap_min, gap_max = gap_range_mm
        sweep: list[dict[str, float]] = []
        for i in range(steps):
            gap_mm = gap_min + (gap_max - gap_min) * i / (steps - 1)
            gap_m = gap_mm / 1000.0
            sweep.append(
                {
                    "gap_mm": gap_mm,
                    "lift_pressure_n_m2": self.array.lift_force_per_unit_area_n_m2(
                        gap_m, velocity_ms
                    ),
                    "drag_pressure_n_m2": self.array.drag_force_per_unit_area_n_m2(
                        gap_m, velocity_ms
                    ),
                    "lift_to_drag": self.array.lift_to_drag_ratio(gap_m, velocity_ms),
                    "field_t": self.array.field_at_gap_t(gap_m),
                }
            )
        return sweep

    def stability_report(self) -> dict[str, Any]:
        """
        Produce a stability analysis summary for the designed system.
        """
        gap_m = self.target_gap_mm / 1000.0
        area = self.required_array_area_m2(velocity_ms=self.min_speed_levitate_ms)
        low_speed_area = self.required_array_area_m2(velocity_ms=2.0)

        return {
            "target_mass_kg": self.target_mass_kg,
            "target_gap_mm": self.target_gap_mm,
            "min_levitation_speed_ms": self.min_speed_levitate_ms,
            "array_config": {
                "n_poles": self.array.n_poles,
                "n_periods": self.array.n_periods,
                "spatial_wavelength_mm": self.array.spatial_wavelength_mm,
                "remanence_t": self.array.remanence_t,
            },
            "field_analysis": {
                "peak_surface_field_t": self.array.peak_surface_field_t(),
                "field_at_nominal_gap_t": self.array.field_at_gap_t(gap_m),
            },
            "area_requirements_m2": {
                "at_min_speed": area,
                "at_2ms": low_speed_area,
                "at_10ms": self.required_array_area_m2(10.0),
                "at_20ms": self.required_array_area_m2(20.0),
            },
            "stabilisation": {
                "max_correction_current_a": self.stabiliser.max_correction_current_a,
                "max_mmf_at": self.stabiliser.max_mmf_at,
                "idle_power_w": self.stabiliser.idle_power_w,
                "peak_power_w": self.stabiliser.peak_power_w,
            },
            "gap_disturbance_mm_per_100N": self.stabiliser.correction_gap_change_mm(
                100.0, self.array, gap_m
            ),
            "pole_comparison": self.optimise_poles(velocity_ms=10.0),
        }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    designer = MagneticSystemDesigner()
    report = designer.stability_report()
    print(json.dumps(report, indent=2))
