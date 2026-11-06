from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from barrot_agent.mcp_adapters import CodebaseMemoryAdapter
from barrot_agent.mcp_discovery import MCPDiscovery, SecurityPosture, ServerInventory, ToolSchema
from barrot_agent.mcp_targets import SUPPORTED_MCP_SERVERS, get_server_by_id
from barrot_agent.repository.codebase_memory import (
    CodebaseMemoryClient,
    CodebaseMemoryError,
    RepositorySyncController,
)


def completed(command, returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(command, returncode, stdout, stderr)


def test_codebase_memory_client_invokes_allowlisted_cli_with_json(tmp_path: Path):
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        return completed(command, stdout='{"ok":true}')

    client = CodebaseMemoryClient(tmp_path, binary="cbm", runner=runner)
    result = client.call_tool("search_graph", {"project": "B-Agent", "name_pattern": "Sync"})

    assert result == {"ok": True}
    command, kwargs = calls[0]
    assert command == ["cbm", "cli", "search_graph", "--format", "json"]
    assert kwargs["cwd"] == str(tmp_path.resolve())
    assert json.loads(kwargs["input"]) == {
        "name_pattern": "Sync",
        "project": "B-Agent",
    }
    assert kwargs["capture_output"] is True
    assert kwargs.get("shell", False) is False


def test_index_repository_is_confined_to_configured_root_and_local_cache(tmp_path: Path):
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        return completed(command, stdout='{"indexed":true}')

    client = CodebaseMemoryClient(tmp_path, binary="cbm", runner=runner)
    client.call_tool("index_repository", {"mode": "moderate"})

    payload = json.loads(calls[0][1]["input"])
    assert payload["repo_path"] == str(tmp_path.resolve())
    assert payload["mode"] == "moderate"
    assert payload["persistence"] is False

    with pytest.raises(ValueError, match="configured repository root"):
        client.call_tool(
            "index_repository",
            {"repo_path": str(tmp_path.parent / "other")},
        )

    with pytest.raises(ValueError, match="persistence is disabled"):
        client.call_tool("index_repository", {"persistence": True})


def test_codebase_memory_client_rejects_unapproved_tools(tmp_path: Path):
    client = CodebaseMemoryClient(tmp_path, binary="cbm", runner=lambda *a, **k: None)

    with pytest.raises(ValueError, match="not allowlisted"):
        client.call_tool("delete_project", {"project": "B-Agent"})


def test_codebase_memory_client_surfaces_missing_binary_and_tool_failures(tmp_path: Path):
    def missing(*args, **kwargs):
        raise FileNotFoundError("missing")

    client = CodebaseMemoryClient(tmp_path, binary="cbm", runner=missing)
    with pytest.raises(CodebaseMemoryError, match="not installed"):
        client.call_tool("list_projects")

    failed = CodebaseMemoryClient(
        tmp_path,
        binary="cbm",
        runner=lambda command, **kwargs: completed(command, 2, stderr="bad query"),
    )
    with pytest.raises(CodebaseMemoryError, match="bad query"):
        failed.call_tool("list_projects")


class FakeIndexer:
    def __init__(self):
        self.calls = []

    def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return {"indexed": True}


def make_git_runner(tmp_path: Path, *, dirty: str = "", fetch_code: int = 0, branch: str = "main"):
    commands = []

    def runner(command, **kwargs):
        args = command[3:]
        commands.append(args)
        if args == ["branch", "--show-current"]:
            return completed(command, stdout=branch + "\n")
        if args == ["rev-parse", "HEAD"]:
            return completed(command, stdout="abc123\n")
        if args == ["status", "--porcelain"]:
            return completed(command, stdout=dirty)
        if args == ["remote", "get-url", "origin"]:
            return completed(command, stdout="https://github.com/Barrot-Agent/B-Agent.git\n")
        if args == [
            "fetch", "--no-tags", "origin",
            "refs/heads/main:refs/remotes/origin/main",
        ]:
            return completed(command, fetch_code, stderr="fetch denied" if fetch_code else "")
        if args == ["rev-parse", "--verify", "refs/remotes/origin/main"]:
            return completed(command, stdout="abc123\n")
        if args == ["rev-list", "--left-right", "--count", "HEAD...refs/remotes/origin/main"]:
            return completed(command, stdout="0\t0\n")
        raise AssertionError(f"Unexpected Git command: {args}")

    return runner, commands


def test_repository_sync_fetches_and_indexes_without_changing_checkout(tmp_path: Path):
    indexer = FakeIndexer()
    runner, commands = make_git_runner(tmp_path)
    result = RepositorySyncController(tmp_path, indexer, git_runner=runner).sync()

    assert result.synchronized is True
    assert result.branch == "main"
    assert result.head_sha == result.remote_sha == "abc123"
    assert result.ahead == 0
    assert result.behind == 0
    assert result.index_succeeded is True
    assert indexer.calls[0][0] == "index_repository"
    assert indexer.calls[0][1]["persistence"] is False
    assert [
        "fetch", "--no-tags", "origin",
        "refs/heads/main:refs/remotes/origin/main",
    ] in commands
    forbidden = {"pull", "checkout", "reset", "merge", "push"}
    assert not any(args and args[0] in forbidden for args in commands)


def test_repository_sync_does_not_claim_dirty_or_non_main_checkout_is_synced(tmp_path: Path):
    indexer = FakeIndexer()
    runner, _ = make_git_runner(tmp_path, dirty=" M README.md\n")
    dirty_result = RepositorySyncController(tmp_path, indexer, git_runner=runner).sync()
    assert dirty_result.index_succeeded is True
    assert dirty_result.synchronized is False
    assert dirty_result.working_tree_dirty is True

    runner, _ = make_git_runner(tmp_path, branch="feature/work")
    branch_result = RepositorySyncController(tmp_path, indexer, git_runner=runner).sync()
    assert branch_result.synchronized is False
    assert branch_result.branch == "feature/work"


def test_repository_sync_reports_fetch_failure_but_still_refreshes_index(tmp_path: Path):
    indexer = FakeIndexer()
    runner, _ = make_git_runner(tmp_path, fetch_code=1)
    result = RepositorySyncController(tmp_path, indexer, git_runner=runner).sync()

    assert result.fetch_succeeded is False
    assert result.index_succeeded is True
    assert result.synchronized is False
    assert "fetch denied" in result.error
    assert len(indexer.calls) == 1


def test_repository_sync_blocks_credentialed_or_non_github_origin(tmp_path: Path):
    indexer = FakeIndexer()
    commands = []

    def runner(command, **kwargs):
        args = command[3:]
        commands.append(args)
        if args == ["branch", "--show-current"]:
            return completed(command, stdout="main\n")
        if args == ["rev-parse", "HEAD"]:
            return completed(command, stdout="abc123\n")
        if args == ["status", "--porcelain"]:
            return completed(command, stdout="")
        if args == ["remote", "get-url", "origin"]:
            return completed(
                command,
                stdout="https://user:secret@github.com/Barrot-Agent/B-Agent.git\n",
            )
        raise AssertionError(f"Unexpected Git command: {args}")

    result = RepositorySyncController(tmp_path, indexer, git_runner=runner).sync()

    assert result.fetch_succeeded is False
    assert result.index_succeeded is True
    assert result.remote_url == ""
    assert "credential-free GitHub URL" in result.error
    assert not any(args and args[0] == "fetch" for args in commands)
    assert "secret" not in result.to_dict().__repr__()


def test_repository_sync_rejects_unsafe_branch_name_before_git(tmp_path: Path):
    indexer = FakeIndexer()
    calls = []

    def runner(command, **kwargs):
        calls.append(command)
        return completed(command, stdout="main\n")

    controller = RepositorySyncController(tmp_path, indexer, git_runner=runner)
    with pytest.raises(ValueError, match="Invalid default branch"):
        controller.sync("../main")
    assert calls == []


def test_mcp_catalogue_registers_mit_codebase_memory_with_expected_tools():
    spec = get_server_by_id("codebase-memory")
    assert spec is not None
    assert spec.license == "MIT"
    assert spec.homepage == "https://github.com/DeusData/codebase-memory-mcp"
    inventory = MCPDiscovery()._discover_server(spec)
    tool_names = {tool.name for tool in inventory.tools}
    assert {"index_repository", "sync_repository", "search_graph", "trace_path"} <= tool_names


def test_codebase_memory_adapter_exposes_only_safe_tools(tmp_path: Path, monkeypatch):
    inventory = ServerInventory(
        server_id="codebase-memory",
        name="codebase-memory-mcp",
        description="Local structural code intelligence.",
        version="0.12.1",
        license="MIT",
        homepage="https://github.com/DeusData/codebase-memory-mcp",
        tool_categories=["code_intelligence"],
        tools=[ToolSchema(name="search_graph", description="Search graph")],
        dependencies=[],
        security=SecurityPosture(requires_auth=False, exposed_env_vars=[], risk_level="low"),
    )
    adapter = CodebaseMemoryAdapter(inventory, repo_root=str(tmp_path), binary="cbm")
    monkeypatch.setattr(
        adapter._client,
        "call_tool",
        lambda name, arguments: {"tool": name, "arguments": arguments},
    )

    result = adapter.call_tool("search_graph", project="B-Agent", name_pattern="Sync")
    assert result.success is True
    assert result.data["tool"] == "search_graph"
    assert "delete_project" not in adapter.supported_tools()

    rejected = adapter.call_tool("delete_project", project="B-Agent")
    assert rejected.success is False


def test_codebase_memory_is_present_in_supported_server_catalogue():
    assert any(server.server_id == "codebase-memory" for server in SUPPORTED_MCP_SERVERS)
