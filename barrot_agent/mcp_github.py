"""
MCP server for B-Agent — GitHub Copilot Chat integration.

Implements the Model Context Protocol (MCP) stdio transport so that GitHub
Copilot Chat (and any MCP-compatible client) can call GitHub operations as
tools.

Protocol overview
-----------------
The MCP server reads JSON-RPC 2.0 messages from *stdin*, one per line, and
writes responses to *stdout*.  A minimal subset of the protocol is
implemented:

  - initialize / initialized  — capability handshake
  - tools/list                — enumerate available tools
  - tools/call                — invoke a tool

Run with:
    python -m scripts.run_mcp_server
    # or
    python scripts/run_mcp_server.py
"""

from __future__ import annotations

import json
import sys
from typing import Any

from barrot_agent.config import AppConfig
from barrot_agent.github_service import make_service

# ------------------------------------------------------------------
# Tool definitions
# ------------------------------------------------------------------

TOOLS: list[dict[str, Any]] = [
    {
        "name": "github_list_issues",
        "description": "List issues for a GitHub repository.",
        "inputSchema": {
            "type": "object",
            "required": ["owner", "repo"],
            "properties": {
                "owner": {"type": "string", "description": "Repository owner (org or user)"},
                "repo": {"type": "string", "description": "Repository name"},
                "state": {
                    "type": "string",
                    "enum": ["open", "closed", "all"],
                    "default": "open",
                    "description": "Issue state filter",
                },
                "per_page": {"type": "integer", "default": 30},
                "page": {"type": "integer", "default": 1},
            },
        },
    },
    {
        "name": "github_get_issue",
        "description": "Get a single GitHub issue by number.",
        "inputSchema": {
            "type": "object",
            "required": ["owner", "repo", "issue_number"],
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "issue_number": {"type": "integer", "description": "Issue number"},
            },
        },
    },
    {
        "name": "github_create_issue",
        "description": "Create a new GitHub issue.",
        "inputSchema": {
            "type": "object",
            "required": ["owner", "repo", "title"],
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "title": {"type": "string"},
                "body": {"type": "string", "default": ""},
                "labels": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    {
        "name": "github_add_comment",
        "description": "Add a comment to an existing GitHub issue.",
        "inputSchema": {
            "type": "object",
            "required": ["owner", "repo", "issue_number", "body"],
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "issue_number": {"type": "integer"},
                "body": {"type": "string", "description": "Comment text (Markdown supported)"},
            },
        },
    },
]


# ------------------------------------------------------------------
# Dispatch
# ------------------------------------------------------------------


def _call_tool(
    name: str,
    arguments: dict[str, Any],
    config: AppConfig,
) -> Any:
    """Execute a tool and return a JSON-serialisable result."""
    token = config.github_token or ""
    default_owner = config.github_default_owner or ""
    default_repo = config.github_default_repo or ""

    svc = make_service(token)

    owner = arguments.get("owner") or default_owner
    repo = arguments.get("repo") or default_repo

    if name == "github_list_issues":
        return svc.list_issues(
            owner=owner,
            repo=repo,
            state=arguments.get("state", "open"),
            per_page=int(arguments.get("per_page", 30)),
            page=int(arguments.get("page", 1)),
        )

    if name == "github_get_issue":
        return svc.get_issue(owner, repo, int(arguments["issue_number"]))

    if name == "github_create_issue":
        return svc.create_issue(
            owner=owner,
            repo=repo,
            title=arguments["title"],
            body=arguments.get("body", ""),
            labels=arguments.get("labels"),
        )

    if name == "github_add_comment":
        return svc.add_comment(
            owner=owner,
            repo=repo,
            issue_number=int(arguments["issue_number"]),
            body=arguments["body"],
        )

    raise ValueError(f"Unknown tool: {name}")


# ------------------------------------------------------------------
# JSON-RPC helpers
# ------------------------------------------------------------------


def _ok(req_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _write(obj: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


# ------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------


def run_server(config: AppConfig | None = None, *, _input=None, _output=None) -> None:  # type: ignore[assignment]
    """Run the MCP stdio server loop.

    Parameters ``_input`` and ``_output`` are used in tests to inject
    alternative streams instead of stdin/stdout.
    """
    cfg = config or AppConfig()
    inp = _input or sys.stdin
    out_write = _output or _write

    server_info = {
        "name": "b-agent-github",
        "version": "1.0.0",
    }

    for raw_line in inp:
        raw_line = raw_line.strip()
        if not raw_line:
            continue

        try:
            msg: dict[str, Any] = json.loads(raw_line)
        except json.JSONDecodeError:
            out_write(_error(None, -32700, "Parse error"))
            continue

        method = msg.get("method", "")
        req_id = msg.get("id")
        params: dict[str, Any] = msg.get("params") or {}

        # Notifications (no id) — acknowledged silently
        if req_id is None and method == "notifications/initialized":
            continue

        if method == "initialize":
            out_write(
                _ok(
                    req_id,
                    {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": server_info,
                        "capabilities": {"tools": {}},
                    },
                )
            )

        elif method == "tools/list":
            out_write(_ok(req_id, {"tools": TOOLS}))

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments: dict[str, Any] = params.get("arguments") or {}
            try:
                result = _call_tool(tool_name, arguments, cfg)
                out_write(
                    _ok(
                        req_id,
                        {
                            "content": [
                                {"type": "text", "text": json.dumps(result, indent=2)}
                            ],
                            "isError": False,
                        },
                    )
                )
            except Exception as exc:  # noqa: BLE001
                out_write(
                    _ok(
                        req_id,
                        {
                            "content": [{"type": "text", "text": str(exc)}],
                            "isError": True,
                        },
                    )
                )

        else:
            if req_id is not None:
                out_write(_error(req_id, -32601, f"Method not found: {method}"))


if __name__ == "__main__":
    run_server()
