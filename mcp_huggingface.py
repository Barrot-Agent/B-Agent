"""
MCP Hugging Face Client
=======================
Manages AI model downloads and caching for the Stupid Sindy video generation
pipeline.  Wraps the ``huggingface_hub`` library with retry logic, progress
reporting, and graceful degradation when the token is absent.

Typical models used by the pipeline
-------------------------------------
* ``stabilityai/stable-diffusion-2-1``   – scene image generation
* ``microsoft/speecht5_tts``             – text-to-speech dialogue
* ``openai/whisper-base``                – transcription / subtitle alignment

Usage
-----
    from mcp_huggingface import HuggingFaceMCP

    hf = HuggingFaceMCP(token="hf_...")
    info = hf.model_info("microsoft/speecht5_tts")
    path = hf.ensure_model("microsoft/speecht5_tts")
    status = hf.get_download_status("microsoft/speecht5_tts")
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_CACHE_DIR = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
_MAX_RETRIES = 3
_RETRY_DELAY = 2.0  # seconds

# Models required by the Stupid Sindy pipeline
SINDY_MODELS: List[str] = [
    "stabilityai/stable-diffusion-2-1",
    "microsoft/speecht5_tts",
    "openai/whisper-base",
]


# ---------------------------------------------------------------------------
# Status types
# ---------------------------------------------------------------------------


class DownloadStatus(str, Enum):
    NOT_CACHED = "not_cached"
    DOWNLOADING = "downloading"
    CACHED = "cached"
    ERROR = "error"


@dataclass
class ModelDownloadState:
    model_id: str
    status: DownloadStatus = DownloadStatus.NOT_CACHED
    progress: float = 0.0  # 0.0 – 1.0
    local_path: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    @property
    def elapsed(self) -> Optional[float]:
        if self.started_at is None:
            return None
        end = self.completed_at or time.time()
        return end - self.started_at


@dataclass
class HFModelInfo:
    model_id: str
    author: str
    tags: List[str] = field(default_factory=list)
    pipeline_tag: Optional[str] = None
    downloads: int = 0
    likes: int = 0


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class HuggingFaceMCP:
    """MCP client for Hugging Face model management."""

    def __init__(
        self,
        token: Optional[str] = None,
        cache_dir: Optional[Path] = None,
    ) -> None:
        self._token = token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
        self._cache_dir = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR
        self._states: Dict[str, ModelDownloadState] = {}

        self._hf_hub = self._load_hf_hub()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_hf_hub(self):
        """Lazily import huggingface_hub; returns None when unavailable."""
        try:
            import huggingface_hub as hub  # noqa: F401

            return hub
        except ImportError:
            logger.warning(
                "huggingface_hub is not installed. " "Install it with: pip install huggingface_hub"
            )
            return None

    def _is_available(self) -> bool:
        return self._hf_hub is not None

    def _get_state(self, model_id: str) -> ModelDownloadState:
        if model_id not in self._states:
            self._states[model_id] = ModelDownloadState(model_id=model_id)
        return self._states[model_id]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def model_info(self, model_id: str) -> Optional[HFModelInfo]:
        """Fetch metadata for *model_id* from the Hub.  Returns None on failure."""
        if not self._is_available():
            logger.warning("huggingface_hub unavailable; cannot fetch model info.")
            return None

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                info = self._hf_hub.model_info(model_id, token=self._token)  # type: ignore[union-attr]
                return HFModelInfo(
                    model_id=model_id,
                    author=info.author or "",
                    tags=list(info.tags or []),
                    pipeline_tag=info.pipeline_tag,
                    downloads=getattr(info, "downloads", 0) or 0,
                    likes=getattr(info, "likes", 0) or 0,
                )
            except Exception as exc:
                logger.warning("model_info attempt %d/%d failed: %s", attempt, _MAX_RETRIES, exc)
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_DELAY * attempt)
        return None

    def is_cached(self, model_id: str) -> bool:
        """Return True if *model_id* is present in the local cache."""
        if not self._is_available():
            return False
        try:
            self._hf_hub.snapshot_download(  # type: ignore[union-attr]
                model_id,
                token=self._token,
                cache_dir=str(self._cache_dir),
                local_files_only=True,
            )
            return True
        except Exception:
            return False

    def ensure_model(self, model_id: str) -> Optional[str]:
        """
        Download *model_id* if not already cached.

        Returns the local snapshot directory path, or None on failure.
        Updates the internal :class:`ModelDownloadState` for progress tracking.
        """
        state = self._get_state(model_id)

        if state.status == DownloadStatus.CACHED and state.local_path:
            logger.info("Model %s already cached at %s", model_id, state.local_path)
            return state.local_path

        if not self._is_available():
            state.status = DownloadStatus.ERROR
            state.error_message = "huggingface_hub not installed"
            return None

        state.status = DownloadStatus.DOWNLOADING
        state.started_at = time.time()
        state.progress = 0.0
        logger.info("Downloading model %s …", model_id)

        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                local_path = self._hf_hub.snapshot_download(  # type: ignore[union-attr]
                    model_id,
                    token=self._token,
                    cache_dir=str(self._cache_dir),
                )
                state.status = DownloadStatus.CACHED
                state.local_path = str(local_path)
                state.progress = 1.0
                state.completed_at = time.time()
                logger.info("Model %s cached at %s", model_id, local_path)
                return str(local_path)
            except Exception as exc:
                logger.warning(
                    "Download attempt %d/%d for %s failed: %s",
                    attempt,
                    _MAX_RETRIES,
                    model_id,
                    exc,
                )
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_DELAY * attempt)

        state.status = DownloadStatus.ERROR
        state.error_message = f"Download failed after {_MAX_RETRIES} attempts"
        return None

    def ensure_sindy_models(self) -> Dict[str, Optional[str]]:
        """Download all models required by the Stupid Sindy pipeline."""
        results: Dict[str, Optional[str]] = {}
        for model_id in SINDY_MODELS:
            results[model_id] = self.ensure_model(model_id)
        return results

    def get_download_status(self, model_id: str) -> ModelDownloadState:
        """Return the current download state for *model_id*."""
        return self._get_state(model_id)

    def all_states(self) -> Dict[str, ModelDownloadState]:
        """Return a snapshot of all tracked model states."""
        return dict(self._states)

    def token_ok(self) -> bool:
        """Return True when a valid HF token is configured."""
        if not self._token:
            return False
        if not self._is_available():
            return False
        try:
            whoami = self._hf_hub.whoami(token=self._token)  # type: ignore[union-attr]
            return bool(whoami)
        except Exception:
            return False
