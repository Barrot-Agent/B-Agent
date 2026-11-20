from __future__ import annotations

import json
from pathlib import Path


def test_lunaroute_mcp_stays_disabled_until_verified() -> None:
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "opencode.json").read_text(encoding="utf-8"))

    server = config["mcp"]["servers"]["lunaroute"]
    assert server["type"] == "remote"
    assert server["url"] == "https://mcp.lunaroute.com/mcp"
    assert server["disabled"] is True
    assert server["oauth"] is False
    assert server["headers"]["Authorization"] == "Bearer {env:LUNAROUTE_API_KEY}"

    agent = config["agent"]["barrot"]
    permissions = agent["permission"]
    assert permissions == {
        "*": "ask",
        "edit": "ask",
        "bash": "ask",
        "webfetch": "ask",
        "read": "allow",
        "glob": "allow",
        "grep": "allow",
        "list": "allow",
        "lsp": "allow",
        "skill": "allow",
        "question": "allow",
    }
    assert "verified" in agent["prompt"].lower()
