"""
magnetic_system_designer.py - Halbach Array Optimisation & Magnetic Field Analysis

Physics-based simulation and optimisation of the hover bike's
magnetic levitation system using Halbach array configurations.
"""

import math
from dataclasses import dataclass
from typing import Callable


# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
MU_0 = 4 * math.pi * 1e-7  # Vacuum permeability [H/m]
G = 9.81                     # Standard gravity [m/s²]


@dataclass
class Magnet:
    """Single permanent magnet specification."""
    grade: str = "N52"
    length_mm: float = 50.0
    width_mm: float = 25.0
    height_mm: float = 12.0
    remanence_t: float = 1.44    # Br for N52
    coercivity_ka_m: float = 1040.0

    @property
    def volume_m3(self) -> float:
        return (self.length_mm * self.width_mm * self.height_mm) * 1e-9

    @property
    def max_energy_product_kj_m3(self) -> float:
        return (self.remanence_t ** 2) / (4 * MU_0) / 1000


@dataclass
class HalbachArray:
    """Halbach array configuration for levitation."""
    magnet: Magnet
    segments_per_period: int = 4    # M value (4 = standard, 8 = enhanced)
    periods: int = 4                 # Number of full periods in array
    array_width_mm: float = 100.0   # Perpendicular to motion

    @property
    def spatial_period_m(self) -> float:
        """λ = length per period."""
        return self.magnet.length_mm * self.segments_per_period / 1000

    @property
    def wave_number(self) -> float:
        """k = 2π/λ."""
        return 2 * math.pi / self.spatial_period_m

    @property
    def enhancement_factor(self) -> float:
        """κ = sin(π/M)/(π/M) — field concentration factor."""
        m = self.segments_per_period
        return math.sin(math.pi / m) / (math.pi / m)

    @property
    def effective_b0(self) -> float:
        """Effective surface field [T] below Halbach array."""
        return self.magnet.remanence_t * self.enhancement_factor * (
            1 - math.exp(-self.wave_number * self.magnet.height_mm / 1000))

    def field_at_gap(self, gap_m: float) -> float:
        """Magnetic field magnitude at levitation gap [T]."""
        return self.effective_b0 * math.exp(-self.wave_number * gap_m)

    def lift_pressure(self, gap_m: float) -> float:
        """Magnetic pressure (lift force per unit area) [Pa]."""
        b = self.field_at_gap(gap_m)
        return b ** 2 / (2 * MU_0)

    def lift_force(self, gap_m: float) -> float:
        """Total lift force for this array [N]."""
        area = (self.magnet.length_mm * self.segments_per_period * self.periods
                * self.array_width_mm) * 1e-6
        return self.lift_pressure(gap_m) * area

    def gap_for_payload(self, total_weight_n: float,
                        num_arrays: int = 4) -> float | None:
        """
        Find the levitation gap that supports a given weight.
        Uses bisection search. Returns gap [m] or None if infeasible.
        """
        def net_force(gap):
            return self.lift_force(gap) * num_arrays - total_weight_n

        lo, hi = 0.001, 0.200
        if net_force(lo) < 0:
            return None  # Cannot lift even at minimum gap
        for _ in range(50):
            mid = (lo + hi) / 2
            if net_force(mid) > 0:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2


@dataclass
class LevitationSystem:
    """Complete four-array levitation system."""
    array: HalbachArray
    num_arrays: int = 4
    active_correction_power_w: float = 80.0

    def total_lift_force(self, gap_m: float) -> float:
        return self.array.lift_force(gap_m) * self.num_arrays

    def stability_analysis(self, gap_m: float,
                           payload_n: float) -> dict:
        """
        Analyse vertical stability at operating point.
        dF/dz < 0 required for passive stability (Earnshaw violation).
        Active PID control compensates.
        """
        dg = 1e-5  # 10 µm finite difference step
        F_plus = self.total_lift_force(gap_m + dg)
        F_minus = self.total_lift_force(gap_m - dg)
        dF_dz = (F_plus - F_minus) / (2 * dg)  # N/m (negative = unstable upward)

        # PID bandwidth needed for stability
        mass = payload_n / G
        omega_n = math.sqrt(abs(dF_dz) / mass)   # Natural frequency [rad/s]
        f_n_hz = omega_n / (2 * math.pi)

        net_force = self.total_lift_force(gap_m) - payload_n
        return {
            "gap_mm": round(gap_m * 1000, 2),
            "total_lift_n": round(self.total_lift_force(gap_m), 2),
            "payload_n": round(payload_n, 2),
            "net_force_n": round(net_force, 2),
            "dF_dz_n_per_m": round(dF_dz, 1),
            "passive_stable": dF_dz < 0,
            "natural_frequency_hz": round(f_n_hz, 2),
            "pid_bandwidth_needed_hz": round(f_n_hz * 3, 2),
            "correction_power_w": self.active_correction_power_w,
        }


