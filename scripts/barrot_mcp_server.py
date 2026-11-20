#!/usr/bin/env python3
"""Barrot MCP server: stdio JSON-RPC 2.0, five tools, no SDK required.

Protocol source: modelcontextprotocol.io, specification 2025-06-18, server/tools.
Quoted in data/mcp/spec_check.json by scripts/mcp_spec_check.py.

Seven tools:
  1. check_capability      real data: barrot_capability_audit.json
  2. run_foundry_cycle     refuses: no Foundry exists in this repo
  3. flight_recorder_replay honest refusal when fewer than two comparable runs exist
  4. reverse_engineer      claims-file summary over the TRACE-5 record
  5. trace5_validate       offline validation of a claims file
  6. verdict_check         verdict structure gate
  7. repo_guard            Liquid-hostile markdown and unguarded optional imports

The original task spec was truncated at tool 4 and never contained tool 5. The
contracts for 4 and 5 are reconstructions, documented as such; 1-3 follow the
recorded spec in docs/barrot-status.md.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "barrot_capability_audit.json"
RECORDER = ROOT / "results" / "flight_recorder"
VALIDATOR = ROOT / "scripts" / "re_v2.py"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def start_background_a2a_runner() -> bool:
    """Start one outbound queue consumer only after explicit opt-in."""
    if os.getenv("BARROT_A2A_AUTO_RUNNER", "").strip().upper() != "YES":
        print("[barrot] A2A runner is disabled by default; explicit BARROT_A2A_AUTO_RUNNER=YES is required after approval and sandbox review", file=sys.stderr)
        return False
    if not os.getenv("BARROT_A2A_URL"):
        return False
    if not (os.getenv("BARROT_AGENT_SECRET") or os.getenv("BRAIN_SHARED_SECRET")):
        print("[barrot] A2A runner not started: runner authentication secret is not available in the OpenCode environment", file=sys.stderr)
        return False
    try:
        from scripts.barrot_a2a_runner import runner_is_active

        if runner_is_active():
            return False
        log_dir = Path.home() / ".barrot"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "a2a-runner.log"
        with log_path.open("a", encoding="utf-8") as log_handle:
            subprocess.Popen(
                [sys.executable, str(ROOT / "scripts" / "barrot_a2a_runner.py")],
                cwd=str(ROOT),
                env=os.environ.copy(),
                stdin=subprocess.DEVNULL,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                close_fds=True,
            )
        return True
    except OSError as exc:
        print(f"[barrot] A2A runner launch failed: {type(exc).__name__}", file=sys.stderr)
        return False


PROTOCOL = "2025-06-18"

TOOLS = [
    {
        "name": "check_capability",
        "title": "Check capability",
        "description": "Look up a capability in barrot_capability_audit.json and return its evidence or the closest names.",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Capability file name, e.g. a2a_server.py"}},
            "required": ["name"],
        },
    },
    {
        "name": "run_foundry_cycle",
        "title": "Run foundry cycle",
        "description": "Run a capability foundry cycle. Refuses with isError when no foundry module exists.",
        "inputSchema": {
            "type": "object",
            "properties": {"goal": {"type": "string", "description": "What the cycle should build"}},
            "required": ["goal"],
        },
    },
    {
        "name": "flight_recorder_replay",
        "title": "Replay a recorded mission",
        "description": "Compare two runs of the same mission and skill version. Refuses when fewer than two comparable runs are recorded.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mission_id": {"type": "string"},
                "skill_version": {"type": "string"},
            },
            "required": ["mission_id", "skill_version"],
        },
    },
    {
        "name": "reverse_engineer",
        "title": "Summarise a claims record",
        "description": "Read a TRACE-5 claims file and return grades, usable claims and the steps used.",
        "inputSchema": {
            "type": "object",
            "properties": {"claims_file": {"type": "string", "description": "Path relative to the repository root"}},
            "required": ["claims_file"],
        },
    },
    {
        "name": "trace5_validate",
        "title": "Validate a claims file",
        "description": "Offline validation: every Q record must quote text present in its stored source.",
        "inputSchema": {
            "type": "object",
            "properties": {"claims_file": {"type": "string"}},
            "required": ["claims_file"],
        },
    },
    {
        "name": "verdict_check",
        "title": "Check a verdict document",
        "description": "Require a verdict letter, a falsifier, an upgrade condition and a stated limit before a verdict is publishable.",
        "inputSchema": {
            "type": "object",
            "properties": {"verdict_file": {"type": "string", "description": "Path relative to the repository root"}},
            "required": ["verdict_file"],
        },
    },
    {
        "name": "repo_guard",
        "title": "Guard docs and optional imports",
        "description": "Find Liquid-hostile markdown that Jekyll would parse and test modules that import optional dependencies without a guard.",
        "inputSchema": {
            "type": "object",
            "properties": {"root": {"type": "string", "description": "Directory relative to the repository root"}},
        },
    },
]


class ToolError(Exception):
    pass


def _resolve(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if ROOT not in path.parents and path != ROOT:
        raise ToolError(f"path escapes the repository: {relative}")
    return path


def check_capability(name: str) -> dict:
    data = json.loads(AUDIT.read_text(encoding="utf-8"))
    evidence = data.get("evidence", {})
    if name in evidence:
        return {"found": True, "name": name, "evidence": evidence[name]}
    matches = [key for key in evidence if name.lower() in key.lower()][:3]
    return {"found": False, "name": name, "closest": matches}


def run_foundry_cycle(goal: str) -> dict:
    hits = [p for p in (ROOT / "barrot_agent").rglob("*.py") if "foundry" in p.name.lower()]
    raise ToolError(
        "NOT_AVAILABLE: no foundry module in this repository "
        f"({len(hits)} files matching 'foundry'); goal recorded but not executed: {goal}"
    )


def flight_recorder_replay(mission_id: str, skill_version: str) -> dict:
    matches = []
    for path in sorted(RECORDER.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(record.get("task", "")) == mission_id and str(record.get("skill_version", "")) == skill_version:
                matches.append({"file": path.name, "cost_usd": record.get("cost_usd"), "minutes": record.get("minutes")})
    if len(matches) < 2:
        raise ToolError(f"INSUFFICIENT_DATA: {len(matches)} comparable run(s) recorded, 2 required")
    return {"mission_id": mission_id, "skill_version": skill_version, "runs": matches}


def reverse_engineer(claims_file: str) -> dict:
    path = _resolve(claims_file)
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    grades: dict[str, int] = {}
    for record in records:
        grades[record.get("status", "?")] = grades.get(record.get("status", "?"), 0) + 1
    usable = sum(1 for r in records if r.get("status") == "Q" and not r.get("excluded_from_evidence"))
    return {
        "claims_file": claims_file,
        "method": payload.get("method"),
        "records": len(records),
        "grades": grades,
        "usable_claims": usable,
        "steps_used": ["target", "retrieve", "assert-quote", "cross-check-or-single", "exit-with-falsifier"],
        "note": "steps_used is the TRACE-5 reconstruction; the original spec was truncated at this field",
    }


def verdict_check(verdict_file: str) -> dict:
    import importlib.util

    path = _resolve(verdict_file)
    spec = importlib.util.spec_from_file_location("verdict_gate", ROOT / "scripts" / "verdict_gate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    problems = module.check_text(path.read_text(encoding="utf-8"))
    return {"verdict_file": verdict_file, "passes": not problems, "problems": problems}


def repo_guard(root: str = ".") -> dict:
    import re

    base = _resolve(root)
    excludes: list[str] = []
    config = ROOT / "_config.yml"
    if config.exists():
        for line in config.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                excludes.append(stripped[2:].strip())

    liquid: list[dict] = []
    raw = re.compile(r"\{%\s*raw\s*%\}.*?\{%\s*endraw\s*%\}", re.DOTALL)
    # Scope comes from the two observed Jekyll failures: a file at the repository
    # root and a file under docs/. Other directories are copied untouched, so a
    # brace there is not a build risk. This keeps the guard from crying wolf.
    candidates = list(base.glob("*.md")) + list((base / "docs").rglob("*.md"))
    for path in sorted(candidates):
        relative = path.relative_to(ROOT).as_posix()
        if relative in excludes or ".git" in path.parts:
            continue
        text = raw.sub("", path.read_text(encoding="utf-8", errors="ignore"))
        if "{{" in text:
            line = next(i for i, row in enumerate(text.splitlines(), 1) if "{{" in row)
            liquid.append({"file": relative, "line": line})

    unguarded: list[dict] = []
    optional = ("scipy", "numpy", "torch", "pandas")
    guard = re.compile(r"importorskip|try:\s*\n\s*import|#\s*noqa", re.IGNORECASE)
    tests_dir = base / "tests"
    for path in sorted(tests_dir.rglob("test_*.py")):
        relative_parts = path.relative_to(tests_dir).parts
        if "fixtures" in relative_parts:
            continue  # fixtures exist to be flagged by the fixture test, not by this scan
        text = path.read_text(encoding="utf-8", errors="ignore")
        if guard.search(text):
            continue
        for name in optional:
            if re.search(rf"^\s*(?:from\s+{name}|import\s+{name})", text, re.MULTILINE):
                unguarded.append({"file": path.relative_to(ROOT).as_posix(), "module": name})

    return {
        "root": root,
        "liquid_hostile": liquid,
        "unguarded_optional_imports": unguarded,
        "clean": not liquid and not unguarded,
        "excluded_from_liquid_scan": excludes,
    }


def trace5_validate(claims_file: str) -> dict:
    import importlib.util

    spec = importlib.util.spec_from_file_location("re_v2", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    issues = module.validate(_resolve(claims_file))
    return {"claims_file": claims_file, "valid": not issues, "issues": issues}


HANDLERS = {
    "check_capability": lambda args: check_capability(args["name"]),
    "run_foundry_cycle": lambda args: run_foundry_cycle(args["goal"]),
    "flight_recorder_replay": lambda args: flight_recorder_replay(args["mission_id"], args["skill_version"]),
    "reverse_engineer": lambda args: reverse_engineer(args["claims_file"]),
    "trace5_validate": lambda args: trace5_validate(args["claims_file"]),
    "verdict_check": lambda args: verdict_check(args["verdict_file"]),
    "repo_guard": lambda args: repo_guard(args.get("root", ".")),
}


def handle(request: dict) -> dict | None:
    method = request.get("method")
    request_id = request.get("id")
    if request_id is None:
        return None
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": PROTOCOL,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "barrot", "version": "1"},
            },
        }
    if method == "ping":
        # Clients probe liveness; an error here can mark the server unhealthy.
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = request.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        if name not in HANDLERS:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": f"Unknown tool: {name}"}}
        try:
            payload = HANDLERS[name](args)
        except ToolError as exc:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": str(exc)}], "isError": True},
            }
        except (KeyError, TypeError) as exc:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": f"Invalid arguments: {exc}"}}
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(payload)}],
                "structuredContent": payload,
                "isError": False,
            },
        }
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}


def main() -> int:
    start_background_a2a_runner()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}), flush=True)
            continue
        response = handle(request)
        if response is not None:
            print(json.dumps(response), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
