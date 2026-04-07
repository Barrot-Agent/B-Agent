"""
assembly_guide_generator.py - Complete Build Documentation Generator

Generates step-by-step assembly instructions, part lists, tool requirements,
troubleshooting guides, and safety procedures for the hover bike.
"""

import json
from pathlib import Path
from dataclasses import dataclass


@dataclass
class AssemblyStep:
    step_number: int
    phase: str
    title: str
    description: str
    parts_needed: list[str]
    tools_needed: list[str]
    time_minutes: int
    safety_notes: list[str]
    tips: list[str]


def generate_assembly_steps() -> list[AssemblyStep]:
    """Generate complete step-by-step assembly instructions."""
    return [
        # Phase 1: Frame Assembly
        AssemblyStep(
            1, "Frame Assembly", "Print and post-process frame sections",
            "Print all 4 frame sections using CF-PLA at 0.2mm layer height, 40% gyroid infill. "
            "Remove supports carefully with flush cutters. Sand joining surfaces to 400 grit.",
            ["frame_assembly.stl (×4 sections)", "CF-PLA filament (×3 spools)"],
            ["3D printer", "flush cutters", "sandpaper 200/400 grit"],
            180, ["Wear gloves - CF-PLA splinters are sharp"],
            ["Print sections vertically for better layer adhesion on stress points"],
        ),
        AssemblyStep(
            2, "Frame Assembly", "Install titanium heat-set inserts",
            "Using soldering iron at 200°C, press M8 titanium inserts into all mounting holes. "
            "Inserts should be flush or 0.2mm below surface.",
            ["Titanium M8 insert kit", "Frame sections"],
            ["Soldering iron (200°C)", "Insert driver bit"],
            30, ["Hot inserts can cause burns - use heat-resistant gloves"],
            ["Heat insert until just flush, then remove iron. Don't over-push."],
        ),
        AssemblyStep(
            3, "Frame Assembly", "Join frame sections",
            "Align front and rear frame halves. Apply structural epoxy (JB Weld) to joint faces. "
            "Bolt together with M8×50mm titanium bolts, torque to 15 N·m.",
            ["Main frame sections ×4", "M8×50 titanium bolts ×16", "JB Weld structural epoxy"],
            ["M8 hex key", "torque wrench", "clamps"],
            45, ["Allow epoxy to cure 24h before applying loads"],
            ["Check alignment with spirit level before epoxy sets"],
        ),

        # Phase 2: Magnet System
        AssemblyStep(
            4, "Magnetic System", "Print and inspect magnet housings",
            "Print 4 magnet housings in PETG at 0.15mm, 80% infill. "
            "Verify all magnet pockets are within ±0.1mm tolerance using digital calipers.",
            ["magnet_housing.stl ×4", "PETG filament"],
            ["3D printer", "digital calipers"],
            90, ["PETG can warp - use enclosed printer or draft shield"],
            ["Print orientation: pockets facing up to avoid support in critical areas"],
        ),
        AssemblyStep(
            5, "Magnetic System", "Assemble Halbach arrays",
            "Insert N52 neodymium magnets into housings following Halbach configuration: "
            "rotate each magnet 90° clockwise from previous. "
            "Sequence: [N↑] [N→] [N↓] [N←] repeat. "
            "Lock with non-magnetic stainless screws.",
            ["N52 magnets (×64 total, 16 per housing)", "M3×6 SS screws ×32"],
            ["plastic mallet", "M3 screwdriver", "magnet safety gloves"],
            60,
            ["DANGER: Neodymium magnets can cause severe pinch injuries",
             "Keep magnets away from electronics and credit cards",
             "Never place two Halbach arrays face-to-face without fixtures"],
            ["Mark each magnet orientation before inserting",
             "Use plastic tweezers near sensor boards"],
        ),
        AssemblyStep(
            6, "Magnetic System", "Mount arrays to frame",
            "Bolt 4 magnet arrays to underside of frame at marked positions (FL, FR, RL, RR). "
            "Arrays should be co-planar within ±1mm. Shim if needed.",
            ["Assembled magnet housings ×4", "M8×20 bolts ×16", "aluminium shims"],
            ["M8 hex key", "feeler gauge", "straight edge 500mm"],
            45,
            ["Check array-to-ground clearance: minimum 5mm above ground surface"],
            ["Use feeler gauge to verify co-planarity before final tighten"],
        ),

        # Phase 3: Power System
        AssemblyStep(
            7, "Power System", "Install battery enclosure",
            "Mount 3D-printed battery enclosure to frame centre (lowest point for CoG). "
            "Install rubber vibration isolators at 4 mounting points.",
            ["battery_enclosure.stl", "vibration isolators ×4", "M6 bolts ×8"],
            ["M6 hex key", "drill for pilot holes if needed"],
            20, ["Ensure enclosure drains are pointed down (if included)"],
            ["Low CoG improves stability - keep battery as low as possible"],
        ),
        AssemblyStep(
            8, "Power System", "Wire power system",
            "Install battery → BMS → main bus bar wiring. "
            "Use 10AWG silicone wire for main power runs. "
            "All positive wires: red. All ground: black. "
            "Install 40A main fuse within 15cm of battery positive terminal.",
            ["LiPo 48V 10Ah battery", "13S BMS", "40A fuse", "Anderson connectors",
             "10AWG silicone wire"],
            ["wire stripper", "crimping tool", "multimeter"],
            90,
            ["CRITICAL: Verify polarity before connecting battery",
             "Install fuse BEFORE any other connections",
             "LiPo batteries can cause fire if shorted"],
            ["Pre-tin all wire ends before crimping",
             "Use heat shrink on all exposed connections"],
        ),
        AssemblyStep(
            9, "Power System", "Install solar panel and DC-DC converter",
            "Mount thin-film solar panel to top of frame. "
            "Connect to 48V charge controller input. "
            "Install DC-DC 48V→12V converter for electronics power rail.",
            ["Solar panel 100W", "MPPT charge controller", "DC-DC converter",
             "mounting tape + cable ties"],
            ["screwdriver", "multimeter"],
            30, ["Verify solar polarity before connecting to charge controller"],
            ["Route solar cables away from moving parts"],
        ),
        AssemblyStep(
            10, "Power System", "Install supercapacitor bank",
            "Mount supercapacitor bank near motor controllers (minimise wire length). "
            "Connect in parallel with main battery bus via balancing circuit.",
            ["Supercapacitor bank 16V 100F", "balancing board"],
            ["screwdriver", "soldering iron"],
            20,
            ["Supercapacitors hold charge - discharge before working on circuit"],
            ["Keep supercap wires <30cm for minimum inductance"],
        ),

        # Phase 4: Propulsion
        AssemblyStep(
            11, "Propulsion", "Install hub motors",
            "Press hub motors into 3D-printed wheel hub adapters. "
            "Bolt adapter to wheel with M6×20 bolts at 6-point pattern. "
            "Torque to 10 N·m. Check for <0.3mm runout.",
            ["Hub motors ×2", "wheel_hub.stl ×2", "M6×20 bolts ×12"],
            ["M6 hex key", "torque wrench", "dial indicator for runout"],
            45, ["Support motor weight during installation - don't stress cable exit"],
            ["Apply Loctite 243 to hub adapter bolts"],
        ),
        AssemblyStep(
            12, "Propulsion", "Wire motor controllers (ESC)",
            "Connect each motor phase to ESC (any order - adjust in firmware). "
            "Connect ESC power to main bus. Connect ESC signal to Raspberry Pi GPIO.",
            ["ESC ×2", "3-phase motor cable ×2"],
            ["soldering iron", "heat shrink", "multimeter"],
            45,
            ["Phase current can exceed 60A at peak - verify all connections are crimped"],
            ["Test each ESC in isolation before connecting both"],
        ),

        # Phase 5: Control System
        AssemblyStep(
            13, "Control System", "Mount Raspberry Pi and sensors",
            "Install Raspberry Pi in control pod with standoffs. "
            "Mount IMU (MPU-6050) at Centre of Gravity of frame. "
            "Mount 4 ultrasonic sensors at corners (pointing down). "
            "Mount Hall effect sensors adjacent to each magnet array.",
            ["Raspberry Pi 4", "MPU-6050 ×2", "HC-SR04 ×4", "A1302 Hall sensors ×8",
             "control_pod.stl"],
            ["M2.5 screwdriver", "hot glue gun"],
            60,
            ["IMU must be rigidly mounted - vibration will corrupt readings",
             "Keep IMU away from magnets (>100mm)"],
            ["Level the RPi board before securing to ensure IMU alignment"],
        ),
        AssemblyStep(
            14, "Control System", "Flash and configure firmware",
            "Install Raspberry Pi OS Lite. Copy control_firmware.py to /home/pi/. "
            "Install dependencies: pip install RPi.GPIO smbus. "
            "Configure I2C in raspi-config. Flash Arduino coprocessor with sensor_fusion.ino.",
            ["SD card with RPi OS", "SSH access or keyboard/display"],
            ["computer with SSH client", "USB-serial adapter for Arduino"],
            90,
            ["Test firmware on bench BEFORE mounting on vehicle"],
            ["Enable I2C and SPI in raspi-config before trying sensor libraries"],
        ),
        AssemblyStep(
            15, "Control System", "Calibrate sensors",
            "Run IMU calibration: place bike on flat surface, run calibration script 60s. "
            "Zero ultrasonic sensors at known height (use 15mm block). "
            "Calibrate Hall sensors with no-load (record zero-current offset).",
            ["15mm calibration block"],
            ["SSH terminal", "digital level"],
            30, ["Calibrate with NO magnets energised for Hall sensor zero"],
            ["Save calibration values to /etc/barrot/calibration.json"],
        ),

        # Phase 6: Testing
        AssemblyStep(
            16, "Testing", "Static levitation test",
            "With bike unloaded (no rider), power on control system. "
            "Enable levitation at low power. Verify stable hover at 10-20mm. "
            "Check all 4 corner heights are equal (±2mm).",
            ["All assembled components"],
            ["safety glasses", "metre rule"],
            30,
            ["Keep hands clear of magnet arrays during first power-on",
             "Have emergency stop ready (main fuse pull)"],
            ["Start at 20% coil power, increase gradually"],
        ),
        AssemblyStep(
            17, "Testing", "Load testing (incremental)",
            "Add weight in 10kg increments (use sandbags). "
            "Verify system holds height and remains stable at each increment. "
            "Record current draw and height at each load step.",
            ["Sandbags 10kg each", "current clamp meter"],
            ["current clamp meter", "notebook for data"],
            60,
            ["Do not exceed 90kg during initial testing",
             "Stop test if height drops below 8mm"],
            ["Log all data - useful for PID tuning"],
        ),
        AssemblyStep(
            18, "Testing", "Dynamic stability and propulsion test",
            "With rider at low speed (5 km/h), verify attitude control maintains stability. "
            "Gradually increase to 20 km/h. Check for oscillations or twitchiness.",
            ["Full assembled hover bike", "safety gear: helmet + pads"],
            ["open flat surface 50m minimum"],
            60,
            ["WEAR FULL PROTECTIVE GEAR for first ride test",
             "Have a safety observer present",
             "Test near walls/barriers for safety",
             "Emergency: lean forward to stop → regenerative braking engages"],
            ["Small test area first - avoid open roads until fully validated"],
        ),
    ]


