"""
hover_bike_generator.py - Barrot Revolution Hover Bike Parametric CAD Generator

Generates complete hover bike specifications, STL model descriptions,
component lists, and assembly instructions from a parametric design system.
"""

import math
import json
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class HoverBikeSpec:
    """Complete hover bike design specification."""
    # Dimensions
    frame_length_mm: float = 1800.0
    frame_width_mm: float = 600.0
    frame_height_mm: float = 400.0
    seat_height_mm: float = 850.0
    wheelbase_mm: float = 1400.0

    # Levitation system
    halbach_array_count: int = 4
    magnet_grade: str = "N52"
    magnet_length_mm: float = 50.0
    magnet_width_mm: float = 25.0
    magnet_height_mm: float = 12.0
    hover_gap_nominal_mm: float = 15.0
    hover_gap_min_mm: float = 8.0
    hover_gap_max_mm: float = 30.0

    # Power system
    battery_capacity_wh: float = 500.0
    battery_voltage_v: float = 48.0
    solar_panel_area_m2: float = 0.5
    solar_panel_efficiency: float = 0.22

    # Propulsion
    motor_count: int = 2
    motor_peak_power_w: float = 800.0
    motor_continuous_power_w: float = 400.0

    # Performance
    max_payload_kg: float = 120.0
    cruise_speed_kmh: float = 40.0
    max_speed_kmh: float = 55.0
    range_km: float = 25.0

    # Structure
    frame_material: str = "carbon_fiber_pla"
    total_weight_target_kg: float = 25.0
    safety_factor: float = 3.0

    # Control
    controller_type: str = "raspberry_pi_4"
    imu_model: str = "MPU6050"
    update_rate_hz: int = 1000


@dataclass
class Component:
    """A single bill-of-materials component."""
    name: str
    quantity: int
    unit: str
    estimated_cost_usd: float
    supplier_hint: str
    notes: str = ""


def generate_bill_of_materials(spec: HoverBikeSpec) -> list[Component]:
    """Generate complete bill of materials from design spec."""
    bom = [
        # Frame
        Component("Carbon Fiber PLA Filament 1kg",
                  8, "spool", 35.0, "Amazon/Polymaker",
                  "For primary structural frame printing"),
        Component("Titanium M8 Insert Set",
                  1, "kit", 45.0, "McMaster-Carr",
                  "Heat-set inserts at stress points"),
        Component("6061-T6 Aluminum Bar 30x30x500mm",
                  4, "piece", 18.0, "Online Metals",
                  "Secondary structural supports"),

        # Levitation
        Component("Neodymium Magnet N52 50x25x12mm",
                  spec.halbach_array_count * 16, "piece", 3.50,
                  "K&J Magnetics / Amazon",
                  "Halbach array magnets, handle with care"),
        Component("3D-Printed Magnet Housing (ABS)",
                  spec.halbach_array_count, "set", 12.0,
                  "Self-print",
                  "STL: magnet_housing.stl"),
        Component("Hall Effect Sensor A1302",
                  8, "piece", 1.20, "DigiKey",
                  "Gap detection for active stabilisation"),
        Component("Stabilisation Electromagnet Coil",
                  4, "piece", 28.0, "Amazon",
                  "20W coil, 12V, active correction"),

        # Power
        Component("LiPo Battery 48V 10Ah",
                  1, "pack", 280.0, "Alibaba/RCGroups",
                  "Primary energy storage, 480Wh"),
        Component("Thin-Film Solar Panel 100W",
                  1, "panel", 95.0, "Renogy",
                  "Lightweight, flexible, roof mount"),
        Component("Battery Management System (BMS)",
                  1, "unit", 55.0, "Amazon",
                  "13S BMS, 40A continuous"),
        Component("DC-DC Converter 48V→12V 30A",
                  1, "unit", 22.0, "Amazon",
                  "Auxiliary electronics power"),
        Component("Supercapacitor Bank 16V 100F",
                  1, "bank", 75.0, "Maxwell/Amazon",
                  "Peak demand buffer, kinetic recovery"),

        # Propulsion
        Component("Hub Motor 48V 500W",
                  spec.motor_count, "motor", 145.0, "Golden Motor",
                  "Direct drive, 85% efficiency"),
        Component("Motor Controller (ESC) 60A",
                  spec.motor_count, "unit", 65.0, "Flipsky",
                  "FOC control, regenerative braking"),
        Component("Linear Motor Stator (3D-print + copper)",
                  2, "set", 85.0, "Self-build",
                  "STL: motor_stator.stl + copper coil wind"),

        # Control
        Component("Raspberry Pi 4 4GB",
                  1, "unit", 75.0, "Raspberry Pi Foundation",
                  "Main flight controller"),
        Component("MPU-6050 IMU",
                  2, "unit", 5.50, "Amazon",
                  "Redundant IMU for sensor fusion"),
        Component("HC-SR04 Ultrasonic Sensor",
                  4, "unit", 2.80, "Amazon",
                  "Altitude measurement, front/rear/left/right"),
        Component("BMP280 Barometric Sensor",
                  1, "unit", 4.20, "Amazon",
                  "Absolute altitude reference"),
        Component("Arduino Nano (coprocessor)",
                  2, "unit", 6.50, "Arduino",
                  "Real-time sensor reading offload"),

        # Misc
        Component("18AWG Silicone Wire 10m",
                  3, "spool", 12.0, "Amazon", "Main power wiring"),
        Component("Anderson Powerpole Connectors",
                  1, "kit", 18.0, "PowerWerx", "Modular power connections"),
        Component("LED Status Strip WS2812B",
                  1, "meter", 8.50, "Amazon", "Visual status indicators"),
        Component("3D Print Bed Adhesive + Consumables",
                  1, "kit", 25.0, "Amazon", "Glue stick, tape"),
    ]
    return bom


