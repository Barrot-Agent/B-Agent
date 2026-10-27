"""
MCP GitHub Client
=================
Auto-commits generated Stupid Sindy episodes, metadata, and video files to
the repository, and triggers CI/CD workflow dispatches.

Uses only the GitHub REST API v3 via ``requests`` – no PyGithub dependency.

Workflow
--------
1. Read the file to commit from disk.
2. Encode as Base64.
3. Create/update the file via the Contents API.
4. Optionally dispatch a workflow (``workflow_dispatch``) to trigger CI/CD.

Usage
-----
    from mcp_github import GitHubMCP

    gh = GitHubMCP(token="ghp_…", owner="Barrot-Agent", repo="B-Agent")
    result = gh.commit_episode_video(episode_number=3, video_path="sindy_videos/ep03.mp4")
    ok = gh.trigger_cicd(workflow_id="sindy-mcp-cicd.yml", episode_number=3)
"""

from __future__ import annotations

import base64
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_API_BASE = "https://api.github.com"
_MAX_RETRIES = 3
_RETRY_DELAY = 2.0
_DEFAULT_TIMEOUT = 30
_DEFAULT_BRANCH = "Main"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class CommitResult:
    success: bool
    sha: Optional[str] = None
    html_url: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class WorkflowDispatchResult:
    success: bool
    workflow_id: str = ""
    error_message: Optional[str] = None


