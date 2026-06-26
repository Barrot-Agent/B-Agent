"""
cost_calculator.py — Total cost estimation tool for the hover bike build.
"""

from __future__ import annotations

from typing import Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from assembly_guide_generator import PARTS_LIST


PRINT_COSTS_PER_KG_USD: dict[str, float] = {
    "CF-PLA": 45.0,
    "PETG": 22.0,
    "ABS-CF": 40.0,
    "Nylon-PA12": 85.0,
    "TPU-95A": 30.0,
}

ELECTRICITY_COST_USD_PER_KWH = 0.12
PRINTER_POWER_W = 300.0  # average FDM printer draw


def calculate_total_cost(
    filament_usage_g: dict[str, float] | None = None,
    total_print_hours: float = 80.0,
) -> dict[str, Any]:
    """
    Calculate full build cost including parts, filament, and electricity.
    """
    filament_usage_g = filament_usage_g or {
        "CF-PLA": 2_400.0,
        "PETG": 1_200.0,
        "ABS-CF": 600.0,
        "Nylon-PA12": 720.0,
        "TPU-95A": 200.0,
    }

    parts_cost = sum(p["qty"] * p["unit_cost_usd"] for p in PARTS_LIST)

    filament_cost: dict[str, float] = {
        mat: (g / 1000) * PRINT_COSTS_PER_KG_USD.get(mat, 30.0)
        for mat, g in filament_usage_g.items()
    }
    total_filament_cost = sum(filament_cost.values())

    electricity_kwh = PRINTER_POWER_W * total_print_hours / 1000
    electricity_cost = electricity_kwh * ELECTRICITY_COST_USD_PER_KWH

    miscellaneous = 80.0  # consumables, sandpaper, gloves, etc.

    total = parts_cost + total_filament_cost + electricity_cost + miscellaneous

    return {
        "parts_cost_usd": round(parts_cost, 2),
        "filament_cost_usd": {k: round(v, 2) for k, v in filament_cost.items()},
        "total_filament_usd": round(total_filament_cost, 2),
        "electricity_cost_usd": round(electricity_cost, 2),
        "miscellaneous_usd": round(miscellaneous, 2),
        "grand_total_usd": round(total, 2),
        "cost_summary": {
            "low_estimate_usd": round(total * 0.90, 2),
            "mid_estimate_usd": round(total, 2),
            "high_estimate_usd": round(total * 1.20, 2),
        },
    }


if __name__ == "__main__":
    import json
    result = calculate_total_cost()
    print(json.dumps(result, indent=2))
