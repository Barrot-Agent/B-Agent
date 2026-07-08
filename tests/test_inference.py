"""
Tests for barrot_agent.inference module.
"""

from unittest.mock import MagicMock

import pytest

from barrot_agent.inference import InferencePipeline
from barrot_agent.models import ModelManager


class TestInferencePipeline:
    def test_init(self) -> None:
        manager = MagicMock(spec=ModelManager)
        pipeline = InferencePipeline(model_manager=manager)
        assert pipeline.model_manager is manager

    def test_run_raises_when_not_loaded(self) -> None:
        manager = MagicMock(spec=ModelManager)
        manager.is_loaded = False
        pipeline = InferencePipeline(model_manager=manager)
        with pytest.raises(RuntimeError, match="Model is not loaded"):
            pipeline.run("hello")

    def test_run_text_only(self) -> None:
        manager = MagicMock(spec=ModelManager)
        manager.is_loaded = True

        mock_processor = MagicMock()
        mock_model = MagicMock()
        mock_processor.return_value = {"input_ids": MagicMock()}
        mock_processor.decode.return_value = "generated text"
        mock_model.generate.return_value = [MagicMock()]

        manager._processor = mock_processor
        manager._model = mock_model

        pipeline = InferencePipeline(model_manager=manager)
        result = pipeline.run("test prompt")
        assert result == "generated text"

    def test_run_with_image(self) -> None:
        manager = MagicMock(spec=ModelManager)
        manager.is_loaded = True

        mock_processor = MagicMock()
        mock_model = MagicMock()
        mock_processor.return_value = {"input_ids": MagicMock()}
        mock_processor.decode.return_value = "image result"
        mock_model.generate.return_value = [MagicMock()]

        manager._processor = mock_processor
        manager._model = mock_model

        pipeline = InferencePipeline(model_manager=manager)
        fake_image = MagicMock()
        result = pipeline.run("describe this image", image=fake_image)
        assert result == "image result"

    def test_run_batch(self) -> None:
        manager = MagicMock(spec=ModelManager)
        manager.is_loaded = True

        mock_processor = MagicMock()
        mock_model = MagicMock()
        mock_processor.return_value = {"input_ids": MagicMock()}
        mock_processor.decode.return_value = "batch result"
        mock_model.generate.return_value = [MagicMock()]

        manager._processor = mock_processor
        manager._model = mock_model

        pipeline = InferencePipeline(model_manager=manager)
        results = pipeline.run_batch(["prompt 1", "prompt 2"])
        assert len(results) == 2

    def test_run_batch_with_images(self) -> None:
        manager = MagicMock(spec=ModelManager)
        manager.is_loaded = True

        mock_processor = MagicMock()
        mock_model = MagicMock()
        mock_processor.return_value = {"input_ids": MagicMock()}
        mock_processor.decode.return_value = "output"
        mock_model.generate.return_value = [MagicMock()]

        manager._processor = mock_processor
        manager._model = mock_model

        pipeline = InferencePipeline(model_manager=manager)
        images = [MagicMock(), MagicMock()]
        results = pipeline.run_batch(["p1", "p2"], images=images)
        assert len(results) == 2
