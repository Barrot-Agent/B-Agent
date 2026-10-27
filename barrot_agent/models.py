"""
Model management for B-Agent (IBM Granite 4.0-3B Vision).
"""

from __future__ import annotations

from typing import Any, Optional

from barrot_agent.config import ModelConfig
from barrot_agent.logger import get_logger

logger = get_logger(__name__)

# IBM Granite 4.0-3B Vision model metadata
GRANITE_METADATA = {
    "model_id": "ibm-granite/granite-4.0-3b-vision",
    "parameters": "4B",
    "tensor_type": "BF16",
    "license": "Apache-2.0",
    "downloads_last_month": 5724,
    "likes": 82,
    "tags": [
        "image-text-to-text",
        "transformers",
        "safetensors",
        "english",
        "granite4_vision",
        "feature-extraction",
        "conversational",
        "custom_code",
    ],
    "arxiv_papers": [
        "2603.27064",
        "2404.19205",
        "2412.07626",
        "2512.10888",
        "2208.00385",
        "2502.09927",
        "2406.04334",
    ],
}


class ModelManager:
    """Manages model loading and lifecycle for B-Agent."""

    def __init__(self, config: ModelConfig | None = None) -> None:
        self.config = config or ModelConfig()
        self._model: Optional[Any] = None
        self._processor: Optional[Any] = None
        logger.info("ModelManager initialized for model=%s", self.config.model_id)

    @property
    def is_loaded(self) -> bool:
        """Return whether the model is currently loaded."""
        return self._model is not None

    def get_metadata(self) -> dict:
        """Return model metadata."""
        return GRANITE_METADATA.copy()

    def load(self) -> None:
        """Load the model and processor from Hugging Face."""
        try:
            import torch
            from transformers import AutoModelForVision2Seq, AutoProcessor

            logger.info("Loading model %s ...", self.config.model_id)

            load_kwargs: dict[str, Any] = {
                "trust_remote_code": self.config.trust_remote_code,
            }

            if self.config.load_in_8bit:
                load_kwargs["load_in_8bit"] = True
            elif self.config.load_in_4bit:
                load_kwargs["load_in_4bit"] = True
            elif self.config.tensor_type == "bf16":
                load_kwargs["torch_dtype"] = torch.bfloat16

            if self.config.device != "auto":
                load_kwargs["device_map"] = self.config.device
            else:
                load_kwargs["device_map"] = "auto"

            self._processor = AutoProcessor.from_pretrained(
                self.config.model_id,
                trust_remote_code=self.config.trust_remote_code,
                revision=self.config.model_revision,
            )
            self._model = AutoModelForVision2Seq.from_pretrained(
                self.config.model_id,
                revision=self.config.model_revision,
                **load_kwargs,
            )
            logger.info("Model loaded successfully.")
        except ImportError as exc:
            logger.error("Required library not available: %s", exc)
            raise
        except Exception as exc:
            logger.error("Failed to load model: %s", exc)
            raise

    def unload(self) -> None:
        """Unload the model to free memory."""
        if self._model is not None:
            del self._model
            self._model = None
        if self._processor is not None:
            del self._processor
            self._processor = None
        logger.info("Model unloaded.")