def compute_design_metrics(spec: HoverBikeSpec) -> dict:
    """Calculate key performance metrics from spec."""
    # Lift force from Halbach array
    B0 = 1.2  # T effective field for N52 Halbach
    mu0 = 4 * math.pi * 1e-7
    k = 2 * math.pi / (spec.magnet_length_mm / 1000)
    g = spec.hover_gap_nominal_mm / 1000

    # Lift pressure per array
    P_lift = (B0 ** 2 / (2 * mu0)) * math.exp(-2 * k * g)
    # Estimate effective array area (all 4 arrays combined)
    array_area = (spec.magnet_length_mm / 1000) * (spec.magnet_width_mm / 1000) * 8
    total_area = array_area * spec.halbach_array_count
    lift_force = P_lift * total_area
    max_payload = lift_force / 9.81

    # Energy budget
    cruise_speed_ms = spec.cruise_speed_kmh / 3.6
    drag_force = 0.5 * 1.225 * 0.3 * 0.8 * cruise_speed_ms ** 2
    propulsion_power = drag_force * cruise_speed_ms
    levitation_power = 75.0  # W active stabilisation
    total_power = propulsion_power + levitation_power

    range_h = spec.battery_capacity_wh / total_power
    range_km = range_h * spec.cruise_speed_kmh

    # Solar contribution
    solar_power_peak = (spec.solar_panel_area_m2 * 1000
                        * spec.solar_panel_efficiency)

    # BOM cost
    bom = generate_bill_of_materials(spec)
    total_cost = sum(c.quantity * c.estimated_cost_usd for c in bom)

    return {
        "lift_force_n": round(lift_force, 1),
        "max_payload_kg": round(max_payload, 1),
        "cruise_drag_force_n": round(drag_force, 1),
        "propulsion_power_w": round(propulsion_power, 1),
        "total_system_power_w": round(total_power, 1),
        "theoretical_range_km": round(range_km, 1),
        "solar_peak_power_w": round(solar_power_peak, 1),
        "total_bom_cost_usd": round(total_cost, 2),
        "bom_item_count": len(bom),
    }


