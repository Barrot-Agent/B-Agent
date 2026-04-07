"""
Tests for barrot_agent.config module.
"""

import os

import pytest

from barrot_agent.config import AppConfig, Environment, ModelConfig, get_config


class TestModelConfig:
    def test_default_model_id(self, model_config: ModelConfig) -> None:
        assert model_config.model_id == "ibm-granite/granite-4.0-3b-vision"

    def test_default_tensor_type(self, model_config: ModelConfig) -> None:
        assert model_config.tensor_type == "bf16"

    def test_default_max_new_tokens(self, model_config: ModelConfig) -> None:
        assert model_config.max_new_tokens == 512

    def test_temperature_range(self) -> None:
        cfg = ModelConfig(temperature=0.5)
        assert cfg.temperature == 0.5

    def test_temperature_out_of_range(self) -> None:
        with pytest.raises(Exception):
            ModelConfig(temperature=3.0)


class TestAppConfig:
    def test_default_environment(self, app_config: AppConfig) -> None:
        assert app_config.environment == Environment.DEVELOPMENT

    def test_debug_mode(self, app_config: AppConfig) -> None:
        assert app_config.debug is True

    def test_app_name(self, app_config: AppConfig) -> None:
        assert app_config.app_name == "B-Agent"

    def test_environment_values(self) -> None:
        assert Environment.DEVELOPMENT == "development"
        assert Environment.STAGING == "staging"
        assert Environment.PRODUCTION == "production"

    def test_model_nested_config(self, app_config: AppConfig) -> None:
        assert app_config.model.model_id == "ibm-granite/granite-4.0-3b-vision"

    def test_get_config_returns_appconfig(self) -> None:
        cfg = get_config()
        assert isinstance(cfg, AppConfig)
