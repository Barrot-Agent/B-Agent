"""
3d_print_preparation.py - STL Model Optimisation & Print Job Preparation

Generates 3D printing specifications, support structures, print time
estimates, material usage, and slice settings for all hover bike components.
"""

import math
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class PrintJob:
    """A single 3D print job specification."""
    filename: str
    component_name: str
    material: str
    layer_height_mm: float
    infill_pct: int
    print_speed_mm_s: int
    nozzle_temp_c: int
    bed_temp_c: int
    supports: bool
    brim_width_mm: float
    estimated_volume_cm3: float
    estimated_time_hours: float
    weight_g: float
    print_notes: str = ""


# Filament density lookup [g/cm³]
FILAMENT_DENSITY = {
    "PLA": 1.24,
    "CF-PLA": 1.30,
    "ABS": 1.04,
    "PETG": 1.27,
    "Nylon": 1.13,
    "TPU": 1.21,
}

# Filament cost per kg [USD]
FILAMENT_COST_PER_KG = {
    "PLA": 22,
    "CF-PLA": 45,
    "ABS": 25,
    "PETG": 28,
    "Nylon": 55,
    "TPU": 38,
}


def generate_print_jobs() -> list[PrintJob]:
    """Return complete print job list for all hover bike components."""
    return [
        PrintJob(
            filename="frame_assembly.stl",
            component_name="Main Aerodynamic Frame",
            material="CF-PLA",
            layer_height_mm=0.2,
            infill_pct=40,
            print_speed_mm_s=40,
            nozzle_temp_c=220,
            bed_temp_c=60,
            supports=True,
            brim_width_mm=8.0,
            estimated_volume_cm3=2154,
            estimated_time_hours=48,
            weight_g=2800,
            print_notes="Split into 4 sections; bolt together with M8 titanium inserts. "
                        "Use gyroid infill pattern for optimal strength/weight.",
        ),
        PrintJob(
            filename="magnet_housing.stl",
            component_name="Halbach Array Magnet Housing (×4)",
            material="PETG",
            layer_height_mm=0.15,
            infill_pct=80,
            print_speed_mm_s=35,
            nozzle_temp_c=240,
            bed_temp_c=75,
            supports=False,
            brim_width_mm=5.0,
            estimated_volume_cm3=267,
            estimated_time_hours=6,
            weight_g=340,
            print_notes="Critical tolerances at magnet pockets (±0.1mm). "
                        "Print slowly. PETG resists magnetic heat.",
        ),
        PrintJob(
            filename="motor_stator.stl",
            component_name="Linear Motor Stator Housing (×2)",
            material="ABS",
            layer_height_mm=0.15,
            infill_pct=60,
            print_speed_mm_s=35,
            nozzle_temp_c=245,
            bed_temp_c=100,
            supports=True,
            brim_width_mm=10.0,
            estimated_volume_cm3=279,
            estimated_time_hours=8,
            weight_g=290,
            print_notes="ABS needed for high-temp tolerance near motor. "
                        "Print in enclosure to prevent warping.",
        ),
        PrintJob(
            filename="battery_enclosure.stl",
            component_name="Battery + BMS Enclosure",
            material="CF-PLA",
            layer_height_mm=0.2,
            infill_pct=50,
            print_speed_mm_s=40,
            nozzle_temp_c=220,
            bed_temp_c=60,
            supports=False,
            brim_width_mm=5.0,
            estimated_volume_cm3=369,
            estimated_time_hours=12,
            weight_g=480,
            print_notes="100% perimeter walls (6 walls) for waterproofing. "
                        "Insert rubber gasket in lid groove.",
        ),
        PrintJob(
            filename="control_pod.stl",
            component_name="Handlebar Control Pod",
            material="PLA",
            layer_height_mm=0.2,
            infill_pct=35,
            print_speed_mm_s=50,
            nozzle_temp_c=210,
            bed_temp_c=55,
            supports=False,
            brim_width_mm=4.0,
            estimated_volume_cm3=117,
            estimated_time_hours=4,
            weight_g=145,
            print_notes="Ergonomic design; smooth outer surface (0.1mm ironing). "
                        "Fit-test display cutout before final assembly.",
        ),
        PrintJob(
            filename="wheel_hub.stl",
            component_name="Motor Wheel Hub Adapter (×2)",
            material="CF-PLA",
            layer_height_mm=0.15,
            infill_pct=70,
            print_speed_mm_s=30,
            nozzle_temp_c=220,
            bed_temp_c=60,
            supports=False,
            brim_width_mm=6.0,
            estimated_volume_cm3=162,
            estimated_time_hours=5,
            weight_g=210,
            print_notes="High mechanical stress component. "
                        "Add M6 steel inserts at motor bolt pattern. "
                        "Verify concentricity <0.2mm before install.",
        ),
        PrintJob(
            filename="sensor_mount.stl",
            component_name="Ultrasonic + Hall Sensor Mounts",
            material="PLA",
            layer_height_mm=0.2,
            infill_pct=40,
            print_speed_mm_s=50,
            nozzle_temp_c=210,
            bed_temp_c=55,
            supports=False,
            brim_width_mm=3.0,
            estimated_volume_cm3=45,
            estimated_time_hours=2,
            weight_g=56,
            print_notes="8 units total (4 ultrasonic + 4 Hall sensor). "
                        "Snap-fit design, no hardware needed.",
        ),
        PrintJob(
            filename="coil_former.stl",
            component_name="Electromagnet Coil Former (×4)",
            material="Nylon",
            layer_height_mm=0.15,
            infill_pct=50,
            print_speed_mm_s=30,
            nozzle_temp_c=260,
            bed_temp_c=80,
            supports=False,
            brim_width_mm=8.0,
            estimated_volume_cm3=88,
            estimated_time_hours=3,
            weight_g=99,
            print_notes="Nylon for heat tolerance during coil winding. "
                        "Wind 250 turns of 22AWG magnet wire after printing.",
        ),
    ]


