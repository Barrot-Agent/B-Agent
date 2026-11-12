"""Coverage for the distributable data and directive-platform packages.

These tests use temporary directories and deterministic local agents only.
They do not invoke external models, deployments, trading or network services.
"""

import json

import pytest

from data import health_check as data_health_check
from data import registry as data_registry
from data import schemas
from directive_platform import (
    Agent,
    AgentRegistry,
    AgentStatus,
    CollaborationSession,
    Directive,
    DirectiveManager,
    DirectivePlatform,
    DirectiveStatus,
    DirectiveType,
    Message,
    MessageType,
    SessionManager,
)


def test_directive_models_round_trip_and_labels():
    agent = Agent(
        agent_id="agent-1",
        name="Analyst",
        description="Local test agent",
        capabilities=["analyze"],
        status=AgentStatus.IDLE,
        created_at=1.0,
    )
    assert Agent.from_dict(agent.to_dict()).to_dict() == agent.to_dict()
    assert "Analyst" in repr(agent)

    directive = Directive(
        directive_id="directive-1",
        title="Reconcile evidence",
        description="Compare independent sources",
        directive_type=DirectiveType.ANALYZE,
        assigned_agent_ids=["agent-1"],
        human_author="Operator",
        status=DirectiveStatus.PENDING,
        created_at=2.0,
        updated_at=3.0,
    )
    assert Directive.from_dict(directive.to_dict()).to_dict() == directive.to_dict()
    assert "Reconcile evidence" in repr(directive)

    message = Message(
        message_id="message-1",
        session_id="session-1",
        sender_id="agent-1",
        sender_name="Analyst",
        content="Evidence reconciled",
        message_type=MessageType.INSIGHT,
        timestamp=4.0,
    )
    assert Message.from_dict(message.to_dict()).to_dict() == message.to_dict()

    session = CollaborationSession(
        session_id="session-1",
        directive_id="directive-1",
        participant_ids=["human", "agent-1"],
        messages=[message],
        status="completed",
        started_at=5.0,
        ended_at=6.0,
    )
    restored = CollaborationSession.from_dict(session.to_dict())
    assert restored.to_dict() == session.to_dict()
    assert "messages=1" in repr(restored)
    assert DirectiveType.label(DirectiveType.ANALYZE)
    assert DirectiveStatus.label(DirectiveStatus.COMPLETED)
    assert AgentStatus.label(AgentStatus.IDLE)
    assert MessageType.HANDOFF in MessageType.ALL


def test_agent_registry_seeds_persists_filters_updates_and_deregisters(tmp_path):
    registry = AgentRegistry(tmp_path / "agents")
    seeded = registry.list_all()
    assert len(seeded) >= 6
    assert registry.get("learner-agent") is not None

    agent = Agent(
        agent_id="local-reviewer",
        name="Local Reviewer",
        description="No network access",
        capabilities=["review", "analyze"],
    )
    assert registry.register(agent) is agent
    assert registry.get(agent.agent_id).to_dict() == agent.to_dict()
    assert registry.find_by_capability("review")[0].agent_id == agent.agent_id

    registry.update_status(agent.agent_id, AgentStatus.ACTIVE, "directive-2")
    updated = registry.get(agent.agent_id)
    assert updated.status == AgentStatus.ACTIVE
    assert updated.current_directive_id == "directive-2"
    assert registry.update_status("missing-agent", AgentStatus.IDLE) is None

    broken = tmp_path / "agents" / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert registry.get("broken") is None
    assert all(item.agent_id != "broken" for item in registry.list_all())
    assert registry.deregister(agent.agent_id) is True
    assert registry.deregister(agent.agent_id) is False


