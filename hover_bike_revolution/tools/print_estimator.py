"""
print_estimator.py — Print time and material estimator for all hover bike components.
"""

from __future__ import annotations

from typing import Any
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import via importlib because filename starts with a digit
import importlib.util, importlib

spec = importlib.util.spec_from_file_location(
    "print_preparation",
    Path(__file__).parent.parent / "src" / "3d_print_preparation.py",
)
mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules["print_preparation"] = mod
spec.loader.exec_module(mod)  # type: ignore[union-attr]
PrintPreparation = mod.PrintPreparation


def estimate_prints() -> dict[str, Any]:
    """Run print estimation and return summary."""
    prep = PrintPreparation()
    report = prep.full_report()
    summary = report["summary"]
    return {
        "total_components": summary["total_components"],
        "total_unique_parts": summary["total_unique_parts"],
        "total_print_time_h": summary["total_print_time_h"],
        "filament_by_material_g": summary["filament_by_material_g"],
        "filament_cost_usd": summary["filament_cost_usd"],
        "total_filament_cost_usd": summary["total_filament_cost_usd"],
        "printer_requirements": report["printer_requirements"],
    }


if __name__ == "__main__":
    import json
    result = estimate_prints()
    print(json.dumps(result, indent=2))
