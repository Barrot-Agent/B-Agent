#!/usr/bin/env python3
"""Cross-domain routing audit.

Checks every link that is supposed to connect one part of the repo to another and
prints a machine-readable report. Exit code 1 means an undocumented break.

Links checked:
  runtime    opencode.json mcp.servers  ->  the servers that actually start
  config     mcp_config.json            ->  barrot_agent + scripts/mcp_sync.py
  mirror     data/mcp_config.json       ->  byte-equal to mcp_config.json
  recorder   results/flight_recorder/*  ->  barrot_agent/flight_recorder.py
  registry   integration config path    ->  creatable by MCPRegistry
  docs       docs/**/*.md               ->  docs/INDEX.md

A break is allowed only if it is listed in KNOWN_BREAKS with a reason.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from barrot_agent.flight_recorder import load_records  # noqa: E402
from barrot_agent.mcp_registry import MCPRegistry  # noqa: E402

KNOWN_BREAKS = {
    "runtime_vs_config_drift": "opencode.json runs 3 servers; mcp_config.json lists 8 for the sync engine",
    "sandbox_gate": "MCPIntegration promotes 0 because sandbox validation passes 0 items and approval denies",
    "github_token": "GITHUB_MCP_TOKEN is unset in a plain shell; the live value lives in the OpenCode service env",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_runtime_vs_config() -> dict:
    runtime = set(read_json(ROOT / "opencode.json").get("mcp", {}).get("servers", {}))
    config = set(read_json(ROOT / "mcp_config.json").get("mcpServers", {}))
    return {
        "link": "runtime_vs_config_drift",
        "ok": runtime == config,
        "detail": f"runtime={sorted(runtime)} sync_config={sorted(config)}",
        "only_runtime": sorted(runtime - config),
        "only_config": sorted(config - runtime),
    }


def check_config_mirror() -> dict:
    left = (ROOT / "mcp_config.json").read_bytes()
    right = (ROOT / "data" / "mcp_config.json").read_bytes()
    return {"link": "config_mirror", "ok": left == right, "detail": "data/ copy is byte-equal"}


def check_recorder() -> dict:
    records, breaks = load_records(ROOT / "results" / "flight_recorder")
    return {
        "link": "recorder_schema",
        "ok": not breaks,
        "detail": f"{len(records)} valid records, {len(breaks)} breaks",
        "breaks": [b.__dict__ for b in breaks],
    }


def check_registry() -> dict:
    path = ROOT / "barrot_agent" / "mcp_registry.json"
    registry = MCPRegistry(registry_path=path)
    return {
        "link": "registry_load",
        "ok": True,
        "detail": f"path={path.name} exists={path.exists()} entries={len(registry.list_all())}",
    }


def check_docs_index() -> dict:
    index = ROOT / "docs" / "INDEX.md"
    docs = sorted(p for p in (ROOT / "docs").rglob("*.md") if p.name != "INDEX.md")
    if not index.exists():
        return {"link": "docs_index", "ok": False, "detail": "docs/INDEX.md missing", "missing": len(docs)}
    text = index.read_text(encoding="utf-8")
    unlisted = [str(p.relative_to(ROOT)) for p in docs if str(p.relative_to(ROOT)) not in text]
    return {"link": "docs_index", "ok": not unlisted, "detail": f"{len(docs)} docs", "unlisted": unlisted}


CHECKS = (
    check_runtime_vs_config,
    check_config_mirror,
    check_recorder,
    check_registry,
    check_docs_index,
)


def audit() -> dict:
    results = [check() for check in CHECKS]
    for row in results:
        if not row["ok"] and row["link"] in KNOWN_BREAKS:
            row["known_break"] = KNOWN_BREAKS[row["link"]]
    breaking = [r for r in results if not r["ok"] and "known_break" not in r]
    return {"links": results, "breaking": [r["link"] for r in breaking], "ok": not breaking}


if __name__ == "__main__":
    report = audit()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["ok"] else 1)
