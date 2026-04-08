"""
assembly_guide_generator.py — Generates complete build documentation for the hover bike.

Produces a detailed step-by-step assembly guide, parts list, tool requirements,
troubleshooting guide, and safety procedures in Markdown format.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Parts list
# ---------------------------------------------------------------------------

PARTS_LIST: list[dict[str, Any]] = [
    # Magnets & levitation
    {"part": "N52 Neodymium magnets 50×25×10 mm", "qty": 64, "unit_cost_usd": 5.00, "supplier": "K&J Magnetics / eBay", "category": "maglev"},
    {"part": "AH3503 Hall effect sensors", "qty": 12, "unit_cost_usd": 1.20, "supplier": "Mouser / LCSC", "category": "maglev"},
    {"part": "Correction coil wire (0.8 mm, 10 m)", "qty": 4, "unit_cost_usd": 8.00, "supplier": "Amazon / local", "category": "maglev"},
    {"part": "Epoxy adhesive (JB Weld)", "qty": 2, "unit_cost_usd": 12.00, "supplier": "Hardware store", "category": "maglev"},

    # Motors & propulsion
    {"part": "BLDC hub motor 750 W, 48 V", "qty": 2, "unit_cost_usd": 220.00, "supplier": "QSMotor / AliExpress", "category": "propulsion"},
    {"part": "VESC 75/300 ESC", "qty": 2, "unit_cost_usd": 100.00, "supplier": "Trampa Boards / Flipsky", "category": "propulsion"},
    {"part": "Motor phase wire 8 AWG (3 m)", "qty": 4, "unit_cost_usd": 6.00, "supplier": "Amazon", "category": "propulsion"},

    # Battery & power
    {"part": "LiFePO4 prismatic cell 3.2 V 20 Ah", "qty": 60, "unit_cost_usd": 8.00, "supplier": "CALB / EVE / AliExpress", "category": "power"},
    {"part": "Daly Smart BMS 48 V 100 A", "qty": 1, "unit_cost_usd": 55.00, "supplier": "AliExpress / Daly", "category": "power"},
    {"part": "MPPT solar charge controller 40 A", "qty": 1, "unit_cost_usd": 35.00, "supplier": "Victron / Renogy", "category": "power"},
    {"part": "Thin-film CIGS solar module 150 Wp", "qty": 1, "unit_cost_usd": 120.00, "supplier": "GlobalSolar / Amazon", "category": "power"},
    {"part": "XT90 anti-spark connectors", "qty": 4, "unit_cost_usd": 4.00, "supplier": "Hobbyking / Amazon", "category": "power"},
    {"part": "8 AWG silicone wire (10 m)", "qty": 1, "unit_cost_usd": 18.00, "supplier": "Amazon", "category": "power"},
    {"part": "100 A fuse + holder", "qty": 2, "unit_cost_usd": 8.00, "supplier": "Amazon", "category": "power"},

    # Control electronics
    {"part": "Raspberry Pi 4B (4 GB)", "qty": 1, "unit_cost_usd": 55.00, "supplier": "Adafruit / RS Components", "category": "control"},
    {"part": "MPU-9250 IMU breakout", "qty": 2, "unit_cost_usd": 8.00, "supplier": "Adafruit / SparkFun", "category": "control"},
    {"part": "BMP388 barometer breakout", "qty": 1, "unit_cost_usd": 7.00, "supplier": "Adafruit", "category": "control"},
    {"part": "HC-SR04 ultrasonic sensor", "qty": 4, "unit_cost_usd": 2.50, "supplier": "Amazon", "category": "control"},
    {"part": "5 V 10 A DC-DC buck converter", "qty": 1, "unit_cost_usd": 12.00, "supplier": "Amazon", "category": "control"},
    {"part": "Emergency cut-off switch 100 A", "qty": 1, "unit_cost_usd": 15.00, "supplier": "Amazon", "category": "control"},
    {"part": "MicroSD card 32 GB", "qty": 1, "unit_cost_usd": 8.00, "supplier": "Amazon", "category": "control"},

    # Mechanical hardware
    {"part": "M8 titanium heat-set inserts (pack 50)", "qty": 2, "unit_cost_usd": 22.00, "supplier": "Amazon / McMaster-Carr", "category": "hardware"},
    {"part": "M8 stainless hex bolts + nuts (pack 50)", "qty": 1, "unit_cost_usd": 18.00, "supplier": "Amazon", "category": "hardware"},
    {"part": "M4 / M6 bolt assortment", "qty": 1, "unit_cost_usd": 14.00, "supplier": "Amazon", "category": "hardware"},
    {"part": "Foam vibration isolation pads", "qty": 1, "unit_cost_usd": 12.00, "supplier": "Amazon", "category": "hardware"},
    {"part": "Pneumatic tyres 16×2 (pair)", "qty": 1, "unit_cost_usd": 30.00, "supplier": "Amazon / bike shop", "category": "hardware"},

    # Filament (CF-PLA, PETG, ABS-CF, PA12, TPU)
    {"part": "CF-PLA 1.75 mm 1 kg spool", "qty": 4, "unit_cost_usd": 45.00, "supplier": "eSUN / PolyMaker", "category": "filament"},
    {"part": "PETG 1.75 mm 1 kg spool", "qty": 2, "unit_cost_usd": 22.00, "supplier": "eSUN / Hatchbox", "category": "filament"},
    {"part": "ABS-CF 1.75 mm 1 kg spool", "qty": 1, "unit_cost_usd": 40.00, "supplier": "PolyMaker", "category": "filament"},
    {"part": "TPU-95A 1.75 mm 0.8 kg spool", "qty": 1, "unit_cost_usd": 28.00, "supplier": "NinjaFlex / Sainsmart", "category": "filament"},
    {"part": "Nylon PA12 SLS printing service (magnet housings)", "qty": 1, "unit_cost_usd": 75.00, "supplier": "Shapeways / local bureau", "category": "filament"},
]

TOOLS_REQUIRED: list[dict[str, str]] = [
    {"tool": "FDM 3D printer (≥ 300×300 mm bed)", "notes": "Creality Ender 5 Plus, Bambu Lab X1C, or similar"},
    {"tool": "Soldering iron with heat-set tip", "notes": "Hakko FX-888D or equivalent, set to 200 °C for PLA inserts"},
    {"tool": "Multimeter (digital)", "notes": "For voltage and continuity checks"},
    {"tool": "Gaussmeter / hall probe", "notes": "Verify magnet polarity and field strength"},
    {"tool": "Torque wrench 5–50 Nm", "notes": "For wheel bolts and structural fasteners"},
    {"tool": "Wire crimping tool + terminals", "notes": "For power connectors"},
    {"tool": "Laptop with SSH / USB access", "notes": "For firmware flashing and PID tuning"},
    {"tool": "Angle grinder + sanding discs", "notes": "For post-processing printed parts"},
    {"tool": "Drill press or hand drill", "notes": "For boring wheel hub tolerances"},
    {"tool": "Anti-static work mat + wrist strap", "notes": "For electronics assembly"},
    {"tool": "Fire extinguisher (Class D)", "notes": "For lithium battery safety"},
    {"tool": "Non-magnetic assembly jig", "notes": "For Halbach array magnet installation"},
    {"tool": "Clamp meter", "notes": "For verifying charge currents and motor draw"},
]

TROUBLESHOOTING_GUIDE: list[dict[str, str]] = [
    {
        "symptom": "Bike sinks or won't maintain hover height",
        "likely_cause": "Insufficient lift force or controller not reaching setpoint",
        "solution": "Check magnet polarity sequence (Halbach order). Increase Kp on gap PID. Verify all correction coils are connected and not open-circuit.",
    },
    {
        "symptom": "Oscillating hover height (bouncing)",
        "likely_cause": "PID Kd too low or Kp too high causing instability",
        "solution": "Reduce Kp by 20 %. Increase Kd by 15 %. Re-test. Use the simulation script to pre-tune gains.",
    },
    {
        "symptom": "One side lower than the other (tilt at rest)",
        "likely_cause": "Unequal magnet array placement or weight distribution",
        "solution": "Measure gap at all four ultrasonic sensors. Re-centre battery pack. Re-seat magnet arrays on level surface.",
    },
    {
        "symptom": "Motors not spinning or spinning in wrong direction",
        "likely_cause": "Incorrect motor phase wire order or VESC misconfiguration",
        "solution": "Run VESC Tool motor detection wizard. Swap any two phase wires to reverse direction if needed.",
    },
    {
        "symptom": "Battery depleting faster than expected",
        "likely_cause": "Correction coils drawing excess power due to poor calibration",
        "solution": "Check IMU calibration. Ensure bike is on level ground before starting. Check for Hall sensor disconnection causing coil overcurrent.",
    },
    {
        "symptom": "Raspberry Pi crashing during operation",
        "likely_cause": "Under-voltage from battery or software exception in control loop",
        "solution": "Monitor Raspberry Pi 5 V rail with multimeter. Increase buck converter capacity. Check control firmware exception logs.",
    },
    {
        "symptom": "Rattling noise from frame",
        "likely_cause": "Loose printed part or heat-set insert backing out",
        "solution": "Inspect all M8 joints. Re-torque to 25 Nm. Add Loctite thread-lock to critical fasteners.",
    },
    {
        "symptom": "Solar not charging battery",
        "likely_cause": "MPPT not configured correctly or insufficient irradiance",
        "solution": "Verify MPPT input voltage range matches solar panel Voc. Check fuse continuity. Test with Voc measurement at panel terminals.",
    },
]


# ---------------------------------------------------------------------------
# Guide generator
# ---------------------------------------------------------------------------

class AssemblyGuideGenerator:
    """
    Generates the complete hover bike assembly guide.
    """

    def __init__(self, output_dir: Path | str = Path("hover_bike_revolution/docs")) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_parts_list(self) -> Path:
        lines = [
            "# Barrot HoverBike MK-I — Complete Parts List\n\n",
            "| Category | Part | Qty | Unit Cost (USD) | Est. Total | Supplier |\n",
            "|----------|------|----:|---------------:|----------:|----------|\n",
        ]
        category_totals: dict[str, float] = {}
        total = 0.0
        for p in PARTS_LIST:
            subtotal = p["qty"] * p["unit_cost_usd"]
            cat = p["category"]
            category_totals[cat] = category_totals.get(cat, 0.0) + subtotal
            total += subtotal
            lines.append(
                f"| {cat} | {p['part']} | {p['qty']} | ${p['unit_cost_usd']:.2f} | "
                f"${subtotal:.2f} | {p['supplier']} |\n"
            )

        lines.append(f"\n**Grand Total: ${total:,.2f} USD**\n\n")
        lines.append("## Cost by Category\n\n")
        for cat, cost in sorted(category_totals.items()):
            lines.append(f"- **{cat.title()}**: ${cost:,.2f}\n")

        path = self.output_dir / "parts_list.md"
        path.write_text("".join(lines), encoding="utf-8")
        return path

    def generate_tools_list(self) -> Path:
        lines = [
            "# Required Tools\n\n",
            "| Tool | Notes |\n",
            "|------|-------|\n",
        ]
        for t in TOOLS_REQUIRED:
            lines.append(f"| {t['tool']} | {t['notes']} |\n")

        path = self.output_dir / "tools_list.md"
        path.write_text("".join(lines), encoding="utf-8")
        return path

    def generate_troubleshooting_guide(self) -> Path:
        lines = ["# Troubleshooting Guide\n\n"]
        for i, entry in enumerate(TROUBLESHOOTING_GUIDE, 1):
            lines += [
                f"## {i}. {entry['symptom']}\n\n",
                f"**Likely cause:** {entry['likely_cause']}\n\n",
                f"**Solution:** {entry['solution']}\n\n",
                "---\n\n",
            ]
        path = self.output_dir / "troubleshooting.md"
        path.write_text("".join(lines), encoding="utf-8")
        return path

    def generate_safety_guide(self) -> Path:
        content = """\