def optimise_halbach_configuration(
        payload_kg: float = 100.0,
        target_gap_mm: float = 15.0,
        max_magnet_mass_kg: float = 5.0) -> dict:
    """
    Optimise Halbach array parameters for a given payload and gap target.
    Searches over (segments_per_period, periods, array_width) combinations.
    """
    best = None
    best_score = float("inf")

    for segments in [4, 8]:
        for periods in [3, 4, 5, 6]:
            for width_mm in [80, 100, 120]:
                magnet = Magnet()
                arr = HalbachArray(magnet, segments, periods, float(width_mm))
                sys = LevitationSystem(arr)

                target_gap = target_gap_mm / 1000
                payload_n = payload_kg * G
                lift = sys.total_lift_force(target_gap)
                if lift < payload_n:
                    continue

                # Magnet mass estimate
                magnet_count = segments * periods * sys.num_arrays
                magnet_mass = magnet_count * magnet.volume_m3 * 7500  # density ~7500 kg/m³
                if magnet_mass > max_magnet_mass_kg:
                    continue

                # Optimise: minimise magnet mass while meeting lift requirement
                score = magnet_mass
                if score < best_score:
                    best_score = score
                    best = {
                        "segments_per_period": segments,
                        "periods": periods,
                        "array_width_mm": width_mm,
                        "effective_b0_t": round(arr.effective_b0, 3),
                        "lift_at_target_gap_n": round(lift, 1),
                        "magnet_count": magnet_count,
                        "magnet_mass_kg": round(magnet_mass, 3),
                        "lift_to_weight_ratio": round(lift / (magnet_mass * G), 2),
                    }

    return best or {"error": "No feasible configuration found for given constraints"}


def field_profile_sweep(array: HalbachArray,
                        gap_min_mm: float = 5.0,
                        gap_max_mm: float = 50.0,
                        steps: int = 20) -> list[dict]:
    """Compute field strength and lift force across a range of gaps."""
    results = []
    for i in range(steps + 1):
        gap_mm = gap_min_mm + (gap_max_mm - gap_min_mm) * i / steps
        gap_m = gap_mm / 1000
        b = array.field_at_gap(gap_m)
        p = array.lift_pressure(gap_m)
        f = array.lift_force(gap_m)
        results.append({
            "gap_mm": round(gap_mm, 1),
            "field_t": round(b, 4),
            "pressure_pa": round(p, 1),
            "lift_force_n": round(f, 2),
        })
    return results


def run_magnetic_analysis(payload_kg: float = 100.0) -> dict:
    """Full magnetic system design and analysis."""
    print("=" * 55)
    print("BARROT HOVER BIKE — MAGNETIC SYSTEM ANALYSIS")
    print("=" * 55)

    # Default design
    magnet = Magnet()
    array = HalbachArray(magnet, segments_per_period=4, periods=4,
                         array_width_mm=100.0)
    system = LevitationSystem(array)
    nominal_gap = 0.015  # 15 mm

    print(f"\nHalbach Array Configuration:")
    print(f"  Magnet grade:          {magnet.grade} (Br={magnet.remanence_t}T)")
    print(f"  Segments per period:   {array.segments_per_period}")
    print(f"  Periods:               {array.periods}")
    print(f"  Enhancement factor κ:  {array.enhancement_factor:.3f}")
    print(f"  Effective B₀:          {array.effective_b0:.3f} T")
    print(f"  Wave number k:         {array.wave_number:.1f} rad/m")

    print(f"\nLevitation at {nominal_gap*1000:.0f}mm gap:")
    lift = system.total_lift_force(nominal_gap)
    print(f"  Total lift force:      {lift:.1f} N")
    print(f"  Payload capacity:      {lift/G:.1f} kg")

    stability = system.stability_analysis(nominal_gap, payload_kg * G)
    print(f"\nStability Analysis (payload={payload_kg}kg):")
    for k, v in stability.items():
        print(f"  {k:<35} {v}")

    print(f"\nOptimising configuration...")
    opt = optimise_halbach_configuration(payload_kg)
    print(f"  Optimal config: {opt}")

    print(f"\nField profile sweep:")
    profile = field_profile_sweep(array, 5, 50, 10)
    for row in profile[::3]:
        bar = "█" * int(row["lift_force_n"] / 5)
        print(f"  {row['gap_mm']:5.1f}mm | {bar:<20} {row['lift_force_n']:.1f}N")

    return {
        "config": {
            "magnet": {"grade": magnet.grade, "Br_T": magnet.remanence_t},
            "array": {
                "segments": array.segments_per_period,
                "periods": array.periods,
                "effective_B0_T": array.effective_b0,
            },
        },
        "performance": {
            "lift_at_15mm_n": round(lift, 1),
            "max_payload_kg": round(lift / G, 1),
        },
        "stability": stability,
        "optimal_config": opt,
        "field_profile": profile,
    }


if __name__ == "__main__":
    import json
    from pathlib import Path
    results = run_magnetic_analysis(payload_kg=100.0)
    out = Path(__file__).parent.parent / "models" / "magnetic_analysis.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved → {out}")
