"""
Tests for barrot_agent.core module.
"""

from barrot_agent.config import AppConfig, Environment
from barrot_agent.core import BAgent


class TestBAgent:
    def test_init_default_config(self) -> None:
        agent = BAgent()
        assert agent is not None

    def test_init_custom_config(self, app_config: AppConfig) -> None:
        agent = BAgent(config=app_config)
        assert agent.config == app_config

    def test_get_version(self) -> None:
        agent = BAgent()
        version = agent.get_version()
        assert isinstance(version, str)
        assert len(version) > 0

    def test_get_model_id(self) -> None:
        agent = BAgent()
        model_id = agent.get_model_id()
        assert "granite" in model_id.lower()

    def test_is_debug_default(self) -> None:
        agent = BAgent()
        assert agent.is_debug() is False

    def test_is_debug_enabled(self, app_config: AppConfig) -> None:
        agent = BAgent(config=app_config)
        assert agent.is_debug() is True
