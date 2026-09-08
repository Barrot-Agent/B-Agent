#!/usr/bin/env python3
"""
BARROT ORBIT CLIENT -- real GitLab Orbit (Knowledge Graph) MCP client.
Calls the real, documented endpoint: POST https://gitlab.com/api/v4/mcp_orbit
JSON-RPC 2.0, two real tools: query_graph, get_graph_schema.
Auth: Personal Access Token with read_api scope (Bearer header).
Read-only -- cannot write to GitLab.
"""

import os, json, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ORBIT_TOKEN = os.environ.get("GITLAB_ORBIT_TOKEN", "")
ORBIT_URL = "https://gitlab.com/api/v4/mcp_orbit"

OUT_FILE = Path("ping-pongings/knowledge-base/orbit_query_log.jsonl")


def call_orbit(method, params=None, req_id=1):
    body = {"jsonrpc": "2.0", "method": method, "id": req_id}
    if params:
        body["params"] = params
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        ORBIT_URL, data=data,
        headers={"Authorization": f"Bearer {ORBIT_TOKEN}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Orbit HTTP {e.code}: {e.read().decode()[:500]}")
        return None
    except Exception as e:
        print(f"Orbit error: {e}")
        return None


def initialize():
    result = call_orbit("initialize", {"protocolVersion": "2025-06-18"}, req_id=1)
    if not result or "result" not in result:
        print("Initialize failed -- check token scope, tier, and that Orbit is enabled on the group")
        return False
    server_info = result["result"].get("serverInfo", {})
    print(f"Connected: {server_info.get('name', 'unknown')}")
    return True


def get_graph_schema(expand_nodes=None):
    params = {"name": "get_graph_schema", "arguments": {}}
    if expand_nodes:
        params["arguments"]["expand_nodes"] = expand_nodes
    result = call_orbit("tools/call", params, req_id=2)
    return result.get("result") if result else None


def query_graph(query_dict):
    params = {"name": "query_graph", "arguments": {"query": query_dict}}
    result = call_orbit("tools/call", params, req_id=3)
    return result.get("result") if result else None


def log_query(description, query_dict, result):
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "description": description,
        "query": query_dict,
        "result_summary": str(result)[:500] if result else "FAILED",
    }
    with open(OUT_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    if not ORBIT_TOKEN:
        print("GITLAB_ORBIT_TOKEN not set")
        raise SystemExit(1)
    if not initialize():
        raise SystemExit(1)

    description = os.environ.get("ORBIT_QUERY_DESCRIPTION", "schema check")
    raw_query = os.environ.get("ORBIT_QUERY_JSON", "")

    if raw_query:
        result = query_graph(json.loads(raw_query))
    else:
        result = get_graph_schema()

    print(json.dumps(result, indent=2)[:2000] if result else "No result -- check log for real error")
    log_query(description, raw_query or "schema", result)
