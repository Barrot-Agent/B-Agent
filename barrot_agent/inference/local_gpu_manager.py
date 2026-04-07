"""Local GPU inference manager — detect GPUs and run models on NVIDIA hardware."""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional CUDA/torch dependency — gracefully degrade when unavailable
# ---------------------------------------------------------------------------
try:
    import torch  # type: ignore

    _HAS_TORCH = True
except ImportError:
    _HAS_TORCH = False


class GPUNotAvailableError(RuntimeError):
    """Raised when no suitable GPU is found for the requested workload."""


class LocalGPUManager:
    """Detect and manage NVIDIA GPU resources for local inference.

    Supports H100, B200, A100, and RTX series GPUs.  When ``torch`` is not
    installed the manager operates in *simulation mode* — GPUs are reported as
    unavailable and all inference calls raise :class:`GPUNotAvailableError`.

    Example::

        gm = LocalGPUManager()
        gpus = gm.detect_gpus()
        gpu_id = gm.get_available_gpu(required_memory_gb=8)
        result = gm.run_inference("llama3", {"prompt": "hello"}, gpu_id=gpu_id)
    """

    _SUPPORTED_SERIES = ("H100", "B200", "A100", "A30", "RTX", "Tesla")

    def __init__(self) -> None:
        self._gpu_cache: Optional[List[Dict[str, Any]]] = None
        self._loaded_models: Dict[str, Any] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # GPU discovery
    # ------------------------------------------------------------------

    def detect_gpus(self) -> List[Dict[str, Any]]:
        """Detect available NVIDIA GPUs.

        Returns:
            A list of dicts, each with keys ``id``, ``name``,
            ``total_memory_gb``, ``free_memory_gb``, ``supported``.
        """
        with self._lock:
            if self._gpu_cache is not None:
                return list(self._gpu_cache)

        gpus: List[Dict[str, Any]] = []
        if _HAS_TORCH and torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                total_gb = props.total_memory / (1024 ** 3)
                free_gb = (
                    props.total_memory - torch.cuda.memory_allocated(i)
                ) / (1024 ** 3)
                supported = any(s in props.name for s in self._SUPPORTED_SERIES)
                gpus.append(
                    {
                        "id": i,
                        "name": props.name,
                        "total_memory_gb": round(total_gb, 2),
                        "free_memory_gb": round(free_gb, 2),
                        "supported": supported,
                    }
                )
        else:
            logger.info(
                "CUDA unavailable — LocalGPUManager operating in simulation mode"
            )

        with self._lock:
            self._gpu_cache = gpus
        return gpus

    def get_available_gpu(
        self, required_memory_gb: Optional[float] = None
    ) -> Optional[int]:
        """Return the ID of a GPU with sufficient free memory.

        Args:
            required_memory_gb: Minimum free memory required; ``None`` means
                                 any GPU will do.

        Returns:
            Integer GPU index, or ``None`` if no GPU qualifies.
        """
        gpus = self.detect_gpus()
        for gpu in sorted(gpus, key=lambda g: g["free_memory_gb"], reverse=True):
            if not gpu.get("supported", False):
                continue
            if required_memory_gb is None or gpu["free_memory_gb"] >= required_memory_gb:
                return gpu["id"]
        return None

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def run_inference(
        self,
        model_name: str,
        inputs: Dict[str, Any],
        gpu_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Run inference for *model_name* on the specified (or auto-selected) GPU.

        Args:
            model_name: Name of the model to use.
            inputs:     Model input dict.
            gpu_id:     Specific GPU to use; ``None`` for auto-selection.

        Returns:
            A dict with keys ``model``, ``gpu_id``, ``output``, ``status``.

        Raises:
            GPUNotAvailableError: When no suitable GPU is found.
        """
        if gpu_id is None:
            gpu_id = self.get_available_gpu()
        if gpu_id is None:
            raise GPUNotAvailableError(
                f"No suitable GPU available for model '{model_name}'"
            )
        model = self._loaded_models.get(model_name)
        if model is None:
            model = self.load_model(model_name, gpu_id=gpu_id)

        logger.info("Running inference: model=%s gpu=%s", model_name, gpu_id)
        # Actual inference delegated to the loaded model object
        if hasattr(model, "__call__"):
            try:
                output = model(**inputs)
            except Exception as exc:
                return {
                    "model": model_name,
                    "gpu_id": gpu_id,
                    "output": None,
                    "status": "error",
                    "error": str(exc),
                }
        else:
            output = {"result": "model_not_callable"}

        return {
            "model": model_name,
            "gpu_id": gpu_id,
            "output": output,
            "status": "success",
        }

    def load_model(
        self, model_name: str, gpu_id: Optional[int] = None
    ) -> Any:
        """Load *model_name* onto *gpu_id* (or CPU) and cache it.

        Args:
            model_name: HuggingFace model identifier or local path.
            gpu_id:     Target GPU index; ``None`` uses CPU.

        Returns:
            The loaded model object (or a placeholder dict in simulation mode).
        """
        with self._lock:
            if model_name in self._loaded_models:
                return self._loaded_models[model_name]

        logger.info("Loading model '%s' on gpu=%s", model_name, gpu_id)

        if _HAS_TORCH:
            try:
                from transformers import pipeline  # type: ignore

                device = gpu_id if gpu_id is not None else -1
                model = pipeline("text-generation", model=model_name, device=device)
            except Exception as exc:
                logger.warning("Could not load model '%s': %s", model_name, exc)
                model = {"name": model_name, "status": "load_failed"}
        else:
            model = {"name": model_name, "status": "simulation"}

        with self._lock:
            self._loaded_models[model_name] = model
        return model

    def get_gpu_stats(self) -> List[Dict[str, Any]]:
        """Return current GPU statistics (refreshes the cache).

        Returns:
            Fresh list of GPU info dicts (same schema as :meth:`detect_gpus`).
        """
        with self._lock:
            self._gpu_cache = None  # Force refresh
        return self.detect_gpus()
