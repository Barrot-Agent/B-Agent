"""
IBM Granite 4.0-3b-vision — Image-Text-to-Text Pipeline
Handles multimodal vision-language inference with BF16 precision.
"""

from __future__ import annotations

from typing import List, Optional, Union

from granite_model_config import (
    INFERENCE_CONFIG,
    LOAD_CONFIG,
    MODEL_ID,
    MODEL_METADATA,
)


def _load_model_and_processor(model_id: str = MODEL_ID):
    """Load the Granite vision model and processor."""
    import torch
    from transformers import AutoModelForVision2Seq, AutoProcessor

    processor = AutoProcessor.from_pretrained(
        model_id,
        trust_remote_code=LOAD_CONFIG["trust_remote_code"],
    )

    dtype = getattr(torch, LOAD_CONFIG["torch_dtype"])
    model = AutoModelForVision2Seq.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map=LOAD_CONFIG["device_map"],
        trust_remote_code=LOAD_CONFIG["trust_remote_code"],
    )
    model.eval()
    return model, processor


class GraniteVisionPipeline:
    """
    Image-Text-to-Text pipeline for ibm-granite/granite-4.0-3b-vision.

    Supports:
    - Single image + text prompt
    - Multi-turn conversation with chat template
    - Feature extraction mode (returns hidden states)
    - BF16 tensor precision
    """

    def __init__(self, model_id: str = MODEL_ID):
        self.model_id = model_id
        self.model = None
        self.processor = None
        self._loaded = False

    # ------------------------------------------------------------------
    # Lazy loading
    # ------------------------------------------------------------------

    def load(self) -> "GraniteVisionPipeline":
        """Explicitly load the model weights into memory."""
        self.model, self.processor = _load_model_and_processor(self.model_id)
        self._loaded = True
        return self

    def _ensure_loaded(self):
        if not self._loaded:
            self.load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        prompt: str,
        images: Optional[Union[str, List[str]]] = None,
        max_new_tokens: int = INFERENCE_CONFIG["max_new_tokens"],
        do_sample: bool = INFERENCE_CONFIG["do_sample"],
        **generation_kwargs,
    ) -> str:
        """
        Run image-text-to-text inference.

        Args:
            prompt: Text prompt or question about the image(s).
            images: Path(s) to image file(s), URL(s), or PIL Image object(s).
            max_new_tokens: Maximum tokens to generate.
            do_sample: Whether to use sampling during generation.
            **generation_kwargs: Additional keyword arguments forwarded to
                ``model.generate()``.

        Returns:
            Generated text response.
        """
        self._ensure_loaded()
        import torch
        from PIL import Image

        loaded_images = _load_images(images) if images is not None else []

        messages = _build_messages(prompt, has_images=bool(loaded_images))
        text_input = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
        )

        inputs = self.processor(
            text=text_input,
            images=loaded_images if loaded_images else None,
            return_tensors="pt",
        ).to(self.model.device)

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                **generation_kwargs,
            )

        input_len = inputs["input_ids"].shape[-1]
        new_tokens = output_ids[:, input_len:]
        return self.processor.decode(new_tokens[0], skip_special_tokens=True)

    def extract_features(
        self,
        prompt: str,
        images: Optional[Union[str, List[str]]] = None,
    ):
        """
        Extract vision-language embeddings (last hidden state).

        Returns:
            torch.Tensor of shape (1, seq_len, hidden_dim) in BF16.
        """
        self._ensure_loaded()
        import torch
        from PIL import Image

        loaded_images = _load_images(images) if images is not None else []

        messages = _build_messages(prompt, has_images=bool(loaded_images))
        text_input = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=False,
        )

        inputs = self.processor(
            text=text_input,
            images=loaded_images if loaded_images else None,
            return_tensors="pt",
        ).to(self.model.device)

        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)

        return outputs.hidden_states[-1]

    # ------------------------------------------------------------------
    # Conversational helper
    # ------------------------------------------------------------------

    def chat(
        self,
        conversation: List[dict],
        images: Optional[Union[str, List[str]]] = None,
        max_new_tokens: int = INFERENCE_CONFIG["max_new_tokens"],
    ) -> str:
        """
        Multi-turn chat using the Granite chat template.

        Args:
            conversation: List of ``{"role": ..., "content": ...}`` dicts.
            images: Image(s) referenced in the conversation.
            max_new_tokens: Maximum tokens to generate.

        Returns:
            Model response as a string.
        """
        self._ensure_loaded()
        import torch

        loaded_images = _load_images(images) if images is not None else []

        text_input = self.processor.apply_chat_template(
            conversation,
            add_generation_prompt=True,
        )

        inputs = self.processor(
            text=text_input,
            images=loaded_images if loaded_images else None,
            return_tensors="pt",
        ).to(self.model.device)

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
            )

        input_len = inputs["input_ids"].shape[-1]
        new_tokens = output_ids[:, input_len:]
        return self.processor.decode(new_tokens[0], skip_special_tokens=True)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @staticmethod
    def model_info() -> dict:
        """Return model metadata from the Hugging Face model card."""
        return MODEL_METADATA


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _load_images(images):
    """Accept file paths, URLs, or PIL Image objects and return a list of PIL Images."""
    import requests
    from PIL import Image

    if not isinstance(images, list):
        images = [images]

    result = []
    for img in images:
        if hasattr(img, "save"):  # already a PIL Image
            result.append(img)
        elif isinstance(img, str) and img.startswith("http"):
            response = requests.get(img, stream=True, timeout=30)
            response.raise_for_status()
            result.append(Image.open(response.raw).convert("RGB"))
        else:
            result.append(Image.open(img).convert("RGB"))
    return result


def _build_messages(prompt: str, has_images: bool) -> list:
    """Build a minimal single-turn message list."""
    content = []
    if has_images:
        content.append({"type": "image"})
    content.append({"type": "text", "text": prompt})
    return [{"role": "user", "content": content}]
