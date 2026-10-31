"""
3d_print_preparation.py — Model optimisation and print preparation for the hover bike.

Generates print-ready specifications, support structure recommendations, material
estimates, and print-time calculations for each component of the hover bike.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Print settings per material
# ---------------------------------------------------------------------------

MATERIAL_PROFILES: dict[str, dict[str, Any]] = {
    "CF-PLA": {
        "description": "Carbon fibre reinforced PLA — structural components",
        "nozzle_temp_c": 220,
        "bed_temp_c": 60,
        "print_speed_mm_s": 45,
        "cooling_pct": 30,
        "nozzle_diameter_mm": 0.6,  # hardened steel required
        "recommended_infill_pct": 40,
        "recommended_infill_pattern": "gyroid",
        "layer_height_mm": 0.2,
        "density_g_cm3": 1.19,
        "tensile_strength_mpa": 65,
        "notes": "Requires hardened steel or ruby nozzle. Abrasive — standard brass nozzles wear rapidly.",
    },
    "PETG": {
        "description": "PETG — electronics enclosures, battery housing",
        "nozzle_temp_c": 235,
        "bed_temp_c": 80,
        "print_speed_mm_s": 50,
        "cooling_pct": 50,
        "nozzle_diameter_mm": 0.4,
        "recommended_infill_pct": 35,
        "recommended_infill_pattern": "gyroid",
        "layer_height_mm": 0.2,
        "density_g_cm3": 1.27,
        "tensile_strength_mpa": 50,
        "notes": "Good chemical resistance and impact toughness. Slightly flexible.",
    },
    "ABS-CF": {
        "description": "Carbon fibre ABS — wheel hubs, high-stress brackets",
        "nozzle_temp_c": 245,
        "bed_temp_c": 110,
        "print_speed_mm_s": 40,
        "cooling_pct": 0,
        "nozzle_diameter_mm": 0.6,
        "recommended_infill_pct": 50,
        "recommended_infill_pattern": "cubic",
        "layer_height_mm": 0.15,
        "density_g_cm3": 1.10,
        "tensile_strength_mpa": 55,
        "notes": "Requires enclosure to prevent warping. High-temperature stable.",
    },
    "Nylon-PA12": {
        "description": "SLS Nylon PA12 — magnet housings (professional print service)",
        "nozzle_temp_c": 270,
        "bed_temp_c": 90,
        "print_speed_mm_s": 30,
        "cooling_pct": 0,
        "nozzle_diameter_mm": 0.4,
        "recommended_infill_pct": 60,
        "recommended_infill_pattern": "solid",
        "layer_height_mm": 0.1,
        "density_g_cm3": 1.01,
        "tensile_strength_mpa": 50,
        "notes": "Preferred via SLS for magnet housings. FDM possible with drybox.",
    },
    "TPU-95A": {
        "description": "TPU 95A — vibration dampers, gaskets",
        "nozzle_temp_c": 230,
        "bed_temp_c": 45,
        "print_speed_mm_s": 20,
        "cooling_pct": 80,
        "nozzle_diameter_mm": 0.4,
        "recommended_infill_pct": 20,
        "recommended_infill_pattern": "concentric",
        "layer_height_mm": 0.25,
        "density_g_cm3": 1.21,
        "tensile_strength_mpa": 25,
        "notes": "Direct-drive extruder strongly recommended. Do not use Bowden tube.",
    },
}


# ---------------------------------------------------------------------------
# Component print specifications
# ---------------------------------------------------------------------------


@dataclass
class ComponentPrintSpec:
    """Print specification for a single 3D-printed component."""

    name: str
    material: str
    volume_cm3: float
    dimensions_mm: tuple[float, float, float]
    infill_pct: float | None = None
    layer_height_mm: float | None = None
    orientation: str = "flat"  # flat | upright | angled
    support_required: bool = False
    support_type: str = "none"  # none | normal | tree | dissolvable
    copies: int = 1
    post_processing: list[str] | None = None

    def mass_g(self) -> float:
        profile = MATERIAL_PROFILES.get(self.material, {})
        density = profile.get("density_g_cm3", 1.2)
        infill = (self.infill_pct or profile.get("recommended_infill_pct", 40)) / 100
        # Shell volume ≈ 30 % of bounding box; infill for the rest
        shell_frac = 0.30
        effective_density = density * (shell_frac + (1 - shell_frac) * infill)
        return self.volume_cm3 * effective_density * self.copies

    def filament_g(self) -> float:
        return self.mass_g()

    def filament_m(self) -> float:
        """Approximate filament length (m) for 1.75 mm filament."""
        profile = MATERIAL_PROFILES.get(self.material, {})
        density = profile.get("density_g_cm3", 1.2)
        r = 0.00175 / 2
        volume_m3 = (self.filament_g() / density) / 1_000_000
        length_m = volume_m3 / (math.pi * r**2)
        return length_m

    def print_time_h(self) -> float:
        """Rough print-time estimate (hours)."""
        profile = MATERIAL_PROFILES.get(self.material, {})
        speed = profile.get("print_speed_mm_s", 50)
        layer_h = self.layer_height_mm or profile.get("layer_height_mm", 0.2)
        # Empirical: vol × constant / speed / layer_h
        return self.volume_cm3 * 0.8 / (speed * layer_h) * self.copies

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "material": self.material,
            "volume_cm3": self.volume_cm3,
            "dimensions_mm": list(self.dimensions_mm),
            "infill_pct": self.infill_pct
            or MATERIAL_PROFILES.get(self.material, {}).get("recommended_infill_pct"),
            "layer_height_mm": self.layer_height_mm
            or MATERIAL_PROFILES.get(self.material, {}).get("layer_height_mm"),
            "orientation": self.orientation,
            "support_required": self.support_required,
            "support_type": self.support_type,
            "copies": self.copies,
            "post_processing": self.post_processing or [],
            "mass_g": round(self.mass_g(), 1),
            "filament_m": round(self.filament_m(), 1),
            "print_time_h": round(self.print_time_h(), 1),
        }


# ---------------------------------------------------------------------------
# Component library
# ---------------------------------------------------------------------------

HOVER_BIKE_COMPONENTS: list[ComponentPrintSpec] = [
    ComponentPrintSpec(
        name="frame_main_front",
        material="CF-PLA",
        volume_cm3=850.0,
        dimensions_mm=(800.0, 600.0, 350.0),
        infill_pct=40,
        orientation="flat",
        support_required=True,
        support_type="tree",
        copies=1,
        post_processing=["sand 220-grit", "install heat-set inserts", "paint with epoxy primer"],
    ),
    ComponentPrintSpec(
        name="frame_main_rear",
        material="CF-PLA",
        volume_cm3=780.0,
        dimensions_mm=(800.0, 600.0, 350.0),
        infill_pct=40,
        orientation="flat",
        support_required=True,
        support_type="tree",
        copies=1,
        post_processing=["sand 220-grit", "install heat-set inserts", "paint with epoxy primer"],
    ),
    ComponentPrintSpec(
        name="magnet_housing",
        material="Nylon-PA12",
        volume_cm3=180.0,
        dimensions_mm=(300.0, 250.0, 40.0),
        infill_pct=60,
        orientation="flat",
        support_required=False,
        copies=4,  # front + rear, left + right
        post_processing=["press-fit magnets with epoxy", "verify with Gaussmeter"],
    ),
    ComponentPrintSpec(
        name="wheel_hub",
        material="ABS-CF",
        volume_cm3=120.0,
        dimensions_mm=(200.0, 200.0, 60.0),
        infill_pct=55,
        orientation="flat",
        support_required=True,
        support_type="normal",
        copies=2,
        post_processing=["bore to tolerance for motor press-fit", "balance if required"],
    ),
    ComponentPrintSpec(
        name="battery_enclosure_main",
        material="PETG",
        volume_cm3=320.0,
        dimensions_mm=(500.0, 200.0, 120.0),
        infill_pct=35,
        orientation="flat",
        support_required=False,
        copies=1,
        post_processing=["fit M4 lid screws", "apply foam gasket seal"],
    ),
    ComponentPrintSpec(
        name="battery_enclosure_lid",
        material="PETG",
        volume_cm3=60.0,
        dimensions_mm=(500.0, 200.0, 5.0),
        infill_pct=35,
        orientation="flat",
        copies=1,
    ),
    ComponentPrintSpec(
        name="control_pod",
        material="PETG",
        volume_cm3=150.0,
        dimensions_mm=(200.0, 150.0, 80.0),
        infill_pct=30,
        orientation="flat",
        support_required=True,
        support_type="normal",
        copies=1,
        post_processing=["drill cable pass-throughs", "install brass thread inserts"],
    ),
    ComponentPrintSpec(
        name="solar_canopy_frame",
        material="PETG",
        volume_cm3=200.0,
        dimensions_mm=(800.0, 400.0, 15.0),
        infill_pct=25,
        orientation="flat",
        support_required=False,
        copies=1,
        post_processing=["bond thin-film solar cells with UV-resistant adhesive"],
    ),
    ComponentPrintSpec(
        name="handlebar_assembly",
        material="CF-PLA",
        volume_cm3=95.0,
        dimensions_mm=(450.0, 100.0, 80.0),
        infill_pct=45,
        orientation="upright",
        support_required=True,
        support_type="tree",
        copies=1,
        post_processing=["install throttle sleeve", "cable routing"],
    ),
    ComponentPrintSpec(
        name="vibration_damper_pad",
        material="TPU-95A",
        volume_cm3=25.0,
        dimensions_mm=(80.0, 80.0, 15.0),
        infill_pct=20,
        orientation="flat",
        copies=8,
        post_processing=["trim excess material"],
    ),
    ComponentPrintSpec(
        name="cable_conduit_section",
        material="PETG",
        volume_cm3=15.0,
        dimensions_mm=(200.0, 20.0, 20.0),
        infill_pct=30,
        orientation="flat",
        copies=12,
    ),
    ComponentPrintSpec(
        name="sensor_mount_ultrasonic",
        material="PETG",
        volume_cm3=8.0,
        dimensions_mm=(40.0, 30.0, 25.0),
        infill_pct=35,
        orientation="flat",
        copies=4,
        post_processing=["press-fit HC-SR04 sensors"],
    ),
]


# ---------------------------------------------------------------------------
# Print preparation report generator
# ---------------------------------------------------------------------------


class PrintPreparation:
    """
    Generates a complete print preparation report for the hover bike.
    """

    def __init__(self, components: list[ComponentPrintSpec] | None = None) -> None:
        self.components = components or HOVER_BIKE_COMPONENTS

    def total_filament_g(self) -> dict[str, float]:
        """Total filament usage by material (g)."""
        usage: dict[str, float] = {}
        for c in self.components:
            usage[c.material] = usage.get(c.material, 0.0) + c.filament_g()
        return usage

    def total_print_time_h(self) -> float:
        return sum(c.print_time_h() for c in self.components)

    def printer_requirements(self) -> dict[str, Any]:
        max_dim = max(max(c.dimensions_mm) for c in self.components)
        return {
            "min_build_volume_mm": "300 × 300 × 350 (XYZ)",
            "max_single_print_dimension_mm": max_dim,
            "required_nozzle_types": ["0.4 mm brass", "0.6 mm hardened steel"],
            "required_materials": list(MATERIAL_PROFILES.keys()),
            "enclosed_chamber_required": True,
            "direct_drive_recommended": True,
            "notes": (
                "Large components can be split and bonded with structural epoxy. "
                "SLS service recommended for Nylon-PA12 magnet housings."
            ),
        }

    def filament_cost_usd(self, cost_per_kg: dict[str, float] | None = None) -> dict[str, float]:
        costs = cost_per_kg or {
            "CF-PLA": 45.0,
            "PETG": 22.0,
            "ABS-CF": 40.0,
            "Nylon-PA12": 85.0,
            "TPU-95A": 30.0,
        }
        filament = self.total_filament_g()
        return {
            mat: round(grams / 1000 * costs.get(mat, 30.0), 2) for mat, grams in filament.items()
        }

    def full_report(self) -> dict[str, Any]:
        return {
            "components": [c.to_dict() for c in self.components],
            "summary": {
                "total_components": sum(c.copies for c in self.components),
                "total_unique_parts": len(self.components),
                "total_print_time_h": round(self.total_print_time_h(), 1),
                "filament_by_material_g": {
                    k: round(v, 1) for k, v in self.total_filament_g().items()
                },
                "filament_cost_usd": self.filament_cost_usd(),
                "total_filament_cost_usd": round(sum(self.filament_cost_usd().values()), 2),
            },
            "printer_requirements": self.printer_requirements(),
            "material_profiles": MATERIAL_PROFILES,
        }

    def write_report(self, path: Path | str) -> Path:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(self.full_report(), indent=2), encoding="utf-8")
        return out


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    prep = PrintPreparation()
    report = prep.full_report()
    print(f"Total print time: {report['summary']['total_print_time_h']:.1f} hours")
    print(f"Total filament cost: ${report['summary']['total_filament_cost_usd']:.2f}")
    print("Filament by material (g):", report["summary"]["filament_by_material_g"])
