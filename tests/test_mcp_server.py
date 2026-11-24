"""The MCP server must answer the protocol and refuse what it cannot do."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.barrot_mcp_server import TOOLS, handle

ROOT = Path(__file__).resolve().parents[1]


def call(name: str, arguments: dict) -> dict:
    return handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}})


def test_initialize_declares_tools_capability():
    response = handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert response["result"]["protocolVersion"] == "2025-06-18"
    assert "tools" in response["result"]["capabilities"]
    assert response["result"]["serverInfo"]["name"] == "barrot"


def test_ping_returns_an_empty_result():
    # Registration in opencode.json means healthy liveness matters.
    response = handle({"jsonrpc": "2.0", "id": 9, "method": "ping"})
    assert response["result"] == {}


def test_registered_in_opencode_config():
    import json

    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    assert config["mcp"]["servers"]["github"]["disabled"] is True
    assert "lunaroute" not in config["mcp"]["servers"]
    server = config["mcp"]["servers"]["barrot"]
    assert server["type"] == "local"
    assert server["command"] == ["python3", "scripts/barrot_mcp_server.py"]
    assert (ROOT / server["command"][1]).exists()
    env = server.get("environment", {})
    assert "BARROT_A2A_URL" not in env
    assert "BRAIN_SHARED_SECRET" not in env
    assert "BARROT_AGENT_SECRET" not in env
    assert config["permission"]["bash"] == "ask"
    assert config["permission"]["edit"] == "ask"
    assert config["permission"]["external_directory"] == "ask"


def test_tools_list_contains_the_original_five():
    response = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = {tool["name"] for tool in response["result"]["tools"]}
    assert {
        "check_capability",
        "run_foundry_cycle",
        "flight_recorder_replay",
        "reverse_engineer",
        "trace5_validate",
    } <= names
    assert len(TOOLS) == 7
    for tool in TOOLS:
        assert tool["inputSchema"]["type"] == "object"


def test_check_capability_returns_real_evidence():
    result = call("check_capability", {"name": "a2a_server.py"})["result"]
    assert result["isError"] is False
    assert result["structuredContent"]["found"] is True
    assert result["structuredContent"]["evidence"]["size"] > 0


def test_check_capability_reports_misses_with_closest_matches():
    result = call("check_capability", {"name": "no_such_capability_xyz"})["result"]
    assert result["structuredContent"]["found"] is False
    assert isinstance(result["structuredContent"]["closest"], list)


def test_foundry_cycle_refuses_instead_of_faking():
    result = call("run_foundry_cycle", {"goal": "build something"})["result"]
    assert result["isError"] is True
    assert "NOT_AVAILABLE" in result["content"][0]["text"]


def test_flight_recorder_refuses_without_two_runs():
    result = call("flight_recorder_replay", {"mission_id": "no such mission", "skill_version": "1"})["result"]
    assert result["isError"] is True
    assert "INSUFFICIENT_DATA" in result["content"][0]["text"]


def test_reverse_engineer_summarises_a_claims_file():
    result = call("reverse_engineer", {"claims_file": "data/millennium/claims/hodge_conjecture.json"})["result"]
    body = result["structuredContent"]
    assert result["isError"] is False
    assert body["records"] == 5
    assert body["usable_claims"] == 3
    assert body["steps_used"] == ["target", "retrieve", "assert-quote", "cross-check-or-single", "exit-with-falsifier"]


def test_trace5_validate_accepts_a_good_file_and_rejects_an_escape():
    good = call("trace5_validate", {"claims_file": "data/millennium/claims/hodge_conjecture.json"})["result"]
    assert good["structuredContent"]["valid"] is True
    bad = call("trace5_validate", {"claims_file": "../../etc/passwd"})["result"]
    assert bad["isError"] is True


def test_unknown_tool_is_a_protocol_error():
    response = call("nope", {})
    assert response["error"]["code"] == -32602


def test_stdio_transport_answers_two_requests():
    payload = "\n".join(
        [
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
        ]
    ) + "\n"
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "barrot_mcp_server.py")],
        input=payload,
        capture_output=True,
        text=True,
        timeout=30,
    )
    lines = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
    assert completed.returncode == 0
    assert lines[0]["result"]["protocolVersion"] == "2025-06-18"
    assert len(lines[1]["result"]["tools"]) == 7


def test_tools_list_has_seven_tools_now():
    response = handle({"jsonrpc": "2.0", "id": 21, "method": "tools/list"})
    names = {tool["name"] for tool in response["result"]["tools"]}
    assert names == {
        "check_capability",
        "run_foundry_cycle",
        "flight_recorder_replay",
        "reverse_engineer",
        "trace5_validate",
        "verdict_check",
        "repo_guard",
    }


def test_verdict_check_passes_the_real_verdict_and_fails_a_fixture():
    good = call("verdict_check", {"verdict_file": "docs/research/CONSCIOUSNESS-BRIDGE.md"})["result"]
    assert good["structuredContent"]["passes"] is True
    bad = call("verdict_check", {"verdict_file": "tests/fixtures/verdicts/missing_upgrade.md"})["result"]
    assert bad["structuredContent"]["passes"] is False
    assert bad["structuredContent"]["problems"]


def test_repo_guard_is_clean_on_this_repository():
    result = call("repo_guard", {})["result"]["structuredContent"]
    assert result["clean"] is True
    assert result["liquid_hostile"] == []
    assert result["unguarded_optional_imports"] == []


def test_repo_guard_flags_both_failure_classes_in_a_fixture_root():
    result = call("repo_guard", {"root": "tests/fixtures/guard/root"})["result"]["structuredContent"]
    assert result["clean"] is False
    files = {item["file"] for item in result["liquid_hostile"]}
    assert "tests/fixtures/guard/root/note.md" in files
    assert "tests/fixtures/guard/root/docs/bad.md" in files
    assert result["unguarded_optional_imports"] == [
        {"file": "tests/fixtures/guard/root/tests/test_bad_import.py", "module": "scipy"}
    ]


def test_mcp_startup_launches_one_outbound_runner_when_credentials_exist(tmp_path, monkeypatch):
    import scripts.barrot_mcp_server as server

    monkeypatch.setenv("BARROT_A2A_URL", "https://barrot-a2a-worker.amazonprostarelite.workers.dev")
    monkeypatch.setenv("BRAIN_SHARED_SECRET", "gateway-test-secret")
    monkeypatch.setenv("BARROT_AGENT_SECRET", "agent-test-secret")
    monkeypatch.setenv("BARROT_A2A_AUTO_RUNNER", "YES")
    monkeypatch.setattr(server.Path, "home", lambda: tmp_path)
    monkeypatch.setattr("scripts.barrot_a2a_runner.runner_is_active", lambda: False)
    with patch.object(server.subprocess, "Popen") as launch:
        assert server.start_background_a2a_runner() is True
    launch.assert_called_once()
    args, kwargs = launch.call_args
    assert args[0][-1].endswith("scripts/barrot_a2a_runner.py")
    assert kwargs["start_new_session"] is True
    assert kwargs["stdin"] == subprocess.DEVNULL



def test_mcp_startup_requires_explicit_opt_in_even_when_credentials_exist(tmp_path, monkeypatch):
    import scripts.barrot_mcp_server as server

    monkeypatch.setenv("BARROT_A2A_URL", "https://barrot-a2a-worker.amazonprostarelite.workers.dev")
    monkeypatch.setenv("BRAIN_SHARED_SECRET", "gateway-test-secret")
    monkeypatch.setenv("BARROT_AGENT_SECRET", "agent-test-secret")
    monkeypatch.delenv("BARROT_A2A_AUTO_RUNNER", raising=False)
    monkeypatch.setattr(server.Path, "home", lambda: tmp_path)
    monkeypatch.setattr("scripts.barrot_a2a_runner.runner_is_active", lambda: False)
    with patch.object(server.subprocess, "Popen") as launch:
        assert server.start_background_a2a_runner() is False
    launch.assert_not_called()


def test_mcp_startup_does_not_launch_runner_with_gateway_secret_only(tmp_path, monkeypatch):
    import scripts.barrot_mcp_server as server

    monkeypatch.setenv("BARROT_A2A_URL", "https://barrot-a2a-worker.amazonprostarelite.workers.dev")
    monkeypatch.setenv("BRAIN_SHARED_SECRET", "gateway-only-secret")
    monkeypatch.delenv("BARROT_AGENT_SECRET", raising=False)
    monkeypatch.setenv("BARROT_A2A_AUTO_RUNNER", "YES")
    monkeypatch.setattr(server.Path, "home", lambda: tmp_path)
    monkeypatch.setattr("scripts.barrot_a2a_runner.runner_is_active", lambda: False)
    with patch.object(server.subprocess, "Popen") as launch:
        assert server.start_background_a2a_runner() is False
    launch.assert_not_called()