def generate_tool_list() -> list[dict]:
    """Comprehensive tool requirements."""
    return [
        {"tool": "3D Printer (300mm+ bed)", "essential": True,
         "note": "Enclosed for ABS/Nylon; hardened nozzle for CF-PLA"},
        {"tool": "Digital Calipers (0.01mm)", "essential": True,
         "note": "Critical for magnet housing tolerance check"},
        {"tool": "Multimeter (true RMS)", "essential": True,
         "note": "For all electrical testing"},
        {"tool": "Soldering Iron (adjustable temp)", "essential": True,
         "note": "For heat inserts and wire work"},
        {"tool": "Crimping Tool (10AWG)", "essential": True,
         "note": "Anderson connector assembly"},
        {"tool": "Torque Wrench (5-30 N·m)", "essential": True,
         "note": "Critical for structural bolts"},
        {"tool": "Hex Key Set (M2.5-M8)", "essential": True, "note": ""},
        {"tool": "Heat Gun", "essential": True,
         "note": "Heat shrink and frame post-processing"},
        {"tool": "Current Clamp Meter (60A+)", "essential": True,
         "note": "Safety: verify current draw"},
        {"tool": "SSH-capable Computer", "essential": True,
         "note": "Firmware programming"},
        {"tool": "Dial Indicator", "essential": False,
         "note": "Motor hub runout verification (<0.3mm)"},
        {"tool": "Oscilloscope", "essential": False,
         "note": "Advanced sensor debugging"},
        {"tool": "3D Printer Enclosure", "essential": False,
         "note": "Required for ABS components"},
    ]


