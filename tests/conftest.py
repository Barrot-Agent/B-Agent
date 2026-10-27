"""
Shared pytest fixtures for B-Agent tests.
"""

import pytest

from barrot_agent.config import AppConfig, Environment, ModelConfig


@pytest.fixture
def model_config() -> ModelConfig:
    """Provide a default ModelConfig for tests."""
    return ModelConfig()


@pytest.fixture
def app_config() -> AppConfig:
    """Provide a default AppConfig for tests."""
    return AppConfig(environment=Environment.DEVELOPMENT, debug=True)
