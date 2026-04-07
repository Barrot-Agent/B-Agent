"""
Tests for barrot_agent.models module.
"""

import pytest

from barrot_agent.config import ModelConfig
from barrot_agent.models import GRANITE_METADATA, ModelManager


class TestGraniteMetadata:
    def test_metadata_has_model_id(self) -> None:
        assert GRANITE_METADATA["model_id"] == "ibm-granite/granite-4.0-3b-vision"

    def test_metadata_has_parameters(self) -> None:
        assert GRANITE_METADATA["parameters"] == "4B"

    def test_metadata_has_tensor_type(self) -> None:
        assert GRANITE_METADATA["tensor_type"] == "BF16"

    def test_metadata_has_license(self) -> None:
        assert GRANITE_METADATA["license"] == "Apache-2.0"

    def test_metadata_arxiv_papers(self) -> None:
        assert len(GRANITE_METADATA["arxiv_papers"]) == 7

    def test_metadata_tags(self) -> None:
        tags = GRANITE_METADATA["tags"]
        assert "image-text-to-text" in tags
        assert "conversational" in tags
        assert "feature-extraction" in tags


class TestModelManager:
    def test_init(self, model_config: ModelConfig) -> None:
        manager = ModelManager(config=model_config)
        assert manager is not None

    def test_not_loaded_initially(self, model_config: ModelConfig) -> None:
        manager = ModelManager(config=model_config)
        assert manager.is_loaded is False

    def test_get_metadata_returns_copy(self, model_config: ModelConfig) -> None:
        manager = ModelManager(config=model_config)
        meta1 = manager.get_metadata()
        meta2 = manager.get_metadata()
        assert meta1 == meta2
        assert meta1 is not meta2

    def test_unload_when_not_loaded(self, model_config: ModelConfig) -> None:
        manager = ModelManager(config=model_config)
        manager.unload()  # Should not raise
        assert manager.is_loaded is False
