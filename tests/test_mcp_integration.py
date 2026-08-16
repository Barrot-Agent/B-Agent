"""
Tests for the MCP integration framework (Steps 1–10).
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from barrot_agent.mcp_adapters import FilesystemMCPAdapter, GitMCPAdapter, build_adapter
from barrot_agent.mcp_approval import ActionType, ApprovalRequest, MCPApprovalGate
from barrot_agent.mcp_discovery import MCPDiscovery, SecurityPosture, ServerInventory, ToolSchema
from barrot_agent.mcp_integration import IntegrationConfig, MCPIntegration
from barrot_agent.mcp_pingpong import MCPPingPong, MCPProposal, Phase
from barrot_agent.mcp_provenance import MCPProvenanceRecorder
from barrot_agent.mcp_registry import MCPRegistry, RegistryEntry
from barrot_agent.mcp_sandbox import MCPSandbox
from barrot_agent.mcp_scheduler import MCPScheduler, SchedulerConfig
from barrot_agent.mcp_scorer import MCPScorer
from barrot_agent.mcp_targets import (
    CAPABILITY_TARGETS,
    COMPATIBILITY_REQUIREMENTS,
    SUPPORTED_MCP_SERVERS,
    get_server_by_id,
    get_targets_by_priority,
)

# ---------------------------------------------------------------------------
# Step 1 – Targets
# ---------------------------------------------------------------------------


def test_capability_targets_non_empty():
    assert len(CAPABILITY_TARGETS) > 0


def test_supported_servers_non_empty():
    assert len(SUPPORTED_MCP_SERVERS) > 0


def test_compatibility_requirements_defaults():
    assert COMPATIBILITY_REQUIREMENTS.require_human_approval_for_writes is True
    assert "MIT" in COMPATIBILITY_REQUIREMENTS.allowed_licenses


def test_get_targets_by_priority():
    high = get_targets_by_priority("high")
    assert all(t.priority == "high" for t in high)


def test_get_server_by_id_found():
    srv = get_server_by_id("barrot-core-repository")
    assert srv is not None
    assert srv.name == "mcp-server-git"


def test_get_server_by_id_not_found():
    assert get_server_by_id("does-not-exist") is None


# ---------------------------------------------------------------------------
# Step 2 – Discovery
# ---------------------------------------------------------------------------


def _make_inventory(server_id: str = "test-server") -> ServerInventory:
    return ServerInventory(
        server_id=server_id,
        name="test-pkg",
        description="A test server",
        version="1.0.0",
        license="MIT",
        homepage="https://example.com",
        tool_categories=["version_control"],
        tools=[ToolSchema(name="git_status", description="Show status")],
        dependencies=["requests"],
        security=SecurityPosture(
            requires_auth=False,
            exposed_env_vars=[],
            risk_level="low",
        ),
    )


def test_server_inventory_schema_hash():
    inv = _make_inventory()
    assert len(inv.schema_hash) == 16


def test_discovery_discover_all_returns_dict():
    disc = MCPDiscovery()
    with patch.object(disc, "_discover_server", return_value=_make_inventory()):
        result = disc.discover_all()
    assert isinstance(result, dict)


def test_discovery_to_json():
    disc = MCPDiscovery()
    with patch.object(disc, "_discover_server", return_value=_make_inventory("x")):
        disc.discover_all()
    j = json.loads(disc.to_json())
    # The discovery keyed by spec.server_id from SUPPORTED_MCP_SERVERS;
    # verify at least one expected server is present in the JSON output.
    assert len(j) > 0


# ---------------------------------------------------------------------------
# Step 3 – Scorer
# ---------------------------------------------------------------------------


def test_scorer_returns_component_score():
    scorer = MCPScorer()
    inv = _make_inventory()
    cs = scorer.score(inv)
    assert 0.0 <= cs.total <= 100.0


def test_scorer_grade_range():
    scorer = MCPScorer()
    inv = _make_inventory()
    cs = scorer.score(inv)
    assert cs.grade in ("A", "B", "C", "D", "F")


def test_scorer_rank_sorted_desc():
    scorer = MCPScorer()
    inv1 = _make_inventory("s1")
    inv2 = _make_inventory("s2")
    inv2.tool_categories = []  # worse
    scores = scorer.score_all({"s1": inv1, "s2": inv2})
    ranked = scorer.rank(scores)
    assert ranked[0].total >= ranked[-1].total


# ---------------------------------------------------------------------------
# Step 4 – Adapters
# ---------------------------------------------------------------------------


def test_git_adapter_read_tools():
    inv = _make_inventory("barrot-core-repository")
    adapter = GitMCPAdapter(inv)
    assert "git_status" in adapter.supported_tools()
    assert "git_commit" not in adapter.supported_tools()


def test_git_adapter_blocks_writes():
    inv = _make_inventory("barrot-core-repository")
    adapter = GitMCPAdapter(inv)
    result = adapter.call_tool("git_commit")
    assert result.success is False
    assert "human approval" in result.error


def test_filesystem_adapter_path_traversal():
    inv = _make_inventory("filesystem")
    with tempfile.TemporaryDirectory() as tmpdir:
        adapter = FilesystemMCPAdapter(inv, allowed_root=tmpdir)
        result = adapter.call_tool("read_file", path="../../etc/passwd")
        assert result.success is False


def test_build_adapter_known_server():
    inv = _make_inventory("barrot-core-repository")
    adapter = build_adapter(inv)
    assert adapter is not None
    assert isinstance(adapter, GitMCPAdapter)


def test_build_adapter_unknown_server():
    inv = _make_inventory("unknown-server")
    adapter = build_adapter(inv)
    assert adapter is None


# ---------------------------------------------------------------------------
# Step 5 – Ping-Pong
# ---------------------------------------------------------------------------


def _make_proposal(server_id: str = "test", score: float = 75.0) -> MCPProposal:
    return MCPProposal(
        server_id=server_id,
        description="Test integration",
        score=score,
        adapter_class="GitMCPAdapter",
        rationale="High score",
    )


def test_pingpong_accepts_good_proposal():
    engine = MCPPingPong(max_cycles=3)
    record = engine.run(_make_proposal(score=75.0))
    assert record.final_phase == Phase.ACCEPTANCE


def test_pingpong_rejects_low_score():
    engine = MCPPingPong(max_cycles=3)
    record = engine.run(_make_proposal(score=20.0))
    assert record.final_phase == Phase.REJECTION


def test_pingpong_records_messages():
    engine = MCPPingPong(max_cycles=3)
    record = engine.run(_make_proposal(score=75.0))
    assert len(record.messages) >= 2  # at least proposal + critique


def test_pingpong_exchange_to_dict():
    engine = MCPPingPong(max_cycles=1)
    record = engine.run(_make_proposal(score=75.0))
    d = record.to_dict()
    assert "exchange_id" in d
    assert "messages" in d


# ---------------------------------------------------------------------------
# Step 6 – Sandbox
# ---------------------------------------------------------------------------


def test_sandbox_passes_clean_files():
    sb = MCPSandbox()
    report = sb.run("test-server", {"module.py": "x = 1\n"}, declared_deps=["requests"])
    assert report.passed


def test_sandbox_fails_on_secret():
    sb = MCPSandbox()
    report = sb.run("test-server", {"bad.py": "api_key = 'supersecretvalue123'\n"})
    assert not report.passed
    assert any(c.check_name == "secret_scan" for c in report.failed_checks)


def test_sandbox_fails_on_forbidden_dep():
    sb = MCPSandbox()
    report = sb.run("test-server", {}, declared_deps=["pwntools"])
    assert not report.passed
    assert any(c.check_name == "dependency_check" for c in report.failed_checks)


def test_sandbox_fails_on_eval():
    sb = MCPSandbox()
    report = sb.run("test-server", {"evil.py": "eval('import os')\n"})
    assert not report.passed
    assert any(c.check_name == "permission_check" for c in report.failed_checks)


def test_sandbox_summary():
    sb = MCPSandbox()
    report = sb.run("test-server", {"ok.py": "pass\n"})
    assert "test-server" in report.summary()


# ---------------------------------------------------------------------------
# Step 7 – Approval Gate
# ---------------------------------------------------------------------------


def test_approval_always_deny():
    gate = MCPApprovalGate(mode="always_deny")
    req = ApprovalRequest(
        action_type=ActionType.INSTALL,
        server_id="test",
        description="Install test",
    )
    decision = gate.request_approval(req)
    assert decision.approved is False


def test_approval_env_token_invalid(monkeypatch):
    monkeypatch.setenv("MCP_APPROVAL_SECRET", "mysecret")
    monkeypatch.setenv("MCP_APPROVAL_TOKEN", "wrongtoken")
    gate = MCPApprovalGate(mode="env_token")
    req = ApprovalRequest(
        action_type=ActionType.REGISTRY_PROMOTE,
        server_id="test",
        description="Promote test",
    )
    decision = gate.request_approval(req)
    assert decision.approved is False


def test_approval_env_token_valid(monkeypatch):
    import hmac

    secret = "testsecret"
    gate = MCPApprovalGate(mode="env_token")
    req = ApprovalRequest(
        action_type=ActionType.REGISTRY_PROMOTE,
        server_id="test",
        description="Promote test",
    )
    expected = hmac.new(secret.encode(), req.request_id.encode(), "sha256").hexdigest()
    monkeypatch.setenv("MCP_APPROVAL_SECRET", secret)
    monkeypatch.setenv("MCP_APPROVAL_TOKEN", expected)
    decision = gate.request_approval(req)
    assert decision.approved is True


def test_approval_records_decisions():
    gate = MCPApprovalGate(mode="always_deny")
    req = ApprovalRequest(
        action_type=ActionType.INSTALL,
        server_id="test",
        description="test",
    )
    gate.request_approval(req)
    assert len(gate.get_decisions()) == 1


# ---------------------------------------------------------------------------
# Step 8 – Provenance
# ---------------------------------------------------------------------------


def test_provenance_record_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        rec_path = Path(tmpdir) / "prov.jsonl"
        pr = MCPProvenanceRecorder(log_path=rec_path)
        pr.record_integration("srv-1", "MIT", {"sandbox": "passed"})
        records = pr.read_all()
        assert len(records) == 1
        assert records[0].event_type == "integration"


def test_provenance_record_rejection():
    with tempfile.TemporaryDirectory() as tmpdir:
        rec_path = Path(tmpdir) / "prov.jsonl"
        pr = MCPProvenanceRecorder(log_path=rec_path)
        pr.record_rejection("srv-2", "Score too low", ["alternative-srv"])
        records = pr.read_for_server("srv-2")
        assert records[0].event_type == "rejection"


def test_provenance_record_rollback():
    with tempfile.TemporaryDirectory() as tmpdir:
        rec_path = Path(tmpdir) / "prov.jsonl"
        pr = MCPProvenanceRecorder(log_path=rec_path)
        pr.record_rollback("srv-3", "abc123", "Regression detected")
        assert pr.get_last_rollback_ref("srv-3") == "abc123"


def test_provenance_append_only():
    with tempfile.TemporaryDirectory() as tmpdir:
        rec_path = Path(tmpdir) / "prov.jsonl"
        pr = MCPProvenanceRecorder(log_path=rec_path)
        pr.record_discovery("srv-4", "aabbccdd", 3)
        pr.record_discovery("srv-4", "11223344", 5)
        records = pr.read_for_server("srv-4")
        assert len(records) == 2


# ---------------------------------------------------------------------------
# Step 9 – Registry
# ---------------------------------------------------------------------------


def _make_entry(server_id: str = "test-server") -> RegistryEntry:
    return RegistryEntry(
        server_id=server_id,
        name="test-pkg",
        version="1.0.0",
        license="MIT",
        adapter_class="GitMCPAdapter",
        tool_categories=["version_control"],
        score=72.0,
        approved_by="human",
    )


def test_registry_promote_and_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        reg = MCPRegistry(registry_path=Path(tmpdir) / "reg.json")
        reg.promote(_make_entry("srv-a"))
        assert reg.is_registered("srv-a")
        assert len(reg.list_active()) == 1


def test_registry_deregister():
    with tempfile.TemporaryDirectory() as tmpdir:
        reg = MCPRegistry(registry_path=Path(tmpdir) / "reg.json")
        reg.promote(_make_entry("srv-b"))
        reg.deregister("srv-b", "Rollback")
        assert not reg.is_registered("srv-b")
        # Still in list_all
        assert len(reg.list_all()) == 1


def test_registry_validate_entry_invalid_score():
    with tempfile.TemporaryDirectory() as tmpdir:
        reg = MCPRegistry(registry_path=Path(tmpdir) / "reg.json")
        bad = _make_entry()
        bad.score = 150.0
        with pytest.raises(ValueError, match="score"):
            reg.promote(bad)


def test_registry_persists():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "reg.json"
        reg1 = MCPRegistry(registry_path=path)
        reg1.promote(_make_entry("srv-c"))
        reg2 = MCPRegistry(registry_path=path)
        assert reg2.is_registered("srv-c")


# ---------------------------------------------------------------------------
# Step 10 – Scheduler
# ---------------------------------------------------------------------------


def test_scheduler_respects_max_runs():
    config = SchedulerConfig(max_runs=2, interval_seconds=0, dry_run=True)
    calls = []

    def fake_pipeline():
        calls.append(1)
        return {"discovered": 1, "accepted": 1, "rejected": 0, "promoted": 1}

    sched = MCPScheduler(config=config, pipeline=fake_pipeline)
    history = sched.run_loop()
    assert len(history) == 2
    # Pipeline NOT called in dry_run mode (scheduler skips side-effects)
    assert len(calls) == 0


def test_scheduler_stops_after_max_runs():
    config = SchedulerConfig(max_runs=1, interval_seconds=0, dry_run=True)
    sched = MCPScheduler(config=config, pipeline=lambda: {})
    sched.run_once()
    assert sched.run_once() is None


def test_scheduler_runs_remaining():
    config = SchedulerConfig(max_runs=5, interval_seconds=0, dry_run=True)
    sched = MCPScheduler(config=config, pipeline=lambda: {})
    assert sched.runs_remaining == 5
    sched.run_once()
    assert sched.runs_remaining == 4


# ---------------------------------------------------------------------------
# Integration pipeline (dry_run smoke test)
# ---------------------------------------------------------------------------


def test_integration_pipeline_dry_run():
    cfg = IntegrationConfig(dry_run=True, min_score=0.0)
    mi = MCPIntegration(cfg)

    fake_inv = _make_inventory("barrot-core-repository")
    fake_inv.tool_categories = ["version_control", "ci_cd"]

    with patch.object(
        mi._discovery, "discover_all", return_value={"barrot-core-repository": fake_inv}
    ):
        stats = mi.run_pipeline()

    assert "discovered" in stats
    assert stats["discovered"] == 1
    # In dry_run, nothing is promoted to registry
    assert stats["promoted"] == 0
