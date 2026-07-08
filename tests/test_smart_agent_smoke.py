"""
Smoke tests for the existing SmartAgent implementation.
"""

from barrot_agent.smart_agent import AgentEventType, SmartAgent


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