def compute_print_cost(job: PrintJob) -> dict:
    """Calculate material cost for a single print job."""
    density = FILAMENT_DENSITY.get(job.material, 1.20)
    cost_per_kg = FILAMENT_COST_PER_KG.get(job.material, 30)

    # Account for infill (total material includes perimeters + infill + supports)
    support_volume_factor = 1.20 if job.supports else 1.0
    actual_volume = job.estimated_volume_cm3 * (job.infill_pct / 100) * support_volume_factor
    # Minimum volume = shell + perimeters (~15% of solid)
    actual_volume = max(actual_volume, job.estimated_volume_cm3 * 0.15)
    mass_kg = actual_volume * density / 1000
    cost_usd = mass_kg * cost_per_kg

    return {
        "material_mass_kg": round(mass_kg, 3),
        "material_cost_usd": round(cost_usd, 2),
    }


def total_project_estimate(jobs: list[PrintJob]) -> dict:
    """Summarise total time, material, and cost across all print jobs."""
    total_time = sum(j.estimated_time_hours for j in jobs)
    total_weight = sum(j.weight_g for j in jobs)
    total_cost = sum(compute_print_cost(j)["material_cost_usd"] for j in jobs)

    material_summary: dict[str, float] = {}
    for job in jobs:
        material_summary[job.material] = (
            material_summary.get(job.material, 0) + job.weight_g)

    return {
        "total_print_time_hours": total_time,
        "total_weight_g": round(total_weight, 1),
        "total_filament_cost_usd": round(total_cost, 2),
        "material_breakdown_g": material_summary,
        "job_count": len(jobs),
    }


def printer_requirements() -> dict:
    """Minimum printer specifications for this project."""
    return {
        "build_volume_mm": "300×300×300 minimum (frame splits into sections)",
        "materials": ["PLA", "CF-PLA", "ABS", "PETG", "Nylon", "TPU"],
        "enclosure": "Required for ABS and Nylon",
        "min_nozzle_size_mm": 0.4,
        "hardened_nozzle": "Required for CF-PLA (abrasive)",
        "bed_leveling": "Auto bed leveling strongly recommended",
        "part_cooling": "Required for PLA/PETG; disabled for ABS",
        "recommended_printers": [
            "Bambu Lab X1-Carbon (best CF-PLA performance)",
            "Prusa MK4 + Enclosure Kit",
            "Creality K1 Max (large bed, fast)",
            "Voron 2.4 (DIY, open material system)",
        ],
    }


def run_print_preparation() -> dict:
    """Full 3D print preparation analysis."""
    print("=" * 55)
    print("BARROT HOVER BIKE — 3D PRINT PREPARATION")
    print("=" * 55)

    jobs = generate_print_jobs()
    summary = total_project_estimate(jobs)
    requirements = printer_requirements()

    print(f"\nPrint Jobs ({summary['job_count']} total):")
    print(f"  {'Component':<35} {'Material':<8} {'Hours':>5} {'Weight':>7}")
    print(f"  {'-'*60}")
    for job in jobs:
        cost = compute_print_cost(job)
        print(f"  {job.component_name:<35} {job.material:<8} "
              f"{job.estimated_time_hours:>5}h {job.weight_g:>6}g")

    print(f"\nProject Totals:")
    print(f"  Total print time:   {summary['total_print_time_hours']}h "
          f"({summary['total_print_time_hours']/24:.1f} days continuous)")
    print(f"  Total weight:       {summary['total_weight_g']}g "
          f"({summary['total_weight_g']/1000:.2f}kg)")
    print(f"  Filament cost:      ${summary['total_filament_cost_usd']}")

    print(f"\nMaterial Breakdown:")
    for mat, weight in summary["material_breakdown_g"].items():
        print(f"  {mat:<8}: {weight:.0f}g ({weight/summary['total_weight_g']*100:.0f}%)")

    return {
        "jobs": [
            {
                "filename": j.filename,
                "component": j.component_name,
                "material": j.material,
                "time_h": j.estimated_time_hours,
                "weight_g": j.weight_g,
                "notes": j.print_notes,
                **compute_print_cost(j),
            }
            for j in jobs
        ],
        "summary": summary,
        "printer_requirements": requirements,
    }


if __name__ == "__main__":
    results = run_print_preparation()
    out = Path(__file__).parent.parent / "models" / "print_preparation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved → {out}")