# Safety Guide — Barrot HoverBike MK-I

## ⚠️ General Safety Principles

1. **Never operate without a helmet and protective gear.**
2. **Perform all first tests in an open, obstacle-free area.**
3. **Keep bystanders ≥ 10 m away during powered testing.**
4. **Install the emergency cut-off switch within easy reach of the rider.**
5. **Never leave the battery charging unattended.**

## 🔋 Lithium Battery Safety

- Use only the specified BMS. Never bypass protection circuitry.
- Store and charge in a **fireproof LiPo bag** or metal container.
- Never charge at above 0.5 C (10 A for a 20 Ah pack).
- Inspect cells for swelling or heat before each ride. Discard damaged cells.
- Keep a **Class D fire extinguisher** nearby when working with cells.
- Minimum discharge voltage: 2.5 V/cell (48 V pack minimum = 37.5 V).

## 🧲 Magnet Safety

- N52 magnets of the sizes used in this project exert forces exceeding **500 N**.
  They can **crush fingers** if mishandled.
- Use **non-magnetic assembly jigs** and wear **anti-crush gloves**.
- Keep magnets **≥ 30 cm from electronic devices, credit cards, and pacemakers**.
- Install magnets one at a time, securing each before handling the next.

## ⚡ Electrical Safety

- Always disconnect the main battery before working on any wiring.
- Verify polarity with a multimeter before connecting any connector.
- Use properly rated wire gauges (minimum 8 AWG for main power runs).
- Insulate all bare connections with heat-shrink tubing.
- Fuse the battery output at 100 A.