def generate_troubleshooting_guide() -> list[dict]:
    """Common issues and solutions."""
    return [
        {
            "symptom": "Hover height oscillates / hunting",
            "cause": "PID gains too aggressive (Kp too high)",
            "solution": "Reduce Kp by 20%. Increase Kd slightly. "
                        "Check IMU is rigidly mounted.",
        },
        {
            "symptom": "System fails to lift at target height",
            "cause": "Halbach arrays not co-planar OR magnet orientation wrong",
            "solution": "Re-verify array mounting with straight edge. "
                        "Check Halbach sequence: each magnet 90° from previous.",
        },
        {
            "symptom": "Motor runs hot (>70°C after 10 min)",
            "cause": "ESC current limit too high OR poor motor cooling",
            "solution": "Reduce ESC current limit by 10A. "
                        "Verify motor can spin freely (no mechanical friction).",
        },
        {
            "symptom": "Battery drains in <10km",
            "cause": "Levitation taking excessive power OR battery health degraded",
            "solution": "Log coil currents - if >60% continuously, "
                        "re-tune height PID. Check battery voltage under load.",
        },
        {
            "symptom": "IMU drift causing tilt over time",
            "cause": "Gyroscope drift (normal) - alpha value too high",
            "solution": "Reduce complementary filter alpha from 0.98 to 0.95. "
                        "Recalibrate IMU on level surface.",
        },
        {
            "symptom": "Hall sensors reading incorrectly",
            "cause": "Sensor too close to permanent magnets",
            "solution": "Move Hall sensors to side of Halbach array, "
                        "not underneath. Minimum 15mm from magnet face.",
        },
    ]


