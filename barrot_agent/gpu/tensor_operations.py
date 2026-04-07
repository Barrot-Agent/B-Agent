"""
Tensor Operations - Matrix math, AI inference acceleration, AMP, batch processing.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TensorSpec:
    """Specification for a tensor."""
    shape: Tuple[int, ...] = ()
    dtype: str = "float32"
    device: str = "cpu"


class TensorOperations:
    """
    GPU-accelerated tensor operations using PyTorch when available.

    Falls back to pure-Python implementations for CPU environments.
    """

    def __init__(self, device: str = "cuda", use_amp: bool = True):
        self.device = device
        self.use_amp = use_amp
        self._torch_available = self._check_torch()
        if not self._torch_available:
            self.device = "cpu"

    def _check_torch(self) -> bool:
        try:
            import torch
            return True
        except ImportError:
            return False

    def create_tensor(
        self,
        data: List[Any],
        dtype: str = "float32",
        device: Optional[str] = None,
    ) -> Any:
        """Create a tensor from a list or nested list."""
        dev = device or self.device
        if self._torch_available:
            import torch
            dtype_map = {"float32": torch.float32, "float16": torch.float16, "int32": torch.int32}
            return torch.tensor(data, dtype=dtype_map.get(dtype, torch.float32), device=dev if torch.cuda.is_available() else "cpu")
        return data

    def matmul(self, a: Any, b: Any) -> Any:
        """Matrix multiplication."""
        if self._torch_available:
            import torch
            if isinstance(a, torch.Tensor) and isinstance(b, torch.Tensor):
                return torch.matmul(a, b)
        # Fallback: simple 2D matmul
        if isinstance(a, list) and isinstance(b, list):
            rows_a = len(a)
            cols_a = len(a[0]) if rows_a > 0 else 0
            cols_b = len(b[0]) if b else 0
            result = [[sum(a[i][k] * b[k][j] for k in range(cols_a)) for j in range(cols_b)] for i in range(rows_a)]
            return result
        return a

    def batch_inference(
        self, model: Any, inputs: List[Any], batch_size: int = 32
    ) -> List[Any]:
        """Run batched model inference."""
        results = []
        for i in range(0, len(inputs), batch_size):
            batch = inputs[i:i + batch_size]
            if callable(model):
                batch_result = model(batch)
            else:
                batch_result = batch
            if isinstance(batch_result, list):
                results.extend(batch_result)
            else:
                results.append(batch_result)
        return results

    def softmax(self, logits: List[float]) -> List[float]:
        """Compute softmax probabilities."""
        if self._torch_available:
            import torch
            t = torch.tensor(logits, dtype=torch.float32)
            return torch.softmax(t, dim=0).tolist()
        import math
        max_val = max(logits) if logits else 0.0
        exps = [math.exp(x - max_val) for x in logits]
        total = sum(exps)
        return [e / max(total, 1e-8) for e in exps]

    def normalize(self, tensor: List[float]) -> List[float]:
        """L2-normalize a vector."""
        import math
        norm = math.sqrt(sum(x * x for x in tensor))
        if norm < 1e-8:
            return tensor
        return [x / norm for x in tensor]

    def get_device_info(self) -> Dict[str, Any]:
        """Return current device information."""
        info: Dict[str, Any] = {"device": self.device, "amp": self.use_amp}
        if self._torch_available:
            import torch
            info["cuda_available"] = torch.cuda.is_available()
            if torch.cuda.is_available():
                info["gpu_name"] = torch.cuda.get_device_name(0)
        return info
