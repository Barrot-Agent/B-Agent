"""
component_sourcer.py — Component sourcing guide for the hover bike.

Provides supplier recommendations, lead times, and alternative sources
for all major components.
"""

from __future__ import annotations

from typing import Any

SOURCING_GUIDE: list[dict[str, Any]] = [
    {
        "component": "N52 Neodymium Magnets (50×25×10 mm)",
        "primary_supplier": "K&J Magnetics (US)",
        "primary_url": "https://www.kjmagnetics.com",
        "alternatives": ["Magnet Expert (UK)", "Supermagnete (EU)", "eBay"],
        "lead_time_days": "3–7 (stock item)",
        "notes": "Buy in bulk (>50) for significant discount. Verify exact dimensions before ordering.",
    },
    {
        "component": "BLDC Hub Motors (750 W, 48 V)",
        "primary_supplier": "QSMotor / AliExpress",
        "primary_url": "https://www.aliexpress.com",
        "alternatives": ["Leafbike", "Cyclone Taiwan", "MXUS"],
        "lead_time_days": "14–30 (international shipping)",
        "notes": "Specify 48 V winding and preferred wheel size. Request test data.",
    },
    {
        "component": "VESC 75/300 ESC",
        "primary_supplier": "Trampa Boards",
        "primary_url": "https://trampaboards.com",
        "alternatives": ["Flipsky VESC 75200", "MakerX Go-FOC"],
        "lead_time_days": "7–14",
        "notes": "VESC is open-source hardware. Flipsky offers cost-effective clones.",
    },
    {
        "component": "LiFePO4 Cells (3.2 V 20 Ah prismatic)",
        "primary_supplier": "CALB / EVE via AliExpress",
        "primary_url": "https://www.aliexpress.com",
        "alternatives": ["Winston Battery", "Headway cells (cylindrical)"],
        "lead_time_days": "14–30",
        "notes": "Grade A cells only. Verify cell QR code with manufacturer. Test each cell before assembly.",
    },
    {
        "component": "Raspberry Pi 4B",
        "primary_supplier": "Adafruit / RS Components",
        "primary_url": "https://www.adafruit.com",
        "alternatives": ["Mouser", "Farnell", "PiShop"],
        "lead_time_days": "1–5",
        "notes": "4 GB RAM minimum for real-time control + logging. Use active cooling.",
    },
    {
        "component": "Thin-film Solar Module (150 Wp)",
        "primary_supplier": "MiaSolé / GlobalSolar",
        "primary_url": "https://www.miasolé.com",
        "alternatives": ["Renogy flexible panels", "Giamax", "SunPower flexible"],
        "lead_time_days": "7–21",
        "notes": "CIGS thin-film preferred for flexibility. Verify Voc < MPPT input limit.",
    },
    {
        "component": "CF-PLA Filament (1.75 mm)",
        "primary_supplier": "PolyMaker PolyLite CF-PLA",
        "primary_url": "https://www.polymaker.com",
        "alternatives": ["eSUN CF-PLA", "Fiberlogy", "ColorFabb CarbonFil"],
        "lead_time_days": "2–7",
        "notes": "Dry filament before printing (3 h at 65 °C). Use hardened nozzle.",
    },
    {
        "component": "Nylon PA12 SLS Printing Service",
        "primary_supplier": "Shapeways",
        "primary_url": "https://www.shapeways.com",
        "alternatives": ["Sculpteo", "i.Materialise", "local SLS bureau"],
        "lead_time_days": "7–14",
        "notes": "Upload STL directly. Choose 'White Strong & Flexible' (PA12). Specify ±0.1 mm tolerance.",
    },
]


def sourcing_report() -> dict[str, Any]:
    return {
        "component_count": len(SOURCING_GUIDE),
        "components": SOURCING_GUIDE,
        "procurement_tips": [
            "Order magnets and LiFePO4 cells first — these have the longest lead times.",
            "Verify dimensions of all press-fit components before printing mating parts.",
            "Source a spare set of Hall sensors and ultrasonic sensors — they are fragile.",
            "Consider buying VESC development kit which includes USB debugger.",
        ],
    }


if __name__ == "__main__":
    import json

    report = sourcing_report()
    print(json.dumps(report, indent=2))
