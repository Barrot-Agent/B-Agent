"""
IBM Granite 4.0-3b-vision — Inference Provider
Provides a simple, high-level interface for Image-Text-to-Text inference,
compatible with the Barrot-Agent infrastructure.
"""

from __future__ import annotations

from typing import List, Optional, Union

from granite_model_config import ARXIV_REFERENCES, CAPABILITIES, MODEL_ID, MODEL_METADATA
from vision_pipeline import GraniteVisionPipeline

# Module-level singleton – shared across calls within a process
_pipeline: Optional[GraniteVisionPipeline] = None


def _get_pipeline() -> GraniteVisionPipeline:
    """Return (and lazily initialise) the shared pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = GraniteVisionPipeline(MODEL_ID)
        _pipeline.load()
    return _pipeline


# ---------------------------------------------------------------------------
# Public inference API
# ---------------------------------------------------------------------------


def infer(
    prompt: str,
    images: Optional[Union[str, List[str]]] = None,
    max_new_tokens: int = 1024,
    do_sample: bool = False,
) -> str:
    """
    Run Image-Text-to-Text inference with ibm-granite/granite-4.0-3b-vision.

    Args:
        prompt: Text prompt or question.
        images: Path(s) to image file(s), URL(s), or PIL Image object(s).
        max_new_tokens: Maximum number of tokens to generate.
        do_sample: Whether to use sampling (False = greedy/beam).

    Returns:
        Generated text response.

    Example::

        from inference_provider import infer
        response = infer("Describe this image.", images="photo.jpg")
        print(response)
    """
    pipeline = _get_pipeline()
    return pipeline.run(
        prompt=prompt,
        images=images,
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
    )


def chat(
    conversation: List[dict],
    images: Optional[Union[str, List[str]]] = None,
    max_new_tokens: int = 1024,
) -> str:
    """
    Multi-turn conversational inference using the Granite chat template.

    Args:
        conversation: List of ``{"role": ..., "content": ...}`` message dicts.
        images: Optional image(s) referenced in the conversation.
        max_new_tokens: Maximum number of tokens to generate.

    Returns:
        Model reply as a plain string.

    Example::

        from inference_provider import chat
        reply = chat(
            conversation=[{"role": "user", "content": "What do you see?"}],
            images="photo.jpg",
        )
        print(reply)
    """
    pipeline = _get_pipeline()
    return pipeline.chat(
        conversation=conversation,
        images=images,
        max_new_tokens=max_new_tokens,
    )


def extract_features(
    prompt: str,
    images: Optional[Union[str, List[str]]] = None,
):
    """
    Extract vision-language embeddings from the model's last hidden layer.

    Args:
        prompt: Text to embed alongside the image(s).
        images: Optional image(s).

    Returns:
        ``torch.Tensor`` of shape ``(1, seq_len, hidden_dim)`` in BF16.
    """
    pipeline = _get_pipeline()
    return pipeline.extract_features(prompt=prompt, images=images)


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------


def get_model_info() -> dict:
    """Return the full model card metadata dict."""
    return {
        **MODEL_METADATA,
        "capabilities": CAPABILITIES,
        "arxiv_references": ARXIV_REFERENCES,
    }


def list_capabilities() -> List[str]:
    """Return a list of capability names supported by this provider."""
    return [k for k, v in CAPABILITIES.items() if v]
