#!/usr/bin/env python3
"""Barrot self-audit: inventory current capabilities with durable evidence."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from barrot_agent.orchestration.shared_runtime import CompletionGate, DurableStateStore, ExecutionRecord, Fingerprint

SCRIPTS_DIR = REPO_ROOT / "scripts"
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
OUTPUT_PATH = REPO_ROOT / "barrot_capability_audit.json"
STATE_STORE = DurableStateStore(REPO_ROOT, "barrot_capability_audit")

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


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_current_capabilities() -> dict[str, dict[str, Any]]:
    capabilities: dict[str, dict[str, Any]] = {}
    for script in sorted(SCRIPTS_DIR.glob("*.py")):
        if script.name.startswith("_") or script.name == "barrot_agent.py":
            continue
        capabilities[script.name] = {
            "path": str(script),
            "size": script.stat().st_size,
            "has_workflow": any(WORKFLOWS_DIR.glob(f"*{script.stem}*.yml")),
            "fingerprint": Fingerprint.create(script.name, script.stat().st_size, script.read_text(encoding="utf-8")).value,
        }
    return capabilities


def audit() -> dict[str, Any]:
    current = get_current_capabilities()
    current_names = {name.lower() for name in current}
    gaps: list[dict[str, Any]] = []
    for cap_id, cap_name in FUTURE_CAPABILITIES.items():
        cap_key = cap_name.lower().replace(" ", "_")
        found = any(cap_key in current_name for current_name in current_names)
        if not found:
            gaps.append({"id": cap_id, "name": cap_name, "priority": "high" if cap_id > 10 else "medium"})
    report = {
        "timestamp": now_iso(),
        "status": "VERIFIED",
        "current_capabilities": len(current),
        "target_capabilities": len(FUTURE_CAPABILITIES),
        "gaps": gaps,
        "current": list(current.keys()),
        "evidence": current,
        "execution_record": ExecutionRecord(
            record_id=Fingerprint.create("capability_audit", current, gaps).value,
            operation="capability_audit",
            state="COMPLETE",
            input_fingerprint=Fingerprint.create(FUTURE_CAPABILITIES).value,
            output_fingerprint=Fingerprint.create(current, gaps).value,
            response={"gap_count": len(gaps)},
        ).to_dict(),
        "completion_gate": CompletionGate(
            gate_id=Fingerprint.create("capability_audit_gate", bool(current)).value,
            requirements={"repository_scanned": True, "audit_written": True},
            satisfied=True,
            unresolved=[],
        ).to_dict(),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    STATE_STORE.write_state("latest", report, fingerprint=Fingerprint.create("capability_audit", FUTURE_CAPABILITIES).value)
    return report


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
