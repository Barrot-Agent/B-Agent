"""Remote endpoint manager — send requests to external inference APIs with retries."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error
import json

logger = logging.getLogger(__name__)


class RemoteRequestError(RuntimeError):
    """Raised when a remote inference request fails after all retries."""


class RemoteEndpointManager:
    """Manage outbound requests to remote inference endpoints.

    Example::

        config = {
            "huggingface_api": {
                "url": "https://api-inference.huggingface.co",
                "token_env_var": "HF_TOKEN",
                "data_anonymization": True,
            }
        }
        rem = RemoteEndpointManager(config)
        result = rem.send_request("huggingface_api", "gpt2", {"inputs": "Hello"})
    """

    _DEFAULT_RETRIES = 3
    _DEFAULT_BACKOFF = 2.0  # seconds

    def __init__(self, endpoints_config: Dict[str, Any]) -> None:
        self._config = endpoints_config
        self._metrics: Dict[str, Dict[str, Any]] = {
            name: {"requests": 0, "errors": 0, "retries": 0, "last_latency_ms": 0.0}
            for name in endpoints_config
        }

    # ------------------------------------------------------------------
    # Request dispatch
    # ------------------------------------------------------------------

    def send_request(
        self,
        endpoint_name: str,
        model: str,
        inputs: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Send an inference request to *endpoint_name*.

        Args:
            endpoint_name: Registered endpoint identifier.
            model:         Model name / path.
            inputs:        Inference payload.
            headers:       Additional HTTP headers.

        Returns:
            Parsed JSON response dict.

        Raises:
            RemoteRequestError: On final failure after retries.
        """
        cfg = self._config.get(endpoint_name, {})
        if not cfg:
            raise RemoteRequestError(f"Unknown endpoint '{endpoint_name}'")

        base_url: str = cfg.get("url", "")
        token_env: Optional[str] = cfg.get("token_env_var")
        token: Optional[str] = None
        if token_env:
            import os
            token = os.environ.get(token_env)

        url = f"{base_url}/models/{model}"
        request_headers = {"Content-Type": "application/json"}
        if token:
            request_headers["Authorization"] = f"Bearer {token}"
        if headers:
            request_headers.update(headers)

        payload = json.dumps(inputs).encode("utf-8")
        last_exc: Optional[Exception] = None

        for attempt in range(self._DEFAULT_RETRIES):
            start = time.monotonic()
            try:
                req = urllib.request.Request(
                    url, data=payload, headers=request_headers, method="POST"
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    response_body = resp.read().decode("utf-8")
                    latency_ms = (time.monotonic() - start) * 1000
                    self._metrics[endpoint_name]["requests"] += 1
                    self._metrics[endpoint_name]["last_latency_ms"] = round(
                        latency_ms, 2
                    )
                    return json.loads(response_body)

            except urllib.error.HTTPError as exc:
                last_exc = exc
                self._metrics[endpoint_name]["errors"] += 1
                if exc.code in (429, 503):
                    backoff = self._DEFAULT_BACKOFF * (2 ** attempt)
                    logger.warning(
                        "Endpoint '%s' returned %s, retrying in %.1fs (attempt %d/%d)",
                        endpoint_name, exc.code, backoff, attempt + 1, self._DEFAULT_RETRIES,
                    )
                    self._metrics[endpoint_name]["retries"] += 1
                    time.sleep(backoff)
                else:
                    break  # Non-retriable HTTP error
            except Exception as exc:
                last_exc = exc
                self._metrics[endpoint_name]["errors"] += 1
                logger.error("Request to '%s' failed: %s", endpoint_name, exc)
                break

        raise RemoteRequestError(
            f"All {self._DEFAULT_RETRIES} attempts to '{endpoint_name}' failed: {last_exc}"
        )

    def handle_retry(self, endpoint_name: str, error: Exception) -> bool:
        """Decide and record whether the error warrants a retry.

        Args:
            endpoint_name: Endpoint that encountered the error.
            error:         The exception that was raised.

        Returns:
            ``True`` if a retry is recommended, ``False`` otherwise.
        """
        retriable = isinstance(error, (urllib.error.URLError, TimeoutError))
        if retriable and endpoint_name in self._metrics:
            self._metrics[endpoint_name]["retries"] += 1
        return retriable

    def get_endpoint_metrics(self, endpoint_name: str) -> Dict[str, Any]:
        """Return performance metrics for *endpoint_name*.

        Args:
            endpoint_name: Registered endpoint identifier.

        Returns:
            Dict with ``requests``, ``errors``, ``retries``,
            ``last_latency_ms``.
        """
        return dict(self._metrics.get(endpoint_name, {}))

    def rotate_endpoint(self, model_name: str) -> Optional[str]:
        """Select the next available healthy endpoint for *model_name*.

        Simple rotation: picks the endpoint with the fewest errors.

        Args:
            model_name: Model identifier (currently informational only).

        Returns:
            The name of the selected endpoint, or ``None`` if none are
            configured.
        """
        if not self._config:
            return None
        # Sort by ascending error count
        ranked = sorted(
            self._config.keys(),
            key=lambda n: self._metrics.get(n, {}).get("errors", 0),
        )
        return ranked[0] if ranked else None
