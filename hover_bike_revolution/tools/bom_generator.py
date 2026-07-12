"""
bom_generator.py — Bill of Materials generator for the hover bike project.

Combines printed parts material costs with purchased components to produce
a comprehensive BOM in multiple formats.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Re-use parts list from assembly guide
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from assembly_guide_generator import PARTS_LIST


def generate_bom(output_dir: Path | str = Path("hover_bike_revolution/docs")) -> dict[str, Any]:
    """Generate a complete Bill of Materials."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    by_category: dict[str, list[dict[str, Any]]] = {}
    total_cost = 0.0

    for p in PARTS_LIST:
        cat = p["category"]
        if cat not in by_category:
            by_category[cat] = []
        line_total = p["qty"] * p["unit_cost_usd"]
        total_cost += line_total
        by_category[cat].append({**p, "line_total_usd": round(line_total, 2)})

    bom = {
        "project": "Barrot HoverBike MK-I",
        "total_cost_usd": round(total_cost, 2),
        "categories": by_category,
        "line_items": len(PARTS_LIST),
    }

    # Write JSON BOM
    json_path = output_dir / "bom.json"
    json_path.write_text(json.dumps(bom, indent=2), encoding="utf-8")

    # Write Markdown BOM
    lines = ["# Bill of Materials — Barrot HoverBike MK-I\n\n"]
    for cat, items in sorted(by_category.items()):
        cat_total = sum(i["line_total_usd"] for i in items)
        lines.append(f"## {cat.title()} (${cat_total:,.2f})\n\n")
        lines.append("| Part | Qty | Unit ($) | Total ($) | Supplier |\n")
        lines.append("|------|----:|---------:|----------:|---------|\n")
        for i in items:
            lines.append(
                f"| {i['part']} | {i['qty']} | {i['unit_cost_usd']:.2f} | "
                f"{i['line_total_usd']:.2f} | {i['supplier']} |\n"
            )
        lines.append("\n")

    lines.append(f"\n**Grand Total: ${total_cost:,.2f} USD**\n")
    md_path = output_dir / "bom.md"
    md_path.write_text("".join(lines), encoding="utf-8")

    return bom


if __name__ == "__main__":
    bom = generate_bom()
    print(f"BOM generated: {bom['line_items']} line items, ${bom['total_cost_usd']:,.2f} total")