def generate_stl_manifest(spec: HoverBikeSpec) -> list[dict]:
    """Generate STL file manifest for 3D printing."""
    return [
        {
            "filename": "frame_assembly.stl",
            "description": "Main aerodynamic teardrop frame body",
            "print_time_hours": 48,
            "material": "CF-PLA",
            "infill_pct": 40,
            "layer_height_mm": 0.2,
            "supports": True,
            "dimensions_mm": f"{spec.frame_length_mm}x{spec.frame_width_mm}x{spec.frame_height_mm}",
            "weight_g": 2800,
        },
        {
            "filename": "magnet_housing.stl",
            "description": "Halbach array magnet housing with embedded pockets",
            "print_time_hours": 6,
            "material": "PETG",
            "infill_pct": 80,
            "layer_height_mm": 0.15,
            "supports": False,
            "dimensions_mm": "250x120x25",
            "weight_g": 340,
        },
        {
            "filename": "motor_stator.stl",
            "description": "Linear motor stator housing (wind coils after printing)",
            "print_time_hours": 8,
            "material": "ABS",
            "infill_pct": 60,
            "layer_height_mm": 0.15,
            "supports": True,
            "dimensions_mm": "180x80x60",
            "weight_g": 290,
        },
        {
            "filename": "battery_enclosure.stl",
            "description": "Integrated battery and BMS housing",
            "print_time_hours": 12,
            "material": "CF-PLA",
            "infill_pct": 50,
            "layer_height_mm": 0.2,
            "supports": False,
            "dimensions_mm": "350x200x80",
            "weight_g": 480,
        },
        {
            "filename": "control_pod.stl",
            "description": "Handlebar control pod with display cutout",
            "print_time_hours": 4,
            "material": "PLA",
            "infill_pct": 35,
            "layer_height_mm": 0.2,
            "supports": False,
            "dimensions_mm": "120x80x50",
            "weight_g": 145,
        },
        {
            "filename": "wheel_hub.stl",
            "description": "Motorised wheel hub adapter for hub motor integration",
            "print_time_hours": 5,
            "material": "CF-PLA",
            "infill_pct": 70,
            "layer_height_mm": 0.15,
            "supports": False,
            "dimensions_mm": "160x160x45",
            "weight_g": 210,
        },
    ]


def generate_full_design(output_dir: Path | None = None) -> dict:
    """
    Generate the complete hover bike design package.
    Returns a comprehensive design document.
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "models"
    output_dir.mkdir(parents=True, exist_ok=True)

    spec = HoverBikeSpec()
    metrics = compute_design_metrics(spec)
    bom = generate_bill_of_materials(spec)
    stl_manifest = generate_stl_manifest(spec)

    design = {
        "project": "Barrot Revolution Hover Bike",
        "version": "1.0",
        "generated_at": str(Path(__file__).stat().st_mtime),
        "spec": asdict(spec),
        "performance_metrics": metrics,
        "stl_manifest": stl_manifest,
        "bill_of_materials": [asdict(c) for c in bom],
        "assembly_phases": [
            "Phase 1: Print all STL components (est. 83 hours total print time)",
            "Phase 2: Assemble Halbach magnet arrays into housings",
            "Phase 3: Wire power system (battery + BMS + solar + supercap)",
            "Phase 4: Install linear motors and hub motors",
            "Phase 5: Mount control pod (RPi + IMU + sensors)",
            "Phase 6: Flash firmware, calibrate IMU and sensors",
            "Phase 7: Static levitation test (unloaded)",
            "Phase 8: Load test (incremental weight)",
            "Phase 9: Dynamic stability test (low speed)",
            "Phase 10: Full performance validation",
        ],
    }

    out_path = output_dir / "hover_bike_design.json"
    out_path.write_text(json.dumps(design, indent=2))
    print(f"Design package saved → {out_path}")

    # Print summary
    print(f"\n{'='*55}")
    print("HOVER BIKE DESIGN SUMMARY")
    print(f"{'='*55}")
    print(f"Max payload:     {metrics['max_payload_kg']:.1f} kg")
    print(f"Total power:     {metrics['total_system_power_w']:.0f} W")
    print(f"Range:           {metrics['theoretical_range_km']:.1f} km")
    print(f"Solar supplement:{metrics['solar_peak_power_w']:.0f} W peak")
    print(f"Estimated cost:  ${metrics['total_bom_cost_usd']:.0f} USD")
    print(f"STL files:       {len(stl_manifest)}")
    print(f"BOM items:       {metrics['bom_item_count']}")
    print(f"{'='*55}")

    return design


if __name__ == "__main__":
    design = generate_full_design()
    print("\nAssembly phases:")
    for i, phase in enumerate(design["assembly_phases"], 1):
        print(f"  {i:2d}. {phase}")