def generate_safety_procedures() -> list[str]:
    """Safety procedures for build and operation."""
    return [
        "MAGNETS: Always handle N52 neodymium magnets with gloves. Keep >300mm from pacemakers.",
        "BATTERY: Never short LiPo terminals. Store at 50% SOC if unused >1 week.",
        "ELECTRICAL: Always disconnect battery before working on circuits.",
        "FIRMWARE: Test all code on bench before installing in vehicle.",
        "RIDING: Wear helmet and full protective gear at all times.",
        "SPEED: Do not exceed 20 km/h until >5 hours of ride time logged.",
        "SURFACE: Only operate on smooth flat surfaces (concrete/asphalt).",
        "OBSERVER: Never ride without a safety observer present.",
        "EMERGENCY: Emergency stop = cut main fuse. Location: battery enclosure left side.",
        "FIRE: Keep Class D / CO2 extinguisher nearby during first power tests.",
    ]


def run_assembly_guide(output_dir: Path | None = None) -> dict:
    """Generate and save complete assembly guide."""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "docs"
    output_dir.mkdir(parents=True, exist_ok=True)

    steps = generate_assembly_steps()
    tools = generate_tool_list()
    troubleshooting = generate_troubleshooting_guide()
    safety = generate_safety_procedures()

    total_time = sum(s.time_minutes for s in steps)

    print("=" * 55)
    print("BARROT HOVER BIKE — ASSEMBLY GUIDE GENERATOR")
    print("=" * 55)
    print(f"\nTotal steps:      {len(steps)}")
    print(f"Total build time: ~{total_time // 60}h {total_time % 60}m")
    print(f"Tool count:       {len(tools)}")
    print(f"Safety rules:     {len(safety)}")

    guide = {
        "title": "Barrot Revolution Hover Bike - Complete Assembly Guide",
        "version": "1.0",
        "total_steps": len(steps),
        "total_time_minutes": total_time,
        "phases": list({s.phase for s in steps}),
        "steps": [
            {
                "number": s.step_number,
                "phase": s.phase,
                "title": s.title,
                "description": s.description,
                "parts": s.parts_needed,
                "tools": s.tools_needed,
                "time_min": s.time_minutes,
                "safety": s.safety_notes,
                "tips": s.tips,
            }
            for s in steps
        ],
        "tools": tools,
        "troubleshooting": troubleshooting,
        "safety_procedures": safety,
    }

    out_json = output_dir / "assembly_guide.json"
    out_json.write_text(json.dumps(guide, indent=2))
    print(f"\nAssembly guide saved → {out_json}")

    # Generate simple markdown version
    md_lines = [
        "# Barrot Revolution Hover Bike — Assembly Guide\n",
        f"**Total build time:** ~{total_time//60}h  ",
        f"**Total steps:** {len(steps)}\n",
        "\n## ⚠️ Safety Procedures\n",
    ]
    for s in safety:
        md_lines.append(f"- {s}")
    md_lines.append("\n## 🔧 Assembly Steps\n")
    for s in steps:
        md_lines.append(f"\n### Step {s.step_number}: {s.title}")
        md_lines.append(f"**Phase:** {s.phase} | **Time:** {s.time_minutes} min\n")
        md_lines.append(s.description)
    md_lines.append("\n## 🔍 Troubleshooting\n")
    for t in troubleshooting:
        md_lines.append(f"\n**{t['symptom']}**  ")
        md_lines.append(f"Cause: {t['cause']}  ")
        md_lines.append(f"Fix: {t['solution']}")

    out_md = output_dir / "assembly_guide.md"
    out_md.write_text("\n".join(md_lines))
    print(f"Markdown guide saved → {out_md}")

    return guide


if __name__ == "__main__":
    guide = run_assembly_guide()
    print(f"\nBuild phases: {guide['phases']}")
    print(f"Total time: {guide['total_time_minutes']//60}h {guide['total_time_minutes']%60}m")
