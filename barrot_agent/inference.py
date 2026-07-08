"""
Inference pipeline for B-Agent (IBM Granite 4.0-3B Vision).
"""

from __future__ import annotations

from typing import Any, Optional

from barrot_agent.logger import get_logger
from barrot_agent.models import ModelManager

logger = get_logger(__name__)


class InferencePipeline:
    """Handles image-text inference for the Granite vision model."""

    def __init__(self, model_manager: ModelManager) -> None:
        self.model_manager = model_manager

    def run(
        self,
        prompt: str,
        image: Optional[Any] = None,
        max_new_tokens: int = 512,
    ) -> str:
        """
        Run inference with the loaded model.

        Args:
            prompt: Text prompt for the model
            image: Optional PIL image for vision tasks
            max_new_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        if not self.model_manager.is_loaded:
            raise RuntimeError("Model is not loaded. Call ModelManager.load() first.")

        logger.debug("Running inference | prompt_len=%d", len(prompt))

        model = self.model_manager._model
        processor = self.model_manager._processor

        inputs: dict[str, Any]
        if image is not None:
            inputs = processor(text=prompt, images=image, return_tensors="pt")
        else:
            inputs = processor(text=prompt, return_tensors="pt")

        outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
        result: str = processor.decode(outputs[0], skip_special_tokens=True)

        logger.debug("Inference complete | output_len=%d", len(result))
        return result

    def run_batch(
        self,
        prompts: list[str],
        images: Optional[list[Any]] = None,
        max_new_tokens: int = 512,
    ) -> list[str]:
        """Run inference on a batch of prompts."""
        results = []
        for i, prompt in enumerate(prompts):
            image = images[i] if images and i < len(images) else None
            results.append(self.run(prompt, image=image, max_new_tokens=max_new_tokens))
        return results
