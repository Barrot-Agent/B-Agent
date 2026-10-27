"""
power_consumption_sim.py — Real-time power consumption simulation.

Simulates battery state-of-charge and power flows for various riding scenarios.
"""

from __future__ import annotations

from typing import Any


def simulate_power(
    capacity_wh: float = 1000.0,
    duration_h: float = 2.0,
    dt_h: float = 1 / 60,
    base_load_w: float = 370.0,
    solar_w: float = 0.0,
    regen_w: float = 20.0,
) -> list[dict[str, Any]]:
    """
    Simulate battery SoC over a ride.

    Parameters
    ----------
    capacity_wh:
        Battery capacity (Wh).
    duration_h:
        Ride duration (hours).
    dt_h:
        Time step (hours).
    base_load_w:
        Constant power draw (W).
    solar_w:
        Solar generation (W).
    regen_w:
        Regenerative recovery (W).

    Returns
    -------
    List of {t_h, soc_pct, battery_v} records.
    """
    soc = 1.0
    records: list[dict[str, Any]] = []
    t = 0.0
    steps = int(duration_h / dt_h)

    for _ in range(steps):
        net_w = base_load_w - solar_w - regen_w
        energy_used_wh = net_w * dt_h
        soc -= energy_used_wh / capacity_wh
        soc = max(0.0, min(1.0, soc))
        records.append(
            {
                "t_h": round(t, 4),
                "soc_pct": round(soc * 100, 2),
                "net_load_w": round(net_w, 1),
            }
        )
        t += dt_h
        if soc <= 0.05:
            break

    return records


if __name__ == "__main__":
    import json

    result = simulate_power(solar_w=80.0, regen_w=30.0)
    print(f"Steps: {len(result)}")
    print(f"Final SoC: {result[-1]['soc_pct']:.1f} %")
    print(f"Duration: {result[-1]['t_h']:.2f} h")
