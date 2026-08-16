"""
MCP Databricks Client
=====================
Offloads Stupid Sindy video rendering to a Databricks cluster for
parallel processing.  Uses the Databricks REST API (Jobs API v2.1) via
plain ``requests`` – no extra SDK required.

Workflow
--------
1. Upload the rendering notebook / script to the workspace.
2. Submit a one-time job run (``runs/submit``).
3. Poll the run until it reaches a terminal state.
4. Retrieve any output artefacts via DBFS.

Usage
-----
    from mcp_databricks import DatabricksMCP

    db = DatabricksMCP(host="https://my.azuredatabricks.net", token="dapi…")
    run_id = db.submit_render_job(episode_number=3)
    state  = db.wait_for_run(run_id, poll_interval=10)
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MAX_RETRIES = 3
_RETRY_DELAY = 2.0
_DEFAULT_POLL_INTERVAL = 15  # seconds
_DEFAULT_TIMEOUT = 30  # seconds for HTTP requests

# Databricks Life Cycle States that indicate a completed run
_TERMINAL_STATES = {"TERMINATED", "SKIPPED", "INTERNAL_ERROR"}
_SUCCESS_RESULT = "SUCCESS"


# ---------------------------------------------------------------------------
# Status types
# ---------------------------------------------------------------------------


class JobRunState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


@dataclass
class RenderJobState:
    episode_number: int
    run_id: Optional[int] = None
    job_state: JobRunState = JobRunState.PENDING
    lifecycle_state: str = ""
    result_state: str = ""
    error_message: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    run_page_url: Optional[str] = None

    @property
    def elapsed(self) -> Optional[float]:
        if self.started_at is None:
            return None
        end = self.completed_at or time.time()
        return end - self.started_at

    @property
    def is_terminal(self) -> bool:
        return self.job_state in (
            JobRunState.COMPLETE,
            JobRunState.FAILED,
            JobRunState.CANCELLED,
        )


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class DatabricksMCP:
    """MCP client for Databricks compute integration."""

    def __init__(
        self,
        host: Optional[str] = None,
        token: Optional[str] = None,
        cluster_id: Optional[str] = None,
        dbfs_output_dir: str = "/sindy_videos",
    ) -> None:
        self._host = (host or os.environ.get("DATABRICKS_HOST", "")).rstrip("/")
        self._token = token or os.environ.get("DATABRICKS_TOKEN", "")
        self._cluster_id = cluster_id or os.environ.get("DATABRICKS_CLUSTER_ID", "")
        self._dbfs_output_dir = dbfs_output_dir
        self._job_states: Dict[int, RenderJobState] = {}  # keyed by episode_number

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def _api(self, path: str) -> str:
        return f"{self._host}/api/2.1{path}"

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = self._api(path)
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = requests.get(
                    url,
                    headers=self._headers(),
                    params=params,
                    timeout=_DEFAULT_TIMEOUT,
                )
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as exc:
                logger.warning("GET %s attempt %d/%d failed: %s", path, attempt, _MAX_RETRIES, exc)
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_DELAY * attempt)
        raise RuntimeError(f"Databricks GET {path} failed after {_MAX_RETRIES} attempts")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self._api(path)
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = requests.post(
                    url,
                    headers=self._headers(),
                    json=payload,
                    timeout=_DEFAULT_TIMEOUT,
                )
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as exc:
                logger.warning("POST %s attempt %d/%d failed: %s", path, attempt, _MAX_RETRIES, exc)
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_DELAY * attempt)
        raise RuntimeError(f"Databricks POST {path} failed after {_MAX_RETRIES} attempts")

    def _is_configured(self) -> bool:
        return bool(self._host and self._token)

    @staticmethod
    def _map_lifecycle(lifecycle: str, result: str) -> JobRunState:
        if lifecycle in _TERMINAL_STATES:
            if result == _SUCCESS_RESULT:
                return JobRunState.COMPLETE
            if lifecycle == "SKIPPED":
                return JobRunState.CANCELLED
            return JobRunState.FAILED
        if lifecycle in {"RUNNING", "TERMINATING"}:
            return JobRunState.RUNNING
        return JobRunState.PENDING

    def _render_notebook_path(self) -> str:
        return "/Shared/sindy_render_episode"

    def _build_notebook_task(self, episode_number: int) -> Dict[str, Any]:
        task: Dict[str, Any] = {
            "notebook_task": {
                "notebook_path": self._render_notebook_path(),
                "base_parameters": {
                    "episode_number": str(episode_number),
                    "output_dir": self._dbfs_output_dir,
                },
            }
        }
        if self._cluster_id:
            task["existing_cluster_id"] = self._cluster_id
        else:
            task["new_cluster"] = {
                "spark_version": "13.3.x-cpu-ml-scala2.12",
                "node_type_id": "i3.xlarge",
                "num_workers": 2,
            }
        return task

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_configured(self) -> bool:
        """Return True when host and token are both set."""
        return self._is_configured()

    def cluster_list(self) -> List[Dict[str, Any]]:
        """List available clusters.  Returns [] when not configured."""
        if not self._is_configured():
            logger.warning("Databricks not configured; skipping cluster_list.")
            return []
        try:
            data = self._get("/clusters/list")
            return data.get("clusters", [])
        except Exception as exc:
            logger.error("cluster_list failed: %s", exc)
            return []

    def submit_render_job(self, episode_number: int) -> Optional[int]:
        """
        Submit a Databricks notebook run to render *episode_number*.

        Returns the ``run_id`` (int) or None on failure.
        """
        state = RenderJobState(episode_number=episode_number, started_at=time.time())
        self._job_states[episode_number] = state

        if not self._is_configured():
            state.job_state = JobRunState.FAILED
            state.error_message = "Databricks host/token not configured"
            logger.warning("Databricks not configured; cannot submit job.")
            return None

        payload: Dict[str, Any] = {
            "run_name": f"sindy_render_ep{episode_number}",
            "tasks": [
                {
                    "task_key": f"render_ep{episode_number}",
                    **self._build_notebook_task(episode_number),
                }
            ],
        }

        try:
            resp = self._post("/jobs/runs/submit", payload)
            run_id: int = resp["run_id"]
            state.run_id = run_id
            state.job_state = JobRunState.RUNNING
            logger.info("Submitted Databricks run %d for episode %d", run_id, episode_number)
            return run_id
        except Exception as exc:
            state.job_state = JobRunState.FAILED
            state.error_message = str(exc)
            logger.error("submit_render_job failed: %s", exc)
            return None

    def poll_run(self, run_id: int) -> RenderJobState:
        """
        Fetch the current state of *run_id* from Databricks.

        Updates the internal state and returns it.
        """
        # Find matching state object
        state = next(
            (s for s in self._job_states.values() if s.run_id == run_id),
            RenderJobState(episode_number=-1, run_id=run_id),
        )

        if not self._is_configured():
            state.job_state = JobRunState.UNKNOWN
            return state

        try:
            data = self._get("/jobs/runs/get", params={"run_id": run_id})
            lifecycle = data.get("state", {}).get("life_cycle_state", "")
            result = data.get("state", {}).get("result_state", "")
            state.lifecycle_state = lifecycle
            state.result_state = result
            state.job_state = self._map_lifecycle(lifecycle, result)
            state.run_page_url = data.get("run_page_url")
            if state.is_terminal:
                state.completed_at = time.time()
                if state.job_state == JobRunState.FAILED:
                    state.error_message = data.get("state", {}).get(
                        "state_message", "Unknown error"
                    )
        except Exception as exc:
            logger.error("poll_run(%d) failed: %s", run_id, exc)
            state.job_state = JobRunState.UNKNOWN
            state.error_message = str(exc)

        return state

    def wait_for_run(
        self,
        run_id: int,
        poll_interval: int = _DEFAULT_POLL_INTERVAL,
        timeout: int = 3600,
    ) -> RenderJobState:
        """
        Block until *run_id* reaches a terminal state or *timeout* seconds
        elapse.  Polls every *poll_interval* seconds.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            state = self.poll_run(run_id)
            logger.info(
                "Run %d: lifecycle=%s result=%s",
                run_id,
                state.lifecycle_state,
                state.result_state,
            )
            if state.is_terminal:
                return state
            time.sleep(poll_interval)

        # Timeout
        state = self.poll_run(run_id)
        state.job_state = JobRunState.FAILED
        state.error_message = f"Timed out after {timeout}s"
        return state

    def cancel_run(self, run_id: int) -> bool:
        """Cancel a running Databricks job.  Returns True on success."""
        if not self._is_configured():
            return False
        try:
            self._post("/jobs/runs/cancel", {"run_id": run_id})
            state = next((s for s in self._job_states.values() if s.run_id == run_id), None)
            if state:
                state.job_state = JobRunState.CANCELLED
                state.completed_at = time.time()
            logger.info("Cancelled run %d", run_id)
            return True
        except Exception as exc:
            logger.error("cancel_run(%d) failed: %s", run_id, exc)
            return False

    def get_job_state(self, episode_number: int) -> Optional[RenderJobState]:
        """Return the latest tracked job state for *episode_number*."""
        return self._job_states.get(episode_number)

    def all_job_states(self) -> Dict[int, RenderJobState]:
        """Return a snapshot of all tracked job states keyed by episode number."""
        return dict(self._job_states)
