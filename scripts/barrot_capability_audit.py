#!/usr/bin/env python3
"""Barrot self-audit: inventory current capabilities, compare vs future state."""
import os, json, subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

FUTURE_CAPABILITIES = {
    1: "Market analysis + trading recommendations",
    2: "System degradation prediction",
    3: "Resource allocation ($5M engine)",
    4: "Multi-agent coordination",
    5: "Embodied learning (emulator)",
    6: "Creative content production (Stupid Sindy)",
    7: "Research synthesis",
    8: "Data contradiction resolution",
    9: "Video analysis + autofix",
    10: "Autonomous design engine",
    11: "Real-time security monitoring",
    12: "Autonomous testing framework",
    13: "Performance optimization pipeline",
    14: "Knowledge graph construction",
    15: "Cross-domain knowledge synthesis",
}

def get_current_capabilities():
    """Scan repo for deployed capabilities."""
    capabilities = {}
    for script in SCRIPTS_DIR.glob("*.py"):
        if script.name.startswith("_") or script.name == "barrot_agent.py":
            continue
        capabilities[script.name] = {
            "path": str(script),
            "size": script.stat().st_size,
            "has_workflow": any(WORKFLOWS_DIR.glob(f"*{script.stem}*.yml"))
        }
    return capabilities

def audit():
    """Compare current vs future, identify gaps."""
    current = get_current_capabilities()
    current_names = set(c.lower() for c in current.keys())
    
    gaps = []
    for cap_id, cap_name in FUTURE_CAPABILITIES.items():
        cap_key = cap_name.lower().replace(" ", "_")
        found = any(cap_key in c.lower() for c in current_names)
        if not found:
            gaps.append({"id": cap_id, "name": cap_name, "priority": "high" if cap_id > 10 else "medium"})
    
    audit_report = {
        "timestamp": os.popen("date -u +%Y-%m-%dT%H:%M:%SZ").read().strip(),
        "current_capabilities": len(current),
        "target_capabilities": len(FUTURE_CAPABILITIES),
        "gaps": gaps,
        "current": list(current.keys())
    }
    
    out_file = "barrot_capability_audit.json"
    with open(out_file, "w") as f:
        json.dump(audit_report, f, indent=2)
    
    print(f"Audit complete: {len(gaps)} capability gaps identified")
    return audit_report

if __name__ == "__main__":
    report = audit()
    print(json.dumps(report, indent=2))
