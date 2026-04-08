"""
hover_bike_generator.py — Parametric 3D-printable hover bike design system.

Generates component specifications, assembly instructions, and STL-compatible
geometry data for a modular, 3D-printable magnetic levitation bike.

All dimensions are in millimetres unless otherwise stated.
All masses are in kilograms.
Physics calculations use SI units internally.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class FrameSpec:
    """Structural frame dimensions and material properties."""
    wheelbase_mm: float = 1_100.0          # distance between axle centres
    overall_length_mm: float = 1_600.0
    overall_width_mm: float = 600.0
    overall_height_mm: float = 350.0       # excluding rider
    wall_thickness_mm: float = 3.0         # FDM shell thickness
    infill_percent: float = 40.0           # recommended infill
    primary_material: str = "Carbon-fibre-reinforced PLA"
    stress_point_inserts: str = "M8 titanium heat-set inserts"
    target_mass_kg: float = 6.5            # frame only, without drivetrain
    safety_factor: float = 3.0

    def volume_estimate_cm3(self) -> float:
        """Rough envelope volume in cubic centimetres."""
        l = self.overall_length_mm / 10
        w = self.overall_width_mm / 10
        h = self.overall_height_mm / 10
        return l * w * h * (self.wall_thickness_mm / (self.overall_height_mm / 2)) * 1.4

    def print_time_hours(self, layer_height_mm: float = 0.2) -> float:
        """Rough FDM print-time estimate (hours)."""
        vol = self.volume_estimate_cm3()
        # empirical constant: ~8 cm³/h at 60 mm/s for a 0.4 mm nozzle
        rate = 8.0 * (0.2 / layer_height_mm)
        return vol / rate


@dataclass
class MaglevSpec:
    """Magnetic levitation system parameters."""
    hover_height_min_mm: float = 100.0
    hover_height_max_mm: float = 300.0
    nominal_hover_height_mm: float = 150.0
    total_rider_mass_kg: float = 100.0     # bike + rider
    gravity_ms2: float = 9.81
    halbach_array_poles: int = 8           # per side
    magnet_grade: str = "N52"
    magnet_dimensions_mm: tuple[float, float, float] = (50.0, 25.0, 10.0)  # L×W×H
    magnets_per_array: int = 16
    active_stabilisation_power_w: float = 75.0
    hall_sensors_count: int = 12
    coil_correction_turns: int = 200

    @property
    def required_lift_force_n(self) -> float:
        return self.total_rider_mass_kg * self.gravity_ms2

    @property
    def lift_force_per_magnet_n(self) -> float:
        total_magnets = self.magnets_per_array * 2  # both sides
        return self.required_lift_force_n / total_magnets

    def gap_to_lift_ratio(self) -> float:
        """Dimensionless ratio: nominal gap / magnet height."""
        return self.nominal_hover_height_mm / self.magnet_dimensions_mm[2]


@dataclass
class PropulsionSpec:
    """Hub-motor propulsion system parameters."""
    motor_type: str = "BLDC hub motor"
    rated_power_w: float = 750.0
    peak_power_w: float = 1_500.0
    efficiency_percent: float = 88.0
    max_speed_kmh: float = 50.0
    wheel_diameter_mm: float = 400.0
    motor_count: int = 2
    esc_model: str = "VESC 75/300"
    stator_poles: int = 14
    rotor_magnets: int = 16

    @property
    def max_torque_nm(self) -> float:
        r = (self.wheel_diameter_mm / 2) / 1000.0
        v = self.max_speed_kmh / 3.6
        omega = v / r
        power_w = self.rated_power_w * (self.efficiency_percent / 100)
        return power_w / omega if omega > 0 else 0.0

    @property
    def total_rated_power_w(self) -> float:
        return self.rated_power_w * self.motor_count


@dataclass
class PowerSpec:
    """Energy storage and power management parameters."""
    battery_chemistry: str = "LiFePO4 (lithium iron phosphate)"
    capacity_wh: float = 1_000.0
    nominal_voltage_v: float = 48.0
    max_discharge_rate_c: float = 3.0
    solar_panel_watt_peak: float = 150.0   # thin-film, roof/canopy
    kinetic_recovery_w: float = 80.0       # regenerative braking estimate
    bms_model: str = "Daly Smart BMS 48V"
    charge_time_hours: float = 3.0

    @property
    def capacity_ah(self) -> float:
        return self.capacity_wh / self.nominal_voltage_v

    @property
    def max_current_a(self) -> float:
        return self.capacity_ah * self.max_discharge_rate_c

    def range_km(self, avg_power_w: float = 300.0, speed_kmh: float = 30.0) -> float:
        """Estimate range in km at given average power and speed."""
        if avg_power_w <= 0:
            return 0.0
        hours = self.capacity_wh / avg_power_w
        return hours * speed_kmh


@dataclass
class ControlSpec:
    """Flight/stabilisation controller parameters."""
    controller: str = "Raspberry Pi 4B"
    imu_model: str = "MPU-9250 (9-DOF)"
    barometer_model: str = "BMP388"
    ultrasonic_sensors: int = 4            # ground clearance
    update_rate_hz: float = 200.0
    pid_kp: float = 1.2
    pid_ki: float = 0.05
    pid_kd: float = 0.08
    firmware: str = "Custom Python stabilisation loop (open-source)"
    failsafe: str = "Soft-land on sensor fault; hard brake on comm loss"


@dataclass
class HoverBikeSpec:
    """Complete hover bike specification."""
    name: str = "Barrot HoverBike MK-I"
    version: str = "1.0.0"
    frame: FrameSpec = field(default_factory=FrameSpec)
    maglev: MaglevSpec = field(default_factory=MaglevSpec)
    propulsion: PropulsionSpec = field(default_factory=PropulsionSpec)
    power: PowerSpec = field(default_factory=PowerSpec)
    control: ControlSpec = field(default_factory=ControlSpec)
    generated_at: float = field(default_factory=time.time)

    # Derived performance metrics ----------------------------------------

    @property
    def total_mass_kg(self) -> float:
        return (
            self.frame.target_mass_kg
            + 2.0   # maglev array housing
            + 8.0   # two hub motors + wheels
            + (self.power.capacity_wh / 100)  # ~10 kg for 1000 Wh LiFePO4
            + 1.5   # control electronics
        )

    @property
    def avg_cruise_power_w(self) -> float:
        return (
            self.maglev.active_stabilisation_power_w
            + self.propulsion.rated_power_w * 0.35  # ~35 % rated at cruise
        )

    @property
    def range_km(self) -> float:
        return self.power.range_km(
            avg_power_w=self.avg_cruise_power_w,
            speed_kmh=30.0,
        )

    @property
    def manufacturing_cost_usd(self) -> dict[str, float]:
        return {
            "Frame (filament + inserts)": 180.0,
            "Neodymium magnets (N52)": 320.0,
            "Hall sensors + coils": 95.0,
            "Hub motors (×2)": 440.0,
            "ESC controllers (×2)": 200.0,
            "LiFePO4 battery pack": 650.0,
            "Solar thin-film panel": 120.0,
            "BMS + charge controller": 80.0,
            "Raspberry Pi + IMU + sensors": 90.0,
            "Wiring + connectors": 60.0,
            "Fasteners + misc": 55.0,
        }

    @property
    def total_cost_usd(self) -> float:
        return sum(self.manufacturing_cost_usd.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "generated_at": self.generated_at,
            "frame": asdict(self.frame),
            "maglev": {
                **asdict(self.maglev),
                "required_lift_force_n": self.maglev.required_lift_force_n,
                "lift_force_per_magnet_n": self.maglev.lift_force_per_magnet_n,
            },
            "propulsion": {
                **asdict(self.propulsion),
                "max_torque_nm": self.propulsion.max_torque_nm,
                "total_rated_power_w": self.propulsion.total_rated_power_w,
            },
            "power": {
                **asdict(self.power),
                "capacity_ah": self.power.capacity_ah,
            },
            "control": asdict(self.control),
            "derived": {
                "total_mass_kg": self.total_mass_kg,
                "avg_cruise_power_w": self.avg_cruise_power_w,
                "range_km": self.range_km,
                "manufacturing_cost_usd": self.manufacturing_cost_usd,
                "total_cost_usd": self.total_cost_usd,
            },
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# ---------------------------------------------------------------------------
# Component geometry helpers (simplified bounding-box representations)
# ---------------------------------------------------------------------------

def _box_vertices(
    cx: float, cy: float, cz: float,
    lx: float, ly: float, lz: float,
) -> list[list[float]]:
    """Return the 8 corner vertices of an axis-aligned box."""
    hx, hy, hz = lx / 2, ly / 2, lz / 2
    return [
        [cx - hx, cy - hy, cz - hz],
        [cx + hx, cy - hy, cz - hz],
        [cx + hx, cy + hy, cz - hz],
        [cx - hx, cy + hy, cz - hz],
        [cx - hx, cy - hy, cz + hz],
        [cx + hx, cy - hy, cz + hz],
        [cx + hx, cy + hy, cz + hz],
        [cx - hx, cy + hy, cz + hz],
    ]


def generate_component_geometry(spec: HoverBikeSpec) -> dict[str, Any]:
    """
    Return a dictionary of named components, each with simplified geometry
    suitable for downstream STL generation or visualisation.
    """
    f = spec.frame

    components: dict[str, Any] = {
        "main_frame": {
            "type": "box",
            "material": f.primary_material,
            "vertices": _box_vertices(
                0, 0, 0,
                f.overall_length_mm, f.overall_width_mm, f.overall_height_mm,
            ),
            "wall_thickness_mm": f.wall_thickness_mm,
            "infill_percent": f.infill_percent,
            "print_orientation": "flat",
        },
        "magnet_housing_front": {
            "type": "box",
            "material": "Nylon PA12 (SLS)",
            "vertices": _box_vertices(
                f.wheelbase_mm / 2, 0, -(f.overall_height_mm / 2 + 40),
                300.0, f.overall_width_mm - 20, 40.0,
            ),
            "embedded_parts": "16× N52 neodymium magnets",
        },
        "magnet_housing_rear": {
            "type": "box",
            "material": "Nylon PA12 (SLS)",
            "vertices": _box_vertices(
                -(f.wheelbase_mm / 2), 0, -(f.overall_height_mm / 2 + 40),
                300.0, f.overall_width_mm - 20, 40.0,
            ),
            "embedded_parts": "16× N52 neodymium magnets",
        },
        "wheel_hub_left": {
            "type": "cylinder",
            "material": "ABS+CF",
            "centre": [-(f.wheelbase_mm / 2), -(f.overall_width_mm / 2 + 30), 0],
            "radius_mm": spec.propulsion.wheel_diameter_mm / 2,
            "height_mm": 60.0,
            "embedded_parts": "BLDC hub motor",
        },
        "wheel_hub_right": {
            "type": "cylinder",
            "material": "ABS+CF",
            "centre": [-(f.wheelbase_mm / 2), (f.overall_width_mm / 2 + 30), 0],
            "radius_mm": spec.propulsion.wheel_diameter_mm / 2,
            "height_mm": 60.0,
            "embedded_parts": "BLDC hub motor",
        },
        "battery_enclosure": {
            "type": "box",
            "material": "PETG",
            "vertices": _box_vertices(0, 0, 30, 500.0, 200.0, 120.0),
            "embedded_parts": f"{spec.power.capacity_wh} Wh LiFePO4 cells + BMS",
        },
        "control_pod": {
            "type": "box",
            "material": "PETG",
            "vertices": _box_vertices(
                f.overall_length_mm / 2 - 100, 0, f.overall_height_mm / 2,
                200.0, 150.0, 80.0,
            ),
            "embedded_parts": "Raspberry Pi 4B, IMU, barometer, telemetry",
        },
        "solar_canopy": {
            "type": "flat_panel",
            "material": "Thin-film amorphous silicon on 3D-printed PETG frame",
            "vertices": _box_vertices(0, 0, f.overall_height_mm, 800.0, 400.0, 5.0),
            "watt_peak": spec.power.solar_panel_watt_peak,
        },
    }
    return components


# ---------------------------------------------------------------------------
# Assembly instructions
# ---------------------------------------------------------------------------

ASSEMBLY_STEPS: list[dict[str, Any]] = [
    {
        "step": 1,
        "title": "Print & prepare frame sections",
        "description": (
            "Print the main frame in sections using CF-PLA at 40 % gyroid infill. "
            "Install M8 titanium heat-set inserts at all marked stress points using a "
            "soldering iron set to 200 °C."
        ),
        "tools": ["FDM printer (300×300 mm+ bed)", "Soldering iron", "M8 tap"],
        "duration_hours": 18,
        "safety": "Wear gloves when handling carbon-fibre dust from post-processing.",
    },
    {
        "step": 2,
        "title": "Assemble Halbach magnet arrays",
        "description": (
            "Press N52 neodymium magnets into the SLS-printed housings following the "
            "Halbach pole sequence (0°, 90°, 180°, 270°). Use epoxy to secure. "
            "Verify field orientation with a Gaussmeter before proceeding."
        ),
        "tools": ["Gaussmeter", "Two-part epoxy (JB Weld)", "Non-magnetic assembly jig"],
        "duration_hours": 4,
        "safety": (
            "Keep magnets away from electronics and pacemakers. "
            "Use anti-crush finger guards — N52 magnets > 50 mm are extremely powerful."
        ),
    },
    {
        "step": 3,
        "title": "Install hub motors & wheels",
        "description": (
            "Press-fit BLDC hub motors into the 3D-printed wheel hubs. Secure with M6 bolts. "
            "Mount wheels on the rear axle mounts. Thread motor phase wires through the frame channels."
        ),
        "tools": ["M6 hex key", "Torque wrench (25 Nm)", "Phase wire labels"],
        "duration_hours": 2,
        "safety": "Ensure wheel nuts are torqued correctly before powering up.",
    },
    {
        "step": 4,
        "title": "Install battery pack & BMS",
        "description": (
            "Mount the LiFePO4 cell pack inside the battery enclosure. "
            "Connect cells in 15S4P configuration to achieve 48 V nominal (15 × 3.2 V = 48 V). "
            "Wire BMS according to Daly datasheet. Verify cell voltage balance."
        ),
        "tools": ["Spot welder / nickel strip", "Multimeter", "BMS programmer cable"],
        "duration_hours": 5,
        "safety": (
            "Never short-circuit lithium cells. "
            "Wear insulated gloves. Have a Class D fire extinguisher nearby."
        ),
    },
    {
        "step": 5,
        "title": "Mount active stabilisation coils & Hall sensors",
        "description": (
            "Wind 200-turn correction coils and epoxy them inside the magnet housing gaps. "
            "Mount Hall effect sensors (AH3503) at the four corners of each magnet array. "
            "Connect to the Raspberry Pi via I²C."
        ),
        "tools": ["Coil winding jig", "Multimeter (resistance check)", "I²C analyser"],
        "duration_hours": 6,
        "safety": "Ensure coil connections are insulated before powering on.",
    },
    {
        "step": 6,
        "title": "Install control electronics & wiring",
        "description": (
            "Mount Raspberry Pi 4B, MPU-9250 IMU, BMP388 barometer and ultrasonic sensors "
            "into the control pod. Route all cables through 3D-printed conduit channels. "
            "Connect VESC ESCs to hub motors and to the Raspberry Pi via USB/CAN bus."
        ),
        "tools": ["Raspberry Pi setup guide", "CAN bus analyser", "Cable ties"],
        "duration_hours": 3,
        "safety": "Power off battery before connecting any electronics.",
    },
    {
        "step": 7,
        "title": "Flash firmware & calibrate sensors",
        "description": (
            "Flash the stabilisation firmware to the Raspberry Pi. "
            "Calibrate the IMU on a level surface using the provided calibration script. "
            "Set PID gains via the configuration file. "
            "Test each sensor independently before first hover."
        ),
        "tools": ["Laptop with SSH access", "Level surface", "USB-C cable"],
        "duration_hours": 2,
        "safety": "Perform first power-on test with bike secured on a stand.",
    },
    {
        "step": 8,
        "title": "First hover test (tethered)",
        "description": (
            "With the bike secured by safety tethers, gradually increase stabilisation power. "
            "Observe hover gap. Adjust PID Kp until stable levitation is achieved at 15 cm. "
            "Check for oscillations — reduce Kd if present."
        ),
        "tools": ["Safety tethers", "Ruler / gap gauge", "Laptop for live PID tuning"],
        "duration_hours": 3,
        "safety": (
            "Keep hands clear of magnet arrays during powered test. "
            "Have emergency cut-off switch accessible."
        ),
    },
    {
        "step": 9,
        "title": "Propulsion system commissioning",
        "description": (
            "With hover stable, test each hub motor at 10 % throttle. "
            "Verify correct rotation direction. "
            "Gradually increase throttle and observe handling. "
            "Adjust VESC motor parameters for smooth acceleration."
        ),
        "tools": ["VESC Tool (laptop)", "Open space ≥ 10 m", "Safety helmet"],
        "duration_hours": 2,
        "safety": "Wear protective gear. Keep bystanders 10 m away during first rides.",
    },
    {
        "step": 10,
        "title": "Solar panel & kinetic recovery integration",
        "description": (
            "Attach solar canopy frame to the top of the control pod. "
            "Wire thin-film solar cells to the MPPT charge controller input. "
            "Enable regenerative braking in VESC firmware. "
            "Verify charging current during braking with a clamp meter."
        ),
        "tools": ["MPPT charge controller", "Clamp meter", "Crimping tool"],
        "duration_hours": 2,
        "safety": "Do not exceed BMS maximum charge current (0.5 C = 5 A).",
    },
]


# ---------------------------------------------------------------------------
# Generator entry point
# ---------------------------------------------------------------------------

class HoverBikeGenerator:
    """
    Orchestrates the generation of all hover bike design artefacts.

    Parameters
    ----------
    output_dir:
        Directory where generated files will be written.
    spec:
        Optional custom specification; uses defaults if not provided.
    """

    def __init__(
        self,
        output_dir: Path | str = Path("hover_bike_revolution"),
        spec: HoverBikeSpec | None = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.spec = spec or HoverBikeSpec()

    def generate_all(self) -> dict[str, Path]:
        """Generate all design artefacts and return a map of name → path."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        outputs: dict[str, Path] = {}

        outputs["spec_json"] = self._write_spec()
        outputs["component_geometry"] = self._write_geometry()
        outputs["assembly_guide"] = self._write_assembly()
        outputs["bom"] = self._write_bom()

        return outputs

    # ------------------------------------------------------------------

    def _write_spec(self) -> Path:
        path = self.output_dir / "hover_bike_spec.json"
        path.write_text(self.spec.to_json(), encoding="utf-8")
        return path

    def _write_geometry(self) -> Path:
        geom = generate_component_geometry(self.spec)
        path = self.output_dir / "component_geometry.json"
        path.write_text(json.dumps(geom, indent=2), encoding="utf-8")
        return path

    def _write_assembly(self) -> Path:
        lines = [
            f"# {self.spec.name} — Assembly Guide\n",
            "Generated by hover_bike_generator.py\n",
            f"Version: {self.spec.version}  |  "
            f"Total mass: {self.spec.total_mass_kg:.1f} kg  |  "
            f"Est. range: {self.spec.range_km:.0f} km  |  "
            f"Est. cost: ${self.spec.total_cost_usd:,.0f} USD\n\n",
        ]
        for step in ASSEMBLY_STEPS:
            lines.append(f"## Step {step['step']}: {step['title']}\n")
            lines.append(f"{step['description']}\n\n")
            lines.append(f"**Tools required:** {', '.join(step['tools'])}\n")
            lines.append(f"**Estimated time:** {step['duration_hours']} hours\n")
            lines.append(f"**⚠️ Safety:** {step['safety']}\n\n")
            lines.append("---\n\n")

        path = self.output_dir / "assembly_guide.md"
        path.write_text("".join(lines), encoding="utf-8")
        return path

    def _write_bom(self) -> Path:
        rows = ["# Bill of Materials\n\n", "| Component | Est. Cost (USD) |\n", "|-----------|----------------:|\n"]
        total = 0.0
        for item, cost in self.spec.manufacturing_cost_usd.items():
            rows.append(f"| {item} | ${cost:,.2f} |\n")
            total += cost
        rows.append(f"| **TOTAL** | **${total:,.2f}** |\n")

        path = self.output_dir / "bill_of_materials.md"
        path.write_text("".join(rows), encoding="utf-8")
        return path


if __name__ == "__main__":
    gen = HoverBikeGenerator(output_dir=Path("hover_bike_revolution"))
    outputs = gen.generate_all()
    for name, path in outputs.items():
        print(f"  {name:30s} → {path}")
