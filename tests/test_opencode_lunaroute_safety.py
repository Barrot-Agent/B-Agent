from __future__ import annotations

import json
from pathlib import Path


def test_lunaroute_is_absent_from_active_opencode_configuration() -> None:
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "opencode.json").read_text(encoding="utf-8"))

    assert "lunaroute" not in config.get("mcp", {}).get("servers", {})
    serialized = json.dumps(config).lower()
    assert "lunaroute" not in serialized
    assert "default_agent" in config and config["default_agent"] == "barrot"
    assert config["model"] == "opencode/deepseek-v4.1-flash-free"
    assert config["agent"]["barrot"]["model"] == config["model"]
    assert config["permission"]["edit"] == "ask"
    assert config["permission"]["bash"] == "ask"
