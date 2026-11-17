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

# This deliberately invalid module is a static fixture for repo_guard tests.
# Keep it available as data, but never import it during pytest collection.
collect_ignore = ["fixtures/guard/root/tests/test_bad_import.py"]