## 🚴 Riding Safety

- Begin hover tests **tethered to a ground anchor**.
- Do not exceed 20 km/h during the first 5 hours of operation.
- Never ride over uneven terrain until fully calibrated.
- The minimum levitation speed (passive Halbach) is approximately 18 km/h.
  Below this speed the active stabilisation coils carry the full load.
- The bike is **not waterproof** — avoid puddles and rain.
- Maximum rider weight: **120 kg** (rider + gear).

## 🏥 Emergency Procedures

1. **Rider fall**: The bike should automatically activate parking mode.
   Approach only after confirming the emergency cut-off is activated.
2. **Battery fire**: Evacuate the area. Use Class D extinguisher or sand.
   Do NOT use water or CO₂ on a lithium fire.
3. **Runaway bike**: Use the RF emergency cut-off fob (if installed) or
   approach from behind and press the physical cut-off switch.
"""
        path = self.output_dir / "safety_guide.md"
        path.write_text(content, encoding="utf-8")
        return path

    def generate_all(self) -> dict[str, Path]:
        return {
            "parts_list": self.generate_parts_list(),
            "tools_list": self.generate_tools_list(),
            "troubleshooting": self.generate_troubleshooting_guide(),
            "safety_guide": self.generate_safety_guide(),
        }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    gen = AssemblyGuideGenerator()
    outputs = gen.generate_all()
    for name, path in outputs.items():
        print(f"  {name:30s} → {path}")
    total_cost = sum(p["qty"] * p["unit_cost_usd"] for p in PARTS_LIST)
    print(f"\nEstimated total parts cost: ${total_cost:,.2f} USD")