@dataclass
class CommitRecord:
    episode_number: int
    file_path: str
    commit_sha: Optional[str] = None
    committed_at: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class GitHubMCP:
    """MCP client for GitHub auto-commit and CI/CD trigger operations."""

    def __init__(
        self,
        token: Optional[str] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        branch: str = _DEFAULT_BRANCH,
    ) -> None:
        self._token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_PAT")
        self._owner = owner or os.environ.get("GITHUB_OWNER", "Barrot-Agent")
        self._repo = repo or os.environ.get("GITHUB_REPO", "B-Agent")
        self._branch = branch
        self._commit_history: List[CommitRecord] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _url(self, path: str) -> str:
        return f"{_API_BASE}{path}"

    def _repo_path(self) -> str:
        return f"/repos/{self._owner}/{self._repo}"

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = requests.get(
                    self._url(path),
                    headers=self._headers(),
                    params=params,
                    timeout=_DEFAULT_TIMEOUT,
                )
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as exc:
                logger.warning("GET %s attempt %d/%d: %s", path, attempt, _MAX_RETRIES, exc)
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_DELAY * attempt)
        raise RuntimeError(f"GitHub GET {path} failed after {_MAX_RETRIES} attempts")

    def _put(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = requests.put(
                    self._url(path),
                    headers=self._headers(),
                    json=payload,
                    timeout=_DEFAULT_TIMEOUT,
                )
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as exc:
                logger.warning("PUT %s attempt %d/%d: %s", path, attempt, _MAX_RETRIES, exc)
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_DELAY * attempt)
        raise RuntimeError(f"GitHub PUT {path} failed after {_MAX_RETRIES} attempts")

    def _post(self, path: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = requests.post(
                    self._url(path),
                    headers=self._headers(),
                    json=payload,
                    timeout=_DEFAULT_TIMEOUT,
                )
                resp.raise_for_status()
                # 204 No Content is valid for workflow dispatch
                if resp.status_code == 204:
                    return {}
                return resp.json()
            except requests.RequestException as exc:
                logger.warning("POST %s attempt %d/%d: %s", path, attempt, _MAX_RETRIES, exc)
                if attempt < _MAX_RETRIES:
                    time.sleep(_RETRY_DELAY * attempt)
        raise RuntimeError(f"GitHub POST {path} failed after {_MAX_RETRIES} attempts")

    def _is_configured(self) -> bool:
        return bool(self._token)

    def _get_existing_sha(self, repo_path: str) -> Optional[str]:
        """Return the blob SHA of an existing file, or None if not present."""
        try:
            data = self._get(
                f"{self._repo_path()}/contents/{repo_path}",
                params={"ref": self._branch},
            )
            return data.get("sha")
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_configured(self) -> bool:
        """Return True when a GitHub token is set."""
        return self._is_configured()

    def token_ok(self) -> bool:
        """Validate the token by calling the /user endpoint."""
        if not self._token:
            return False
        try:
            data = self._get("/user")
            return bool(data.get("login"))
        except Exception:
            return False

    def commit_file(
        self,
        local_path: str,
        repo_path: str,
        commit_message: str,
    ) -> CommitResult:
        """
        Create or update a file in the repository.

        Parameters
        ----------
        local_path:     Absolute or relative path to the file on disk.
        repo_path:      Path inside the repository (e.g. ``sindy_videos/ep01.mp4``).
        commit_message: Commit message string.
        """
        if not self._is_configured():
            return CommitResult(
                success=False,
                error_message="GitHub token not configured",
            )

        file_bytes = Path(local_path).read_bytes()
        content_b64 = base64.b64encode(file_bytes).decode()

        existing_sha = self._get_existing_sha(repo_path)

        payload: Dict[str, Any] = {
            "message": commit_message,
            "content": content_b64,
            "branch": self._branch,
        }
        if existing_sha:
            payload["sha"] = existing_sha

        try:
            data = self._put(f"{self._repo_path()}/contents/{repo_path}", payload)
            commit_info = data.get("commit", {})
            return CommitResult(
                success=True,
                sha=commit_info.get("sha"),
                html_url=commit_info.get("html_url"),
            )
        except Exception as exc:
            logger.error("commit_file %s failed: %s", repo_path, exc)
            return CommitResult(success=False, error_message=str(exc))

    def commit_episode_video(
        self,
        episode_number: int,
        video_path: str,
    ) -> CommitResult:
        """Commit the MP4 video for *episode_number* to the repository."""
        ep_str = f"{episode_number:02d}"
        repo_path = f"sindy_videos/ep{ep_str}.mp4"
        commit_msg = f"chore(sindy): add rendered video for episode {episode_number} [skip ci]"
        result = self.commit_file(video_path, repo_path, commit_msg)
        self._commit_history.append(
            CommitRecord(
                episode_number=episode_number,
                file_path=repo_path,
                commit_sha=result.sha,
                committed_at=time.time(),
                success=result.success,
                error_message=result.error_message,
            )
        )
        return result

    def commit_episode_metadata(
        self,
        episode_number: int,
        metadata: Dict[str, Any],
    ) -> CommitResult:
        """Commit episode metadata JSON to the repository."""
        import json
        import tempfile

        ep_str = f"{episode_number:02d}"
        repo_path = f"sindy_videos/ep{ep_str}_metadata.json"
        commit_msg = f"chore(sindy): add metadata for episode {episode_number} [skip ci]"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(metadata, tmp, indent=2)
            tmp_path = tmp.name

        try:
            result = self.commit_file(tmp_path, repo_path, commit_msg)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        self._commit_history.append(
            CommitRecord(
                episode_number=episode_number,
                file_path=repo_path,
                commit_sha=result.sha,
                committed_at=time.time(),
                success=result.success,
                error_message=result.error_message,
            )
        )
        return result

    def trigger_cicd(
        self,
        workflow_id: str = "sindy-mcp-cicd.yml",
        episode_number: Optional[int] = None,
        extra_inputs: Optional[Dict[str, str]] = None,
    ) -> WorkflowDispatchResult:
        """
        Trigger a ``workflow_dispatch`` event on *workflow_id*.

        Parameters
        ----------
        workflow_id:    Workflow file name (e.g. ``sindy-mcp-cicd.yml``).
        episode_number: Passed as a workflow input when provided.
        extra_inputs:   Additional key/value workflow inputs.
        """
        if not self._is_configured():
            return WorkflowDispatchResult(
                success=False,
                workflow_id=workflow_id,
                error_message="GitHub token not configured",
            )

        inputs: Dict[str, str] = {}
        if episode_number is not None:
            inputs["episode_number"] = str(episode_number)
        if extra_inputs:
            inputs.update(extra_inputs)

        payload: Dict[str, Any] = {"ref": self._branch}
        if inputs:
            payload["inputs"] = inputs

        path = f"{self._repo_path()}/actions/workflows/{workflow_id}/dispatches"
        try:
            self._post(path, payload)
            logger.info("Triggered workflow %s (ep=%s)", workflow_id, episode_number)
            return WorkflowDispatchResult(success=True, workflow_id=workflow_id)
        except Exception as exc:
            logger.error("trigger_cicd %s failed: %s", workflow_id, exc)
            return WorkflowDispatchResult(
                success=False,
                workflow_id=workflow_id,
                error_message=str(exc),
            )

    def commit_history(self) -> List[CommitRecord]:
        """Return the list of commits made during this session."""
        return list(self._commit_history)

    def latest_workflow_runs(
        self,
        workflow_id: str = "sindy-mcp-cicd.yml",
        per_page: int = 5,
    ) -> List[Dict[str, Any]]:
        """Return the most recent runs for *workflow_id*."""
        try:
            data = self._get(
                f"{self._repo_path()}/actions/workflows/{workflow_id}/runs",
                params={"per_page": per_page, "branch": self._branch},
            )
            return data.get("workflow_runs", [])
        except Exception as exc:
            logger.error("latest_workflow_runs failed: %s", exc)
            return []
