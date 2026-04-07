"""Endpoint health monitor — background async health checks for inference endpoints."""

from __future__ import annotations

import logging
import threading
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class EndpointHealthMonitor:
    """Continuously monitor the health of inference endpoints.

    A background daemon thread probes each registered endpoint at a
    configurable interval.  Health results are stored in memory and can be
    queried at any time.

    Example::

        monitor = EndpointHealthMonitor()
        monitor.check_health("local_gpu", "http://localhost:8000/health")
        status = monitor.get_health_status("local_gpu")
        monitor.start_monitoring(interval_seconds=30)
        # ... later ...
        monitor.stop_monitoring()
    """

    def __init__(self) -> None:
        self._statuses: Dict[str, Dict[str, Any]] = {}
        self._endpoints: Dict[str, str] = {}  # name → url
        self._lock = threading.Lock()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # One-shot health check
    # ------------------------------------------------------------------

    def check_health(self, endpoint_name: str, endpoint_url: str) -> Dict[str, Any]:
        """Perform a synchronous HTTP health check.

        Attempts a GET request to *endpoint_url*.  The endpoint is considered
        **healthy** when the HTTP response status is 2xx, **degraded** for 5xx,
        and **unhealthy** for connection errors.

        Args:
            endpoint_name: Identifier to store the result under.
            endpoint_url:  URL to probe (e.g. ``"http://localhost:8000/health"``).

        Returns:
            Status dict with keys ``status``, ``latency_ms``, ``checked_at``,
            ``error`` (optional).
        """
        with self._lock:
            self._endpoints[endpoint_name] = endpoint_url

        start = time.monotonic()
        status_info: Dict[str, Any] = {
            "endpoint": endpoint_name,
            "url": endpoint_url,
            "checked_at": datetime.now(tz=timezone.utc).isoformat(),
        }

        try:
            req = urllib.request.Request(endpoint_url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                latency_ms = (time.monotonic() - start) * 1000
                http_status = resp.status
                if 200 <= http_status < 300:
                    status_info.update(
                        {"status": "healthy", "latency_ms": round(latency_ms, 2)}
                    )
                else:
                    status_info.update(
                        {
                            "status": "degraded",
                            "latency_ms": round(latency_ms, 2),
                            "http_status": http_status,
                        }
                    )
        except urllib.error.HTTPError as exc:
            latency_ms = (time.monotonic() - start) * 1000
            status_info.update(
                {
                    "status": "degraded",
                    "latency_ms": round(latency_ms, 2),
                    "error": str(exc),
                    "http_status": exc.code,
                }
            )
        except Exception as exc:
            latency_ms = (time.monotonic() - start) * 1000
            status_info.update(
                {
                    "status": "unhealthy",
                    "latency_ms": round(latency_ms, 2),
                    "error": str(exc),
                }
            )

        with self._lock:
            self._statuses[endpoint_name] = status_info

        logger.debug(
            "Health check %s → %s (%.1fms)",
            endpoint_name,
            status_info["status"],
            status_info.get("latency_ms", 0),
        )
        return status_info

    # ------------------------------------------------------------------
    # Status retrieval
    # ------------------------------------------------------------------

    def get_health_status(self, endpoint_name: str) -> Optional[Dict[str, Any]]:
        """Return the latest health status for *endpoint_name*, or ``None``.

        Args:
            endpoint_name: Registered endpoint identifier.
        """
        with self._lock:
            return dict(self._statuses[endpoint_name]) if endpoint_name in self._statuses else None

    def get_all_health_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Return a snapshot of all known endpoint statuses."""
        with self._lock:
            return {k: dict(v) for k, v in self._statuses.items()}

    # ------------------------------------------------------------------
    # Background monitoring
    # ------------------------------------------------------------------

    def start_monitoring(self, interval_seconds: int = 30) -> None:
        """Start the background health-check thread.

        Args:
            interval_seconds: Seconds between check rounds.

        Raises:
            RuntimeError: If monitoring is already running.
        """
        if self._monitor_thread and self._monitor_thread.is_alive():
            raise RuntimeError("Health monitoring is already running")
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            name="endpoint-health-monitor",
            daemon=True,
        )
        self._monitor_thread.start()
        logger.info(
            "Endpoint health monitoring started (interval=%ds)", interval_seconds
        )

    def stop_monitoring(self) -> None:
        """Stop the background health-check thread gracefully."""
        self._stop_event.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=10)
        logger.info("Endpoint health monitoring stopped")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _monitor_loop(self, interval_seconds: int) -> None:
        while not self._stop_event.wait(timeout=interval_seconds):
            with self._lock:
                endpoints_snapshot = dict(self._endpoints)
            for name, url in endpoints_snapshot.items():
                try:
                    self.check_health(name, url)
                except Exception as exc:  # noqa: BLE001
                    logger.error("Health check error for '%s': %s", name, exc)