def test_directive_manager_lifecycle_and_invalid_type(tmp_path):
    manager = DirectiveManager(tmp_path / "directives")
    with pytest.raises(ValueError):
        manager.create(
            title="Bad",
            description="Invalid type",
            directive_type="unknown",
            assigned_agent_ids=[],
            human_author="Operator",
        )

    directive = manager.create(
        title="XRP source reconciliation",
        description="Preserve conflicting source vintages",
        directive_type=DirectiveType.CROSS_CORROBORATE,
        assigned_agent_ids=["corroboration-agent"],
        human_author="Operator",
    )
    assert manager.get(directive.directive_id).status == DirectiveStatus.PENDING
    assert manager.list_by_status(DirectiveStatus.PENDING)
    assert manager.update_status(directive.directive_id, DirectiveStatus.ACTIVE) is True
    assert manager.add_result(directive.directive_id, {"result": "disagreement preserved"}) is True
    restored = manager.get(directive.directive_id)
    assert restored.results[0]["result"] == "disagreement preserved"
    assert manager.update_status("missing", DirectiveStatus.FAILED) is False
    assert manager.add_result("missing", {}) is False
    assert manager.delete(directive.directive_id) is True
    assert manager.delete(directive.directive_id) is False


def test_session_manager_persists_messages_filters_and_closes(tmp_path):
    manager = SessionManager(tmp_path / "sessions")
    session = manager.create_session("directive-3", ["human", "analyst-agent"])
    message = Message(
        session_id=session.session_id,
        sender_id="human",
        sender_name="Operator",
        content="Check the data cutoff",
        message_type=MessageType.QUERY,
    )
    assert manager.add_message(session.session_id, message) is True
    assert manager.add_message("missing", message) is False
    assert manager.get_session(session.session_id).messages[0].content == "Check the data cutoff"
    assert manager.list_sessions("directive-3")
    assert manager.list_sessions("other") == []
    assert manager.close_session(session.session_id, "completed") is True
    assert manager.get_session(session.session_id).status == "completed"
    assert manager.close_session("missing") is False
    assert manager.delete(session.session_id) is True
    assert manager.delete(session.session_id) is False


def test_directive_platform_executes_and_persists_local_agent_turns(tmp_path):
    platform = DirectivePlatform(tmp_path / "platform")
    directive = platform.issue_directive(
        title="Reconcile XRP evidence",
        description="Keep independent source groups and counter-evidence",
        directive_type=DirectiveType.ANALYZE,
        agent_ids=["learner-agent", "analyst-agent"],
        human_author="Operator",
    )
    assert directive.status == DirectiveStatus.PENDING
    session = platform.run_directive(directive.directive_id)
    assert session.status == "completed"
    assert session.directive_id == directive.directive_id
    assert any(message.message_type == MessageType.DIRECTIVE for message in session.messages)
    assert any(message.message_type == MessageType.INSIGHT for message in session.messages)
    assert any(message.message_type == MessageType.RESULT for message in session.messages)
    assert platform.directives.get(directive.directive_id).status == DirectiveStatus.COMPLETED
    assert platform.directives.get(directive.directive_id).results
    assert platform.registry.get("learner-agent").status == AgentStatus.IDLE
    assert platform.platform_dir == tmp_path / "platform"


def test_directive_platform_streaming_and_failure_cleanup(tmp_path):
    platform = DirectivePlatform(tmp_path / "streaming")
    directive = platform.issue_directive(
        title="Stream local analysis",
        description="Emit deterministic agent messages",
        directive_type=DirectiveType.LEARN,
        agent_ids=["learner-agent"],
        human_author="Operator",
    )
    events = list(platform.run_directive_streaming(directive.directive_id))
    assert events
    assert events[-1][0].message_type == MessageType.RESULT
    assert platform.directives.get(directive.directive_id).status == DirectiveStatus.COMPLETED

    failed = platform.issue_directive(
        title="Fail safely",
        description="Verify lifecycle cleanup",
        directive_type=DirectiveType.ANALYZE,
        agent_ids=["learner-agent"],
        human_author="Operator",
    )

    def fail_agent_turn(*_args):
        raise RuntimeError("deterministic test failure")

    platform._agent_turn = fail_agent_turn
    with pytest.raises(RuntimeError, match="deterministic test failure"):
        platform.run_directive(failed.directive_id)
    assert platform.directives.get(failed.directive_id).status == DirectiveStatus.FAILED
    failed_session = platform.sessions.list_sessions(failed.directive_id)[0]
    assert failed_session.status == "failed"
    assert platform.registry.get("learner-agent").status == AgentStatus.IDLE
    with pytest.raises(ValueError, match="not found"):
        platform.run_directive("missing-directive")


