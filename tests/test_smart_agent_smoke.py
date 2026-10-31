"""
Smoke tests for the existing SmartAgent implementation.
"""

import pytest

from barrot_agent.smart_agent import AgentEventType, SmartAgent, ToolResult, _BuiltinTools


class TestSmartAgentSmoke:
    def test_run_produces_final_answer(self) -> None:
        agent = SmartAgent()

        events = list(agent.run("Summarize how this repository works"))

        assert events[0].type == AgentEventType.GOAL
        assert events[-1].type == AgentEventType.ANSWER
        assert "Task Complete" in events[-1].content

    def test_empty_goal_returns_error(self) -> None:
        agent = SmartAgent()

        events = list(agent.run("   "))

        assert len(events) == 1
        assert events[0].type == AgentEventType.ERROR


class TestRepoHuntTool:
    """Unit tests for the _BuiltinTools.repo_hunt static method."""

    def test_both_mode_returns_contribute_and_integrate(self) -> None:
        result = _BuiltinTools.repo_hunt(topic="AI agents", mode="both")

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.tool_name == "repo_hunt"
        assert "🔧" in result.output
        assert "🔌" in result.output
        assert result.metadata["contribute_count"] == 4
        assert result.metadata["integrate_count"] == 4

    def test_contribute_mode_omits_integrate_section(self) -> None:
        result = _BuiltinTools.repo_hunt(topic="open source", mode="contribute")

        assert result.success is True
        assert "🔧" in result.output
        assert "🔌" not in result.output
        assert result.metadata["contribute_count"] == 4
        assert result.metadata["integrate_count"] == 0

    def test_integrate_mode_omits_contribute_section(self) -> None:
        result = _BuiltinTools.repo_hunt(topic="open source", mode="integrate")

        assert result.success is True
        assert "🔌" in result.output
        assert "🔧" not in result.output
        assert result.metadata["contribute_count"] == 0
        assert result.metadata["integrate_count"] == 4

    def test_deterministic_for_same_topic(self) -> None:
        r1 = _BuiltinTools.repo_hunt(topic="LLM tooling")
        r2 = _BuiltinTools.repo_hunt(topic="LLM tooling")

        # Output lines should be identical (excluding call_id which is random)
        assert r1.output == r2.output

    def test_different_topics_produce_different_outputs(self) -> None:
        r1 = _BuiltinTools.repo_hunt(topic="robotics")
        r2 = _BuiltinTools.repo_hunt(topic="bioinformatics")

        # At minimum one of the selected repos should differ
        assert r1.output != r2.output

    def test_metadata_contains_topic(self) -> None:
        result = _BuiltinTools.repo_hunt(topic="search engine")

        assert result.metadata["topic"] == "search engine"
        assert result.metadata["mode"] == "both"


class TestRepoHuntSmartAgent:
    """Integration tests: SmartAgent routing and execution for repo-hunt goals."""

    @pytest.mark.parametrize(
        "goal",
        [
            "repo hunt for AI agent frameworks",
            "find repos we could contribute to",
            "hunt repos to integrate with",
            "github repos to contribute to and integrate with",
        ],
    )
    def test_repo_hunt_goal_produces_final_answer(self, goal: str) -> None:
        agent = SmartAgent()
        events = list(agent.run(goal))

        assert events[0].type == AgentEventType.GOAL
        assert events[-1].type == AgentEventType.ANSWER
        assert "Task Complete" in events[-1].content

    def test_repo_hunt_goal_uses_repo_hunt_tool(self) -> None:
        agent = SmartAgent()
        events = list(agent.run("repo hunt for potential GitHub integrations"))

        tool_result_events = [e for e in events if e.type == AgentEventType.TOOL_RESULT]
        tool_names = [e.data.get("tool") for e in tool_result_events]

        assert "repo_hunt" in tool_names

    def test_repo_hunt_tool_result_contains_repo_sections(self) -> None:
        agent = SmartAgent()
        events = list(agent.run("repo hunt for AI agent integrations"))

        tool_result_events = [
            e
            for e in events
            if e.type == AgentEventType.TOOL_RESULT and e.data.get("tool") == "repo_hunt"
        ]

        assert len(tool_result_events) == 1
        output = tool_result_events[0].content
        assert "🔧" in output or "🔌" in output
