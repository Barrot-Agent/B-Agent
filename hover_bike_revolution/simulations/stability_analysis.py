"""
stability_analysis.py — Parametric stability analysis for the hover bike.

Sweeps PID gains and hover gaps to identify stable operating regions.
"""

from __future__ import annotations

from typing import Any


def pid_stability_sweep(
    kp_range: tuple[float, float] = (0.5, 2.5),
    kd_range: tuple[float, float] = (0.02, 0.15),
    steps: int = 5,
    simulation_duration_s: float = 2.0,
) -> list[dict[str, Any]]:
    """
    Sweep Kp/Kd combinations and report settling time and undershoot percentage.

    Uses a simplified first-order model: dz/dt = f(gap, cmd).
    """
    results: list[dict[str, Any]] = []
    kp_step = (kp_range[1] - kp_range[0]) / (steps - 1)
    kd_step = (kd_range[1] - kd_range[0]) / (steps - 1)

    for i in range(steps):
        for j in range(steps):
            kp = kp_range[0] + i * kp_step
            kd = kd_range[0] + j * kd_step
            settling, undershoot_pct = _first_order_pid_sim(kp, kd, simulation_duration_s)
            results.append(
                {
                    "kp": round(kp, 3),
                    "kd": round(kd, 3),
                    "settling_s": round(settling, 3),
                    "undershoot_pct": round(undershoot_pct, 1),
                    "stable": undershoot_pct < 30.0 and settling < simulation_duration_s,
                }
            )
    return results


def _first_order_pid_sim(kp: float, kd: float, duration_s: float) -> tuple[float, float]:
    """Simple PD controller on a 1-D spring-mass system (no Ki for brevity)."""
    dt = 0.005
    target = 0.15
    gap = 0.20  # start 5 cm above target
    v = 0.0
    mass = 120.0
    k_spring = 5_000.0
    settling_threshold = 0.002  # 2 mm

    min_gap = gap  # track minimum gap to measure undershoot below target
    settled_at = duration_s  # default: not settled
    steps = int(duration_s / dt)
    prev_err = gap - target

    for step in range(steps):
        err = gap - target
        d_err = (err - prev_err) / dt
        cmd = -(kp * err + kd * d_err)  # corrective force direction
        f_mag = k_spring * cmd
        f_grav = -mass * 9.81
        f_net = f_mag + f_grav + mass * 9.81
        a = f_net / mass
        v += a * dt
        gap += v * dt
        if gap < min_gap:
            min_gap = gap
        if abs(gap - target) < settling_threshold and step * dt > 0.1:
            settled_at = step * dt
            break
        prev_err = err

    # Undershoot = how far the gap dropped below target as % of initial step size
    step_size = 0.20 - target  # = 0.05 m (initial offset from target)
    undershoot_m = max(0.0, target - min_gap)
    undershoot_pct = (undershoot_m / step_size) * 100 if step_size > 0 else 0.0
    return settled_at, undershoot_pct


if __name__ == "__main__":
    import json

    results = pid_stability_sweep()
    stable = [r for r in results if r["stable"]]
    print(f"Stable configurations: {len(stable)} / {len(results)}")
    best = min(stable, key=lambda r: r["settling_s"]) if stable else None
    print(f"Best config: {json.dumps(best, indent=2)}")