def test_data_registry_cache_reload_missing_assets_and_health(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(data_registry, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(data_registry, "_FILE_MAP", {"sample": "sample.json", "missing": "missing.json"})
    monkeypatch.setattr(data_registry, "_CACHE", {})
    sample_path = tmp_path / "sample.json"
    sample_path.write_text('{"value": 1}', encoding="utf-8")

    first = data_registry._load("sample")
    assert first == {"value": 1}
    assert data_registry._load("sample") is first
    sample_path.write_text('{"value": 2}', encoding="utf-8")
    assert data_registry._load("sample", force_reload=True) == {"value": 2}
    assert data_registry.list_assets()["sample"]["exists"] is True
    assert data_registry.list_assets()["missing"]["exists"] is False

    assert data_registry.health_check() is False
    assert "MISSING" in capsys.readouterr().out
    data_registry.clear_cache("sample")
    assert "sample" not in data_registry._CACHE
    with pytest.raises(KeyError):
        data_registry._load("unknown")
    with pytest.raises(FileNotFoundError):
        data_registry._load("missing")
    data_registry.clear_cache()
    assert data_registry._CACHE == {}


def test_data_health_topology_schema_checks_and_persistence(tmp_path, monkeypatch, capsys):
    valid_merge = {
        "patterns": [{"pattern_id": "p1", "name": "pattern", "conflict_type": "content"}],
        "scenarios": [],
        "tools": [],
        "best_practices": [],
        "resolution_techniques": [],
        "learning_outcomes": [],
        "knowledge_summary": {},
    }
    assert data_health_check._check_merge_conflict(valid_merge) == []
    assert data_health_check._check_merge_conflict({})

    valid_millennium = {
        "problems": [
            {"number": i, "name": f"Problem {i}", "problem_statement": "Statement", "official_status": "open"}
            for i in range(7)
        ],
        "overview": [],
        "taxonomy": {},
        "search_summaries": {},
    }
    assert data_health_check._check_millennium_problems(valid_millennium) == []
    assert data_health_check._check_millennium_problems({})

    assert data_health_check._check_mmi_monetization(
        {"mmi_recommendations": {}, "monetization_protocols": {}, "council_weights": {}}
    ) == []
    assert data_health_check._check_character_capabilities(
        {"character_database": {}, "discovered_capabilities": {}}
    ) == []

    monkeypatch.setattr(data_health_check, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(
        data_health_check,
        "list_assets",
        lambda: {
            "merge_conflict": {
                "path": str(tmp_path / "merge.json"),
                "exists": True,
                "size_bytes": 10,
                "cached": False,
            }
        },
    )
    monkeypatch.setattr(data_health_check, "_load", lambda _name: valid_merge)
    topology = data_health_check.get_topology()
    assert topology["summary"]["healthy"] is True
    assert topology["assets"]["merge_conflict"]["record_count"] == 1
    assert data_health_check.run_health_check(verbose=False) is True
    output = tmp_path / "topology.json"
    assert data_health_check.save_topology(str(output)) == str(output)
    assert json.loads(output.read_text(encoding="utf-8"))["summary"]["healthy"] is True
    assert "HEALTHY" in capsys.readouterr().out


def test_packaged_data_schema_types_cover_canonical_domains():
    assert {"pattern_id", "name", "conflict_type"}.issubset(schemas.MergeConflictPattern.__annotations__)
    assert {"number", "name", "problem_statement"}.issubset(schemas.MillenniumProblem.__annotations__)
    assert {"recommendations", "total_sources_identified"}.issubset(schemas.MMIRecommendations.__annotations__)
    assert {"protocols", "engine_version"}.issubset(schemas.MonetizationProtocols.__annotations__)
    assert {"target_asset", "council_action"}.issubset(schemas.CouncilWeights.__annotations__)
    assert {"character_database", "discovered_capabilities"}.issubset(
        schemas.CharacterCapabilitiesUnified.__annotations__
    )
